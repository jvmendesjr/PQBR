"""Plano do fallback pelo Studio (t124u).

A API segue sendo o caminho. Quando o refresh volta invalid_grant, a publicação inteira
daquele envio (subida privada, agenda e privacidade) fica para o Camofox. O roteiro de
cliques no Studio ainda é hipótese: aqui só se grava o plano, com as mesmas regras da API
(private, containsSyntheticMedia, código PQBR-EP, publishAt). Não abre o navegador e não envia.
"""
from __future__ import annotations
import json


def _dir():
    from . import youtube as yt
    return yt.SIM_DIR


def planejar(arquivo: str, corpo: dict, codigo: str, motivo: str = "renovacao_oauth") -> dict:
    if corpo["status"]["privacyStatus"] != "private" or corpo["status"]["containsSyntheticMedia"] is not True:
        raise ValueError("plano do Studio fora da regra (privado + mídia sintética)")
    d = _dir(); d.mkdir(parents=True, exist_ok=True)
    plano = {**corpo, "_arquivo": arquivo, "_caminho": "camofox", "_motivo": motivo, "_executado": False}
    f = d / f"{codigo}-camofox.json"
    f.write_text(json.dumps(plano, ensure_ascii=False, indent=1))
    return {"caminho": "camofox", "simulado": True, "executado": False, "video_id": None,
            "payload": str(f), "motivo": motivo, "privacidade": "private"}


def planejar_privacidade(codigo: str, video_id: str | None, privacidade: str, motivo: str = "renovacao_oauth") -> dict:
    if privacidade not in ("public", "private"):
        raise ValueError("privacidade inválida")
    d = _dir(); d.mkdir(parents=True, exist_ok=True)
    plano = {"codigo": codigo, "video_id": video_id, "privacidade": privacidade,
             "_caminho": "camofox", "_motivo": motivo, "_executado": False}
    f = d / f"{codigo}-camofox-privacidade.json"
    f.write_text(json.dumps(plano, ensure_ascii=False, indent=1))
    return {"caminho": "camofox", "executado": False, "payload": str(f), **plano}
