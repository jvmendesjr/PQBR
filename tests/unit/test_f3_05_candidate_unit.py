"""Candidata local: testes em memória, sem servidor ou backend real."""
import asyncio
from copy import deepcopy
import random
import unittest
from unittest.mock import AsyncMock, patch

from temporalio.common import WorkflowIDConflictPolicy, WorkflowIDReusePolicy

from pqbr.contratos import TriagemCorrecao, ResultadoIntervencao, VerificacaoCorrecao
from pqbr.workflows import candidato_sessao as C
from tests.workflows.composicao_candidata import workers_experimentais, BackendsFalsos


def config():
    return C.configuracao('sessao-teste', C.PREFIXO + 'wf-unit', C.PREFIXO + 'camofox-unit')


def pedido(**kwargs):
    return dict(ferramenta='camofox', sessao='sessao-teste', passo='acao-teste',
                erro='erro-teste', simulacao={}, **kwargs)


class ContratoAtor(unittest.TestCase):
    def setUp(self):
        self.config = config()
        self.ator = C.AtorSessaoCandidato(dict(config=self.config))
        self.envelope = dict(config=self.config, operacao_id='operacao', pedido=pedido(), versao=1)

    def test_mesmo_id_mesma_sessao(self):
        self.assertEqual(C.ator_id('sessao'), C.ator_id('sessao'))
        self.assertNotEqual(C.ator_id('sessao'), C.ator_id('sessao '))

    def test_dedup_normaliza_defaults(self):
        self.ator.solicitar(self.envelope)
        env = deepcopy(self.envelope)
        env['pedido'] = C.normalizar(env['pedido'], self.config['sessao'])
        self.ator.solicitar(env)
        self.assertEqual(list(self.ator.fila), ['operacao'])
        self.assertEqual(self.ator.observacoes[-1]['estado'], 'duplicado')

    def test_payload_divergente_nao_substitui_original(self):
        self.ator.solicitar(self.envelope)
        env = deepcopy(self.envelope)
        env['pedido']['erro'] = 'erro divergente'
        self.ator.solicitar(env)
        self.assertEqual(self.ator.observacoes[-1]['estado'], 'payload_divergente')
        self.assertEqual(self.ator.aceitos['operacao']['erro'], 'erro-teste')

    def test_sessao_divergente_recusada(self):
        self.envelope['pedido']['sessao'] = 'outra'
        self.ator.solicitar(self.envelope)
        self.assertEqual(self.ator.observacoes[-1]['estado'], 'pedido_invalido')
        self.assertFalse(self.ator.fila)

    def test_ferramenta_divergente_recusada(self):
        self.envelope['pedido']['ferramenta'] = 'drive'
        self.ator.solicitar(self.envelope)
        self.assertEqual(self.ator.observacoes[-1]['estado'], 'pedido_invalido')

    def test_config_divergente(self):
        self.envelope['config'] = {**self.config, 'fila_camofox': C.PREFIXO + 'camofox-outra'}
        self.ator.solicitar(self.envelope)
        self.assertEqual(self.ator.observacoes[-1]['estado'], 'configuracao_divergente')

    def test_versao_incompativel(self):
        for version in (2, True, '1', None):
            self.ator.solicitar({**self.envelope, 'versao': version})
        self.assertTrue(all(o['estado'] == 'versao_incompativel' for o in self.ator.observacoes))
        self.assertFalse(self.ator.fila)

    def test_envelope_v1_sem_versao_compativel(self):
        del self.envelope['versao']
        self.ator.solicitar(self.envelope)
        self.assertEqual(list(self.ator.fila), ['operacao'])

    def test_operacao_invalida(self):
        for key in ('', None, 1, 'a' * 201):
            self.ator.solicitar({**self.envelope, 'operacao_id': key})
        self.assertFalse(self.ator.fila)

    def test_handler_sem_efeito_e_fechamento_recusa_novos(self):
        self.ator.solicitar(self.envelope)
        self.ator.fechar()
        self.ator.solicitar({**self.envelope, 'operacao_id': 'nova'})
        self.assertEqual(self.ator.observacoes[-1]['estado'], 'encerrando')
        self.assertEqual(self.ator.resultados, {})

    def test_limite_nao_descarta_ids_existentes(self):
        original = C.normalizar(pedido(), 'sessao-teste')
        self.ator.aceitos = {str(n): original for n in range(1000)}
        self.ator.solicitar(self.envelope)
        self.assertEqual(self.ator.observacoes[-1]['estado'], 'capacidade_experimental')
        self.assertEqual(len(self.ator.aceitos), 1000)

    def test_filas_operacionais_bloqueadas(self):
        for wf, act in [('default', 'camofox-pqbr'), (C.PREFIXO + 'wf-unit', 'camofox-pqbr')]:
            with self.assertRaises(ValueError):
                C.configuracao('sessao', wf, act)

    def test_registro_sem_optin_bloqueado(self):
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(RuntimeError):
                workers_experimentais(object(), self.config, BackendsFalsos())


