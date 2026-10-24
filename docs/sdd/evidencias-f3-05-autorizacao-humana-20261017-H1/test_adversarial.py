import unittest
from dataclasses import replace

from contratos import (
    Escopo, PoliticaAutorizadores, PedidoDecisao, Recusado,
    ComandoRetomada, selar,
)
from fluxo import AutorizacaoHumana
from fakes import RelogioFake, FakePaperclip, FakePainel, FakeDiscord, FakeSupervisorTemporal


class Adversarial(unittest.TestCase):
    def setUp(self):
        self.clock = RelogioFake()
        self.log = []
        self.scope = Escopo('SUP-1', 'RUN-1', 4, 'FAIL-1', 'CHILD-1',
                            'RECEIPT-1', ('OP-1', 'OP-2'))
        self.policy = PoliticaAutorizadores((('paperclip', ('HUMAN-PC',)),
                                              ('discord', ('HUMAN-DC',))))
        self.tickets = FakePaperclip(self.clock, self.log)
        self.panel, self.discord = FakePainel(self.clock), FakeDiscord(self.clock)
        self.supervisor = FakeSupervisorTemporal(self.scope, self.tickets, self.policy,
                                                 self.clock, self.log)
        self.facade = AutorizacaoHumana(self.tickets, self.panel, self.discord,
                                        self.supervisor, self.policy, self.clock)
        self.ticket, _ = self.facade.abrir_pedido()

    def event(self, key='DEC-1', decision='aprovar', channel='paperclip',
              actor='HUMAN-PC', ticket=None, timestamp=None):
        t = ticket or self.ticket
        p = PedidoDecisao(t.ticket_id, t.revisao, t.escopo, decision, key)
        eid = 'EV-' + key
        port = self.panel if channel == 'paperclip' else self.discord
        port.autenticar_fixture(eid, actor, p, timestamp)
        return eid

    def test_approval_resumes_only_accepted_pending(self):
        eid = self.event()
        self.assertEqual(self.facade.pelo_painel(eid), 'retomada_confirmada')
        self.assertEqual(self.supervisor.executados, ['OP-1', 'OP-2'])
        self.assertFalse(self.supervisor.bloqueado)

    def test_ticket_revision_race_between_read_and_cas_is_rejected(self):
        def race():
            t = self.tickets.registros[self.ticket.ticket_id]
            self.tickets.registros[t.ticket_id] = selar(replace(t, revisao=t.revisao + 1))
        self.tickets.antes_decidir = race
        with self.assertRaises(Recusado):
            self.facade.pelo_painel(self.event())
        self.assertEqual(self.supervisor.chamadas, 0)

    def test_supervisor_swap_after_persist_before_resume_is_rejected(self):
        def swap():
            self.supervisor.pendentes = ('OP-1',)
        self.tickets.depois_decidir = swap
        with self.assertRaises(Recusado):
            self.facade.pelo_painel(self.event())
        self.assertEqual(self.supervisor.executados, [])

    def test_mutated_receipt_is_rejected(self):
        t = self.tickets.registros[self.ticket.ticket_id]
        self.tickets.registros[t.ticket_id] = replace(t, receipt='fake-receipt:forged')
        with self.assertRaises(Recusado):
            self.facade.pelo_painel(self.event())

    def test_direct_resume_without_approved_ticket_rejected(self):
        cmd = ComandoRetomada(self.ticket.ticket_id, 2, 'forged', self.scope,
                              'HUMAN-PC', 'paperclip', self.clock.agora(), 'FORGED')
        with self.assertRaises(Recusado):
            self.supervisor.retomar(cmd)
        self.assertEqual(self.supervisor.executados, [])

    def test_direct_resume_with_altered_command_rejected(self):
        eid = self.event()
        self.facade.pelo_painel(eid)
        decided = self.tickets.ler(self.ticket.ticket_id)
        from contratos import comando_para
        cmd = comando_para(decided)
        with self.assertRaises(Recusado):
            self.supervisor.retomar(replace(cmd, acao='executar_tudo'))

    def test_new_operation_injected_into_scope_is_rejected(self):
        self.supervisor.pendentes = ('OP-1', 'OP-NEW')
        self.supervisor.aceitos.add('OP-NEW')
        # Open a ticket against the changed snapshot, to reach eligibility validation.
        ticket, _ = self.facade.abrir_pedido()
        p = PedidoDecisao(ticket.ticket_id, ticket.revisao, ticket.escopo, 'aprovar', 'NEW-DEC')
        self.panel.autenticar_fixture('EV-NEW', 'HUMAN-PC', p)
        with self.assertRaises(Recusado):
            self.facade.pelo_painel('EV-NEW')
        self.assertEqual(self.supervisor.executados, [])

    def test_failed_operation_cannot_be_pending(self):
        self.supervisor.pendentes = ('FAIL-1',)
        with self.assertRaises(Recusado):
            self.facade.abrir_pedido()

    def test_completed_operation_cannot_be_pending(self):
        self.supervisor.pendentes = ('SYN-OP-concluida',)
        with self.assertRaises(Recusado):
            self.facade.abrir_pedido()

    def test_wrong_event_channel_rejected(self):
        eid = self.event(channel='discord', actor='HUMAN-DC')
        with self.assertRaises(Recusado):
            self.facade.pelo_painel(eid)

    def test_conflicting_idempotency_replay_rejected(self):
        eid = self.event()
        self.facade.pelo_painel(eid)
        other = self.event(key='OTHER-KEY', ticket=self.tickets.ler(self.ticket.ticket_id))
        with self.assertRaises(Recusado):
            self.facade.pelo_painel(other)

    def test_old_authorization_rejected(self):
        eid = self.event(timestamp=self.clock.agora() - self.policy.idade_maxima_evento - 1)
        with self.assertRaises(Recusado):
            self.facade.pelo_painel(eid)

    def test_lost_resume_ack_retry_via_facade_is_idempotent(self):
        eid = self.event()
        self.supervisor.perder_resposta = True
        with self.assertRaises(TimeoutError):
            self.facade.pelo_painel(eid)
        self.assertEqual(self.facade.pelo_painel(eid), 'retomada_ja_confirmada')
        self.assertEqual(self.supervisor.executados, ['OP-1', 'OP-2'])

    def test_lost_decision_response_does_not_resume_on_first_attempt(self):
        eid = self.event()
        self.tickets.perder_resposta.add('decidir')
        with self.assertRaises(TimeoutError):
            self.facade.pelo_painel(eid)
        self.assertEqual(self.supervisor.chamadas, 0)


if __name__ == '__main__':
    unittest.main()
