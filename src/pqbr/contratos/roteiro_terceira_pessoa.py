"""Checagem determinística de narração em 3ª pessoa (ERR-ROT-02, José 25/10/2026).

Contrato editorial §11.6: um único narrador (Larissa) em 3ª pessoa ou 1ª do plural ("a gente" como
brasileiros, nunca como personagem). Personagens só REAGEM: sem fala, sem diálogo, sem sincronia labial.
Reprova: 1ª pessoa do singular na narração, diálogo/rótulo de fala, e prompts de cena em que o personagem
fala, explica, narra, apresenta ou mexe a boca para a câmera."""
from __future__ import annotations
import re
from pydantic import BaseModel, ConfigDict, model_validator

ROTEIRO_3P_VERSAO = "1.0.0"
_PRIMEIRA_SING = re.compile(r"\b(eu|meu|meus|minha|minhas|mim|comigo|me)\b", re.I)
_DIALOGO = [re.compile(p, re.M) for p in (r"^\s*[—–-]\s*\S", r"^\s*[A-ZÀ-Ú][\wÀ-ú]{1,20}\s*:\s", r"[\"“][^\"”]{3,}[\"”]\s*,?\s*(disse|falou|respondeu|perguntou|gritou)\b")]
_FALA_PERSONAGEM = re.compile(
    r"\b(talk\w*|speak\w*|says?|saying|said|explain\w*|narrat\w*|tells?|telling|lip[- ]?sync\w*|lips? mov\w*|"
    r"mouth (?:mov\w*|open\w*)|present\w* to (?:the )?camera|address\w* (?:the )?(?:camera|viewer)|"
    r"(?:looks?|looking|turns?|turning) (?:directly )?(?:at|to) the camera|to the camera)\b", re.I)


def problemas_roteiro(r: dict) -> list[str]:
    """Lista de violações (vazia = ok). r = roteiro.json do lote (falas, cta_final, cenas[].clipes[])."""
    p: list[str] = []
    textos = list(r.get("falas", [])) + [s.get("fala", "") for s in r.get("cenas", [])]
    for t in dict.fromkeys(textos):
        if m := _PRIMEIRA_SING.search(t): p.append(f"1ª pessoa do singular na narração ('{m.group(0)}'): {t[:80]}")
        for rx in _DIALOGO:
            if rx.search(t): p.append(f"diálogo/rótulo de fala na narração: {t[:80]}"); break
    for s in r.get("cenas", []):
        for c in s.get("clipes", []):
            for k in ("prompt_imagem_en", "movimento_en"):
                if m := _FALA_PERSONAGEM.search(c.get(k, "")):
                    p.append(f"{c.get('id','?')}.{k}: personagem fala/encara a câmera ('{m.group(0)}'); deve só reagir")
    return p


class RoteiroTerceiraPessoa(BaseModel):
    """Validador Pydantic: instanciar com o roteiro.json falha se houver fala de personagem."""
    model_config = ConfigDict(extra="allow")
    falas: list[str]
    cta_final: str = ""
    cenas: list[dict] = []

    @model_validator(mode="after")
    def _terceira_pessoa(self):
        p = problemas_roteiro(self.model_dump())
        if p: raise ValueError("ERR-ROT-02 narração/personagem fora da 3ª pessoa: " + " | ".join(p))
        return self
