"""Opt-in exclusivamente em Temporal descartável isolado; sem efeito externo."""
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
from temporalio.exceptions import ApplicationError, WorkflowAlreadyStartedError
from temporalio.service import RetryConfig
from temporalio.worker import Replayer
from pqbr.workflows.candidato_sessao import CorrecaoCandidata, configuracao
from pqbr.workflows.correcao import Tentativa
from pqbr.contratos import ResultadoIntervencao
from tests.workflows.composicao_candidata import BackendsFalsos
from tests.workflows.prototipo_recuperacao_pendentes import AtorRecuperacao, ator_id, workers_sinteticos


class FalsosRecuperacao(BackendsFalsos):
    @activity.defn(name='intervir_agente')
    async def intervir(self, t: Tentativa) -> ResultadoIntervencao:
        result = await super().intervir(t)
        if t.pedido.erro == 'falha-desconhecida':
            raise ApplicationError('erro sintético não autorizado para recuperação', type='OutraFalhaFalsa')
        return result


@unittest.skipUnless(os.environ.get('PQBR_RECOVERY_ISOLATED') == '1', 'exige gate/container isolado')
class RecuperacaoRuntime(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        for family in ('-4', '-6'):
            routes = json.loads(subprocess.check_output(['/usr/bin/ip', '-j', family, 'route']))
            self.assertFalse(any(r.get('dst') == 'default' for r in routes))
        self.out = Path(os.environ['PQBR_CANDIDATE_OUT'])
        self.assertTrue(json.loads((self.out.parent / 'isolation-gate.json').read_text())['passed'])
        self.client = await Client.connect('127.0.0.1:7233', namespace='f3-05-recovery',
            data_converter=pydantic_data_converter, retry_config=RetryConfig(max_retries=0))
        self.stack = AsyncExitStack()
        await self.stack.__aenter__()
        self.fake = FalsosRecuperacao()
        self.sessao = self._testMethodName
        prefix = 'teste-f3-05-candidato-'
        self.config = configuracao(self.sessao, prefix + 'wf-' + self.sessao + '-recuperacao',
                                  prefix + 'camofox-' + self.sessao + '-recuperacao')
        self.handles = []
        self.captured = set()
        self.sequencia = 0

    async def asyncTearDown(self):
        self.fake.liberar.set()
        try:
            for h in self.handles:
                d = await h.describe()
                if d.status.name == 'RUNNING':
                    await h.terminate('limpeza exclusiva do protótipo sintético')
                await self.capture(h)
        finally:
            await self.stack.aclose()

    def pedido(self, op, erro='falha falsa'):
        return dict(ferramenta='camofox', sessao=self.sessao, passo=op, erro=erro, simulacao={})

    def envelope(self, op, erro='falha falsa'):
        return dict(versao=1, config=self.config, operacao_id=op, pedido=self.pedido(op, erro))

    async def enviar(self, op, erro='falha falsa'):
        h = await self.client.start_workflow(AtorRecuperacao.run,
            dict(versao=1, somente_sintetico=True, config=self.config), id=ator_id(self.sessao),
            task_queue=self.config['fila_workflow'], start_signal='solicitar',
            start_signal_args=[self.envelope(op, erro)],
            id_conflict_policy=WorkflowIDConflictPolicy.USE_EXISTING,
            id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
            retry_policy=RetryPolicy(maximum_attempts=1))
        if not any(x.id == h.id for x in self.handles):
            self.handles.append(h)
        return h

    async def abrir_workers(self):
        for w in workers_sinteticos(self.client, self.config, self.fake):
            await self.stack.enter_async_context(w)

    async def esperar(self, pred, prazo=20):
        async def loop():
            while True:
                value = await pred()
                if value:
                    return value
                await asyncio.sleep(.02)
        return await asyncio.wait_for(loop(), prazo)

    async def estado_ate(self, h, pred):
        async def check():
            s = await h.query('estado')
            return s if pred(s) else None
        return await self.esperar(check)

    def comando(self, state):
        b = state['bloqueio']
        return dict(versao=1, decisao='retomar_somente_pendentes', revisao=state['revisao'],
                    falha_id=b['operacao_id'], filho_run_id=b['filho_run_id'])

    async def preparar_falha(self, pendentes=('seguinte',), primeira='falha'):
        self.fake.bloquear = True
        await self.abrir_workers()
        h = await self.enviar(primeira, 'falha-tecnica')
        for op in pendentes:
            await self.enviar(op, 'falha-tecnica' if op.startswith('falha') else 'falha falsa')
        await self.estado_ate(h, lambda s: len(s['aceitos']) == len(pendentes) + 1)
        self.fake.liberar.set()
        state = await self.estado_ate(h, lambda s: s['bloqueio'] is not None)
        self.assertEqual(state['pendentes'], list(pendentes))
        self.assertEqual([c['passo'] for c in self.fake.calls], [primeira])
        self.assertEqual(self.fake.registros, [])
        self.assertEqual(state['resultados'], {})
        self.assertEqual((await h.describe()).status.name, 'RUNNING')
        await self.capture(h)
        return h, state

    async def fechar(self, h):
        await h.signal('fechar')
        result = await asyncio.wait_for(h.result(), 30)
        await self.capture(h)
        return result

    async def capture(self, h):
        hist = await h.fetch_history()
        run_id = hist.events[0].workflow_execution_started_event_attributes.original_execution_run_id
        key = (h.id, run_id, len(hist.events))
        if key in self.captured:
            return hist
        self.captured.add(key)
        self.sequencia += 1
        stem = self._testMethodName + f'.{self.sequencia:02d}'
        (self.out / (stem + '.history.json')).write_text(hist.to_json() + '\n')
        await Replayer(workflows=[AtorRecuperacao, CorrecaoCandidata],
            data_converter=pydantic_data_converter).replay_workflow(hist, raise_on_replay_failure=True)
        activities = [e.activity_task_scheduled_event_attributes for e in hist.events
                      if e.HasField('activity_task_scheduled_event_attributes')]
        for a in activities:
            iv = a.activity_type.name == 'intervir_agente'
            self.assertEqual(a.task_queue.name, self.config['fila_camofox' if iv else 'fila_workflow'])
            self.assertEqual(a.retry_policy.maximum_attempts, 1 if iv else 3)
            if iv:
                self.assertTrue(300 <= a.start_to_close_timeout.seconds <= 900)
        (self.out / (stem + '.summary.json')).write_text(json.dumps(dict(
            workflow_id=h.id, run_id=run_id, eventos=len(hist.events), replay='ok',
            activities=[dict(nome=a.activity_type.name, fila=a.task_queue.name,
                             max_tentativas=a.retry_policy.maximum_attempts, id=a.activity_id,
                             timeout_s=a.start_to_close_timeout.seconds) for a in activities]), indent=2) + '\n')
        for e in hist.events:
            if e.HasField('child_workflow_execution_started_event_attributes'):
                ex = e.child_workflow_execution_started_event_attributes.workflow_execution
                await self.capture(self.client.get_workflow_handle(ex.workflow_id, run_id=ex.run_id))
        return hist

    def evidenciar(self, **values):
        (self.out / (self._testMethodName + '.result.json')).write_text(json.dumps(dict(
            **values, calls=self.fake.calls, registros=self.fake.registros,
            max_sessao=self.fake.max_sessao, max_global=self.fake.max_global), indent=2) + '\n')

    async def test_pausa_recusa_comandos_e_recupera_so_aceitos(self):
        h, state = await self.preparar_falha(('seguinte-a', 'seguinte-b'))
        command = self.comando(state)
        for invalid in (None, {}, {**command, 'revisao': True}, {**command, 'versao': True},
                        {**command, 'filho_run_id': 'outro'}, {**command, 'falha_id': 'seguinte-a'},
                        {**command, 'decisao': 'reexecutar_falha'}, {**command, 'extra': 1}):
            await h.signal('recuperar', invalid)
        await self.enviar('nova-nao-aceita')
        await self.enviar('seguinte-a')
        await self.enviar('falha', 'falha-tecnica')
        await h.signal('solicitar', self.envelope('seguinte-a', 'payload divergente'))
        await h.signal('fechar')
        paused = await self.estado_ate(h, lambda s: s['fechando'])
        self.assertEqual(paused['pendentes'], ['seguinte-a', 'seguinte-b'])
        self.assertEqual(len(self.fake.calls), 1)
        self.assertNotIn('nova-nao-aceita', paused['aceitos'])
        self.assertEqual(sum(o['estado'] == 'recuperacao_recusada' for o in paused['observacoes']), 8)
        self.assertEqual((await h.describe()).status.name, 'RUNNING')
        await h.signal('recuperar', command)
        await h.signal('recuperar', command)
        result = await asyncio.wait_for(h.result(), 30)
        await self.capture(h)
        self.assertEqual([c['passo'] for c in self.fake.calls], ['falha', 'seguinte-a', 'seguinte-b'])
        self.assertEqual(set(result['resultados']), {'seguinte-a', 'seguinte-b'})
        self.assertEqual(result['falhas'], state['falhas'])
        self.assertEqual(len(result['recuperacoes']), 1)
        self.assertEqual(len(self.fake.registros), 2)
        self.assertTrue(all(c['tentativa'] == 1 for c in self.fake.calls))
        self.assertEqual(self.fake.max_sessao[self.sessao], 1)
        self.assertTrue(all(a['fim'] <= b['inicio'] for a, b in zip(self.fake.calls, self.fake.calls[1:])))
        child = self.client.get_workflow_handle(state['bloqueio']['filho_id'], run_id=state['bloqueio']['filho_run_id'])
        hist = await child.fetch_history()
        self.assertEqual((await child.describe()).status.name, 'FAILED')
        self.assertEqual(sum(e.HasField('activity_task_failed_event_attributes') for e in hist.events), 1)
        self.assertFalse(any(e.HasField('timer_started_event_attributes') for e in hist.events))
        with self.assertRaises(WorkflowAlreadyStartedError):
            await self.enviar('seguinte-a')
        self.evidenciar(estado_final=result, filho_falho_sem_retry=True, somente_pendentes=True)

    async def test_restart_durante_pausa_e_apos_recuperacao(self):
        h, state = await self.preparar_falha()
        await self.stack.aclose()
        await self.enviar('seguinte')
        await h.signal('recuperar', {**self.comando(state), 'revisao': 999})
        await self.abrir_workers()
        paused = await self.estado_ate(h, lambda s: any(o['estado'] == 'recuperacao_recusada' for o in s['observacoes']))
        self.assertEqual(paused['falhas'], state['falhas'])
        self.assertEqual(paused['pendentes'], ['seguinte'])
        self.assertEqual(len(self.fake.calls), 1)
        await h.signal('recuperar', self.comando(state))
        await self.estado_ate(h, lambda s: 'seguinte' in s['resultados'])
        await self.stack.aclose()
        await self.enviar('seguinte')
        await self.abrir_workers()
        result = await self.fechar(h)
        self.assertEqual([c['passo'] for c in self.fake.calls], ['falha', 'seguinte'])
        self.assertEqual(len(result['recuperacoes']), 1)
        self.evidenciar(estado_final=result, worker_recriado_duas_vezes=True)

    async def test_continue_as_new_transfere_pausa_fila_e_dedup(self):
        h, state = await self.preparar_falha(('seguinte-a', 'seguinte-b'))
        old = (await h.describe()).run_id
        await h.signal('continuar')
        async def changed():
            d = await h.describe()
            return d.run_id if d.run_id != old else None
        new = await self.esperar(changed)
        await self.capture(self.client.get_workflow_handle(h.id, run_id=old))
        current = self.client.get_workflow_handle(h.id, run_id=new)
        paused = await self.estado_ate(current, lambda s: s['geracao'] == 1)
        for field in ('aceitos', 'resultados', 'falhas', 'pendentes', 'bloqueio', 'revisao'):
            self.assertEqual(paused[field], state[field])
        await self.enviar('falha', 'falha-tecnica')
        await self.enviar('seguinte-a')
        await self.enviar('intrusa')
        await current.signal('recuperar', self.comando(state))
        await self.estado_ate(current, lambda s: len(s['resultados']) == 2)
        await current.signal('continuar')
        async def changed_again():
            d = await h.describe()
            return d.run_id if d.run_id != new else None
        final_run = await self.esperar(changed_again)
        await self.capture(current)
        final = self.client.get_workflow_handle(h.id, run_id=final_run)
        await self.enviar('seguinte-b')
        result = await self.fechar(final)
        self.assertEqual(result['geracao'], 2)
        self.assertEqual(len(result['recuperacoes']), 1)
        self.assertEqual(result['falhas'], state['falhas'])
        self.assertNotIn('intrusa', result['aceitos'])
        self.assertEqual([c['passo'] for c in self.fake.calls], ['falha', 'seguinte-a', 'seguinte-b'])
        self.evidenciar(estado_final=result, duas_geracoes_preservadas=True)

    async def test_duas_falhas_recusam_recuperacao_obsoleta(self):
        h, first = await self.preparar_falha(('falha-dois', 'seguinte'))
        cmd1 = self.comando(first)
        await h.signal('recuperar', cmd1)
        second = await self.estado_ate(h, lambda s: s['revisao'] == 2)
        self.assertEqual(second['pendentes'], ['seguinte'])
        await h.signal('recuperar', cmd1)
        paused = await self.estado_ate(h, lambda s: s['observacoes'][-1]['estado'] == 'recuperacao_recusada')
        self.assertIsNotNone(paused['bloqueio'])
        self.assertEqual(len(self.fake.calls), 2)
        await h.signal('recuperar', self.comando(second))
        result = await self.fechar(h)
        self.assertEqual(set(result['falhas']), {'falha', 'falha-dois'})
        self.assertEqual(set(result['resultados']), {'seguinte'})
        self.assertEqual(len(result['recuperacoes']), 2)
        self.assertEqual([c['passo'] for c in self.fake.calls], ['falha', 'falha-dois', 'seguinte'])
        self.evidenciar(estado_final=result, comando_obsoleto_recusado=True)

    async def test_erro_desconhecido_propaga_sem_recuperacao(self):
        self.fake.bloquear = True
        await self.abrir_workers()
        h = await self.enviar('falha', 'falha-desconhecida')
        await self.enviar('seguinte')
        await self.estado_ate(h, lambda s: len(s['aceitos']) == 2)
        self.fake.liberar.set()
        with self.assertRaises(WorkflowFailureError):
            await asyncio.wait_for(h.result(), 20)
        self.assertEqual((await h.describe()).status.name, 'FAILED')
        await self.capture(h)
        self.assertEqual([c['passo'] for c in self.fake.calls], ['falha'])
        self.assertEqual(self.fake.registros, [])
        self.evidenciar(erro_nao_allowlisted_propagou=True)

    async def test_confirmacao_antecipada_nao_autoriza_falha_futura(self):
        self.fake.bloquear = True
        await self.abrir_workers()
        h = await self.enviar('falha', 'falha-tecnica')
        await self.enviar('seguinte')
        await h.signal('recuperar', dict(versao=1, decisao='retomar_somente_pendentes',
                                        revisao=1, falha_id='falha', filho_run_id='inventado'))
        await self.estado_ate(h, lambda s: any(o['estado'] == 'recuperacao_recusada' for o in s['observacoes']))
        self.fake.liberar.set()
        paused = await self.estado_ate(h, lambda s: s['bloqueio'] is not None)
        self.assertEqual(len(self.fake.calls), 1)
        self.assertEqual(paused['recuperacoes'], [])
        await h.signal('recuperar', self.comando(paused))
        result = await self.fechar(h)
        self.evidenciar(estado_final=result, confirmacao_antecipada_recusada=True)

    async def test_resultado_anterior_preservado_apos_falha(self):
        await self.abrir_workers()
        h = await self.enviar('anterior')
        before = await self.estado_ate(h, lambda s: 'anterior' in s['resultados'])
        self.fake.bloquear = True
        await self.enviar('falha', 'falha-tecnica')
        await self.enviar('seguinte')
        await self.estado_ate(h, lambda s: len(s['aceitos']) == 3)
        self.fake.liberar.set()
        paused = await self.estado_ate(h, lambda s: s['bloqueio'] is not None)
        self.assertEqual(paused['resultados'], before['resultados'])
        await h.signal('recuperar', self.comando(paused))
        result = await self.fechar(h)
        self.assertEqual(result['resultados']['anterior'], before['resultados']['anterior'])
        self.assertEqual([c['passo'] for c in self.fake.calls], ['anterior', 'falha', 'seguinte'])
        self.assertNotIn('falha', result['resultados'])
        self.evidenciar(estado_final=result, resultado_anterior_preservado=True)

    async def test_ingresso_invalido_nao_despacha(self):
        h = await self.enviar('valida')
        for env in ({**self.envelope('versao'), 'versao': 2},
                    {**self.envelope('bool'), 'versao': True},
                    {**self.envelope('config'), 'config': {**self.config, 'fila_camofox': 'camofox-pqbr'}},
                    {**self.envelope('sessao'), 'pedido': {**self.pedido('sessao'), 'sessao': 'outra'}},
                    {**self.envelope('ferramenta'), 'pedido': {**self.pedido('ferramenta'), 'ferramenta': 'notebooklm'}},
                    {**self.envelope(''), 'operacao_id': ''}):
            await h.signal('solicitar', env)
        await self.abrir_workers()
        result = await self.fechar(h)
        self.assertEqual(list(result['aceitos']), ['valida'])
        self.assertEqual(len(self.fake.calls), 1)
        self.evidenciar(estado_final=result, ingresso_invalido_recusado=True)
