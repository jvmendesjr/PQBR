"""Orquestração offline: não importa SDKs, workflows ou credenciais reais."""
from dataclasses import asdict
from contratos import (
    Escopo, EventoAutenticado, TicketPaperclipPort, PainelPaperclipPort,
    DiscordPort, SupervisorTemporalPort, RelogioPort, PoliticaAutorizadores,
    exigir, digest, validar_ticket, comando_para,
)


class AutorizacaoHumana:
    def __init__(self, tickets: TicketPaperclipPort, painel: PainelPaperclipPort,
                 discord: DiscordPort, supervisor: SupervisorTemporalPort,
                 politica: PoliticaAutorizadores, relogio: RelogioPort):
        self.tickets, self.painel, self.discord = tickets, painel, discord
        self.supervisor, self.politica, self.relogio = supervisor, politica, relogio

    def abrir_pedido(self, validade_segundos=300):
        exigir(type(validade_segundos) is int and validade_segundos > 0, 'validade')
        escopo = self.supervisor.consultar()
        escopo.validar()
        key = 'abertura:' + digest(asdict(escopo))
        ticket = self.tickets.abrir(escopo, self.relogio.agora() + validade_segundos, key)
        validar_ticket(ticket)
        exigir(ticket.escopo == escopo and ticket.abertura_key == key, 'abertura_divergente')
        # Indisponibilidade do aviso não dá autorização nem perde registro oficial.
        notificado = True
        try:
            self.discord.avisar(ticket.ticket_id, ticket.revisao, 'aviso:' + key)
        except (ConnectionError, TimeoutError):
            notificado = False
        return ticket, notificado

    def pelo_painel(self, evento_id):
        return self._decidir(self.painel.receber_decisao(evento_id), 'paperclip')

    def pelo_discord(self, evento_id):
        return self._decidir(self.discord.receber_decisao(evento_id), 'discord')

    def _decidir(self, evento, canal):
        exigir(isinstance(evento, EventoAutenticado) and evento.canal == canal,
               'metadado_nao_autenticado')
        self.politica.validar(evento.ator_id, canal)
        p = evento.pedido
        exigir(p.decisao in ('aprovar', 'recusar'), 'decisao_invalida')
        exigir(type(p.idempotency_key) is str and bool(p.idempotency_key), 'key_ausente')
        exigir(type(p.revisao_ticket) is int and p.revisao_ticket > 0, 'revisao_ticket')
        ticket = self.tickets.ler(p.ticket_id)
        validar_ticket(ticket)
        exigir(ticket.ticket_id == p.ticket_id and ticket.escopo == p.escopo,
               'ticket_ou_escopo_divergente')
        agora = self.relogio.agora()
        exigir(type(evento.timestamp) is int and ticket.criado_em <= evento.timestamp <= agora,
               'evento_fora_janela')
        exigir(agora < ticket.expira_em and agora - evento.timestamp <= self.politica.idade_maxima_evento,
               'autorizacao_antiga')
        if ticket.estado == 'decidido':
            # Retry do MESMO despacho, não nova decisão para ticket já encerrado.
            exigir((ticket.decisao_key, ticket.ator_id, ticket.canal, ticket.decisao,
                    ticket.evento_em, ticket.revisao) ==
                   (p.idempotency_key, evento.ator_id, canal, p.decisao,
                    evento.timestamp, p.revisao_ticket + 1), 'decisao_conflitante')
        else:
            exigir(ticket.estado == 'pendente' and ticket.revisao == p.revisao_ticket,
                   'ticket_stale')
            atual = self.supervisor.consultar()
            exigir(atual == ticket.escopo, 'supervisor_divergente')
            atual.validar()
            # CAS também no backend; perda da resposta NÃO chama Temporal nesta tentativa.
            confirmado = self.tickets.decidir(evento)
            validar_ticket(confirmado)
            ticket = self.tickets.ler(p.ticket_id)  # read-after-write/receipt canônico
            exigir(ticket == confirmado, 'persistencia_nao_confirmada')
            validar_ticket(ticket)
        exigir(ticket.estado == 'decidido' and ticket.decisao == p.decisao
               and ticket.ator_id == evento.ator_id and ticket.canal == canal
               and ticket.decisao_key == p.idempotency_key
               and ticket.evento_em == evento.timestamp
               and ticket.revisao == p.revisao_ticket + 1,
               'receipt_decisao_divergente')
        if ticket.decisao == 'recusar':
            return 'bloqueado_por_recusa'
        # O receptor revalida estado atual + ticket/receipt, atomicamente com dedup.
        return self.supervisor.retomar(comando_para(ticket))

    def expirar(self, ticket_id):
        ticket = self.tickets.ler(ticket_id)
        validar_ticket(ticket)
        exigir(self.relogio.agora() >= ticket.expira_em, 'prazo_nao_esgotado')
        return self.tickets.expirar(ticket_id, ticket.revisao)
