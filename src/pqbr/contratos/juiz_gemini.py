"""Juiz Gemini por etapa (t108u). Lido de config/motores.json["gemini_juiz"]; etapa vem do workflow (argumento da activity)."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict

VERSAO = "1.0.0"
Etapa = Literal["pre_producao", "producao"]
Nivel = Literal["Baixo", "Médio", "Alto"]


class JuizEtapa(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    modelo: str
    raciocinio: Nivel | None = None   # None ⇒ não mexe no nível


class JuizGeminiConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    versao: Literal["1.0.0"] = VERSAO
    pre_producao: JuizEtapa
    producao: JuizEtapa

    def de(self, etapa: Etapa) -> JuizEtapa:
        return getattr(self, etapa)
