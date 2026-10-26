"""Gate determinístico de publicação (F8-01, t540). Única barreira antes da agenda: o código decide.
Passa só com: código PQBR-EP; A1–A3 técnico PASS; B1–B10 editorial PASS; LOOP do Gemini (imagem×fala, capa×título,
loop textual; inclui o VISUAL com texto) publicável; hash do arquivo vigente = hash registrado; tema não adiado."""
from __future__ import annotations
import json
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field

PUBLICAVEL = ("aprova", "aprova_com_ressalva")


class DecisaoGate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str | None
    publicavel: bool
    motivos: list[str] = Field(default_factory=list)
    ressalvas: list[str] = Field(default_factory=list)
    video: str | None = None
    sha256: str | None = None


def hash_vigente(g: dict) -> str | None:
    v = g.get("pronto_vigente") or g.get("pronto")
    if g.get("pronto_v2") and g["pronto_v2"].get("arquivo") == v: return g["pronto_v2"].get("sha256")
    return g.get("sha256") if v == g.get("pronto") else None


def avaliar(g: dict, loop: dict | None, sha_real: str | None, adiados: set[str] = frozenset()) -> DecisaoGate:
    m, r = [], []
    cod = g.get("codigo"); gate = g.get("gate", {}); sha = hash_vigente(g)
    if not cod: m.append("sem_codigo_pqbr_ep")
    if not str(gate.get("A1_A3_tecnico", "")).startswith("PASS"): m.append("A1_A3_tecnico")
    if not str(gate.get("B1_B10_editorial", "")).startswith("PASS"): m.append("B1_B10_editorial")
    if g.get("tema") in adiados or g.get("adiado"): m.append("tema_adiado")
    if not loop: m.append("loop_gemini_ausente")
    else:
        if loop.get("veredito") not in PUBLICAVEL: m.append(f"loop_gemini:{loop.get('veredito')}")
        for k in ("imagem_fala", "capa_titulo", "loop_texto"):
            if loop.get(k) == "aprova_com_ressalva": r.append(k)
    if not sha: m.append("hash_nao_registrado")
    elif sha_real != sha: m.append("hash_diverge")
    if g.get("publicado"): m.append("ja_publicado")
    return DecisaoGate(codigo=cod, publicavel=not m, motivos=m, ressalvas=r,
                       video=g.get("pronto_vigente") or g.get("pronto"), sha256=sha)


def avaliar_pasta(pasta: str, adiados: set[str] = frozenset()) -> DecisaoGate:
    from ..integrations.youtube import sha256
    p = Path(pasta); g = json.loads((p / "gate-pronto.json").read_text())
    lf = p / "loop-gemini.json"; loop = json.loads(lf.read_text()) if lf.exists() else None
    v = g.get("pronto_vigente") or g.get("pronto"); raiz = Path(__file__).resolve().parents[3]
    arq = raiz / v
    return avaliar(g, loop, sha256(str(arq)) if arq.exists() else None, adiados)
