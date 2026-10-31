"""Opt-in obrigatório: loopback isolado, servidor local, Activities falsas."""
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
from temporalio.client import Client, WorkflowFailureError, WorkflowHistory
from temporalio.common import WorkflowIDReusePolicy
from temporalio.exceptions import ApplicationError, WorkflowAlreadyStartedError
from temporalio.runtime import Runtime, TelemetryConfig
from temporalio.service import RPCError, RPCStatusCode
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Replayer, Worker
from temporalio.api.workflowservice.v1 import DeleteWorkflowExecutionRequest
from temporalio.api.common.v1 import WorkflowExecution
from tests.workflows.prototipo_signal_with_start import AtorSignalSintetico as Ator, ator_id, enviar_signal_with_start


class Falsa:
    def __init__(self):
        self.liberar = asyncio.Event()
        self.calls = []
        self.ativos = 0
        self.por_sessao = {}
        self.max_sessao = {}
        self.max_global = 0

    @activity.defn(name="efeito_signal_sintetico_v1")
    async def efeito(self, pedido: dict) -> dict:
        s = pedido["sessao"]
        self.ativos += 1
        self.por_sessao[s] = self.por_sessao.get(s, 0) + 1
        self.max_sessao[s] = max(self.max_sessao.get(s, 0), self.por_sessao[s])
        self.max_global = max(self.max_global, self.ativos)
        call = dict(pedido=pedido, inicio=time.monotonic(), fim=None, attempt=activity.info().attempt)
        self.calls.append(call)
        try:
            await self.liberar.wait()
            if pedido["falhar"]:
                raise ApplicationError("falha tecnica sintetica", type="FalhaTecnicaSintetica")
            return dict(sintetico=True)
        finally:
            call["fim"] = time.monotonic()
            self.ativos -= 1
            self.por_sessao[s] -= 1


