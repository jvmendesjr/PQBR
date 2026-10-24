"""Fakes em memória. IDs artificiais, sem rede/SDK/segredo/worker.

Persistência significa confirmação no armazenamento canônico falso; não há prova
sobre banco real, reinício de processo, exactly-once externo ou autenticação real.
"""
from dataclasses import asdict, replace
from threading import RLock
from contratos import (
    Ticket, EventoAutenticado, PedidoDecisao, Escopo, Recusado,
    exigir, selar, validar_ticket, comando_para,
)


class RelogioFake:
    def __init__(self):
        self.valor = 1_800_000_000

    def agora(self):
        return self.valor


class FakePaperclip:
    def __init__(self, relogio, trilha):
        self.relogio, self.trilha = relogio, trilha
        self.registros, self.chaves = {}, {}
        self.lock = RLock()
        self.falhar = set()
        self.perder_resposta = set()
        self.antes_decidir = None
        self.depois_decidir = None

    def _disponivel(self, operacao):
        if operacao in self.falhar:
            raise ConnectionError('Ticket API fake indisponivel: ' + operacao)

    def _responder(self, operacao, valor):
        if operacao in self.perder_resposta:
            self.perder_resposta.remove(operacao)
            raise TimeoutError('resposta fake perdida: ' + operacao)
        return valor

    def abrir(self, escopo, expira_em, key):
        with self.lock:
            self._disponivel('abrir')
            escopo.validar()
            if key in self.chaves:
                ticket = self.registros[self.chaves[key]]
                exigir(ticket.escopo == escopo, 'abertura_key_conflitante')
                return ticket
            ticket_id = 'SYN-TICKET-' + str(len(self.registros) + 1)
            ticket = selar(Ticket(ticket_id, escopo, self.relogio.agora(), expira_em, key))
            validar_ticket(ticket)
            self.registros[ticket_id] = ticket
            self.chaves[key] = ticket_id
            self.trilha.append(('ticket_aberto', ticket_id, ticket.revisao))
            return self._responder('abrir', ticket)

    def ler(self, ticket_id):
        with self.lock:
            self._disponivel('ler')
            exigir(ticket_id in self.registros, 'ticket_ausente')
            self.trilha.append(('ticket_lido', ticket_id, self.registros[ticket_id].revisao))
            return self.registros[ticket_id]

    def decidir(self, evento):
        with self.lock:
            self._disponivel('decidir')
            if self.antes_decidir:
                self.antes_decidir()
            p = evento.pedido
            ticket = self.ler(p.ticket_id)
            validar_ticket(ticket)
            exigir(ticket.estado == 'pendente' and ticket.revisao == p.revisao_ticket,
                   'cas_ticket_stale')
            exigir(ticket.escopo == p.escopo and self.relogio.agora() < ticket.expira_em,
                   'cas_escopo_ou_expiracao')
            decidido = selar(replace(ticket, revisao=ticket.revisao + 1,
                                     estado='decidido', decisao=p.decisao,
                                     ator_id=evento.ator_id, canal=evento.canal,
                                     decidido_em=self.relogio.agora(), evento_em=evento.timestamp,
                                     decisao_key=p.idempotency_key))
            validar_ticket(decidido)
            self.registros[ticket.ticket_id] = decidido
            self.trilha.append(('decisao_persistida', ticket.ticket_id, decidido.revisao))
            if self.depois_decidir:
                self.depois_decidir()
            return self._responder('decidir', decidido)

    def expirar(self, ticket_id, revisao):
        with self.lock:
            self._disponivel('expirar')
            ticket = self.ler(ticket_id)
            validar_ticket(ticket)
            exigir(self.relogio.agora() >= ticket.expira_em, 'nao_expirou')
            exigir(ticket.revisao == revisao, 'cas_expiracao')
            if ticket.estado == 'expirado':
                return ticket
            exigir(ticket.estado == 'pendente', 'decisao_ja_final')
            ticket = selar(replace(ticket, estado='expirado', revisao=ticket.revisao + 1))
            self.registros[ticket_id] = ticket
            self.trilha.append(('expirado', ticket_id, ticket.revisao))
            return ticket


