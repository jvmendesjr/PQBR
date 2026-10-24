"""F3-05: contratos SINTÉTICOS; nenhuma integração operacional.

As portas são limites de confiança: identidade vem de metadado server-side,
nunca de campos enviados pelo usuário. Hash de receipt NÃO autentica um ator.
"""
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json
from typing import Protocol


class Recusado(ValueError):
    pass


def exigir(ok, motivo):
    if not ok:
        raise Recusado(motivo)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


@dataclass(frozen=True)
class Escopo:
    supervisor_id: str
    supervisor_run_id: str
    revisao_falha: int
    falha_id: str
    filho_run_id: str
    registro_falha_receipt: str
    pendentes: tuple[str, ...]
    versao: int = 1

    def validar(self):
        exigir(type(self.versao) is int and self.versao == 1, 'versao')
        exigir(type(self.revisao_falha) is int and self.revisao_falha > 0, 'revisao_falha')
        for value in (self.supervisor_id, self.supervisor_run_id, self.falha_id,
                      self.filho_run_id, self.registro_falha_receipt, *self.pendentes):
            exigir(type(value) is str and 0 < len(value) <= 200, 'id_ausente_ou_invalido')
        exigir(type(self.pendentes) is tuple and bool(self.pendentes), 'pendentes')
        exigir(len(set(self.pendentes)) == len(self.pendentes), 'pendentes_duplicados')
        exigir(self.falha_id not in self.pendentes, 'falho_na_fila')


@dataclass(frozen=True)
class PedidoDecisao:
    ticket_id: str
    revisao_ticket: int
    escopo: Escopo
    decisao: str
    idempotency_key: str


@dataclass(frozen=True)
class EventoAutenticado:
    """Só retornado pela porta confiável; sem bool autenticado no payload."""
    ator_id: str
    canal: str
    timestamp: int
    pedido: PedidoDecisao


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    escopo: Escopo
    criado_em: int
    expira_em: int
    abertura_key: str
    revisao: int = 1
    versao: int = 1
    estado: str = 'pendente'
    decisao: str | None = None
    ator_id: str | None = None
    canal: str | None = None
    decidido_em: int | None = None
    evento_em: int | None = None
    decisao_key: str | None = None
    receipt: str | None = None


def selar(ticket):
    data = asdict(replace(ticket, receipt=None))
    return replace(ticket, receipt='fake-receipt:' + digest(data))


def validar_ticket(ticket):
    exigir(isinstance(ticket, Ticket), 'ticket_ausente')
    ticket.escopo.validar()
    exigir(type(ticket.versao) is int and ticket.versao == 1, 'versao_ticket')
    exigir(type(ticket.revisao) is int and ticket.revisao > 0, 'revisao_ticket')
    exigir(bool(ticket.ticket_id) and bool(ticket.abertura_key), 'ticket_sem_id')
    exigir(type(ticket.criado_em) is int and type(ticket.expira_em) is int
           and ticket.criado_em < ticket.expira_em, 'prazo_ticket')
    exigir(bool(ticket.receipt) and selar(ticket).receipt == ticket.receipt, 'receipt_invalido')
    exigir(ticket.estado in ('pendente', 'decidido', 'expirado'), 'estado_ticket')
    if ticket.estado == 'decidido':
        exigir(ticket.decisao in ('aprovar', 'recusar') and bool(ticket.ator_id)
               and ticket.canal in ('paperclip', 'discord') and bool(ticket.decisao_key)
               and type(ticket.decidido_em) is int and type(ticket.evento_em) is int
               and ticket.criado_em <= ticket.evento_em <= ticket.decidido_em < ticket.expira_em
               and ticket.revisao >= 2, 'decisao_incompleta')
    else:
        exigir(all(v is None for v in (ticket.decisao, ticket.ator_id, ticket.canal,
                                       ticket.decidido_em, ticket.evento_em, ticket.decisao_key)),
               'decisao_fora_estado')


@dataclass(frozen=True)
class ComandoRetomada:
    ticket_id: str
    revisao_ticket: int
    receipt: str
    escopo: Escopo
    ator_id: str
    canal: str
    decidido_em: int
    idempotency_key: str
    versao: int = 1
    acao: str = 'retomar_somente_pendentes_ja_aceitos'


def comando_para(ticket):
    validar_ticket(ticket)
    exigir(ticket.estado == 'decidido' and ticket.decisao == 'aprovar', 'sem_aprovacao')
    return ComandoRetomada(ticket.ticket_id, ticket.revisao, ticket.receipt,
                          ticket.escopo, ticket.ator_id, ticket.canal, ticket.decidido_em,
                          'resume:' + digest([ticket.ticket_id, ticket.decisao_key, ticket.receipt]))


class TicketPaperclipPort(Protocol):
    def abrir(self, escopo: Escopo, expira_em: int, key: str) -> Ticket: ...
    def ler(self, ticket_id: str) -> Ticket: ...
    def decidir(self, evento: EventoAutenticado) -> Ticket:
        """CAS atômico, first-decision-wins, receipt canônico após persistência."""
        ...
    def expirar(self, ticket_id: str, revisao: int) -> Ticket: ...


class PainelPaperclipPort(Protocol):
    def receber_decisao(self, evento_id: str) -> EventoAutenticado: ...


class DiscordPort(Protocol):
    def avisar(self, ticket_id: str, revisao: int, key: str) -> None: ...
    def receber_decisao(self, evento_id: str) -> EventoAutenticado: ...


class SupervisorTemporalPort(Protocol):
    def consultar(self) -> Escopo: ...
    def retomar(self, comando: ComandoRetomada) -> str:
        """Revalida ticket/receipt e faz CAS do escopo + dedup na recepção."""
        ...


class RelogioPort(Protocol):
    def agora(self) -> int: ...


@dataclass(frozen=True)
class PoliticaAutorizadores:
    por_canal: tuple[tuple[str, tuple[str, ...]], ...]
    idade_maxima_evento: int = 300

    def validar(self, ator, canal):
        exigir(type(ator) is str and bool(ator), 'ator_nao_autenticado')
        exigir(canal in ('paperclip', 'discord'), 'canal_invalido')
        exigir(ator in dict(self.por_canal).get(canal, ()), 'ator_fora_allowlist')
