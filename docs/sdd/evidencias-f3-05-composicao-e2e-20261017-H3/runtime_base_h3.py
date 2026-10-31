"""Opt-in: somente Temporal descartável após gate de isolamento aprovado."""
import asyncio
from contextlib import AsyncExitStack
import json
import os
from pathlib import Path
import subprocess
import unittest
from ponte_h3 import ValidadorCanonico
from pqbr.contratos import TriagemCorrecao, ResultadoIntervencao
from pqbr.workflows.correcao import PedidoCorrecao, Tentativa
from temporalio import activity
from temporalio.client import Client, WorkflowFailureError
from temporalio.common import RetryPolicy, WorkflowIDConflictPolicy, WorkflowIDReusePolicy
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.exceptions import ApplicationError
from temporalio.service import RetryConfig
from temporalio.worker import Replayer
from pqbr.workflows.candidato_sessao import CorrecaoCandidata, configuracao
from tests.workflows.composicao_candidata import BackendsFalsos
from supervisor_h3 import SupervisorSessao, ator_id, workers_sinteticos, NAMESPACE


class FalsosSupervisor(BackendsFalsos):
    def __init__(self):
        super().__init__()
        self.eventos_falha = []
        self.tentativas_registro = []
        self.falhar_registro = False
        self.recibo_invalido = False

    @activity.defn(name='registrar_falha_supervisor_falsa')
    async def registrar_falha(self, evento: dict) -> dict:
        self.tentativas_registro.append(dict(evento=evento, tentativa=activity.info().attempt))
        if self.falhar_registro:
            raise ApplicationError('registro falso indisponível', type='FalhaRegistroFalsa')
        self.eventos_falha.append(evento)
        return dict(registro_id='invalido' if self.recibo_invalido else evento['registro_id'])


class FalsosH3(FalsosSupervisor, ValidadorCanonico):
    def __init__(self):
        FalsosSupervisor.__init__(self)
        ValidadorCanonico.__init__(self)
    def permitir(self, p):
        if (not p.sessao.startswith('FAKE-H3-') or p.passo not in ('primeira','segunda')
                or p.erro not in ('falha-tecnica','falha falsa') or p.simulacao is None):
            raise ApplicationError('fora da allowlist sintética H3', non_retryable=True)
    @activity.defn(name='triagem_jev')
    async def triagem(self, p: PedidoCorrecao) -> TriagemCorrecao:
        self.permitir(p)
        self.triagens += 1
        return TriagemCorrecao(classe='corrigivel', motivo='somente fixture sintética H3')
    @activity.defn(name='intervir_agente')
    async def intervir(self, t: Tentativa) -> ResultadoIntervencao:
        self.permitir(t.pedido)
        return await super().intervir(t)

