"""Leitura do config/caderno_mestre_auditoria.json (t170u). Sem segredos.

Espelha config_caderno_mestre.py, para o segundo mestre canônico:
o Mestre de Auditoria. Ele nunca gera mídia e nunca gera episódio.
O efêmero de auditoria é outro caderno, por episódio, e recebe uma
cópia versionada (snapshot) das regras deste mestre, nunca um link:
um caderno não pode usar outro caderno como fonte.
"""
from __future__ import annotations
import json
from pathlib import Path

_CFG = Path(__file__).resolve().parents[2] / "config" / "caderno_mestre_auditoria.json"


def _load() -> dict:
    if not _CFG.is_file():
        return {}
    return json.loads(_CFG.read_text(encoding="utf-8"))


def id_mestre_auditoria() -> str | None:
    v = _load().get("caderno_mestre_auditoria_id")
    return v if isinstance(v, str) and v.strip() else None


def titulo_mestre_auditoria() -> str:
    return str(_load().get("titulo") or "PQBR - Mestre de Auditoria")


def versao_regras() -> str:
    return str(_load().get("versao_regras") or "1.0.0")


def eh_mestre_auditoria(caderno: str) -> bool:
    mid = id_mestre_auditoria()
    return bool(mid and caderno == mid)


def recusar_midia_se_mestre_auditoria(caderno: str) -> None:
    """Trava: mestre de auditoria nunca gera mídia nem episódio."""
    if eh_mestre_auditoria(caderno):
        raise RuntimeError("mestre de auditoria nunca gera mídia nem episódio (t170u)")


def gravar_id(caderno_id: str) -> None:
    d = _load()
    d["caderno_mestre_auditoria_id"] = caderno_id
    _CFG.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
