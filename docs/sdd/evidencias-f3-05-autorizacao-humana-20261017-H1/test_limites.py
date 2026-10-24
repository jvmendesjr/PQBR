from dataclasses import replace
import unittest
from contratos import PedidoDecisao, Recusado, selar, comando_para
from test_autorizacao import ambiente


class Limites(unittest.TestCase):
    def setUp(self):
        self.f, self.t, self.p, self.d, self.s, self.r, self.trilha = ambiente()
        self.ticket, _ = self.f.abrir_pedido(1000)
        self.pedido = PedidoDecisao(self.ticket.ticket_id, 1, self.ticket.escopo,
                                   'aprovar', 'SYN-KEY-1')

    def event(self, pedido=None, timestamp=None, key='SYN-EV-1'):
        self.p.autenticar_fixture(key, 'SYN-HUMANO-painel', pedido or self.pedido, timestamp)
        return key

    def test_evento_antigo_com_ticket_ainda_vigente(self):
        event = self.event()
        self.r.valor += 301
        with self.assertRaisesRegex(Recusado, 'antiga'):
            self.f.pelo_painel(event)
        self.assertEqual(self.s.chamadas, 0)

    def test_evento_futuro(self):
        event = self.event(timestamp=self.r.valor + 1)
        with self.assertRaisesRegex(Recusado, 'fora_janela'):
            self.f.pelo_painel(event)
        self.assertEqual(self.s.chamadas, 0)

    def test_recusa_nao_pode_ser_convertida_em_aprovacao(self):
        refusal = replace(self.pedido, decisao='recusar')
        self.f.pelo_painel(self.event(refusal))
        with self.assertRaises(Recusado):
            self.f.pelo_painel(self.event(key='SYN-EV-2'))
        self.assertEqual(self.s.chamadas, 0)
        self.assertTrue(self.s.bloqueado)

    def test_outra_identidade_nao_reusa_dispatch(self):
        event = self.event()
        self.t.perder_resposta.add('decidir')
        with self.assertRaises(TimeoutError):
            self.f.pelo_painel(event)
        # Humano de outro canal, mesmo key: não substitui ator da decisão original.
        self.d.autenticar_fixture('SYN-DISCORD-1', 'SYN-HUMANO-discord', self.pedido)
        with self.assertRaises(Recusado):
            self.f.pelo_discord('SYN-DISCORD-1')
        self.assertEqual(self.s.chamadas, 0)

    def test_receipt_decisao_sem_ator(self):
        event = self.event()
        self.t.perder_resposta.add('decidir')
        with self.assertRaises(TimeoutError):
            self.f.pelo_painel(event)
        ticket = self.t.registros[self.ticket.ticket_id]
        self.t.registros[ticket.ticket_id] = selar(replace(ticket, ator_id=None))
        with self.assertRaises(Recusado):
            self.f.pelo_painel(event)
        self.assertEqual(self.s.chamadas, 0)

    def test_canonico_trocado_apos_escrita_nao_chama_temporal(self):
        def swap():
            ticket = self.t.registros[self.ticket.ticket_id]
            self.t.registros[ticket.ticket_id] = selar(replace(ticket, decisao='recusar'))
        self.t.depois_decidir = swap
        with self.assertRaises(Recusado):
            self.f.pelo_painel(self.event())
        self.assertEqual(self.s.chamadas, 0)
        self.assertTrue(self.s.bloqueado)

    def test_revogacao_allowlist_antes_retry(self):
        event = self.event()
        self.t.perder_resposta.add('decidir')
        with self.assertRaises(TimeoutError):
            self.f.pelo_painel(event)
        self.f.politica = replace(self.f.politica, por_canal=())
        with self.assertRaises(Recusado):
            self.f.pelo_painel(event)
        self.assertEqual(self.s.chamadas, 0)

    def test_sem_receipt_canonico_apos_aprovacao(self):
        event = self.event()
        self.t.perder_resposta.add('decidir')
        with self.assertRaises(TimeoutError):
            self.f.pelo_painel(event)
        ticket = self.t.registros[self.ticket.ticket_id]
        cmd = comando_para(ticket)
        self.t.registros[ticket.ticket_id] = replace(ticket, receipt=None)
        with self.assertRaises(Recusado):
            self.s.retomar(cmd)
        self.assertTrue(self.s.bloqueado)
        self.assertFalse(self.s.executados)

    def test_aprovacao_expira_entre_persistencia_e_resume(self):
        def advance():
            self.r.valor += 1000
        self.t.depois_decidir = advance
        with self.assertRaises(Recusado):
            self.f.pelo_painel(self.event())
        self.assertTrue(self.s.bloqueado)
        self.assertFalse(self.s.executados)

    def test_recibo_de_outro_ticket_nao_autoriza(self):
        event = self.event()
        self.t.perder_resposta.add('decidir')
        with self.assertRaises(TimeoutError):
            self.f.pelo_painel(event)
        cmd = comando_para(self.t.ler(self.ticket.ticket_id))
        with self.assertRaises(Recusado):
            self.s.retomar(replace(cmd, ticket_id='SYN-TICKET-outro'))
        self.assertTrue(self.s.bloqueado)

    def test_expiracao_durante_cas_decisao(self):
        self.t.antes_decidir = lambda: setattr(self.r, 'valor', self.ticket.expira_em)
        with self.assertRaises(Recusado):
            self.f.pelo_painel(self.event())
        self.assertEqual(self.s.chamadas, 0)
        self.assertEqual(self.t.ler(self.ticket.ticket_id).estado, 'pendente')

    def test_reordenar_pendentes_apos_abertura_recusado(self):
        self.s.pendentes = tuple(reversed(self.s.pendentes))
        with self.assertRaises(Recusado):
            self.f.pelo_painel(self.event())
        self.assertEqual(self.s.chamadas, 0)