@unittest.skipUnless(os.environ.get('PQBR_SUPERVISOR_ISOLATED') == '1', 'exige gate descartável')
class RuntimeBase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        for family in ('-4', '-6'):
            routes = json.loads(subprocess.check_output(['/usr/bin/ip', '-j', family, 'route']))
            self.assertFalse(any(r.get('dst') == 'default' for r in routes))
        self.out = Path(os.environ['PQBR_CANDIDATE_OUT'])
        self.assertTrue(json.loads((self.out.parent / 'isolation-gate.json').read_text())['passed'])
        self.client = await Client.connect('127.0.0.1:7233', namespace=NAMESPACE,
            data_converter=pydantic_data_converter, retry_config=RetryConfig(max_retries=0))
        self.stack = AsyncExitStack()
        await self.stack.__aenter__()
        self.fake = FalsosH3()
        self.sessao = 'FAKE-H3-' + self._testMethodName
        self.config = configuracao(self.sessao,
            'teste-f3-05-candidato-wf-' + self.sessao + '-supervisor',
            'teste-f3-05-candidato-camofox-' + self.sessao + '-supervisor')
        self.handles = []
        self.captured = set()
        self.sequencia = 0

    async def asyncTearDown(self):
        self.fake.liberar.set()
        try:
            for h in self.handles:
                if (await h.describe()).status.name == 'RUNNING':
                    await h.terminate('limpeza somente do supervisor sintético')
                await self.capture(h)
        finally:
            await self.stack.aclose()

    async def abrir_workers(self):
        for w in workers_sinteticos(self.client, self.config, self.fake):
            await self.stack.enter_async_context(w)

    def envelope(self, op, erro):
        return dict(versao=1, config=self.config, operacao_id=op, pedido=dict(
            ferramenta='camofox', sessao=self.sessao, passo=op, erro=erro, simulacao={}))

    async def enviar(self, op, erro='falha falsa'):
        h = await self.client.start_workflow(SupervisorSessao.run,
            dict(versao=1, somente_sintetico=True, config=self.config), id=ator_id(self.sessao),
            task_queue=self.config['fila_workflow'], start_signal='solicitar',
            start_signal_args=[self.envelope(op, erro)],
            id_conflict_policy=WorkflowIDConflictPolicy.USE_EXISTING,
            id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
            retry_policy=RetryPolicy(maximum_attempts=1))
        if not self.handles:
            self.handles.append(h)
        return h

    async def estado_ate(self, h, pred):
        async def loop():
            while True:
                s = await h.query('estado')
                if pred(s):
                    return s
                await asyncio.sleep(.02)
        return await asyncio.wait_for(loop(), 25)

    def comando(self, state):
        b = state['bloqueio']
        return dict(versao=1, decisao='retomar_somente_pendentes', revisao=state['revisao'],
                    falha_id=b['operacao_id'], filho_run_id=b['filho_run_id'])

    async def preparar_duas_operacoes(self):
        self.fake.bloquear = True
        await self.abrir_workers()
        h = await self.enviar('primeira', 'falha-tecnica')
        await self.enviar('segunda')
        aceitos = await self.estado_ate(h, lambda s: len(s['aceitos']) == 2)
        self.assertEqual(set(aceitos['aceitos']), {'primeira', 'segunda'})
        # Não confundir confirmação RPC com admissão: a query acima prova ambas aceitas.
        self.fake.liberar.set()
        paused = await self.estado_ate(h, lambda s: s['bloqueio'] is not None and s['ativo'] is None)
        self.assertEqual(paused['pendentes'], ['segunda'])
        self.assertEqual(paused['resultados'], {})
        self.assertEqual([c['passo'] for c in self.fake.calls], ['primeira'])
        self.assertEqual(self.fake.calls[0]['tentativa'], 1)
        self.assertEqual(self.fake.registros, [])
        child = self.client.get_workflow_handle(paused['bloqueio']['filho_id'],
                                                 run_id=paused['bloqueio']['filho_run_id'])
        self.assertEqual((await child.describe()).status.name, 'FAILED')
        hist = await child.fetch_history()
        self.assertEqual(sum(e.HasField('activity_task_failed_event_attributes') for e in hist.events), 1)
        self.assertFalse(any(e.HasField('timer_started_event_attributes') for e in hist.events))
        await self.capture(h)
        return h, paused, child

    async def capture(self, h):
        hist = await h.fetch_history()
        run_id = hist.events[0].workflow_execution_started_event_attributes.original_execution_run_id
        key = (h.id, run_id, len(hist.events))
        if key in self.captured:
            return
        self.captured.add(key)
        self.sequencia += 1
        stem = self._testMethodName + f'.{self.sequencia:02d}'
        (self.out / (stem + '.history.json')).write_text(hist.to_json() + '\n')
        await Replayer(workflows=[SupervisorSessao, CorrecaoCandidata], namespace=NAMESPACE,
            data_converter=pydantic_data_converter).replay_workflow(hist, raise_on_replay_failure=True)
        scheduled = [e.activity_task_scheduled_event_attributes for e in hist.events
                     if e.HasField('activity_task_scheduled_event_attributes')]
        for a in scheduled:
            intervention = a.activity_type.name == 'intervir_agente'
            registro_falha = a.activity_type.name == 'registrar_falha_supervisor_falsa'
            self.assertEqual(a.task_queue.name, self.config['fila_camofox' if intervention else 'fila_workflow'])
            self.assertEqual(a.retry_policy.maximum_attempts, 1 if intervention or registro_falha or a.activity_type.name == 'reler_confirmacao_canonica_falsa' else 3)
        (self.out / (stem + '.summary.json')).write_text(json.dumps(dict(
            workflow_id=h.id, run_id=run_id, eventos=len(hist.events), replay='ok',
            activities=[dict(nome=a.activity_type.name, fila=a.task_queue.name,
                             max_tentativas=a.retry_policy.maximum_attempts) for a in scheduled]), indent=2) + '\n')
        for e in hist.events:
            if e.HasField('child_workflow_execution_started_event_attributes'):
                ex = e.child_workflow_execution_started_event_attributes.workflow_execution
                await self.capture(self.client.get_workflow_handle(ex.workflow_id, run_id=ex.run_id))

    def evidenciar(self, **values):
        (self.out / (self._testMethodName + '.result.json')).write_text(json.dumps(dict(
            **values, chamadas=self.fake.calls, registros_sucesso=self.fake.registros,
            eventos_falha=self.fake.eventos_falha, tentativas_registro=self.fake.tentativas_registro),
            ensure_ascii=False, indent=2) + '\n')

