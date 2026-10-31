"""Leitura do config/caderno_mestre.json (José 31/10/2026, t168u). Sem segredos."""
from __future__ import annotations
import json
from pathlib import Path

_CFG = Path(__file__).resolve().parents[2] / "config" / "caderno_mestre.json"


def _load() -> dict:
    if not _CFG.is_file():
        return {}
    return json.loads(_CFG.read_text(encoding="utf-8"))


def id_mestre() -> str | None:
    v = _load().get("caderno_mestre_id")
    return v if isinstance(v, str) and v.strip() else None


def titulo_mestre() -> str:
    return str(_load().get("titulo") or "PQBR - Mestre canônico")


def mestres_legado() -> set[str]:
    return set(_load().get("mestres_legado_proibidos") or [])


def eh_mestre_norteador(caderno: str) -> bool:
    mid = id_mestre()
    return bool(mid and caderno == mid)


def recusar_midia_se_mestre(caderno: str) -> None:
    """Trava: mestre norteador nunca gera mídia."""
    if eh_mestre_norteador(caderno):
        raise RuntimeError("caderno mestre nunca gera mídia (t168u)")


def gravar_id(caderno_id: str) -> None:
    d = _load()
    d["caderno_mestre_id"] = caderno_id
    _CFG.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
