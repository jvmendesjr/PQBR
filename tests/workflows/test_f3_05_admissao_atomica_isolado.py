"""Opt-in: servidor efêmero sem rede externa, somente dados/Activities sintéticos."""
import asyncio
from contextlib import AsyncExitStack
from datetime import timedelta
import json
import os
from pathlib import Path
import socket
import time
import unittest
import uuid

from temporalio import activity
from temporalio.client import Client, WorkflowFailureError, WorkflowHistory, WorkflowUpdateFailedError
from temporalio.exceptions import ApplicationError, TimeoutError, WorkflowAlreadyStartedError
from temporalio.api.enums.v1 import TimeoutType
from temporalio.runtime import Runtime, TelemetryConfig
from temporalio.service import RPCError, RPCStatusCode
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Replayer, Worker
from tests.workflows.prototipo_admissao_atomica import AtorSessaoAtomicoSintetico, admitir_atomico, ator_id

SERVER = Path("/tmp/temporal-test-server-sdk-python-1.34.0")
OPT_IN = os.environ.get("PQBR_TEMPORAL_ISOLADO") == "1"


class Falsa:
    def __init__(self):
        self.liberar = asyncio.Event()
        self.calls = []
        self.ativos = 0
        self.max_global = 0
        self.por_sessao = {}
        self.max_sessao = {}

    @activity.defn(name="intervir_camofox_sintetico_v1")
    async def intervir(self, pedido: dict) -> dict:
        info = activity.info()
        sessao = pedido["sessao"]
        self.ativos += 1
        self.max_global = max(self.max_global, self.ativos)
        self.por_sessao[sessao] = self.por_sessao.get(sessao, 0) + 1
        self.max_sessao[sessao] = max(self.max_sessao.get(sessao, 0), self.por_sessao[sessao])
        call = dict(pedido=pedido, inicio=time.monotonic(), fim=None, fila=info.task_queue,
                    workflow_id=info.workflow_id, attempt=info.attempt)
        self.calls.append(call)
        try:
            await self.liberar.wait()
            if pedido["falhar"]:
                raise ApplicationError("falha tecnica sintetica", type="FalhaTecnicaSintetica")
            return {"sintetico": True}
        finally:
            call["fim"] = time.monotonic()
            self.ativos -= 1
            self.por_sessao[sessao] -= 1


