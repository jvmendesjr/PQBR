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
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Replayer, Worker
from tests.workflows.prototipo_ator_sessao import AtorSessaoSintetico, obter_ator

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
class AtorSessaoTemporalIsolado(unittest.IsolatedAsyncioTestCase):
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
                client, task_queue=self.fila_wf, workflows=[AtorSessaoSintetico],
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

    async def ator(self, sessao, prazo_s=10):
        h = await obter_ator(self.env.client, sessao, self.fila_wf, self.fila_atividade, prazo_s)
        self.handles.append(h)
        return h

    async def pedir(self, h, chave, sessao="sessao-A", falhar=False):
        return await h.execute_update(AtorSessaoSintetico.solicitar,
                                      dict(id=chave, sessao=sessao, falhar=falhar))

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
        await Replayer(workflows=[AtorSessaoSintetico]).replay_workflow(
            WorkflowHistory.from_json(h.id, text), raise_on_replay_failure=True)
        summary = dict(teste=self._testMethodName, workflow_id=h.id, run_id=d.run_id,
                       estado=d.status.name, pending_activities=0, replay="ok",
                       atividades_agendadas=len(scheduled), fila_explicita=self.fila_atividade,
                       calls=self.falsa.calls, max_global=self.falsa.max_global,
                       max_por_sessao=self.falsa.max_sessao, erro=erro)
        (self.out / (stem + ".summary.json")).write_text(json.dumps(summary, indent=2) + "\n")
        return history

    async def test_mesma_sessao_serial_deduplicada_multiplos_workers(self):
        await self.consumidores()
        a, b = await asyncio.gather(self.ator("sessao-A"), self.ator("sessao-A"))
        self.assertEqual((await a.describe()).run_id, (await b.describe()).run_id)
        self.assertEqual(await self.pedir(a, "a1"), "aceito")
        await self.esperar(lambda: self.falsa.ativos == 1)
        self.assertEqual(await self.pedir(b, "a2"), "aceito")
        self.assertEqual(await self.pedir(b, "a1"), "duplicado")
        with self.assertRaises(WorkflowUpdateFailedError):
            await self.pedir(b, "a1", falhar=True)
        self.assertEqual((await a.query(AtorSessaoSintetico.estado))["pendentes"], ["a2"])
        await asyncio.sleep(0.15)
        self.assertEqual(len(self.falsa.calls), 1)
        await a.signal(AtorSessaoSintetico.fechar)
        self.falsa.liberar.set()
        r = await asyncio.wait_for(a.result(), 15)
        self.assertEqual(r["concluidos"], ["a1", "a2"])
        self.assertEqual(r["pendentes"], [])
        self.assertEqual(self.falsa.max_sessao, {"sessao-A": 1})
        self.assertLessEqual(self.falsa.calls[0]["fim"], self.falsa.calls[1]["inicio"])
        await self.capturar(a)
        with self.assertRaises(WorkflowAlreadyStartedError):
            await self.ator("sessao-A")

    async def test_sessoes_distintas_progridem_em_paralelo(self):
        await self.consumidores()
        a, b = await asyncio.gather(self.ator("sessao-A"), self.ator("sessao-B"))
        await asyncio.gather(self.pedir(a, "a1"), self.pedir(b, "b1", "sessao-B"))
        await self.esperar(lambda: self.falsa.ativos == 2)
        self.assertEqual(self.falsa.max_global, 2)
        self.assertEqual(self.falsa.max_sessao, {"sessao-A": 1, "sessao-B": 1})
        self.falsa.liberar.set()
        await asyncio.gather(a.signal(AtorSessaoSintetico.fechar), b.signal(AtorSessaoSintetico.fechar))
        await asyncio.wait_for(asyncio.gather(a.result(), b.result()), 15)
        x, y = self.falsa.calls
        self.assertLess(max(x["inicio"], y["inicio"]), min(x["fim"], y["fim"]))
        await self.capturar(a)
        await self.capturar(b)

    async def test_sem_consumidor_timeout_terminal_sem_tarefa_orfa(self):
        h = await self.ator("sessao-A", prazo_s=2)
        await self.pedir(h, "a1")
        await self.pedir(h, "a2")
        await h.signal(AtorSessaoSintetico.fechar)
        with self.assertRaises(WorkflowFailureError) as ctx:
            await asyncio.wait_for(h.result(), 15)
        self.assertIsInstance(ctx.exception.cause.cause, TimeoutError)
        self.assertEqual(ctx.exception.cause.cause.type, TimeoutType.TIMEOUT_TYPE_SCHEDULE_TO_CLOSE)
        history = await self.capturar(h, "SCHEDULE_TO_CLOSE")
        self.assertEqual(sum(e.HasField("activity_task_scheduled_event_attributes") for e in history.events), 1)
        self.assertFalse(any(e.HasField("activity_task_started_event_attributes") for e in history.events))
        await self.consumidores()
        await asyncio.sleep(0.3)
        self.assertEqual(self.falsa.calls, [])
        (self.out / "consumidor-tardio.json").write_text(json.dumps(dict(
            calls=[], observacao_s=0.3, estado=(await h.describe()).status.name,
            pending_activities=len((await h.describe()).raw_description.pending_activities))) + "\n")

    async def test_excecao_tecnica_propaga_sem_retry_nem_proximo_pedido(self):
        await self.consumidores()
        h = await self.ator("sessao-A")
        await self.pedir(h, "a1", falhar=True)
        await self.esperar(lambda: self.falsa.ativos == 1)
        await self.pedir(h, "a2")
        await h.signal(AtorSessaoSintetico.fechar)
        self.falsa.liberar.set()
        with self.assertRaises(WorkflowFailureError) as ctx:
            await asyncio.wait_for(h.result(), 15)
        self.assertEqual(ctx.exception.cause.cause.type, "FalhaTecnicaSintetica")
        self.assertEqual([(c["pedido"]["id"], c["attempt"]) for c in self.falsa.calls], [("a1", 1)])
        history = await self.capturar(h, "FalhaTecnicaSintetica")
        self.assertEqual(sum(e.HasField("activity_task_scheduled_event_attributes") for e in history.events), 1)
        self.assertFalse(any(e.HasField("timer_started_event_attributes") for e in history.events))
        self.assertEqual(self.falsa.ativos, 0)

    async def test_admissao_rejeita_outra_sessao_e_fechamento_drena(self):
        await self.consumidores()
        h = await self.ator("sessao-A")
        with self.assertRaises(WorkflowUpdateFailedError):
            await self.pedir(h, "invasor", "sessao-B")
        await self.pedir(h, "a1")
        await self.esperar(lambda: self.falsa.ativos == 1)
        await self.pedir(h, "a2")
        await h.signal(AtorSessaoSintetico.fechar)
        with self.assertRaises(WorkflowUpdateFailedError):
            await self.pedir(h, "a3")
        self.falsa.liberar.set()
        r = await asyncio.wait_for(h.result(), 15)
        self.assertEqual(r["aceitos"], ["a1", "a2"])
        self.assertEqual(r["concluidos"], ["a1", "a2"])
        await self.capturar(h)


if __name__ == "__main__":
    unittest.main()