class FakePainel:
    canal = 'paperclip'

    def __init__(self, relogio):
        self.relogio = relogio
        self.eventos = {}

    def autenticar_fixture(self, evento_id, ator_id, pedido, timestamp=None):
        """Fixture server-side, NÃO endpoint que aceita identidade do payload."""
        exigir(evento_id not in self.eventos, 'evento_fixture_duplicado')
        self.eventos[evento_id] = EventoAutenticado(
            ator_id, self.canal, self.relogio.agora() if timestamp is None else timestamp, pedido)

    def receber_decisao(self, evento_id):
        exigir(evento_id in self.eventos, 'evento_nao_autenticado')
        return self.eventos[evento_id]


class FakeDiscord(FakePainel):
    canal = 'discord'

    def __init__(self, relogio):
        super().__init__(relogio)
        self.indisponivel = False
        self.avisos = {}

    def avisar(self, ticket_id, revisao, key):
        if self.indisponivel:
            raise ConnectionError('Discord fake indisponivel')
        value = (ticket_id, revisao)
        if key in self.avisos:
            # Atualizações do ticket não criam um segundo aviso de abertura.
            exigir(self.avisos[key][0] == ticket_id, 'aviso_conflitante')
        else:
            self.avisos[key] = value

    def receber_decisao(self, evento_id):
        if self.indisponivel:
            raise ConnectionError('Discord fake indisponivel')
        return super().receber_decisao(evento_id)


class FakeSupervisorTemporal:
    def __init__(self, escopo, tickets, politica, relogio, trilha):
        self.escopo, self.tickets, self.politica = escopo, tickets, politica
        self.relogio, self.trilha = relogio, trilha
        self.aceitos = set(escopo.pendentes) | {escopo.falha_id, 'SYN-OP-concluida'}
        self.pendentes = escopo.pendentes
        # Captura imutável no instante da falha; aceitos mutável não amplia direitos.
        self.elegiveis_na_falha = frozenset(escopo.pendentes)
        self.falhas = {escopo.falha_id}
        self.concluidos = {'SYN-OP-concluida'}
        self.bloqueado, self.admissao_fechada = True, True
        self.consumidos, self.executados = {}, []
        self.chamadas = 0
        self.perder_resposta = False
        self.falhar_antes = False
        self.lock = RLock()

    def consultar(self):
        with self.lock:
            exigir(self.bloqueado, 'supervisor_nao_bloqueado')
            exigir(not (set(self.pendentes) & (self.falhas | self.concluidos)),
                   'falho_ou_concluido_na_fila')
            return replace(self.escopo, pendentes=self.pendentes)

    def admitir(self, operacao_id):
        exigir(not self.admissao_fechada, 'admissao_fechada')
        self.aceitos.add(operacao_id)

    def retomar(self, comando):
        with self.lock:
            self.chamadas += 1
            self.trilha.append(('resume_chamado', comando.ticket_id, comando.revisao_ticket))
            if self.falhar_antes:
                raise ConnectionError('Temporal fake indisponivel')
            ticket = self.tickets.ler(comando.ticket_id)
            validar_ticket(ticket)
            exigir(comando == comando_para(ticket), 'comando_sem_receipt_canonico')
            self.politica.validar(ticket.ator_id, ticket.canal)
            if comando.idempotency_key in self.consumidos:
                exigir(self.consumidos[comando.idempotency_key] == comando, 'resume_key_conflitante')
                return 'retomada_ja_confirmada'
            exigir(self.relogio.agora() < ticket.expira_em, 'aprovacao_expirada')
            exigir(self.bloqueado and self.consultar() == comando.escopo, 'cas_supervisor_divergente')
            comando.escopo.validar()
            exigir(set(self.pendentes) <= self.aceitos and
                   set(self.pendentes) <= self.elegiveis_na_falha and
                   not (set(self.pendentes) & (self.falhas | self.concluidos)),
                   'pendentes_nao_elegiveis')
            # Seção crítica fake: validação final + consumo da autorização.
            self.consumidos[comando.idempotency_key] = comando
            self.executados.extend(self.pendentes)
            self.concluidos.update(self.pendentes)
            self.pendentes = ()
            self.bloqueado = False
            self.trilha.append(('retomada_aplicada', ticket.ticket_id, ticket.revisao))
            if self.perder_resposta:
                self.perder_resposta = False
                raise TimeoutError('ACK fake perdido apos retomada')
            return 'retomada_confirmada'