@unittest.skipUnless(OPT_IN, "exige runner opt-in com namespace isolado")
class AdmissaoAtomicaTemporalIsolada(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.assertNotEqual(os.readlink("/proc/self/ns/net"), os.environ["PQBR_HOST_NETNS"])
        self.assertEqual([name for _, name in socket.if_nameindex()], ["lo"])
        self.assertEqual(len(Path("/proc/net/route").read_text().splitlines()), 1)
        self.out = Path(os.environ["PQBR_TEMPORAL_EVIDENCIAS"])
        self.env = await WorkflowEnvironment.start_time_skipping(test_server_existing_path=str(SERVER))
        self.addAsyncCleanup(self.env.shutdown)
        self.handles = []
        self.stack = AsyncExitStack()
        self.addAsyncCleanup(self.stack.aclose)
        self.addAsyncCleanup(self.limpar)
        self.falsa = Falsa()
        suffix = uuid.uuid4().hex
        self.fila_wf = "teste-ator-workflow-" + suffix
        self.fila_atividade = "teste-camofox-ator-" + suffix
        self.clients = []
        for _ in range(2):
            client = await Client.connect(self.env.client.service_client.config.target_host,
                                          runtime=Runtime(telemetry=TelemetryConfig()))
            self.clients.append(client)
            await self.stack.enter_async_context(Worker(
                client, task_queue=self.fila_wf, workflows=[AtorSessaoAtomicoSintetico],
                max_cached_workflows=0, graceful_shutdown_timeout=timedelta(seconds=1)))

    async def limpar(self):
        self.falsa.liberar.set()
        for h in self.handles:
            d = await h.describe()
            if d.status.name == "RUNNING":
                await h.terminate("cleanup exclusivo do teste sintetico")

    async def consumidores(self):
        for client in self.clients:
            await self.stack.enter_async_context(Worker(
                client, task_queue=self.fila_atividade, activities=[self.falsa.intervir],
                max_concurrent_activities=4, graceful_shutdown_timeout=timedelta(seconds=1)))

    async def admitir(self, chave, sessao="sessao-A", falhar=False, client=None,
                       prazo_s=10, fila_workflow=None, fila_camofox=None):
        # Registrar handle mesmo se a resposta se perder ou o Update for rejeitado.
        h = self.env.client.get_workflow_handle(ator_id(sessao))
        if not any(x.id == h.id for x in self.handles):
            self.handles.append(h)
        return await admitir_atomico(
            client or self.env.client, sessao, fila_workflow or self.fila_wf,
            fila_camofox or self.fila_atividade,
            dict(id=chave, sessao=sessao, falhar=falhar), prazo_s=prazo_s)

    async def concluir(self, h):
        await h.signal(AtorSessaoAtomicoSintetico.fechar)
        self.falsa.liberar.set()
        r = await asyncio.wait_for(h.result(), 15)
        await self.capturar(h)
        return r

    async def esperar(self, condicao):
        deadline = time.monotonic() + 10
        while not condicao():
            self.assertLess(time.monotonic(), deadline, "barreira sintetica nao atingida")
            await asyncio.sleep(0.01)

    async def capturar(self, h, erro=None):
        d = await h.describe()
        self.assertNotEqual(d.status.name, "RUNNING")
        self.assertEqual(len(d.raw_description.pending_activities), 0)
        history = await h.fetch_history()
        scheduled = [e.activity_task_scheduled_event_attributes for e in history.events
                     if e.HasField("activity_task_scheduled_event_attributes")]
        self.assertTrue(scheduled)
        self.assertTrue(all(a.task_queue.name == self.fila_atividade for a in scheduled))
        self.assertTrue(all(a.retry_policy.maximum_attempts == 1 for a in scheduled))
        self.assertTrue(all(a.schedule_to_close_timeout.seconds > 0 for a in scheduled))
        text = history.to_json()
        stem = self._testMethodName + "-" + h.id[-12:]
        (self.out / (stem + ".history.json")).write_text(text + "\n")
        await Replayer(workflows=[AtorSessaoAtomicoSintetico]).replay_workflow(
            WorkflowHistory.from_json(h.id, text), raise_on_replay_failure=True)
        summary = dict(teste=self._testMethodName, workflow_id=h.id, run_id=d.run_id,
                       estado=d.status.name, pending_activities=0, replay="ok",
                       atividades_agendadas=len(scheduled), fila_explicita=self.fila_atividade,
                       calls=self.falsa.calls, max_global=self.falsa.max_global,
                       max_por_sessao=self.falsa.max_sessao, erro=erro)
        (self.out / (stem + ".summary.json")).write_text(json.dumps(summary, indent=2) + "\n")
        return history

    async def test_primeiro_pedido_concorrente_cria_um_ator_e_serializa(self):
        await self.consumidores()
        results = await asyncio.gather(*[
            self.admitir(f"p{i}", client=self.clients[i % 2]) for i in range(12)])
        self.assertEqual([r for r, _ in results], ["aceito"] * 12)
        hs = [h for _, h in results]
        self.assertEqual(len({(await h.describe()).run_id for h in hs}), 1)
        h = hs[0]
        await self.esperar(lambda: self.falsa.ativos == 1)
        state = await h.query(AtorSessaoAtomicoSintetico.estado)
        self.assertEqual(len(state["aceitos"]), 12)
        self.assertEqual(len(self.falsa.calls), 1)
        r = await self.concluir(h)
        self.assertEqual(r["concluidos"], state["aceitos"])
        self.assertEqual(self.falsa.max_sessao, {"sessao-A": 1})
        for a, b in zip(self.falsa.calls, self.falsa.calls[1:]):
            self.assertLessEqual(a["fim"], b["inicio"])
        history = await h.fetch_history()
        self.assertEqual(sum(e.HasField("workflow_execution_started_event_attributes") for e in history.events), 1)
        self.assertEqual(sum(e.HasField("workflow_execution_update_completed_event_attributes") for e in history.events), 12)

    async def test_reenvio_resposta_descartada_e_colisao_payload(self):
        await self.consumidores()
        # A chamada real completa, mas seu resultado é descartado pelo chamador.
        async def descartar():
            await self.admitir("a1")
            raise ConnectionError("resposta sintetica descartada apos admissao")
        with self.assertRaises(ConnectionError):
            await descartar()
        await self.esperar(lambda: self.falsa.ativos == 1)
        ack, h = await self.admitir("a1")
        self.assertEqual(ack, "aceito")  # Mesmo Update ID: resultado original.
        with self.assertRaises(WorkflowUpdateFailedError) as ctx:
            await self.admitir("a1", falhar=True)
        self.assertEqual(ctx.exception.cause.type, "AdmissaoInvalida")
        from tests.workflows.prototipo_admissao_atomica import configuracao
        config = configuracao("sessao-A", self.fila_wf, self.fila_atividade)
        self.assertEqual(await h.execute_update(AtorSessaoAtomicoSintetico.solicitar,
            dict(config=config, pedido=dict(id="a1", sessao="sessao-A", falhar=False))), "duplicado")
        r = await self.concluir(h)
        self.assertEqual(r["concluidos"], ["a1"])
        self.assertEqual(len(self.falsa.calls), 1)
        history = await h.fetch_history()
        # O reenvio idêntico não produz outro Update no histórico.
        self.assertEqual(sum(e.HasField("workflow_execution_update_completed_event_attributes") for e in history.events), 3)

    async def test_config_divergente_na_reutilizacao_nao_enfileira(self):
        await self.consumidores()
        _, h = await self.admitir("a1")
        for overrides in [dict(prazo_s=11),
                          dict(fila_camofox=self.fila_atividade + "-outra"),
                          dict(fila_workflow=self.fila_wf + "-outra")]:
            with self.assertRaises(WorkflowUpdateFailedError) as ctx:
                await self.admitir("rejeitado", **overrides)
            self.assertEqual(ctx.exception.cause.type, "ConfigDivergente")
        state = await h.query(AtorSessaoAtomicoSintetico.estado)
        self.assertEqual(state["aceitos"], ["a1"])
        self.assertEqual((await self.concluir(h))["concluidos"], ["a1"])

    async def test_sem_worker_admissao_pendente_e_reenvio_mesmo_ator(self):
        queue = self.fila_wf + "-atrasada"
        sessao = "sessao-sem-worker"
        h = self.env.client.get_workflow_handle(ator_id(sessao))
        self.handles.append(h)
        pending = asyncio.create_task(self.admitir("a1", sessao=sessao, fila_workflow=queue))
        try:
            await asyncio.sleep(0.15)
            self.assertFalse(pending.done())
            before = await h.describe()
            self.assertEqual(before.status.name, "RUNNING")
            self.assertEqual(self.falsa.calls, [])
            await self.stack.enter_async_context(Worker(
                self.clients[0], task_queue=queue, workflows=[AtorSessaoAtomicoSintetico],
                max_cached_workflows=0))
            await self.consumidores()
            ack, recovered = await asyncio.wait_for(pending, 15)
            self.assertEqual(ack, "aceito")
            self.assertEqual((await recovered.describe()).run_id, before.run_id)
            ack2, h2 = await self.admitir("a1", sessao=sessao, fila_workflow=queue)
            self.assertEqual(ack2, "aceito")
            self.assertEqual((await h2.describe()).run_id, before.run_id)
            self.assertEqual((await self.concluir(h))["concluidos"], ["a1"])
            self.assertEqual(len(self.falsa.calls), 1)
        finally:
            if not pending.done():
                pending.cancel()
            await asyncio.gather(pending, return_exceptions=True)

    async def test_sessoes_distintas_em_paralelo(self):
        await self.consumidores()
        (_, a), (_, b) = await asyncio.gather(
            self.admitir("a1"), self.admitir("b1", sessao="sessao-B"))
        await self.esperar(lambda: self.falsa.ativos == 2)
        self.assertEqual(self.falsa.max_global, 2)
        self.assertEqual(self.falsa.max_sessao, {"sessao-A": 1, "sessao-B": 1})
        await asyncio.gather(self.concluir(a), self.concluir(b))
        x, y = self.falsa.calls
        self.assertLess(max(x["inicio"], y["inicio"]), min(x["fim"], y["fim"]))

    async def test_sem_consumidor_timeout_terminal_sem_execucao_tardia(self):
        _, h = await self.admitir("a1", prazo_s=2)
        await self.admitir("a2", prazo_s=2)
        await h.signal(AtorSessaoAtomicoSintetico.fechar)
        with self.assertRaises(WorkflowFailureError) as ctx:
            await asyncio.wait_for(h.result(), 15)
        self.assertIsInstance(ctx.exception.cause.cause, TimeoutError)
        self.assertEqual(ctx.exception.cause.cause.type, TimeoutType.TIMEOUT_TYPE_SCHEDULE_TO_CLOSE)
        history = await self.capturar(h, "SCHEDULE_TO_CLOSE")
        self.assertEqual(sum(e.HasField("activity_task_scheduled_event_attributes") for e in history.events), 1)
        await self.consumidores()
        await asyncio.sleep(0.3)
        self.assertEqual(self.falsa.calls, [])

    async def test_excecao_tecnica_sem_retry_sem_proximo(self):
        await self.consumidores()
        _, h = await self.admitir("a1", falhar=True)
        await self.esperar(lambda: self.falsa.ativos == 1)
        await self.admitir("a2")
        await h.signal(AtorSessaoAtomicoSintetico.fechar)
        self.falsa.liberar.set()
        with self.assertRaises(WorkflowFailureError) as ctx:
            await asyncio.wait_for(h.result(), 15)
        self.assertEqual(ctx.exception.cause.cause.type, "FalhaTecnicaSintetica")
        self.assertEqual([(c["pedido"]["id"], c["attempt"]) for c in self.falsa.calls], [("a1", 1)])
        history = await self.capturar(h, "FalhaTecnicaSintetica")
        self.assertEqual(sum(e.HasField("activity_task_scheduled_event_attributes") for e in history.events), 1)
        self.assertFalse(any(e.HasField("timer_started_event_attributes") for e in history.events))
        with self.assertRaises(RPCError) as closed:
            await self.admitir("a3")
        self.assertEqual(closed.exception.status, RPCStatusCode.ALREADY_EXISTS)

    async def test_fechamento_drena_rejeita_novo_e_nao_reabre(self):
        await self.consumidores()
        _, h = await self.admitir("a1")
        await self.esperar(lambda: self.falsa.ativos == 1)
        await self.admitir("a2")
        await h.signal(AtorSessaoAtomicoSintetico.fechar)
        with self.assertRaises(WorkflowUpdateFailedError) as ctx:
            await self.admitir("a3")
        self.assertEqual(ctx.exception.cause.type, "AdmissaoFechada")
        self.assertEqual((await self.concluir(h))["concluidos"], ["a1", "a2"])
        with self.assertRaises(RPCError) as closed:
            await self.admitir("a4")
        self.assertEqual(closed.exception.status, RPCStatusCode.ALREADY_EXISTS)

    async def test_primeiro_update_invalido_nao_reverte_start(self):
        await self.consumidores()
        # Update-with-Start não é transação de negócio com rollback do start.
        with self.assertRaises(WorkflowUpdateFailedError):
            await self.admitir("")
        h = self.handles[0]
        self.assertEqual((await h.describe()).status.name, "RUNNING")
        self.assertEqual((await h.query(AtorSessaoAtomicoSintetico.estado))["aceitos"], [])
        self.assertEqual(self.falsa.calls, [])
        await self.admitir("valido")
        self.assertEqual((await self.concluir(h))["concluidos"], ["valido"])

    async def test_config_concorrente_primeiro_start_fixa_contrato(self):
        await self.consumidores()
        outcomes = await asyncio.gather(self.admitir("prazo10", prazo_s=10),
                                       self.admitir("prazo11", prazo_s=11),
                                       return_exceptions=True)
        errors = [x for x in outcomes if isinstance(x, Exception)]
        successes = [x for x in outcomes if not isinstance(x, Exception)]
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], WorkflowUpdateFailedError)
        self.assertEqual(errors[0].cause.type, "ConfigDivergente")
        self.assertEqual(len(successes), 1)
        _, h = successes[0]
        state = await h.query(AtorSessaoAtomicoSintetico.estado)
        self.assertEqual(len(state["aceitos"]), 1)
        self.assertEqual((await self.concluir(h))["concluidos"], state["aceitos"])

if __name__ == "__main__":
    unittest.main()
