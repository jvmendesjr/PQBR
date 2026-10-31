"""F3-05: runtime Temporal real, exclusivamente no runner isolado opt-in.

Rodar tests/workflows/run_f3_05_isolado.sh. Não acessa serviços reais.
Retomada neste teste não equivale a durabilidade após perda do servidor.
"""
import asyncio
from collections import Counter
from datetime import timedelta
import hashlib
import json
import os
from pathlib import Path
import socket
import unittest
import uuid

from temporalio import activity
from temporalio.api.enums.v1 import EventType
from temporalio.client import WorkflowFailureError, WorkflowHistory
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.exceptions import ApplicationError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Replayer, Worker

from pqbr.contratos import (
    ResultadoCorrecao, ResultadoIntervencao, TriagemCorrecao, VerificacaoCorrecao,
)
from pqbr.workflows import correcao as C

SERVER = Path("/tmp/temporal-test-server-sdk-python-1.34.0")
OPT_IN = os.environ.get("PQBR_TEMPORAL_ISOLADO") == "1"


class ActivitiesFalsas:
    """Só dados sintéticos; registrar nunca chama a implementação de produção."""

    def __init__(self):
        self.calls = []
        self.registros = []
        self.falhas = {}

    def observar(self, nome, n=None):
        attempt = activity.info().attempt
        self.calls.append({"activity": nome, "attempt": attempt, "n": n})
        if attempt <= self.falhas.get(nome, 0):
            raise ApplicationError("falha sintetica transitoria", type="FalhaSintetica")

    @activity.defn(name="triagem_jev")
    async def triagem(self, p: C.PedidoCorrecao) -> TriagemCorrecao:
        self.observar("triagem_jev")
        return await C.triagem_jev(p)

    @activity.defn(name="intervir_agente")
    async def intervir(self, t: C.Tentativa) -> ResultadoIntervencao:
        self.observar("intervir_agente", t.n)
        return await C.intervir_agente(t)

    @activity.defn(name="verificar_jev")
    async def verificar(self, t: C.Tentativa) -> VerificacaoCorrecao:
        self.observar("verificar_jev", t.n)
        return await C.verificar_jev(t)

    @activity.defn(name="registrar_correcao")
    async def registrar(self, r: ResultadoCorrecao) -> None:
        self.observar("registrar_correcao")
        assert type(r) is ResultadoCorrecao
        self.registros.append(r)

    def lista(self):
        return [self.triagem, self.intervir, self.verificar, self.registrar]


