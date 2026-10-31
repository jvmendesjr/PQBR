"""Diagnóstico de despacho F3-05, opt-in isolado. Não corrige Workers reais."""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import socket
import unittest
import uuid
from datetime import timedelta

from temporalio import activity
from temporalio.client import WorkflowFailureError, WorkflowHistory
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Replayer, Worker

from pqbr.workflows import correcao as C
from tests.workflows.test_f3_05_temporal_isolado import ActivitiesFalsas

SERVER = Path("/tmp/temporal-test-server-sdk-python-1.34.0")
ROOT = Path(__file__).resolve().parents[2]
OPT_IN = os.environ.get("PQBR_TEMPORAL_ISOLADO") == "1"


class FalsasComFila(ActivitiesFalsas):
    def observar(self, nome, n=None):
        info = activity.info()
        super().observar(nome, n)
        self.calls[-1].update(task_queue=info.task_queue, workflow_id=info.workflow_id)


@unittest.skipUnless(OPT_IN, "exige runner opt-in isolado")
class RoteamentoTemporalIsolado(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        host = os.environ.get("PQBR_HOST_NETNS")
        self.assertTrue(host and os.readlink("/proc/self/ns/net") != host)
        self.assertEqual([name for _, name in socket.if_nameindex()], ["lo"])
        self.assertEqual(len(Path("/proc/net/route").read_text().splitlines()), 1)
        self.assertTrue(SERVER.is_file() and os.access(SERVER, os.X_OK))
        self.out = Path(os.environ["PQBR_TEMPORAL_EVIDENCIAS"])
        self.assertTrue(self.out.is_dir())
        suffix = uuid.uuid4().hex
        self.principal = "teste-pqbr-episodio-" + suffix
        self.sessao = "teste-camofox-pqbr-" + suffix
        self.main_fake, self.session_fake = FalsasComFila(), FalsasComFila()
        self.env = await WorkflowEnvironment.start_time_skipping(
            data_converter=pydantic_data_converter,
            test_server_existing_path=str(SERVER),
        )
        self.addAsyncCleanup(self.env.shutdown)

    def worker(self, queue, fake, workflow=False, only_intervention=False, without_intervention=False):
        activities = fake.lista()
        if only_intervention:
            activities = [fake.intervir]
        if without_intervention:
            activities = [fake.triagem, fake.verificar, fake.registrar]
        return Worker(
            self.env.client, task_queue=queue,
            workflows=[C.CorrecaoAutonomaWorkflow] if workflow else [],
            activities=activities, max_concurrent_activities=1,
            max_cached_workflows=0, graceful_shutdown_timeout=timedelta(seconds=1),
        )

    async def start(self, queue, ferramenta="camofox", **overrides):
        fields = dict(ferramenta=ferramenta, sessao="pqbr", passo="localizar botao sintetico",
                      erro="seletor sintetico indisponivel", simulacao=C.Simulacao())
        fields.update(overrides)
        return await self.env.client.start_workflow(
            C.CorrecaoAutonomaWorkflow.run, C.PedidoCorrecao(**fields),
            id="roteamento-" + uuid.uuid4().hex, task_queue=queue,
            execution_timeout=timedelta(hours=2),
        )

    def scheduled(self, history, name="intervir_agente"):
        return [e.activity_task_scheduled_event_attributes for e in history.events
                if e.HasField("activity_task_scheduled_event_attributes")
                and e.activity_task_scheduled_event_attributes.activity_type.name == name]

    async def capture(self, handle, expected_queue, result=None, error=None):
        history = await handle.fetch_history()
        self.assertEqual([a.task_queue.name for a in self.scheduled(history)], [expected_queue])
        self.assertEqual(self.scheduled(history)[0].retry_policy.maximum_attempts, 1)
        text = history.to_json()
        stem = self._testMethodName
        (self.out / (stem + ".history.json")).write_text(text + "\n")
        await Replayer(workflows=[C.CorrecaoAutonomaWorkflow],
                       data_converter=pydantic_data_converter).replay_workflow(
            WorkflowHistory.from_json(handle.id, text), raise_on_replay_failure=True)
        summary = dict(
            teste=stem, workflow_id=handle.id, principal=self.principal, sessao=self.sessao,
            fila_intervencao=[a.task_queue.name for a in self.scheduled(history)],
            main_calls=self.main_fake.calls, session_calls=self.session_fake.calls,
            main_records=[r.model_dump(mode="json") for r in self.main_fake.registros],
            session_records=[r.model_dump(mode="json") for r in self.session_fake.registros],
            resultado=result.model_dump(mode="json") if result else None,
            falha=type(error.cause).__name__ if error else None,
            replay="ok", eventos=len(history.events),
        )
        (self.out / (stem + ".summary.json")).write_text(json.dumps(summary, indent=2) + "\n")
        return history

    async def test_camofox_herda_principal_mesmo_com_worker_sessao_disponivel(self):
        async with self.worker(self.principal, self.main_fake, workflow=True), \
                self.worker(self.sessao, self.session_fake, only_intervention=True):
            handle = await self.start(self.principal)
            result = await asyncio.wait_for(handle.result(), 30)
            self.assertEqual(result.resultado, "corrigido")
            self.assertEqual(self.session_fake.calls, [])
            self.assertEqual([c["task_queue"] for c in self.main_fake.calls], [self.principal] * 4)
            self.assertEqual(self.main_fake.registros, [result])
            await self.capture(handle, self.principal, result=result)

    async def test_controle_workflow_na_fila_sessao_herda_sessao(self):
        # Controle experimental: não representa configuração do Worker persistente.
        async with self.worker(self.principal, self.main_fake, only_intervention=True), \
                self.worker(self.sessao, self.session_fake, workflow=True):
            handle = await self.start(self.sessao)
            result = await asyncio.wait_for(handle.result(), 30)
            self.assertEqual(result.resultado, "corrigido")
            self.assertEqual(self.main_fake.calls, [])
            self.assertEqual([c["task_queue"] for c in self.session_fake.calls], [self.sessao] * 4)
            self.assertEqual(self.session_fake.registros, [result])
            await self.capture(handle, self.sessao, result=result)

    async def test_sem_registro_na_principal_sessao_nao_resgata_activity(self):
        async with self.worker(self.principal, self.main_fake, workflow=True, without_intervention=True), \
                self.worker(self.sessao, self.session_fake, only_intervention=True):
            handle = await self.start(self.principal)
            with self.assertRaises(WorkflowFailureError) as ctx:
                await asyncio.wait_for(handle.result(), 30)
            self.assertIn("intervir_agente", str(ctx.exception.cause.cause))
            self.assertIn("not registered", str(ctx.exception.cause.cause))
            self.assertEqual(self.session_fake.calls, [])
            self.assertEqual([c["activity"] for c in self.main_fake.calls], ["triagem_jev"])
            history = await self.capture(handle, self.principal, error=ctx.exception)
            self.assertEqual(self.main_fake.registros, [])
            failures = [e for e in history.events if e.HasField("activity_task_failed_event_attributes")]
            self.assertEqual(len(failures), 1)
            self.assertFalse(any(e.HasField("timer_started_event_attributes") for e in history.events))

    async def test_excecao_tecnica_mantem_uma_execucao_sem_registro(self):
        self.main_fake.falhas["intervir_agente"] = 5
        async with self.worker(self.principal, self.main_fake, workflow=True), \
                self.worker(self.sessao, self.session_fake, only_intervention=True):
            handle = await self.start(self.principal)
            with self.assertRaises(WorkflowFailureError) as ctx:
                await asyncio.wait_for(handle.result(), 30)
            self.assertEqual(ctx.exception.cause.cause.type, "FalhaSintetica")
            self.assertEqual([(c["activity"], c["attempt"]) for c in self.main_fake.calls],
                             [("triagem_jev", 1), ("intervir_agente", 1)])
            self.assertEqual(self.main_fake.registros, [])
            self.assertEqual(self.session_fake.calls, [])
            history = await self.capture(handle, self.principal, error=ctx.exception)
            self.assertFalse(any(e.HasField("timer_started_event_attributes") for e in history.events))

    async def test_replay_32_historicos_existentes(self):
        summaries = []
        for folder, expected in [("evidencias-f3-05-temporal-isolado-20261017", 14),
                                 ("evidencias-f3-05-intervalo-20261017", 18)]:
            paths = sorted((ROOT / "docs/sdd" / folder).glob("*.history.json"))
            self.assertEqual(len(paths), expected)
            for path in paths:
                text = path.read_text()
                await Replayer(workflows=[C.CorrecaoAutonomaWorkflow],
                               data_converter=pydantic_data_converter).replay_workflow(
                    WorkflowHistory.from_json("anterior-" + path.stem, text),
                    raise_on_replay_failure=True)
                summaries.append(dict(arquivo=str(path.relative_to(ROOT)), replay="ok",
                                      sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        (self.out / "replay-anteriores.summary.json").write_text(json.dumps(summaries, indent=2) + "\n")


if __name__ == "__main__":
    unittest.main()
