"""Portas e adaptadores dos motores (t513, ADR-011: sistema modular).

Cada motor é peça trocável atrás de um contrato Pydantic v2 + adaptador, escolhido por config
(`config/motores.json`). Hoje: MotorIntelectual = notebooklm; GeradorVideo = flow (alternativas:
notebooklm_video, meta_vibes, google_vids). Workflows/atividades chamam a PORTA, nunca o serviço direto."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Protocol, runtime_checkable
from ..contratos import PedidoMotor, RespostaMotor, PedidoVideo, ResultadoVideo  # contratos num lugar só (t515)

RAIZ = Path(__file__).resolve().parents[3]
CONFIG = Path(os.environ.get("PQBR_MOTORES_CONFIG", str(RAIZ / "config" / "motores.json")))


@runtime_checkable
class MotorIntelectual(Protocol):
    nome: str
    def consultar(self, pedido: PedidoMotor) -> RespostaMotor: ...


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
