"""Pré-condição fail-closed do processo canônico de criação (t160u / José t149u).

Antes de qualquer produção visual, o Temporal (e scripts manuais) conferem que
`docs/processos/CRIACAO-README.md` existe, tem a versão SemVer pinada e bate o
playbook da plataforma. Hash SHA-256 do núcleo entra no resultado para auditoria.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RAIZ = Path(__file__).resolve().parents[3]
DIR_PROCESSOS = RAIZ / "docs" / "processos"
DOC_NUCLEO = DIR_PROCESSOS / "CRIACAO-README.md"

# Pin: ao bump do doc canônico, atualizar aqui + testes + CHANGELOG (OK José se MAJOR).
VERSAO_ESPERADA = "1.0.0"

PLATAFORMAS = ("flow", "google_vids", "meta_vibes")
PLAYBOOK = {
    "flow": DIR_PROCESSOS / "flow.md",
    "google_vids": DIR_PROCESSOS / "google-vids.md",
    "meta_vibes": DIR_PROCESSOS / "meta-vibes.md",
}

# Aceita "- **versão:** 1.0.0" ou "versão: 1.0.0"
_RE_VERSAO = re.compile(r"vers[aã]o:\*{0,2}\s*(\d+\.\d+\.\d+)", re.IGNORECASE)


class ResultadoProcessoCriacao(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    ok: bool
    versao: str | None = None
    versao_esperada: str = VERSAO_ESPERADA
    sha256: str | None = None
    plataforma: str | None = None
    playbook: str | None = None
    playbook_status: str | None = None
    motivos: list[str] = Field(default_factory=list)


def extrair_versao(texto: str) -> str | None:
    m = _RE_VERSAO.search(texto)
    return m.group(1) if m else None


def status_playbook(texto: str) -> str:
    low = texto.lower()
    if "a descobrir" in low:
        return "a_descobrir"
    if "[aprovado]" in low:
        return "aprovado"
    return "desconhecido"


def sha256_arquivo(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def conferir(
    plataforma: Literal["flow", "google_vids", "meta_vibes"] = "flow",
    *,
    exigir_playbook_operavel: bool = False,
) -> ResultadoProcessoCriacao:
    """Fail-closed: doc ausente, versão divergente ou playbook inexistente → ok=False.

    `exigir_playbook_operavel=True` também recusa stubs `a descobrir` (Vids/Vibes).
    Na entrada do EpisodioWorkflow usamos False para o núcleo+existência; a geração
    visual na plataforma ativa deve passar True.
    """
    motivos: list[str] = []
    if plataforma not in PLATAFORMAS:
        return ResultadoProcessoCriacao(
            ok=False, plataforma=plataforma, motivos=["plataforma_desconhecida"]
        )

    if not DOC_NUCLEO.is_file():
        return ResultadoProcessoCriacao(
            ok=False, plataforma=plataforma, motivos=["nucleo_ausente"]
        )

    texto = DOC_NUCLEO.read_text(encoding="utf-8")
    versao = extrair_versao(texto)
    sha = sha256_arquivo(DOC_NUCLEO)
    if not versao:
        motivos.append("versao_nao_encontrada")
    elif versao != VERSAO_ESPERADA:
        motivos.append(f"versao_diverge:{versao}!={VERSAO_ESPERADA}")

    pb = PLAYBOOK[plataforma]
    pb_status = None
    if not pb.is_file():
        motivos.append("playbook_ausente")
    else:
        pb_txt = pb.read_text(encoding="utf-8")
        pb_status = status_playbook(pb_txt)
        if exigir_playbook_operavel and pb_status == "a_descobrir":
            motivos.append("playbook_a_descobrir")
        elif exigir_playbook_operavel and pb_status != "aprovado":
            motivos.append(f"playbook_nao_aprovado:{pb_status}")

    return ResultadoProcessoCriacao(
        ok=not motivos,
        versao=versao,
        sha256=sha,
        plataforma=plataforma,
        playbook=str(pb.relative_to(RAIZ)) if pb.is_file() else None,
        playbook_status=pb_status,
        motivos=motivos,
    )


def exigir(
    plataforma: Literal["flow", "google_vids", "meta_vibes"] = "flow", **kw
) -> ResultadoProcessoCriacao:
    """Como `conferir`, mas levanta RuntimeError se ok=False (para activities)."""
    r = conferir(plataforma, **kw)
    if not r.ok:
        raise RuntimeError("processo_criacao fail-closed: " + ", ".join(r.motivos))
    return r