class PoliticaCandidata(unittest.IsolatedAsyncioTestCase):
    async def test_signal_with_start_so_retorna_handle(self):
        client = AsyncMock()
        marker = object()
        client.start_workflow.return_value = marker
        value = await C.enviar_signal_with_start(client, 'sessao-teste', config()['fila_workflow'],
                                                config()['fila_camofox'], 'id', pedido())
        self.assertIs(value, marker)
        self.assertEqual(client.start_workflow.await_count, 1)
        args, kwargs = client.start_workflow.call_args
        self.assertEqual(kwargs['start_signal'], 'solicitar')
        self.assertEqual(kwargs['id_conflict_policy'], WorkflowIDConflictPolicy.USE_EXISTING)
        self.assertEqual(kwargs['id_reuse_policy'], WorkflowIDReusePolicy.REJECT_DUPLICATE)
        self.assertEqual(kwargs['retry_policy'].maximum_attempts, 1)
        self.assertEqual(kwargs['task_queue'], config()['fila_workflow'])

    async def test_erro_rpc_propaga_sem_reenvio(self):
        client = AsyncMock()
        client.start_workflow.side_effect = RuntimeError('rpc falsa')
        with self.assertRaisesRegex(RuntimeError, 'rpc falsa'):
            await C.enviar_signal_with_start(client, 'sessao-teste', config()['fila_workflow'],
                                            config()['fila_camofox'], 'id', pedido())
        self.assertEqual(client.start_workflow.await_count, 1)

    async def executar(self, effects, *, patched=True):
        self.exec = AsyncMock(side_effect=effects)
        self.sleep = AsyncMock()
        with patch.object(C.workflow, 'execute_activity', self.exec), \
             patch.object(C.workflow, 'sleep', self.sleep), \
             patch.object(C.workflow, 'random', return_value=random.Random(123)), \
             patch.object(C.workflow, 'patched', return_value=patched):
            return await C.CorrecaoCandidata().run(dict(config=config(), pedido=pedido()))

    async def test_roteamento_e_retries_por_activity(self):
        result = await self.executar([
            TriagemCorrecao(classe='corrigivel', motivo='falso'),
            ResultadoIntervencao(resolvido=True, conta_confere=True),
            VerificacaoCorrecao(ok=True), None])
        self.assertEqual(result['resultado'], 'corrigido')
        for call in self.exec.call_args_list:
            fn, _ = call.args
            intervention = fn is C.intervir_agente
            self.assertEqual(call.kwargs['task_queue'], config()['fila_camofox' if intervention else 'fila_workflow'])
            self.assertEqual(call.kwargs['retry_policy'].maximum_attempts, 1 if intervention else 3)
        self.assertEqual(self.sleep.await_count, 0)

    async def test_excecao_tecnica_sem_registro_retry_ou_escada(self):
        with self.assertRaisesRegex(RuntimeError, 'tecnica'):
            await self.executar([TriagemCorrecao(classe='corrigivel', motivo='falso'), RuntimeError('tecnica')])
        self.assertEqual(self.exec.await_count, 2)
        self.assertEqual(self.sleep.await_count, 0)

    async def test_tres_negativas_tem_duas_esperas_sorteadas(self):
        result = await self.executar([TriagemCorrecao(classe='corrigivel', motivo='falso'),
            *[ResultadoIntervencao(resolvido=False, conta_confere=True) for _ in range(3)], None])
        self.assertEqual(result['resultado'], 'esgotado')
        self.assertEqual(result['tentativas'], 3)
        self.assertEqual(self.sleep.await_count, 2)
        for call in self.sleep.call_args_list:
            self.assertTrue(300 <= call.args[0].total_seconds() <= 900)
        interventions = [c for c in self.exec.call_args_list if c.args[0] is C.intervir_agente]
        self.assertEqual(len(interventions), 3)
        for c in interventions:
            self.assertTrue(300 <= c.kwargs['start_to_close_timeout'].total_seconds() <= 900)
            self.assertEqual(c.kwargs['retry_policy'].maximum_attempts, 1)

    async def test_conta_divergente_nao_verifica(self):
        result = await self.executar([TriagemCorrecao(classe='corrigivel', motivo='falso'),
            ResultadoIntervencao(resolvido=True, conta_confere=False), None])
        self.assertEqual(result['resultado'], 'sensivel')
        self.assertEqual(self.exec.await_count, 3)
        self.assertFalse(any(c.args[0] is C.verificar_jev for c in self.exec.call_args_list))

    async def test_patch_preserva_comando_v1(self):
        await self.executar([TriagemCorrecao(classe='corrigivel', motivo='falso'),
            ResultadoIntervencao(resolvido=True, conta_confere=True), VerificacaoCorrecao(ok=True), None], patched=False)
        call = next(c for c in self.exec.call_args_list if c.args[0] is C.intervir_agente)
        self.assertNotIn('activity_id', call.kwargs)

    async def test_patch_novo_adiciona_id_estavel(self):
        await self.executar([TriagemCorrecao(classe='corrigivel', motivo='falso'),
            ResultadoIntervencao(resolvido=True, conta_confere=True), VerificacaoCorrecao(ok=True), None])
        call = next(c for c in self.exec.call_args_list if c.args[0] is C.intervir_agente)
        self.assertEqual(call.kwargs['activity_id'], 'intervencao-1')