@unittest.skipUnless(OPT_IN, "exige runner opt-in com namespace isolado")
class TemporalIsolado(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Recusa ativação apenas pela variável de ambiente no namespace do host.
        host = os.environ.get("PQBR_HOST_NETNS")
        atual = os.readlink("/proc/self/ns/net")
        self.assertTrue(host and atual != host, "namespace de rede não isolado")
        self.assertEqual([name for _, name in socket.if_nameindex()], ["lo"])
        self.assertEqual(len(Path("/proc/net/route").read_text().splitlines()), 1)
        self.assertTrue(SERVER.is_file() and os.access(SERVER, os.X_OK))
        self.out = Path(os.environ["PQBR_TEMPORAL_EVIDENCIAS"])
        self.assertTrue(self.out.is_dir())
        self.fake = ActivitiesFalsas()
        self.fila = "f3-05-isolado-" + uuid.uuid4().hex
        self.ferramenta = "camofox"
        self.env = await WorkflowEnvironment.start_time_skipping(
            data_converter=pydantic_data_converter,
            test_server_existing_path=str(SERVER),
        )
        self.addAsyncCleanup(self.env.shutdown)

    def worker(self, somente_workflow=False):
        return Worker(
            self.env.client, task_queue=self.fila,
            workflows=[C.CorrecaoAutonomaWorkflow],
            activities=[] if somente_workflow else self.fake.lista(),
            no_remote_activities=somente_workflow,
            max_cached_workflows=0,
            max_concurrent_activities=1,
            graceful_shutdown_timeout=timedelta(seconds=1),
        )

    def pedido(self, **overrides):
        fields = dict(ferramenta="camofox", passo="localizar botao sintetico",
                      erro="seletor sintetico indisponivel", simulacao=C.Simulacao())
        fields.update(overrides)
        return C.PedidoCorrecao(**fields)

    async def iniciar(self, pedido):
        self.ferramenta = pedido.ferramenta
        return await self.env.client.start_workflow(
            C.CorrecaoAutonomaWorkflow.run, pedido,
            id="f3-05-teste-" + uuid.uuid4().hex, task_queue=self.fila,
            execution_timeout=timedelta(hours=2),
        )

    async def concluir(self, handle, falha=False):
        error = None
        result = None
        try:
            result = await asyncio.wait_for(handle.result(), timeout=30)
        except WorkflowFailureError as exc:
            error = exc
        history = await handle.fetch_history()
        # Recarrega os bytes JSON capturados do servidor, não cria eventos artificiais.
        text = history.to_json()
        stem = self._testMethodName
        with (self.out / (stem + ".history.json")).open("x") as f:
            f.write(text + "\n")
        replay_history = WorkflowHistory.from_json(handle.id, text)
        await Replayer(
            workflows=[C.CorrecaoAutonomaWorkflow], data_converter=pydantic_data_converter,
        ).replay_workflow(replay_history, raise_on_replay_failure=True)
        timers = [e for e in history.events if e.HasField("timer_started_event_attributes")]
        # Em execuções terminadas normalmente há uma espera por nova intervenção,
        # e nenhuma antes da primeira, após a última ou nas outras ferramentas.
        if not error:
            quantidade = max(0, len(self.chamadas("intervir_agente")) - 1)
            self.validar_esperas(history, quantidade if self.ferramenta == "camofox" else 0)
        summary = dict(
            teste=stem, workflow_id=handle.id, replay="ok", eventos=len(history.events),
            atividades=self.fake.calls,
            registros=[r.model_dump(mode="json") for r in self.fake.registros],
            resultado=result.model_dump(mode="json") if result is not None else None,
            falha=type(error).__name__ if error else None,
            timers=sum(e.event_type == EventType.EVENT_TYPE_TIMER_STARTED for e in history.events),
            esperas=[dict(event_id=e.event_id,
                          segundos=e.timer_started_event_attributes.start_to_fire_timeout.ToTimedelta().total_seconds(),
                          inicio=e.event_time.ToDatetime().isoformat()) for e in timers],
        )
        with (self.out / (stem + ".summary.json")).open("x") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            f.write("\n")
        if falha:
            self.assertIsInstance(error, WorkflowFailureError)
        elif error:
            raise error
        else:
            self.assertIsInstance(result, ResultadoCorrecao)
            self.assertEqual(self.fake.registros, [result])
        return error if falha else result, history

    async def executar(self, pedido=None, falha=False):
        async with self.worker():
            return await self.concluir(await self.iniciar(pedido or self.pedido()), falha)

    def chamadas(self, name):
        return [c for c in self.fake.calls if c["activity"] == name]

    def agendadas(self, history, name):
        return [e.activity_task_scheduled_event_attributes for e in history.events
                if e.HasField("activity_task_scheduled_event_attributes")
                and e.activity_task_scheduled_event_attributes.activity_type.name == name]

    def validar_esperas(self, history, quantidade):
        timers = [e for e in history.events if e.HasField("timer_started_event_attributes")]
        fired = [e for e in history.events if e.HasField("timer_fired_event_attributes")]
        intervencoes = [e for e in history.events if e.HasField("activity_task_scheduled_event_attributes")
                        and e.activity_task_scheduled_event_attributes.activity_type.name == "intervir_agente"]
        self.assertEqual(len(timers), quantidade)
        self.assertEqual(len(fired), quantidade)
        for anterior, proxima, timer in zip(intervencoes, intervencoes[1:], timers):
            segundos = timer.timer_started_event_attributes.start_to_fire_timeout.ToTimedelta().total_seconds()
            self.assertTrue(300 <= segundos <= 900)
            conclusao = next(e for e in history.events if e.HasField("activity_task_completed_event_attributes")
                             and e.activity_task_completed_event_attributes.scheduled_event_id == anterior.event_id)
            disparo = next(e for e in fired
                           if e.timer_fired_event_attributes.started_event_id == timer.event_id)
            self.assertLess(conclusao.event_id, timer.event_id)
            self.assertLess(timer.event_id, disparo.event_id)
            self.assertLess(disparo.event_id, proxima.event_id)
            self.assertGreaterEqual((disparo.event_time.ToDatetime() - timer.event_time.ToDatetime()).total_seconds(), segundos)
            self.assertGreaterEqual((proxima.event_time.ToDatetime() - conclusao.event_time.ToDatetime()).total_seconds(), segundos)
            # Se houve verificação, a espera só começa depois da sua conclusão.
            verificacoes = [e for e in history.events if e.HasField("activity_task_scheduled_event_attributes")
                            and e.activity_task_scheduled_event_attributes.activity_type.name == "verificar_jev"
                            and anterior.event_id < e.event_id < proxima.event_id]
            for verificacao in verificacoes:
                fim = next(e for e in history.events if e.HasField("activity_task_completed_event_attributes")
                           and e.activity_task_completed_event_attributes.scheduled_event_id == verificacao.event_id)
                self.assertLess(fim.event_id, timer.event_id)

    async def test_corrige_na_primeira_e_serializa_resultado(self):
        r, h = await self.executar()
        self.assertEqual((r.resultado, r.tentativas, r.chamar_jose), ("corrigido", 1, False))
        self.assertTrue(r.proposta_script)
        self.assertEqual([c["activity"] for c in self.fake.calls],
                         ["triagem_jev", "intervir_agente", "verificar_jev", "registrar_correcao"])
        self.assertEqual(len(self.agendadas(h, "registrar_correcao")), 1)

    async def test_terceira_tentativa_tem_duas_esperas_e_timeouts_separados(self):
        r, h = await self.executar(self.pedido(simulacao=C.Simulacao(intervencoes=[False, False, True])))
        self.assertEqual((r.resultado, r.tentativas), ("corrigido", 3))
        self.assertEqual([c["n"] for c in self.chamadas("intervir_agente")], [1, 2, 3])
        self.assertEqual([c["attempt"] for c in self.chamadas("intervir_agente")], [1, 1, 1])
        scheduled = self.agendadas(h, "intervir_agente")
        self.assertEqual(len(scheduled), 3)
        for attrs in scheduled:
            self.assertEqual(attrs.retry_policy.maximum_attempts, 1)
            self.assertTrue(300 <= attrs.start_to_close_timeout.ToTimedelta().total_seconds() <= 900)
        self.validar_esperas(h, 2)

    async def test_corrige_na_segunda_com_uma_espera(self):
        r, h = await self.executar(self.pedido(simulacao=C.Simulacao(intervencoes=[False, True])))
        self.assertEqual((r.resultado, r.tentativas), ("corrigido", 2))
        self.validar_esperas(h, 1)

    async def test_outra_ferramenta_tres_tentativas_sem_espera(self):
        r, h = await self.executar(self.pedido(ferramenta="drive", simulacao=C.Simulacao(intervencoes=[False])))
        self.assertEqual((r.resultado, r.tentativas), ("esgotado", 3))
        self.validar_esperas(h, 0)
        self.assertTrue(all(a.start_to_close_timeout.ToTimedelta() == timedelta(minutes=10)
                            for a in self.agendadas(h, "intervir_agente")))

    async def test_tres_intervencoes_negativas_esgotam(self):
        r, _ = await self.executar(self.pedido(simulacao=C.Simulacao(intervencoes=[False])))
        self.assertEqual((r.resultado, r.tentativas, r.chamar_jose), ("esgotado", 3, True))
        self.assertEqual(len(self.chamadas("intervir_agente")), 3)
        self.assertEqual(self.chamadas("verificar_jev"), [])

    async def test_verificacao_negativa_impede_sucesso(self):
        r, _ = await self.executar(self.pedido(simulacao=C.Simulacao(verificacoes=[False])))
        self.assertEqual((r.resultado, r.tentativas), ("esgotado", 3))
        self.assertEqual(len(self.chamadas("verificar_jev")), 3)

    async def test_passo_sensivel_para_antes_do_backend(self):
        r, _ = await self.executar(self.pedido(passo="solicitar pagamento", simulacao=None))
        self.assertEqual((r.resultado, r.tentativas), ("sensivel", 0))
        self.assertEqual(self.chamadas("intervir_agente"), [])

    async def test_triagem_fora_de_escopo_nao_intervem(self):
        r, _ = await self.executar(self.pedido(simulacao=C.Simulacao(triagem="fora_de_escopo")))
        self.assertEqual((r.resultado, r.tentativas), ("sensivel", 0))
        self.assertEqual(self.chamadas("intervir_agente"), [])

    async def test_conta_divergente_interrompe_sem_verificar(self):
        r, _ = await self.executar(self.pedido(simulacao=C.Simulacao(conta_confere=False)))
        self.assertEqual((r.resultado, r.tentativas, r.motivo), ("sensivel", 1, "conta/sessão divergente"))
        self.assertEqual(len(self.chamadas("intervir_agente")), 1)
        self.assertEqual(self.chamadas("verificar_jev"), [])

    async def test_sem_backend_falha_uma_vez_sem_registro(self):
        error, _ = await self.executar(self.pedido(simulacao=None), falha=True)
        self.assertEqual([c["attempt"] for c in self.chamadas("triagem_jev")], [1])
        self.assertEqual(error.cause.cause.type, "EmConstrucao")
        self.assertTrue(error.cause.cause.non_retryable)
        self.assertEqual(self.fake.registros, [])
        self.assertEqual(self.chamadas("intervir_agente"), [])

    async def test_retry_real_de_triagem(self):
        self.fake.falhas["triagem_jev"] = 2
        r, _ = await self.executar()
        self.assertEqual(r.resultado, "corrigido")
        self.assertEqual([c["attempt"] for c in self.chamadas("triagem_jev")], [1, 2, 3])

    async def test_retry_real_de_verificacao(self):
        self.fake.falhas["verificar_jev"] = 2
        r, _ = await self.executar()
        self.assertEqual(r.resultado, "corrigido")
        self.assertEqual([c["attempt"] for c in self.chamadas("verificar_jev")], [1, 2, 3])
        self.assertEqual(len(self.chamadas("intervir_agente")), 1)

    async def test_retry_real_de_registro_falso(self):
        self.fake.falhas["registrar_correcao"] = 2
        r, _ = await self.executar()
        self.assertEqual(r.resultado, "corrigido")
        self.assertEqual([c["attempt"] for c in self.chamadas("registrar_correcao")], [1, 2, 3])
        self.assertEqual(len(self.fake.registros), 1)
        self.assertEqual(len(self.chamadas("intervir_agente")), 1)

    async def test_retry_de_triagem_para_na_terceira_falha(self):
        self.fake.falhas["triagem_jev"] = 5
        _, _ = await self.executar(falha=True)
        self.assertEqual([c["attempt"] for c in self.chamadas("triagem_jev")], [1, 2, 3])
        self.assertEqual(self.chamadas("intervir_agente"), [])
        self.assertEqual(self.fake.registros, [])

    async def test_excecao_na_intervencao_nao_repete_activity(self):
        self.fake.falhas["intervir_agente"] = 5
        error, h = await self.executar(falha=True)
        self.assertEqual(error.cause.cause.type, "FalhaSintetica")
        self.validar_esperas(h, 0)
        self.assertEqual([c["attempt"] for c in self.chamadas("intervir_agente")], [1])
        self.assertEqual(self.chamadas("verificar_jev"), [])
        self.assertEqual(self.fake.registros, [])

    async def test_novo_worker_retoma_activity_pendente_no_mesmo_servidor(self):
        async with self.worker(somente_workflow=True):
            handle = await self.iniciar(self.pedido())
            for _ in range(200):
                h = await handle.fetch_history()
                if self.agendadas(h, "triagem_jev"):
                    break
                await asyncio.sleep(0.025)
            else:
                self.fail("workflow não agendou a Activity no prazo local")
            self.assertEqual(self.fake.calls, [])
        async with self.worker():
            r, h = await self.concluir(handle)
        self.assertEqual(r.resultado, "corrigido")
        self.assertEqual(len(self.agendadas(h, "triagem_jev")), 1)
        self.assertEqual(Counter(c["activity"] for c in self.fake.calls), {
            "triagem_jev": 1, "intervir_agente": 1, "verificar_jev": 1, "registrar_correcao": 1,
        })

    async def aguardar_timer_pendente(self, handle):
        # Não aguarda result(): time skipping ainda não é habilitado.
        for _ in range(200):
            history = await handle.fetch_history()
            if any(e.HasField("timer_started_event_attributes") for e in history.events):
                self.assertFalse(any(e.HasField("timer_fired_event_attributes") for e in history.events))
                self.assertEqual([c["n"] for c in self.chamadas("intervir_agente")], [1])
                return history
            await asyncio.sleep(0.025)
        self.fail("workflow não agendou timer no prazo local")

    async def test_cancelamento_durante_espera_nao_intervem_novamente(self):
        async with self.worker():
            handle = await self.iniciar(self.pedido(simulacao=C.Simulacao(intervencoes=[False])))
            await self.aguardar_timer_pendente(handle)
            await handle.cancel()
            error, h = await self.concluir(handle, falha=True)
        self.assertEqual(type(error.cause).__name__, "CancelledError")
        self.assertEqual([c["n"] for c in self.chamadas("intervir_agente")], [1])
        self.assertEqual(self.fake.registros, [])
        self.assertEqual(sum(e.HasField("timer_canceled_event_attributes") for e in h.events), 1)
        self.assertEqual(sum(e.HasField("timer_fired_event_attributes") for e in h.events), 0)
        self.assertEqual(h.events[-1].event_type, EventType.EVENT_TYPE_WORKFLOW_EXECUTION_CANCELED)

    async def test_novo_worker_retoma_timer_sem_duplicar_intervencao(self):
        async with self.worker():
            handle = await self.iniciar(self.pedido(simulacao=C.Simulacao(intervencoes=[False, True])))
            antes = await self.aguardar_timer_pendente(handle)
            timer_id = next(e.event_id for e in antes.events if e.HasField("timer_started_event_attributes"))
        async with self.worker():
            r, h = await self.concluir(handle)
        self.assertEqual((r.resultado, r.tentativas), ("corrigido", 2))
        self.assertEqual([c["n"] for c in self.chamadas("intervir_agente")], [1, 2])
        self.validar_esperas(h, 1)
        self.assertEqual(next(e.event_id for e in h.events if e.HasField("timer_started_event_attributes")), timer_id)

    async def test_replay_dos_14_historicos_anteriores_sem_timer(self):
        anteriores = Path(__file__).resolve().parents[2] / "docs/sdd/evidencias-f3-05-temporal-isolado-20261017"
        arquivos = sorted(anteriores.glob("*.history.json"))
        self.assertEqual(len(arquivos), 14)
        resultados = []
        for arquivo in arquivos:
            text = arquivo.read_text()
            history = WorkflowHistory.from_json("legado-" + arquivo.stem, text)
            await Replayer(
                workflows=[C.CorrecaoAutonomaWorkflow], data_converter=pydantic_data_converter,
            ).replay_workflow(history, raise_on_replay_failure=True)
            resultados.append(dict(arquivo=arquivo.name, replay="ok", sha256=hashlib.sha256(text.encode()).hexdigest()))
        with (self.out / "replay-legado.summary.json").open("x") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
            f.write("\n")


if __name__ == "__main__":
    unittest.main()
