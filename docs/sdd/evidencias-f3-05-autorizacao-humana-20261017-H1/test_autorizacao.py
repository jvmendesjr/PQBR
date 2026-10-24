"""E2E da fachada até supervisor fake; nenhuma chamada a serviços reais."""
from dataclasses import asdict, replace
import json
import unittest
from contratos import (Escopo, PedidoDecisao, PoliticaAutorizadores, Recusado,
                       comando_para, selar)
from fluxo import AutorizacaoHumana
from fakes import FakePaperclip, FakePainel, FakeDiscord, FakeSupervisorTemporal, RelogioFake


def ambiente():
    relogio, trilha = RelogioFake(), []
    politica = PoliticaAutorizadores((('paperclip', ('SYN-HUMANO-painel',)),
                                     ('discord', ('SYN-HUMANO-discord',))))
    escopo = Escopo('SYN-SUP-1', 'SYN-SUP-RUN-1', 1, 'SYN-OP-falha',
                    'SYN-FILHO-RUN-falha', 'SYN-REGISTRO-FALHA-RECEIPT',
                    ('SYN-OP-pendente-1', 'SYN-OP-pendente-2'))
    tickets = FakePaperclip(relogio, trilha)
    painel, discord = FakePainel(relogio), FakeDiscord(relogio)
    supervisor = FakeSupervisorTemporal(escopo, tickets, politica, relogio, trilha)
    fluxo = AutorizacaoHumana(tickets, painel, discord, supervisor, politica, relogio)
    return fluxo, tickets, painel, discord, supervisor, relogio, trilha


