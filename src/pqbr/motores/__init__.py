"""Portas e adaptadores dos motores (t513, ADR-011: sistema modular).

Cada motor é peça trocável atrás de um contrato Pydantic v2 + adaptador, escolhido por config
(`config/motores.json`). Hoje: MotorIntelectual = notebooklm; GeradorVideo = flow (alternativas:
notebooklm_video, meta_vibes, google_vids). Workflows/atividades chamam a PORTA, nunca o serviço direto."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Literal, Protocol, runtime_checkable
from pydantic import BaseModel, ConfigDict, Field

RAIZ = Path(__file__).resolve().parents[3]
CONFIG = Path(os.environ.get("PQBR_MOTORES_CONFIG", str(RAIZ / "config" / "motores.json")))


class _C(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


# ---- MotorIntelectual -------------------------------------------------------------------------
class PedidoMotor(_C):
    tarefa: Literal["temas", "roteiro", "seo", "pesquisa", "direcao"]
    pergunta: str = Field(min_length=10, max_length=20000)
    contexto: str = Field(default="", max_length=200000)     # vira fonte do caderno/sessão (ex.: temas já usados)
    sessao: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,60}$")  # rótulo da sessão efêmera (no NotebookLM: título "Short - <sessao>")
    pesquisa_web: str | None = Field(default=None, max_length=1500)


class RespostaMotor(_C):
    motor: str
    sessao_id: str
    texto: str = Field(max_length=20000)
    meta: dict = Field(default_factory=dict)


@runtime_checkable
class MotorIntelectual(Protocol):
    nome: str
    def consultar(self, pedido: PedidoMotor) -> RespostaMotor: ...


# ---- GeradorVideo -----------------------------------------------------------------------------
class PedidoVideo(_C):
    codigo: str
    roteiro: str = Field(min_length=10)
    bloco_visual: dict = Field(default_factory=dict)
    destino: str
    vertical: bool = True


class ResultadoVideo(_C):
    gerador: str
    arquivo: str
    meta: dict = Field(default_factory=dict)


@runtime_checkable
class GeradorVideo(Protocol):
    nome: str
    def gerar(self, pedido: PedidoVideo) -> ResultadoVideo: ...


# ---- seleção por config ----------------------------------------------------------------------
def config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def motor_intelectual(nome: str | None = None) -> MotorIntelectual:
    nome = nome or config()["intelectual"]
    if nome == "notebooklm":
        from .notebooklm import MotorNotebookLM
        return MotorNotebookLM()
    raise KeyError(f"MotorIntelectual sem adaptador: {nome}")


GERADORES_VIDEO = ("flow", "notebooklm_video", "meta_vibes", "google_vids")


def gerador_video(nome: str | None = None) -> GeradorVideo:
    """Adaptadores de vídeo ainda vivem nos workflows de produção (Flow via camofox-pqbr); a migração para esta porta é F1-03."""
    nome = nome or config()["video"]
    if nome not in GERADORES_VIDEO:
        raise KeyError(f"GeradorVideo desconhecido: {nome}")
    raise NotImplementedError(f"GeradorVideo '{nome}': adaptador ainda não extraído para a porta (ver ROADMAP F1-03)")
