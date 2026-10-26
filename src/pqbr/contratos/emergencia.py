"""Contratos do botão de emergência da publicação (t541, José 25/10/2026) — v1.0.0.
Comandos pelo @ottopulsar_bot, aceitos só do `from.id` do José (comparado como número, nunca texto livre):
  /pausar <motivo>                 → PAUSA GERAL: congela publicação agendada e workflows (flag global, fail-closed)
  /retomar <motivo>                → única forma de sair da pausa
  /privar PQBR-EP1234 <motivo>     → volta 1 vídeo para privado
  /privar todos <motivo>           → volta todos os publicados para privado
Nunca apaga nada. Todo comando vira linha em `pqbr.auditoria_publicacao` (motivo, autor, hora)."""
from __future__ import annotations
import re
from datetime import datetime
from typing import Literal
from pydantic import Field, model_validator
from . import Contrato

Acao = Literal["pausar", "retomar", "privar"]
CODIGO = r"^PQBR-EP[0-9]{4,}$"


class ComandoEmergencia(Contrato):
    update_id: int = Field(ge=0)
    autor_id: str = Field(pattern=r"^[0-9]{1,32}$")
    acao: Acao
    alvo: str | None = None                     # PQBR-EP… | "todos" (só privar)
    motivo: str = Field(min_length=3, max_length=300)

    @model_validator(mode="after")
    def _alvo(self):
        if self.acao == "privar":
            if not (self.alvo == "todos" or (self.alvo and re.match(CODIGO, self.alvo))):
                raise ValueError("privar exige PQBR-EP ou 'todos'")
        elif self.alvo is not None:
            raise ValueError("pausar/retomar não têm alvo")
        return self


class EstadoControle(Contrato):
    pausado: bool
    desde: datetime | None = None
    autor_id: str | None = None
    motivo: str = ""


class RegistroAuditoria(Contrato):
    acao: Literal["pausar", "retomar", "privar", "reverter", "publicar"]
    alvo: str
    video_id: str | None = None
    motivo: str
    autor_id: str
    origem: Literal["telegram", "sinal", "sistema"]
    simulado: bool
    em: datetime


def interpretar(texto: str, update_id: int, autor_id: str) -> ComandoEmergencia:
    """Texto do Telegram → comando. Determinístico; qualquer outra coisa levanta ValueError."""
    t = (texto or "").strip()
    m = re.match(r"^/(pausar|retomar|privar)(?:@\w+)?(?:\s+(.*))?$", t, re.S | re.I)
    if not m: raise ValueError("comando desconhecido")
    acao, resto = m.group(1).lower(), (m.group(2) or "").strip()
    alvo = None
    if acao == "privar":
        p = resto.split(maxsplit=1); alvo = p[0] if p else None
        alvo = "todos" if (alvo or "").lower() == "todos" else (alvo or "").upper() or None
        resto = p[1] if len(p) > 1 else ""
    return ComandoEmergencia(update_id=update_id, autor_id=str(autor_id), acao=acao, alvo=alvo,
                             motivo=resto or "sem motivo informado")


VERSOES_EMERGENCIA = {"ComandoEmergencia": "1.0.0", "EstadoControle": "1.0.0", "RegistroAuditoria": "1.0.0"}
