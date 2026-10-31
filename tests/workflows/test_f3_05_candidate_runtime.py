"""Opt-in: somente container Temporal descartável com gate externo obrigatório."""
import asyncio
from contextlib import AsyncExitStack
from datetime import timedelta
import json
import os
from pathlib import Path
import subprocess
import unittest

from temporalio.client import Client, WorkflowFailureError
from temporalio.common import WorkflowIDReusePolicy
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.exceptions import WorkflowAlreadyStartedError
from temporalio.service import RetryConfig
from temporalio.worker import Replayer

from pqbr.workflows.candidato_sessao import (
    AtorSessaoCandidato, CorrecaoCandidata, PATCH_INTERVENCAO,
    configuracao, enviar_signal_with_start, ator_id,
)
from tests.workflows.composicao_candidata import BackendsFalsos, workers_experimentais


@unittest.skipUnless(os.environ.get('PQBR_CANDIDATE_ISOLATED') == '1', 'exige gate/container descartável')
class CandidataRuntime(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Nenhum tráfego externo: somente leitura da tabela de rotas antes da conexão.
        for family in ('-4', '-6'):
            routes = json.loads(subprocess.check_output(['/usr/bin/ip', '-j', family, 'route']))
            self.assertFalse(any(r.get('dst') == 'default' for r in routes))
        self.out = Path(os.environ['PQBR_CANDIDATE_OUT'])
        gate = json.loads((self.out.parent / 'isolation-gate.json').read_text())
        self.assertTrue(gate['passed'])
        self.client = await Client.connect('127.0.0.1:7233', namespace='f3-05-candidate',
            data_converter=pydantic_data_converter, retry_config=RetryConfig(max_retries=0))
        self.stack = AsyncExitStack()
        await self.stack.__aenter__()
        self.fake = BackendsFalsos()
        self.sessao = self._testMethodName
        prefix = 'teste-f3-05-candidato-'
        self.config = configuracao(self.sessao, prefix + 'wf-' + self.sessao, prefix + 'camofox-' + self.sessao)
        self.handles = []
        self.captured = set()
        self.sequencia = 0

    async def asyncTearDown(self):
        self.fake.liberar.set()
        # Captura também falhas; não reenvia pedidos nem mascara resultado do teste.
        try:
            for h in self.handles:
                try:
                    d = await h.describe()
                    if d.status.name == 'RUNNING':
                        await h.terminate('limpeza do teste candidato')
                    await self.capture(h)
                except Exception as exc:
                    (self.out / (self._testMethodName + '.cleanup-error.txt')).write_text(repr(exc) + '\n')
                    raise
        finally:
            await self.stack.aclose()

    def pedido(self, op='acao', sessao=None, **kwargs):
        return dict(ferramenta='camofox', sessao=sessao or self.sessao, passo=op,
                    erro=kwargs.get('erro', 'falha falsa'), simulacao=kwargs.get('simulacao', {}))

    async def enviar(self, op='acao', sessao=None, pedido=None):
        sessao = sessao or self.sessao
        h = await enviar_signal_with_start(self.client, sessao, self.config['fila_workflow'],
            self.config['fila_camofox'], op, pedido or self.pedido(op, sessao))
        if not any(x.id == h.id for x in self.handles):
            self.handles.append(h)
        return h

    async def abrir_workers(self, *, camofox=True, legado=False):
        principal, destino = workers_experimentais(self.client, self.config, self.fake, legado=legado)
        await self.stack.enter_async_context(principal)
        if camofox:
            await self.stack.enter_async_context(destino)
        return principal, destino

    async def esperar(self, predicate, prazo=15):
        async def poll():
            while True:
                value = await predicate()
                if value:
                    return value
                await asyncio.sleep(0.02)
        return await asyncio.wait_for(poll(), prazo)

    async def estado_ate(self, h, predicate):
        async def poll():
            state = await h.query('estado')
            return state if predicate(state) else None
        return await self.esperar(poll)

    async def fechar(self, h):
        await h.signal('fechar')
        result = await asyncio.wait_for(h.result(), 30)
        await self.capture(h)
        return result

    async def capture(self, h):
        history = await h.fetch_history()
        run_id = history.events[0].workflow_execution_started_event_attributes.original_execution_run_id
        chave = (h.id, run_id, len(history.events))
        if chave in self.captured:
            return history
        self.captured.add(chave)
        self.sequencia += 1
        stem = self._testMethodName + f'.{self.sequencia:02d}'
        (self.out / (stem + '.history.json')).write_text(history.to_json() + '\n')
        await Replayer(workflows=[AtorSessaoCandidato, CorrecaoCandidata],
            data_converter=pydantic_data_converter).replay_workflow(history, raise_on_replay_failure=True)
        activities = [e.activity_task_scheduled_event_attributes for e in history.events
                      if e.HasField('activity_task_scheduled_event_attributes')]
        for a in activities:
            intervencao = a.activity_type.name == 'intervir_agente'
            self.assertEqual(a.task_queue.name, self.config['fila_camofox' if intervencao else 'fila_workflow'])
            self.assertEqual(a.retry_policy.maximum_attempts, 1 if intervencao else 3)
            if intervencao:
                self.assertTrue(300 <= a.start_to_close_timeout.seconds <= 900)
        (self.out / (stem + '.summary.json')).write_text(json.dumps(dict(
            workflow_id=h.id, run_id=run_id, eventos=len(history.events), replay='ok',
            activities=[dict(nome=a.activity_type.name, fila=a.task_queue.name,
                             max_tentativas=a.retry_policy.maximum_attempts, id=a.activity_id,
                             timeout_s=a.start_to_close_timeout.seconds) for a in activities]), indent=2) + '\n')
        for event in history.events:
            if event.HasField('start_child_workflow_execution_initiated_event_attributes'):
                attrs = event.start_child_workflow_execution_initiated_event_attributes
                await self.capture(self.client.get_workflow_handle(attrs.workflow_id))
        return history

    def evidenciar(self, **values):
        (self.out / (self._testMethodName + '.result.json')).write_text(json.dumps(dict(
            **values, calls=self.fake.calls, max_sessao=self.fake.max_sessao,
            max_global=self.fake.max_global, registros=self.fake.registros), indent=2) + '\n')

    async def filho(self, h):
        async def poll():
            history = await h.fetch_history()
            for event in history.events:
                if event.HasField('child_workflow_execution_started_event_attributes'):
                    a = event.child_workflow_execution_started_event_attributes.workflow_execution
                    return self.client.get_workflow_handle(a.workflow_id, run_id=a.run_id)
        return await self.esperar(poll)

    async def test_mesma_sessao_concorrente_sem_sobreposicao(self):
        self.fake.bloquear = True
        await self.abrir_workers()
        handles = await asyncio.gather(*(self.enviar(f'acao-{n:02d}') for n in range(12)))
        self.assertEqual(len({h.result_run_id for h in handles}), 1)
        h = handles[0]
        await self.estado_ate(h, lambda s: len(s['aceitos']) == 12 and s['ativo'] is not None)
        async def primeiro(): return len(self.fake.calls) == 1
        await self.esperar(primeiro)
        self.fake.liberar.set()
        result = await self.fechar(h)
        self.assertEqual(len(result['resultados']), 12)
        self.assertEqual(self.fake.max_sessao[self.sessao], 1)
        calls = self.fake.calls
        self.assertTrue(all(a['fim'] <= b['inicio'] for a, b in zip(calls, calls[1:])))
        self.assertEqual([c['passo'] for c in calls], result['aceitos'])
        self.evidenciar(operacoes=12, sem_sobreposicao=True)

    async def test_sessoes_diferentes_em_paralelo(self):
        self.fake.bloquear = True
        await self.abrir_workers()
        a, b = await asyncio.gather(self.enviar('acao-a'), self.enviar('acao-b', sessao=self.sessao + '-b'))
        async def dois(): return len(self.fake.calls) == 2
        await self.esperar(dois)
        self.assertEqual(self.fake.max_global, 2)
        self.assertTrue(all(x == 1 for x in self.fake.max_sessao.values()))
        self.fake.liberar.set()
        await asyncio.gather(self.fechar(a), self.fechar(b))
        self.evidenciar(paralelismo_observado=True)

    async def test_sem_worker_workflow_rpc_nao_processa_e_retoma(self):
        h = await self.enviar()
        await self.enviar()
        before = await h.fetch_history()
        self.assertFalse(any(e.HasField('workflow_task_completed_event_attributes') for e in before.events))
        self.assertEqual(sum(e.HasField('workflow_execution_signaled_event_attributes') for e in before.events), 2)
        await self.capture(h)
        self.assertEqual(self.fake.calls, [])
        await self.abrir_workers()
        result = await self.fechar(h)
        self.assertEqual(len(self.fake.calls), 1)
        self.assertEqual([o['estado'] for o in result['observacoes']], ['aceito', 'duplicado'])
        self.evidenciar(rpc_sem_processamento=True, retomou_mesmo_run=True)

    async def test_fila_camofox_sem_consumidor_e_retomada_explicita(self):
        _, destino = await self.abrir_workers(camofox=False)
        h = await self.enviar()
        child = await self.filho(h)
        async def agendada():
            history = await child.fetch_history()
            return any(e.HasField('activity_task_scheduled_event_attributes') and
                       e.activity_task_scheduled_event_attributes.activity_type.name == 'intervir_agente'
                       for e in history.events)
        await self.esperar(agendada)
        self.assertEqual(self.fake.calls, [])
        self.assertEqual(self.fake.triagens, 1)
        await self.capture(child)
        await self.stack.enter_async_context(destino)
        await self.fechar(h)
        self.assertEqual(len(self.fake.calls), 1)
        self.assertEqual(self.fake.calls[0]['fila'], self.config['fila_camofox'])
        self.evidenciar(fila_pendente_sem_consumidor=True, consumidor_tardio_executou=True)

    async def test_dedup_payload_config_e_versao(self):
        await self.abrir_workers()
        h = await self.enviar()
        await self.estado_ate(h, lambda s: len(s['resultados']) == 1)
        await self.enviar()
        await self.enviar(pedido=self.pedido(erro='outro erro'))
        envelope = dict(config=self.config, operacao_id='versao', pedido=self.pedido(), versao=2)
        await h.signal('solicitar', envelope)
        envelope = dict(config={**self.config, 'fila_camofox': self.config['fila_camofox'] + '-outra'},
                        operacao_id='config', pedido=self.pedido(), versao=1)
        await h.signal('solicitar', envelope)
        # Envelope v1 legado sem campo versao, defaults normalizados: mesmo pedido.
        await h.signal('solicitar', dict(config=self.config, operacao_id='acao', pedido=self.pedido()))
        result = await self.fechar(h)
        self.assertEqual([o['estado'] for o in result['observacoes']],
                         ['aceito', 'duplicado', 'payload_divergente', 'versao_incompativel', 'configuracao_divergente', 'duplicado'])
        self.assertEqual(len(self.fake.calls), 1)
        self.evidenciar(observacoes=result['observacoes'])

    async def test_excecao_tecnica_falha_sem_retry_fallback_ou_proximo(self):
        self.fake.bloquear = True
        await self.abrir_workers()
        h = await self.enviar('acao-falha', pedido=self.pedido('acao-falha', erro='falha-tecnica'))
        await self.enviar('acao-seguinte')
        await self.estado_ate(h, lambda s: len(s['aceitos']) == 2)
        self.fake.liberar.set()
        with self.assertRaises(WorkflowFailureError):
            await asyncio.wait_for(h.result(), 20)
        history = await self.capture(h)
        self.assertTrue(any(e.HasField('workflow_execution_failed_event_attributes') for e in history.events))
        self.assertEqual(len(self.fake.calls), 1)
        self.assertEqual(self.fake.calls[0]['tentativa'], 1)
        self.assertEqual(self.fake.registros, [])
        child = await self.filho(h)
        hist = await child.fetch_history()
        self.assertFalse(any(e.HasField('timer_started_event_attributes') for e in hist.events))
        self.assertEqual(sum(e.HasField('activity_task_failed_event_attributes') for e in hist.events), 1)
        with self.assertRaises(WorkflowAlreadyStartedError):
            await self.enviar('acao-seguinte')
        self.evidenciar(excecao_propagada=True, sem_retry=True, aceito_seguinte_nao_executado=True)

    async def test_restart_worker_reconstroi_dedup_do_historico(self):
        await self.abrir_workers()
        h = await self.enviar()
        await self.estado_ate(h, lambda s: len(s['resultados']) == 1)
        await self.stack.aclose()
        await self.enviar()
        await self.abrir_workers()
        result = await self.fechar(h)
        self.assertEqual(len(self.fake.calls), 1)
        self.assertEqual(result['observacoes'][-1]['estado'], 'duplicado')
        self.evidenciar(worker_recriado=True)

    async def test_continue_as_new_preserva_ids_e_resultados(self):
        await self.abrir_workers()
        h = await self.enviar()
        await self.estado_ate(h, lambda s: len(s['resultados']) == 1)
        old_id = (await h.describe()).run_id
        await h.signal('continuar')
        async def mudou():
            d = await h.describe()
            return d.run_id if d.run_id != old_id else None
        new_id = await self.esperar(mudou)
        await self.capture(self.client.get_workflow_handle(h.id, run_id=old_id))
        current = self.client.get_workflow_handle(h.id, run_id=new_id)
        await self.enviar()
        await self.estado_ate(current, lambda s: bool(s['observacoes']))
        result = await self.fechar(current)
        self.assertEqual(result['geracao'], 1)
        self.assertEqual(result['observacoes'][-1]['estado'], 'duplicado')
        self.assertEqual(len(self.fake.calls), 1)
        self.evidenciar(continue_as_new_preserva_dedup=True)

    async def test_replay_versao_anterior_sem_patch_e_nova_com_patch(self):
        await self.abrir_workers(legado=True)
        old = await self.enviar('acao-legado')
        await self.fechar(old)
        child = await self.filho(old)
        history = await child.fetch_history()
        self.assertFalse(any(e.HasField('marker_recorded_event_attributes') and
                             e.marker_recorded_event_attributes.marker_name == 'core_patch'
                             for e in history.events))
        await self.stack.aclose()
        await self.abrir_workers()
        novo = await self.enviar('acao-nova', sessao=self.sessao + '-nova')
        await self.fechar(novo)
        new_child = await self.filho(novo)
        new_history = await new_child.fetch_history()
        # to_json representa Payload.data em base64; conferir protobuf decodificado.
        patch_ids = []
        for event in new_history.events:
            if event.HasField('marker_recorded_event_attributes'):
                marker = event.marker_recorded_event_attributes
                if marker.marker_name == 'core_patch':
                    patch_ids.extend(json.loads(p.data)['id']
                                     for p in marker.details['patch-data'].payloads)
        self.assertIn(PATCH_INTERVENCAO, patch_ids)
        activities = [e.activity_task_scheduled_event_attributes for e in new_history.events
                      if e.HasField('activity_task_scheduled_event_attributes')]
        self.assertEqual(next(a for a in activities if a.activity_type.name == 'intervir_agente').activity_id, 'intervencao-1')
        self.evidenciar(replay_legado_sem_patch=True, nova_execucao_com_patch=True, patch_ids=patch_ids)

    async def test_trava_sensivel_e_conta_divergente(self):
        await self.abrir_workers()
        h = await self.enviar('login-sensivel')
        result = await self.fechar(h)
        self.assertEqual(result['resultados']['login-sensivel']['resultado'], 'sensivel')
        self.assertEqual(len(self.fake.calls), 0)
        other = await self.enviar('acao-conta', sessao=self.sessao + '-conta',
            pedido=self.pedido('acao-conta', self.sessao + '-conta', simulacao={'conta_confere': False}))
        result = await self.fechar(other)
        self.assertEqual(result['resultados']['acao-conta']['resultado'], 'sensivel')
        self.assertEqual(len(self.fake.calls), 1)
        self.evidenciar(trava_sensivel=True, conta_divergente_interrompe=True)
