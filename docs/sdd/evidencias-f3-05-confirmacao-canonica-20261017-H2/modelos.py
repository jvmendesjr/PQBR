"""H2 OFFLINE: contratos locais. Não importar em Workers nem tratar hash como assinatura."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Protocol


class Bloqueado(ValueError):
    pass


def exigir(condicao, motivo):
    if not condicao:
        raise Bloqueado(motivo)


def json_canonico(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(obj):
    return sha256(json_canonico(obj).encode()).hexdigest()


def iso(segundos):
    exigir(type(segundos) is int, 'timestamp_invalido')
    return datetime.fromtimestamp(segundos, timezone.utc).isoformat().replace('+00:00', 'Z')


def timestamp(valor):
    exigir(type(valor) is str, 'timestamp_ausente')
    try:
        dt = datetime.fromisoformat(valor.replace('Z', '+00:00'))
        exigir(dt.utcoffset() is not None, 'timestamp_sem_timezone')
        ts = dt.timestamp()
        exigir(ts.is_integer(), 'timestamp_fracionario')
        return int(ts)
    except (ValueError, OverflowError) as exc:
        raise Bloqueado('timestamp_invalido') from exc


@dataclass(frozen=True)
class Escopo:
    supervisor_id: str
    supervisor_run_id: str
    revisao: int
    falha_id: str
    filho_run_id: str
    registro_falha_receipt: str
    pendentes: tuple[str, ...]

    def validar(self):
        exigir(type(self.revisao) is int and self.revisao > 0, 'revisao_invalida')
        exigir(type(self.pendentes) is tuple and bool(self.pendentes), 'pendentes_invalidos')
        for valor in (self.supervisor_id, self.supervisor_run_id, self.falha_id,
                      self.filho_run_id, self.registro_falha_receipt, *self.pendentes):
            exigir(type(valor) is str and 0 < len(valor) <= 200, 'id_invalido')
        exigir(len(set(self.pendentes)) == len(self.pendentes), 'pendentes_duplicados')
        exigir(self.falha_id not in self.pendentes, 'terminal_na_fila')


@dataclass(frozen=True)
class Contexto:
    """Captura da falha; prazo não é renovado em reenvios. IDs não são credenciais."""
    issue_id: str
    escopo: Escopo
    criado_em: int
    expira_em: int

    def validar(self):
        self.escopo.validar()
        exigir(type(self.issue_id) is str and bool(self.issue_id), 'issue_ausente')
        exigir(type(self.criado_em) is int and type(self.expira_em) is int
               and self.criado_em < self.expira_em, 'prazo_invalido')


@dataclass(frozen=True)
class EventoVinculado:
    """Só a porta confiável entrega isso; ator nunca vem do texto da mensagem."""
    usuario_paperclip: str
    canal: str
    issue_id: str
    interaction_id: str
    revisao: int
    escopo: Escopo
    decisao: str
    timestamp: int


@dataclass(frozen=True)
class Receipt:
    """Projeção LOCAL do registro canônico fake; não é receipt assinado da API."""
    issue_id: str
    interaction_id: str
    autor: str
    decisao: str
    timestamp: str
    revisao: int
    escopo: Escopo
    registro_hash: str
    confirmacao_key: str

    @property
    def consumo_key(self):
        # Uma autorização por interação, independente de canal/evento/ACK.
        return 'consumo:' + digest([self.issue_id, self.interaction_id])


class PaperclipPort(Protocol):
    def criar_interacao(self, issue_id: str, corpo: dict) -> dict: ...
    def listar_interacoes(self, issue_id: str) -> list[dict]: ...
    def resolver_como_humano(self, evento: EventoVinculado) -> dict:
        """Porta de sessão humana autenticada já vinculada, nunca credencial de agente."""
        ...


class VinculoExistentePort(Protocol):
    def autorizador(self) -> str:
        """Identidade Paperclip já vinculada/aprovada; não cadastra outra allowlist."""
        ...
    def evento(self, evento_id: str, canal: str) -> EventoVinculado: ...


class SupervisorPort(Protocol):
    def consultar(self) -> Escopo: ...
    def retomar(self, receipt: Receipt) -> str:
        """Releitura canônica, revalidação e consumo indivisível exigidos no receptor."""
        ...