@unittest.skipUnless(os.environ.get("PQBR_TEMPORAL_ISOLADO") == "1", "exige runner isolado")
class SignalWithStartIsolado(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.assertNotEqual(os.readlink("/proc/self/ns/net"), os.environ["PQBR_HOST_NETNS"])
        self.assertEqual([n for _, n in socket.if_nameindex()], ["lo"])
        self.assertEqual(len(Path("/proc/net/route").read_text().splitlines()), 1)
        self.out = Path(os.environ["PQBR_TEMPORAL_EVIDENCIAS"])
        self.env = await WorkflowEnvironment.start_time_skipping(
            test_server_existing_path="/tmp/temporal-test-server-sdk-python-1.34.0")
        self.addAsyncCleanup(self.env.shutdown)
        self.stack = AsyncExitStack()
        self.addAsyncCleanup(self.stack.aclose)
        self.addAsyncCleanup(self.limpar)
        self.handles = []
        self.falsa = Falsa()
        suffix = uuid.uuid4().hex
        self.wq = "teste-sws-wf-" + suffix
        self.aq = "teste-sws-act-" + suffix
        self.clients = [await Client.connect(self.env.client.service_client.config.target_host,
                        runtime=Runtime(telemetry=TelemetryConfig())) for _ in range(2)]
        for c in self.clients:
            await self.worker(c, self.wq)

    async def worker(self, client, queue):
        return await self.stack.enter_async_context(Worker(client, task_queue=queue,
            workflows=[Ator], max_cached_workflows=0,
            graceful_shutdown_timeout=timedelta(seconds=1)))

    async def consumidores(self):
        for c in self.clients:
            await self.stack.enter_async_context(Worker(c, task_queue=self.aq,
                activities=[self.falsa.efeito], max_concurrent_activities=4,
                graceful_shutdown_timeout=timedelta(seconds=1)))

    async def limpar(self):
        self.falsa.liberar.set()
        for h in self.handles:
            try:
                if (await h.describe()).status.name == "RUNNING":
                    await h.terminate("cleanup sintetico")
            except RPCError as e:
                if e.status != RPCStatusCode.NOT_FOUND:
                    raise

    async def enviar(self, chave, sessao="sessao-A", falhar=False, client=None,
                     queue=None, reuse=WorkflowIDReusePolicy.REJECT_DUPLICATE, prazo_s=10):
        h = self.env.client.get_workflow_handle(ator_id(sessao))
        self.handles.append(h)
        return await enviar_signal_with_start(client or self.env.client, sessao,
            queue or self.wq, self.aq, dict(id=chave, sessao=sessao, falhar=falhar),
            reuse=reuse, prazo_s=prazo_s)

    async def esperar(self, condicao):
        deadline = time.monotonic() + 12
        while not condicao():
            self.assertLess(time.monotonic(), deadline)
            await asyncio.sleep(0.01)

    async def observar(self, h, pred):
        deadline = time.monotonic() + 12
        while True:
            state = await h.query(Ator.estado)
            if pred(state):
                return state
            self.assertLess(time.monotonic(), deadline, str(state))
            await asyncio.sleep(0.01)

    async def concluir(self, h):
        await h.signal(Ator.fechar)
        self.falsa.liberar.set()
        result = await asyncio.wait_for(h.result(), 15)
        await self.capturar(h)
        return result

    async def capturar(self, h):
        d = await h.describe()
        self.assertNotEqual(d.status.name, "RUNNING")
        self.assertEqual(len(d.raw_description.pending_activities), 0)
        history = await h.fetch_history()
        text = history.to_json()
        stem = self._testMethodName + "-" + d.run_id
        (self.out / (stem + ".history.json")).write_text(text + "\n")
        await Replayer(workflows=[Ator]).replay_workflow(
            WorkflowHistory.from_json(h.id, text), raise_on_replay_failure=True)
        scheduled = [e.activity_task_scheduled_event_attributes for e in history.events
                     if e.HasField("activity_task_scheduled_event_attributes")]
        for a in scheduled:
            self.assertEqual(a.task_queue.name, self.aq)
            self.assertEqual(a.retry_policy.maximum_attempts, 1)
            self.assertGreater(a.schedule_to_close_timeout.seconds, 0)
        summary = dict(teste=self._testMethodName, workflow_id=h.id, run_id=d.run_id,
            estado=d.status.name, replay="ok", pending_activities=0,
            atividades_agendadas=len(scheduled),
            signals=sum(e.HasField("workflow_execution_signaled_event_attributes") for e in history.events),
            calls=self.falsa.calls, max_global=self.falsa.max_global, max_sessao=self.falsa.max_sessao)
        (self.out / (stem + ".summary.json")).write_text(json.dumps(summary, indent=2) + "\n")
        return history

    async def test_concorrencia_start_signal_mesma_sessao(self):
        await self.consumidores()
        results = await asyncio.gather(*[self.enviar(f"p{i}", client=self.clients[i % 2]) for i in range(12)],
                                       return_exceptions=True)
        erros = [dict(indice=i, tipo=type(r).__name__, mensagem=str(r))
                 for i, r in enumerate(results) if isinstance(r, BaseException)]
        (self.out / "concorrencia-rpcs.json").write_text(json.dumps(dict(
            chamadas=12, sucesso=12-len(erros), erros=erros, retry_aplicacao=False), indent=2) + "\n")
        hs = [r for r in results if not isinstance(r, BaseException)]
        if erros:
            await self.concluir(hs[0])
            self.fail("Signal-With-Start concorrente recusado pelo servidor local: " + str(erros))
        self.assertEqual(len({(await h.describe()).run_id for h in hs}), 1)
        h = hs[0]
        state = await self.observar(h, lambda s: len(s["aceitos"]) == 12)
        await self.esperar(lambda: self.falsa.ativos == 1)
        self.assertEqual(len(self.falsa.calls), 1)
        r = await self.concluir(h)
        self.assertEqual(r["concluidos"], state["aceitos"])
        self.assertEqual(self.falsa.max_sessao, {"sessao-A": 1})
        for a, b in zip(self.falsa.calls, self.falsa.calls[1:]):
            self.assertLessEqual(a["fim"], b["inicio"])
        history = await h.fetch_history()
        self.assertEqual(sum(e.HasField("workflow_execution_started_event_attributes") for e in history.events), 1)

    async def test_duplicado_payload_divergente_e_config(self):
        await self.consumidores()
        h = await self.enviar("id-1")
        await self.enviar("id-1")
        # Todas as RPCs retornam normalmente: rejeição ocorre só no estado do ator.
        await self.enviar("id-1", falhar=True)
        await self.enviar("outro", prazo_s=11)
        state = await self.observar(h, lambda s: len(s["observacoes"]) == 4)
        self.assertEqual([o["estado"] for o in state["observacoes"]],
                         ["aceito", "duplicado", "payload_divergente", "configuracao_divergente"])
        self.assertEqual((await self.concluir(h))["concluidos"], ["id-1"])
        self.assertEqual(len(self.falsa.calls), 1)

    async def test_sem_worker_rpc_retorna_signal_duravel_retomada(self):
        q = self.wq + "-tardia"
        h = await asyncio.wait_for(self.enviar("id-1", queue=q), 5)
        before = await h.describe()
        hist = await h.fetch_history()
        self.assertEqual(before.status.name, "RUNNING")
        self.assertEqual(sum(e.HasField("workflow_execution_started_event_attributes") for e in hist.events), 1)
        self.assertEqual(sum(e.HasField("workflow_execution_signaled_event_attributes") for e in hist.events), 1)
        self.assertFalse(any(e.HasField("workflow_task_completed_event_attributes") for e in hist.events))
        self.assertEqual(self.falsa.calls, [])
        (self.out / "sem-worker-antes.history.json").write_text(hist.to_json() + "\n")
        await self.enviar("id-1", queue=q)
        await self.worker(self.clients[0], q)
        await self.consumidores()
        state = await self.observar(h, lambda s: len(s["observacoes"]) == 2)
        self.assertEqual(state["observacoes"][1]["estado"], "duplicado")
        self.assertEqual((await h.describe()).run_id, before.run_id)
        self.assertEqual((await self.concluir(h))["concluidos"], ["id-1"])
        self.assertEqual(len(self.falsa.calls), 1)

    async def test_duas_sessoes_paralelas(self):
        await self.consumidores()
        a, b = await asyncio.gather(self.enviar("a"), self.enviar("b", sessao="sessao-B"))
        await self.esperar(lambda: self.falsa.ativos == 2)
        await asyncio.gather(self.concluir(a), self.concluir(b))
        self.assertEqual(self.falsa.max_global, 2)
        self.assertEqual(self.falsa.max_sessao, {"sessao-A": 1, "sessao-B": 1})
        x, y = self.falsa.calls
        self.assertLess(max(x["inicio"], y["inicio"]), min(x["fim"], y["fim"]))

    async def test_fechando_rejeicao_assincrona_e_reuso_explicito(self):
        await self.consumidores()
        h = await self.enviar("id-1")
        await self.esperar(lambda: self.falsa.ativos == 1)
        await h.signal(Ator.fechar)
        await self.observar(h, lambda s: s["fechando"])
        await self.enviar("id-novo")
        await self.observar(h, lambda s: any(o["estado"] == "encerrando" for o in s["observacoes"]))
        old_run = (await h.describe()).run_id
        self.assertEqual((await self.concluir(h))["concluidos"], ["id-1"])
        with self.assertRaises((WorkflowAlreadyStartedError, RPCError)):
            await self.enviar("id-1")
        novo = await self.enviar("id-1", reuse=WorkflowIDReusePolicy.ALLOW_DUPLICATE)
        self.assertNotEqual((await novo.describe()).run_id, old_run)
        self.assertEqual((await self.concluir(novo))["concluidos"], ["id-1"])
        self.assertEqual(len(self.falsa.calls), 2)  # Sem dedup entre runs independentes.

    async def test_registro_removido_nao_simula_tempo_de_retention(self):
        await self.consumidores()
        h = await self.enviar("id-1")
        await self.concluir(h)
        old = await h.describe()
        try:
            await self.env.client.workflow_service.delete_workflow_execution(DeleteWorkflowExecutionRequest(
                namespace=self.env.client.namespace, workflow_execution=WorkflowExecution(
                    workflow_id=h.id, run_id=old.run_id)))
        except RPCError as e:
            if e.status != RPCStatusCode.UNIMPLEMENTED:
                raise
            (self.out / "retention-nao-validada.json").write_text(json.dumps(dict(
                status="NAO_VALIDADO", motivo=str(e),
                limite="Sem expiracao real de retention nem simulacao de remocao"), indent=2) + "\n")
            self.skipTest("test-server nao implementa DeleteWorkflowExecution; retention nao validada")
        with self.assertRaises(RPCError) as ctx:
            await h.describe()
        self.assertEqual(ctx.exception.status, RPCStatusCode.NOT_FOUND)
        # Remoção explícita no servidor efêmero, NÃO esperar expiração da retenção.
        novo = await self.enviar("id-1")
        self.assertNotEqual((await novo.describe()).run_id, old.run_id)
        await self.concluir(novo)
        self.assertEqual(len(self.falsa.calls), 2)

    async def test_falha_tecnica_sem_retry_dedup_nao_cruza_reuso(self):
        await self.consumidores()
        h = await self.enviar("id-falha", falhar=True)
        await self.esperar(lambda: self.falsa.ativos == 1)
        await self.enviar("id-posterior")
        await self.observar(h, lambda s: len(s["aceitos"]) == 2)
        self.falsa.liberar.set()
        with self.assertRaises(WorkflowFailureError) as ctx:
            await asyncio.wait_for(h.result(), 15)
        self.assertEqual(ctx.exception.cause.cause.type, "FalhaTecnicaSintetica")
        history = await self.capturar(h)
        self.assertEqual(len(self.falsa.calls), 1)
        self.assertEqual(self.falsa.calls[0]["attempt"], 1)
        self.assertFalse(any(e.HasField("timer_started_event_attributes") for e in history.events))
        with self.assertRaises((WorkflowAlreadyStartedError, RPCError)):
            await self.enviar("id-falha", falhar=True)
        novo = await self.enviar("id-falha", falhar=True, reuse=WorkflowIDReusePolicy.ALLOW_DUPLICATE)
        with self.assertRaises(WorkflowFailureError):
            await asyncio.wait_for(novo.result(), 15)
        await self.capturar(novo)
        self.assertEqual(len(self.falsa.calls), 2)
        self.assertTrue(all(c["pedido"]["id"] == "id-falha" for c in self.falsa.calls))

    async def test_continue_as_new_preservando_dedup(self):
        await self.verificar_continue(True)

    async def test_continue_as_new_sem_estado_repete_efeito(self):
        await self.verificar_continue(False)

    async def verificar_continue(self, preservar):
        await self.consumidores()
        self.falsa.liberar.set()
        h = await self.enviar("id-1")
        await self.observar(h, lambda s: s["concluidos"] == ["id-1"])
        old_run = (await h.describe()).run_id
        antigo = self.env.client.get_workflow_handle(h.id, run_id=old_run)
        await h.signal(Ator.continuar, preservar)
        # Query enviada ao run encerrando pode ficar pendente no test-server.
        # Esperar a troca por Describe e consultar explicitamente o novo run.
        deadline = time.monotonic() + 12
        while (d := await h.describe()).run_id == old_run:
            self.assertLess(time.monotonic(), deadline)
            await asyncio.sleep(0.01)
        novo_run = self.env.client.get_workflow_handle(h.id, run_id=d.run_id)
        await self.observar(novo_run, lambda s: s["geracao"] == 1)
        await self.capturar(antigo)
        novo = await self.enviar("id-1")
        self.assertNotEqual((await novo.describe()).run_id, old_run)
        state = await self.observar(novo, lambda s: len(s["observacoes"]) == 1)
        self.assertEqual(state["observacoes"][0]["estado"], "duplicado" if preservar else "aceito")
        await self.concluir(novo)
        self.assertEqual(len(self.falsa.calls), 1 if preservar else 2)

    async def test_worker_recriado_reconstroi_dedup_do_historico(self):
        q = self.wq + "-reinicio"
        await self.consumidores()
        self.falsa.liberar.set()
        w = await self.worker(self.clients[0], q)
        h = await self.enviar("id-1", queue=q)
        await self.observar(h, lambda s: s["concluidos"] == ["id-1"])
        await w.shutdown()
        await self.enviar("id-1", queue=q)
        await self.worker(self.clients[1], q)
        state = await self.observar(h, lambda s: len(s["observacoes"]) == 2)
        self.assertEqual(state["observacoes"][1]["estado"], "duplicado")
        await self.concluir(h)
        self.assertEqual(len(self.falsa.calls), 1)


if __name__ == "__main__":
    unittest.main()
