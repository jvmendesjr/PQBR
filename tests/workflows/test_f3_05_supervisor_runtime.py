"""Opt-in: somente Temporal descartável após gate de isolamento aprovado."""
import asyncio
from contextlib import AsyncExitStack
import json
import os
from pathlib import Path
import subprocess
import unittest
from temporalio import activity
from temporalio.client import Client, WorkflowFailureError
from temporalio.common import RetryPolicy, WorkflowIDConflictPolicy, WorkflowIDReusePolicy
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.exceptions import ApplicationError
from temporalio.service import RetryConfig
from temporalio.worker import Replayer
from pqbr.workflows.candidato_sessao import CorrecaoCandidata, configuracao
from tests.workflows.composicao_candidata import BackendsFalsos
from tests.workflows.prototipo_supervisor_sessao import SupervisorSessao, ator_id, workers_sinteticos, NAMESPACE


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


@unittest.skipUnless(os.environ.get('PQBR_SUPERVISOR_ISOLATED') == '1', 'exige gate descartável')
class SupervisorRuntime(unittest.IsolatedAsyncioTestCase):
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
        self.fake = FalsosSupervisor()
        self.sessao = self._testMethodName
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
            self.assertEqual(a.retry_policy.maximum_attempts, 1 if intervention or registro_falha else 3)
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

    async def test_duas_operacoes_falha_terminal_e_retomada_explicita(self):
        h, paused, child = await self.preparar_duas_operacoes()
        self.assertEqual(paused['bloqueio']['registro'], 'confirmado')
        self.assertEqual(len(self.fake.eventos_falha), 1)
        self.assertEqual(self.fake.eventos_falha[0]['operacao_id'], 'primeira')
        self.assertEqual(self.fake.eventos_falha[0]['resultado_efeito'], 'nao_reconciliado')
        # Recria só os Workers sintéticos: estado e pausa vêm do histórico.
        await self.stack.aclose()
        await self.enviar('primeira', 'falha-tecnica')
        await self.enviar('segunda')
        await self.abrir_workers()
        cmd = self.comando(paused)
        await h.signal('retomar', {**cmd, 'revisao': 999})
        await h.signal('fechar')
        still = await self.estado_ate(h, lambda s: s['fechando'] and any(
            o['estado'] == 'retomada_recusada' for o in s['observacoes']))
        self.assertEqual(still['pendentes'], ['segunda'])
        self.assertEqual(still['falhas'], paused['falhas'])
        self.assertEqual([c['passo'] for c in self.fake.calls], ['primeira'])
        self.assertEqual((await h.describe()).status.name, 'RUNNING')
        await self.capture(h)
        await h.signal('retomar', cmd)
        await h.signal('retomar', cmd)
        result = await asyncio.wait_for(h.result(), 30)
        self.assertEqual(list(result['resultados']), ['segunda'])
        self.assertEqual(result['pendentes'], [])
        self.assertEqual(result['falhas'], paused['falhas'])
        self.assertEqual(len(result['retomadas']), 1)
        self.assertEqual([c['passo'] for c in self.fake.calls], ['primeira', 'segunda'])
        self.assertTrue(all(c['tentativa'] == 1 for c in self.fake.calls))
        self.assertEqual(len(self.fake.registros), 1)
        self.assertEqual(len(self.fake.tentativas_registro), 1)
        self.assertEqual(self.fake.tentativas_registro[0]['tentativa'], 1)
        self.assertEqual((await child.describe()).status.name, 'FAILED')
        self.assertEqual(self.fake.max_sessao[self.sessao], 1)
        self.assertLessEqual(self.fake.calls[0]['fim'], self.fake.calls[1]['inicio'])
        parent = await h.fetch_history()
        self.assertEqual(sum(e.HasField('start_child_workflow_execution_initiated_event_attributes') for e in parent.events), 2)
        self.assertFalse(any(e.HasField('timer_started_event_attributes') for e in parent.events))
        await self.capture(h)
        self.evidenciar(estado_pausado=paused, estado_final=result, filho_falho_terminal=True,
                        worker_sintetico_recriado=True, somente_pendentes_retomados=True)

    async def test_falha_registro_nao_repete_nem_libera_segunda(self):
        self.fake.falhar_registro = True
        h, paused, child = await self.preparar_duas_operacoes()
        self.assertEqual(paused['bloqueio']['registro'], 'falhou')
        await h.signal('retomar', self.comando(paused))
        state = await self.estado_ate(h, lambda s: any(o['estado'] == 'retomada_recusada' for o in s['observacoes']))
        self.assertEqual(state['pendentes'], ['segunda'])
        self.assertEqual(len(self.fake.tentativas_registro), 1)
        self.assertEqual(self.fake.tentativas_registro[0]['tentativa'], 1)
        self.assertEqual(self.fake.eventos_falha, [])
        self.assertEqual([c['passo'] for c in self.fake.calls], ['primeira'])
        self.evidenciar(estado_pausado=state, registro_falho_fail_closed=True)

    async def test_recibo_invalido_nao_libera_segunda(self):
        self.fake.recibo_invalido = True
        h, paused, child = await self.preparar_duas_operacoes()
        self.assertEqual(paused['bloqueio']['registro'], 'recibo_invalido')
        await h.signal('retomar', self.comando(paused))
        state = await self.estado_ate(h, lambda s: any(o['estado'] == 'retomada_recusada' for o in s['observacoes']))
        self.assertEqual(state['pendentes'], ['segunda'])
        self.assertEqual(len(self.fake.tentativas_registro), 1)
        self.assertEqual([c['passo'] for c in self.fake.calls], ['primeira'])
        self.evidenciar(estado_pausado=state, recibo_invalido_fail_closed=True)
