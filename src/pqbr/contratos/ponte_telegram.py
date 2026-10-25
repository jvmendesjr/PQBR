"""Contratos da ponte durável Telegram ↔ Temporal (F05-06/F05-08, rascunho t536).

Saída: todo aviso/pedido vira uma linha na outbox `pqbr.saida_telegram` (chave idempotente).
Entrada: todo callback do Telegram é deduplicado em `pqbr.entrada_telegram` (update_id único e
uma decisão por pedido) antes de virar o sinal `aprovacao_jose` no workflow."""
from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import Field
from . import Contrato

ClasseSaida = Literal["pedido_aprovacao", "pedido_acesso", "aviso_operacional", "lembrete"]
EstadoSaida = Literal["pendente", "enviando", "enviado", "incerto", "falhou", "ticket"]
StatusDecisao = Literal["sinalizado", "duplicado", "remetente_recusado", "pedido_desconhecido",
                        "expirado", "estado_invalido", "config_ausente", "falha_temporal", "ticket"]


class MensagemSaida(Contrato):
    chave: str = Field(min_length=8, max_length=200, pattern=r"^[a-z0-9_:.\-]+$")
    classe: ClasseSaida
    texto: str = Field(min_length=1, max_length=3500)
    # pedido de aprovação: token opaco no callback_data; nunca o workflow_id em claro
    ref_pedido: str | None = Field(default=None, min_length=16, max_length=64)


class PedidoAprovacao(Contrato):
    token: str = Field(min_length=16, max_length=64)
    workflow_id: str = Field(min_length=3, max_length=128)
    etapa: str = Field(min_length=3, max_length=64)        # etapa exigida no workflow (ex.: aguardando_aprovacao)
    tarefa: str = Field(min_length=3, max_length=300)
    expira_em: datetime


class ReciboEntrega(Contrato):
    chave: str
    estado: EstadoSaida
    tentativas: int = Field(ge=0)
    mensagem_id: int | None = None                       # message_id do Telegram quando confirmado
    motivo: str = Field(default="", max_length=200)


class EventoCallbackTelegram(Contrato):
    update_id: int = Field(ge=0)
    remetente_id: str = Field(min_length=1, max_length=32, pattern=r"^[0-9]+$")   # from.id do update, nunca texto
    ref_pedido: str = Field(min_length=16, max_length=64)
    decisao: Literal["aprovar", "negar"]


class ResultadoDecisao(Contrato):
    status: StatusDecisao
    ref_pedido: str
    workflow_id: str | None = None
    tentativas: int = Field(default=0, ge=0)
    motivo: str = Field(default="", max_length=200)


VERSOES_PONTE = {"MensagemSaida": "1.0.0", "PedidoAprovacao": "1.0.0", "ReciboEntrega": "1.0.0",
                 "EventoCallbackTelegram": "1.0.0", "ResultadoDecisao": "1.0.0"}