class FluxoE2E(unittest.TestCase):
    def setUp(self):
        (self.f, self.t, self.p, self.d, self.s, self.r, self.trilha) = ambiente()
        self.ticket, _ = self.f.abrir_pedido()

    def evento(self, canal='paperclip', decisao='aprovar', ator=None, key='SYN-DEC-1',
               ticket=None, timestamp=None, evento_id='SYN-EVENT-1', **changes):
        ticket = ticket or self.ticket
        pedido = PedidoDecisao(ticket.ticket_id, ticket.revisao, ticket.escopo, decisao, key)
        pedido = replace(pedido, **changes)
        port = self.p if canal == 'paperclip' else self.d
        port.autenticar_fixture(evento_id, ator if ator is not None else 'SYN-HUMANO-' +
                                ('painel' if canal == 'paperclip' else 'discord'), pedido, timestamp)
        return evento_id

    def bloqueado(self):
        self.assertTrue(self.s.bloqueado)
        self.assertEqual(self.s.chamadas, 0)
        self.assertEqual(self.s.executados, [])
        self.assertEqual(self.s.pendentes, self.ticket.escopo.pendentes)

    def test_aprovacao_painel_persistida_antes_resume(self):
        evento = self.evento()
        self.assertEqual(self.f.pelo_painel(evento), 'retomada_confirmada')
        ticket = self.t.ler(self.ticket.ticket_id)
        self.assertEqual((ticket.decisao, ticket.ator_id, ticket.canal, ticket.revisao),
                         ('aprovar', 'SYN-HUMANO-painel', 'paperclip', 2))
        estados = [item[0] for item in self.trilha]
        self.assertLess(estados.index('decisao_persistida'), estados.index('resume_chamado'))
        self.assertEqual(self.s.executados, list(self.ticket.escopo.pendentes))
        self.assertEqual(self.s.falhas, {'SYN-OP-falha'})
        self.assertNotIn('SYN-OP-falha', self.s.executados)
        self.assertTrue(self.s.admissao_fechada)
        with self.assertRaises(Recusado):
            self.s.admitir('SYN-OP-nova')

    def test_discord_atualiza_mesmo_ticket_canonico(self):
        self.assertEqual(self.f.pelo_discord(self.evento('discord')), 'retomada_confirmada')
        self.assertEqual(len(self.t.registros), 1)
        ticket = self.t.ler(self.ticket.ticket_id)
        self.assertEqual((ticket.canal, ticket.ator_id, ticket.decisao),
                         ('discord', 'SYN-HUMANO-discord', 'aprovar'))
        self.assertEqual(list(self.d.avisos.values()), [(self.ticket.ticket_id, 1)])

    def test_recusa_painel(self):
        event = self.evento(decisao='recusar')
        self.assertEqual(self.f.pelo_painel(event), 'bloqueado_por_recusa')
        self.assertEqual(self.f.pelo_painel(event), 'bloqueado_por_recusa')
        self.assertEqual(self.t.ler(self.ticket.ticket_id).decisao, 'recusar')
        self.bloqueado()

    def test_recusa_discord(self):
        self.assertEqual(self.f.pelo_discord(self.evento('discord', 'recusar')),
                         'bloqueado_por_recusa')
        self.bloqueado()

    def test_ausencia_ator_autenticado(self):
        for call in (self.f.pelo_painel, self.f.pelo_discord):
            with self.assertRaisesRegex(Recusado, 'nao_autenticado'):
                call('SYN-EVENT-INEXISTENTE')
        self.bloqueado()

    def test_ator_fora_allowlist(self):
        event = self.evento(ator='SYN-HUMANO-intruso')
        with self.assertRaisesRegex(Recusado, 'allowlist'):
            self.f.pelo_painel(event)
        self.assertEqual(self.t.ler(self.ticket.ticket_id).estado, 'pendente')
        self.bloqueado()

    def test_identidade_nao_herda_permissao_outro_canal(self):
        event = self.evento('discord', ator='SYN-HUMANO-painel')
        with self.assertRaisesRegex(Recusado, 'allowlist'):
            self.f.pelo_discord(event)
        self.bloqueado()

    def test_identidade_vazia_recusada(self):
        with self.assertRaises(Recusado):
            self.f.pelo_painel(self.evento(ator=''))
        self.bloqueado()

    def test_aprovacao_sem_ticket(self):
        event = self.evento(ticket_id='SYN-TICKET-inexistente')
        with self.assertRaisesRegex(Recusado, 'ticket_ausente'):
            self.f.pelo_painel(event)
        self.bloqueado()

    def test_ticket_sem_receipt(self):
        self.t.registros[self.ticket.ticket_id] = replace(self.ticket, receipt=None)
        with self.assertRaisesRegex(Recusado, 'receipt'):
            self.f.pelo_painel(self.evento())
        self.bloqueado()

    def test_ticket_stale(self):
        event = self.evento(revisao_ticket=7)
        with self.assertRaisesRegex(Recusado, 'stale'):
            self.f.pelo_painel(event)
        self.bloqueado()

    def test_divergencias_escopo_do_evento(self):
        for field, value in [('supervisor_id', 'SYN-SUP-OUTRO'),
                             ('supervisor_run_id', 'SYN-RUN-OUTRO'),
                             ('falha_id', 'SYN-OP-outra-falha'), ('filho_run_id', 'SYN-FILHO-OUTRO'),
                             ('revisao_falha', 2), ('pendentes', ('SYN-OP-nova',)),
                             ('registro_falha_receipt', '')]:
            with self.subTest(field=field):
                event = self.evento(evento_id='SYN-EVENT-' + field,
                                    escopo=replace(self.ticket.escopo, **{field: value}))
                with self.assertRaises(Recusado):
                    self.f.pelo_painel(event)
        self.bloqueado()

    def test_supervisor_mudou_apos_abertura(self):
        self.s.escopo = replace(self.s.escopo, revisao_falha=2)
        with self.assertRaisesRegex(Recusado, 'supervisor_divergente'):
            self.f.pelo_painel(self.evento())
        self.bloqueado()

    def test_expiracao_nao_retoma(self):
        event = self.evento()
        self.r.valor += 300
        expirado = self.f.expirar(self.ticket.ticket_id)
        self.assertEqual(expirado.estado, 'expirado')
        self.assertEqual(self.f.expirar(self.ticket.ticket_id), expirado)
        with self.assertRaises(Recusado):
            self.f.pelo_painel(event)
        self.bloqueado()

    def test_expiracao_implicita_falha_fechada(self):
        self.r.valor += 301
        with self.assertRaises(Recusado):
            self.f.pelo_discord(self.evento('discord'))
        self.bloqueado()

    def test_expiracao_antecipada_recusada(self):
        with self.assertRaisesRegex(Recusado, 'prazo_nao_esgotado'):
            self.f.expirar(self.ticket.ticket_id)
        self.bloqueado()

    def test_duplicatas_dos_dois_canais(self):
        for canal in ('paperclip', 'discord'):
            with self.subTest(canal=canal):
                self.setUp()
                event = self.evento(canal)
                call = self.f.pelo_painel if canal == 'paperclip' else self.f.pelo_discord
                self.assertEqual(call(event), 'retomada_confirmada')
                for _ in range(4):
                    self.assertEqual(call(event), 'retomada_ja_confirmada')
                self.assertEqual(self.s.executados, list(self.ticket.escopo.pendentes))
                self.assertEqual(len(self.s.consumidos), 1)
                self.assertEqual(sum(x[0] == 'decisao_persistida' for x in self.trilha), 1)

    def test_abertura_e_notificacao_idempotentes(self):
        self.r.valor += 1
        again, ok = self.f.abrir_pedido()
        self.assertEqual(again, self.ticket)
        self.assertTrue(ok)
        self.assertEqual(len(self.t.registros), 1)
        self.assertEqual(len(self.d.avisos), 1)
        self.bloqueado()

    def test_perda_resposta_abertura_retry(self):
        self.f, self.t, self.p, self.d, self.s, self.r, self.trilha = ambiente()
        self.t.perder_resposta.add('abrir')
        with self.assertRaises(TimeoutError):
            self.f.abrir_pedido()
        self.ticket, ok = self.f.abrir_pedido()
        self.assertTrue(ok)
        self.assertEqual(len(self.t.registros), 1)
        self.bloqueado()

    def test_perda_resposta_decisao_retry_sem_dupla_escrita(self):
        event = self.evento('discord')
        self.t.perder_resposta.add('decidir')
        with self.assertRaises(TimeoutError):
            self.f.pelo_discord(event)
        self.assertEqual(self.t.ler(self.ticket.ticket_id).decisao, 'aprovar')
        self.bloqueado()
        # Recriar fachada (sem cache local) não perde correlação ou dedup canônica.
        self.f = AutorizacaoHumana(self.t, self.p, self.d, self.s, self.f.politica, self.r)
        self.assertEqual(self.f.pelo_discord(event), 'retomada_confirmada')
        self.assertEqual(sum(x[0] == 'decisao_persistida' for x in self.trilha), 1)

    def test_perda_ack_temporal_retry_sem_repetir_pendentes(self):
        event = self.evento()
        self.s.perder_resposta = True
        with self.assertRaises(TimeoutError):
            self.f.pelo_painel(event)
        self.assertFalse(self.s.bloqueado)
        self.assertEqual(self.f.pelo_painel(event), 'retomada_ja_confirmada')
        self.assertEqual(self.s.executados, list(self.ticket.escopo.pendentes))

    def test_falha_ticket_api_abrir(self):
        self.f, self.t, self.p, self.d, self.s, self.r, self.trilha = ambiente()
        self.t.falhar.add('abrir')
        with self.assertRaises(ConnectionError):
            self.f.abrir_pedido()
        self.assertFalse(self.t.registros)
        self.bloqueado()

    def test_falha_ticket_api_decidir_retry_explicito(self):
        event = self.evento()
        self.t.falhar.add('decidir')
        with self.assertRaises(ConnectionError):
            self.f.pelo_painel(event)
        self.bloqueado()
        self.assertEqual(self.t.ler(self.ticket.ticket_id).estado, 'pendente')
        self.t.falhar.clear()
        self.assertEqual(self.f.pelo_painel(event), 'retomada_confirmada')

    def test_falha_ticket_api_leitura(self):
        self.t.falhar.add('ler')
        with self.assertRaises(ConnectionError):
            self.f.pelo_painel(self.evento())
        self.bloqueado()

    def test_read_after_write_indisponivel_nao_chama_temporal(self):
        self.t.depois_decidir = lambda: self.t.falhar.add('ler')
        event = self.evento()
        with self.assertRaises(ConnectionError):
            self.f.pelo_painel(event)
        self.bloqueado()
        self.t.falhar.clear()
        self.assertEqual(self.f.pelo_painel(event), 'retomada_confirmada')

    def test_discord_indisponivel_nao_impede_registro_nem_painel(self):
        self.d.indisponivel = True
        ticket, ok = self.f.abrir_pedido()
        self.assertFalse(ok)
        self.assertEqual(ticket, self.ticket)
        self.bloqueado()
        self.assertEqual(self.f.pelo_painel(self.evento()), 'retomada_confirmada')

    def test_discord_indisponivel_nao_inventa_decisao(self):
        event = self.evento('discord')
        self.d.indisponivel = True
        with self.assertRaises(ConnectionError):
            self.f.pelo_discord(event)
        self.bloqueado()

    def test_temporal_indisponivel_nao_repete_decisao(self):
        event = self.evento()
        self.s.falhar_antes = True
        with self.assertRaises(ConnectionError):
            self.f.pelo_painel(event)
        self.assertTrue(self.s.bloqueado)
        self.assertEqual(self.s.executados, [])
        self.assertEqual(self.t.ler(self.ticket.ticket_id).decisao, 'aprovar')
        self.s.falhar_antes = False
        self.assertEqual(self.f.pelo_painel(event), 'retomada_confirmada')

    def test_ticket_minimo_sem_payload_erro_ou_identidade_real(self):
        raw = json.dumps(asdict(self.ticket))
        for forbidden in ('senha', 'token', 'email', 'traceback', 'pedido_bruto', 'excecao'):
            self.assertNotIn(forbidden, raw)
        self.assertEqual(set(asdict(self.ticket.escopo)), {
            'supervisor_id', 'supervisor_run_id', 'revisao_falha', 'falha_id',
            'filho_run_id', 'registro_falha_receipt', 'pendentes', 'versao'})

    def test_sem_registro_falha_nao_abre_ticket(self):
        self.s.escopo = replace(self.s.escopo, registro_falha_receipt='')
        with self.assertRaises(Recusado):
            self.f.abrir_pedido()
        self.bloqueado()

    def test_revisao_booleana_recusada(self):
        with self.assertRaises(Recusado):
            self.f.pelo_painel(self.evento(revisao_ticket=True))
        self.bloqueado()


if __name__ == '__main__':
    unittest.main()
