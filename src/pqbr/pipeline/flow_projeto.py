"""Gate fail-closed do projeto Google Flow por episódio (t161u).

Um episódio = um projeto `PQBR-EP<nnnn>-<slug>` registrado em
`config/flow_projetos.json`. Sem fichas entregues no projeto → bloqueia
storyboard/cenas. Sem storyboard_ok → bloqueia geração de cenas/vídeo.
O projeto de testes (`projeto_testes`) nunca é usado como destino de episódio.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

RAIZ = Path(__file__).resolve().parents[3]
CFG = RAIZ / "config" / "flow_projetos.json"

_RE_TITULO = re.compile(r"^PQBR-EP(\d{4})-([a-z0-9]+(?:-[a-z0-9]+)*)$")


class ResultadoFlowProjeto(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    ok: bool
    codigo: str | None = None
    titulo: str | None = None
    project_id: str | None = None
    fichas_ok: bool = False
    storyboard_ok: bool = False
    pode_pedir_storyboard: bool = False
    pode_gerar_cenas: bool = False
    motivos: list[str] = Field(default_factory=list)


def _carregar(path: Path | None = None) -> dict[str, Any]:
    p = path or CFG
    if not p.is_file():
        raise FileNotFoundError(f"flow_projetos ausente: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def titulo_canonico(codigo_ep: str, slug: str) -> str:
    """Normaliza EP1003 / 1003 → PQBR-EP1003-<slug>."""
    digits = re.sub(r"\D", "", codigo_ep)
    if len(digits) < 4:
        digits = digits.zfill(4)
    else:
        digits = digits[-4:]
    slug_n = re.sub(r"[^a-z0-9-]", "", slug.lower().strip().replace("_", "-"))
    return f"PQBR-EP{digits}-{slug_n}"


def validar_titulo(titulo: str) -> bool:
    return bool(_RE_TITULO.match(titulo or ""))


def conferir_episodio(
    codigo_ep: str,
    *,
    exigir_fichas: bool = True,
    exigir_storyboard: bool = False,
    cfg_path: Path | None = None,
) -> ResultadoFlowProjeto:
    """Fail-closed: episódio sem projeto registrado / fichas / storyboard conforme flags."""
    motivos: list[str] = []
    data = _carregar(cfg_path)
    testes_id = (data.get("projeto_testes") or {}).get("id")
    # chave EP1003 ou 1003
    key = codigo_ep if codigo_ep.startswith("EP") else f"EP{re.sub(r'\D', '', codigo_ep)[-4:].zfill(4)}"
    projetos = data.get("projetos") or {}
    entry = projetos.get(key)
    if not entry:
        return ResultadoFlowProjeto(ok=False, codigo=key, motivos=["projeto_nao_registrado"])

    titulo = entry.get("titulo") or ""
    pid = entry.get("id")
    if not validar_titulo(titulo):
        motivos.append("titulo_invalido")
    if not pid:
        motivos.append("project_id_ausente")
    if testes_id and pid == testes_id:
        motivos.append("projeto_testes_proibido_para_episodio")

    fichas_ok = bool(entry.get("fichas_ok"))
    storyboard_ok = bool(entry.get("storyboard_ok"))
    if exigir_fichas and not fichas_ok:
        motivos.append("fichas_nao_entregues")
    if exigir_storyboard and not storyboard_ok:
        motivos.append("storyboard_ausente")

    pode_sb = fichas_ok and not motivos
    # pedir storyboard exige fichas; gerar cenas exige storyboard_ok explícito
    pode_cenas = fichas_ok and storyboard_ok and not motivos

    return ResultadoFlowProjeto(
        ok=not motivos,
        codigo=key,
        titulo=titulo,
        project_id=pid,
        fichas_ok=fichas_ok,
        storyboard_ok=storyboard_ok,
        pode_pedir_storyboard=pode_sb and not storyboard_ok,
        pode_gerar_cenas=pode_cenas,
        motivos=motivos,
    )


def exigir_episodio(codigo_ep: str, **kw) -> ResultadoFlowProjeto:
    r = conferir_episodio(codigo_ep, **kw)
    if not r.ok:
        raise RuntimeError("flow_projeto fail-closed: " + ", ".join(r.motivos))
    return r


def exigir_antes_cenas(codigo_ep: str, **kw) -> ResultadoFlowProjeto:
    """Gate cenas/vídeo: fichas + storyboard_ok obrigatórios."""
    return exigir_episodio(codigo_ep, exigir_fichas=True, exigir_storyboard=True, **kw)
