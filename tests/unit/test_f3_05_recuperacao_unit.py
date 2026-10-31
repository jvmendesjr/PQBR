"""Sem rede, servidor, segredo ou efeito externo."""
from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from tests.workflows import prototipo_recuperacao_pendentes as P


def config():
    return dict(sessao='sintetica', fila_workflow='teste-f3-05-candidato-wf-unit-recuperacao',
                fila_camofox='teste-f3-05-candidato-camofox-unit-recuperacao')


class ProtocoloRecuperacao(unittest.TestCase):
    def setUp(self):
        self.a = P.AtorRecuperacao(dict(config=config()))
        self.e = dict(versao=1, config=config(), operacao_id='op',
                      pedido=dict(ferramenta='camofox', sessao='sintetica', passo='acao', erro='falso', simulacao={}))
        self.b = dict(operacao_id='falha', filho_run_id='run-falho', revisao=1)
        self.cmd = dict(versao=1, decisao='retomar_somente_pendentes', revisao=1,
                        falha_id='falha', filho_run_id='run-falho')

    def test_filas_operacionais_recusadas(self):
        for wf, ca in [('default', 'camofox-pqbr'),
                       ('teste-f3-05-candidato-wf-unit', 'teste-f3-05-candidato-camofox-unit')]:
            with self.assertRaises(ValueError):
                P.validar_config({**config(), 'fila_workflow': wf, 'fila_camofox': ca})

    def test_sem_optin_nao_constroi_workers(self):
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(RuntimeError):
                P.workers_sinteticos(SimpleNamespace(namespace='f3-05-recovery'), config(), None)

    def test_namespace_errado_bloqueado(self):
        with patch.dict('os.environ', {'PQBR_RECOVERY_ISOLATED': '1', 'PQBR_CANDIDATE_ISOLATED': '1'}, clear=True):
            with self.assertRaises(RuntimeError):
                P.workers_sinteticos(SimpleNamespace(namespace='default'), config(), None)

    def test_id_distinto_da_candidata(self):
        from pqbr.workflows.candidato_sessao import ator_id
        self.assertNotEqual(P.ator_id('sintetica'), ator_id('sintetica'))
        self.assertNotEqual(P.ator_id('sintetica'), P.ator_id('sintetica '))

    def test_dedup_antes_e_apos_pausa(self):
        self.a.solicitar(self.e)
        self.a.admissao_fechada = True
        self.a.solicitar(self.e)
        self.assertEqual(list(self.a.fila), ['op'])
        self.assertEqual(self.a.observacoes[-1]['estado'], 'duplicado')

    def test_divergencia_nao_substitui_aceito(self):
        self.a.solicitar(self.e)
        other = deepcopy(self.e)
        other['pedido']['erro'] = 'outro'
        self.a.solicitar(other)
        self.assertEqual(self.a.observacoes[-1]['estado'], 'payload_divergente')
        self.assertEqual(self.a.aceitos['op']['erro'], 'falso')

    def test_nova_operacao_apos_pausa_recusada(self):
        self.a.admissao_fechada = True
        self.a.solicitar(self.e)
        self.assertEqual(self.a.observacoes[-1]['estado'], 'admissao_fechada')
        self.assertFalse(self.a.aceitos)

    def test_confirmacao_antecipada_nao_fica_armada(self):
        self.a.recuperar(self.cmd)
        self.assertFalse(self.a.recuperacoes)
        self.a.bloqueio = self.b
        self.a.revisao = 1
        self.assertIsNotNone(self.a.bloqueio)

    def test_confirmacao_exata_preserva_falha_e_nao_reenfileira(self):
        self.a.solicitar(self.e)
        self.a.bloqueio = self.b
        self.a.falhas['falha'] = deepcopy(self.b)
        self.a.revisao = 1
        self.a.admissao_fechada = True
        self.a.recuperar(self.cmd)
        self.assertIsNone(self.a.bloqueio)
        self.assertEqual(self.a.falhas['falha'], self.b)
        self.assertEqual(list(self.a.fila), ['op'])
        self.assertTrue(self.a.admissao_fechada)
        self.a.recuperar(self.cmd)
        self.assertEqual(len(self.a.recuperacoes), 1)

    def test_confirmacao_divergente_recusada(self):
        self.a.bloqueio = self.b
        self.a.revisao = 1
        for cmd in (None, {}, {**self.cmd, 'versao': True}, {**self.cmd, 'revisao': True},
                    {**self.cmd, 'revisao': 2}, {**self.cmd, 'falha_id': 'outra'},
                    {**self.cmd, 'filho_run_id': 'outro'}, {**self.cmd, 'extra': True}):
            self.a.recuperar(cmd)
            self.assertEqual(self.a.bloqueio, self.b)
        self.assertFalse(self.a.recuperacoes)

    def test_fechar_nao_libera_bloqueio(self):
        self.a.bloqueio = self.b
        self.a.fechar()
        self.assertEqual(self.a.bloqueio, self.b)
        self.assertTrue(self.a.fechando)

    def test_seed_preserva_fila_falha_e_resultado(self):
        self.a.solicitar(self.e)
        self.a.bloqueio = self.b
        self.a.revisao = 1
        self.a.falhas['falha'] = self.b
        self.a.resultados['antes'] = {'resultado': 'corrigido'}
        self.a.admissao_fechada = True
        self.a.observacoes.append({'estado': 'pausado_apos_falha'})
        state = self.a.estado()
        state['fila'] = state.pop('pendentes')
        b = P.AtorRecuperacao(dict(config=config(), seed=deepcopy(state), geracao=1))
        expected = self.a.estado()
        expected['geracao'] = 1
        self.assertEqual(b.estado(), expected)
