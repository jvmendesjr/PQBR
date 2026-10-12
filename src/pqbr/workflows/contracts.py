"""Contratos Pydantic v2 do teste de 1 dia (subconjunto de ARQUITETURA §11). RoteiroShort vem de pqbr.contratos."""
from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from ..contratos import RoteiroShort  # t437: formato antigo aposentado; único RoteiroShort


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class EpisodioInput(_Base):
    episodio_id: str = Field(pattern=r"^[a-z0-9-]{3,64}$")
    tema: str = Field(min_length=3, max_length=200)
    timer_segundos: int = Field(ge=0, le=86_400, default=30)
    falhas_simuladas: int = Field(ge=0, le=5, default=2)  # tentativas que a Activity falha antes de passar
    espera_aprovacao_segundos: int = Field(ge=1, le=86_400, default=600)
    aprovacao_automatica: bool = False  # só para o soak


class AprovacaoJose(_Base):
    remetente_id: str
    decisao: Literal["aprovar", "negar"]
    motivo: str = ""


class PropostaAgente(_Base):
    agente: str
    tipo: Literal["correcao", "melhoria", "manutencao"]
    resumo: str = Field(min_length=5, max_length=500)
    risco: Literal["baixo", "medio", "alto"]


class OutboxEvento(_Base):
    chave_idempotencia: str
    tabela: str
    dados: dict
    criado_em: datetime


class EstadoEpisodio(_Base):
    episodio_id: str
    etapa: str
    roteiro: RoteiroShort | None = None
    aprovacao: AprovacaoJose | None = None
    propostas_aceitas: int = 0
    propostas_rejeitadas: int = 0
    sinais_ignorados: int = 0
    outbox_gravado: bool = False


class PonteInput(_Base):
    """Entrada do teste da ponte Temporal ↔ Paperclip (TZ-04)."""
    company_id: str
    project_id: str
    agente_id: str
    espera_proposta_segundos: int = Field(ge=10, le=86_400, default=900)
    espera_aprovacao_segundos: int = Field(ge=10, le=86_400, default=900)
    intervalo_leitura_segundos: int = Field(ge=2, le=600, default=10)


class ResultadoPonte(_Base):
    issue_id: str
    etapa: str
    propostas_rejeitadas: int
    proposta_aplicada: PropostaAgente | None = None
