"""Validação fail-closed da direção de cenas (passo 1 pós-roteiro).

Regras (José 30/10/2026):
- refs existem no catálogo (`banco-fichas/`);
- personagem com trava stickman;
- persona adulta quando a ficha diz adulta;
- nada de `girl` (nem `menina` como idade) nos prompts quando PERS-menina-rosa está em refs.
"""
from __future__ import annotations
import re
from pathlib import Path
from pqbr.contratos.cena import CenaIndividual
from pqbr.contratos.catalogo_visual import FichaCatalogo, ID_PERSONAGEM
from pqbr.pipeline import banco_fichas as bf

_GIRL = re.compile(r"\bgirl\b", re.I)
_MENINA_IDADE = re.compile(r"\bmenina\b", re.I)
_ADULTA_TXT = re.compile(r"\b(adult[ao]|mulher jovem adulta|young adult woman|adult woman)\b", re.I)
_STICKMAN = re.compile(r"stickman", re.I)


def _fichas_por_id(raiz: Path | str | None = None) -> dict[str, FichaCatalogo]:
    return {f.id: f for f in bf.fichas(raiz) if f.papel == "item"}


def _ficha_diz_adulta(f: FichaCatalogo, raiz: Path | str | None = None) -> bool:
    if any(t in {"adulta", "adulto", "adult"} for t in f.tags):
        return True
    if _ADULTA_TXT.search(f.trava or ""):
        return True
    md = bf.caminho_md(f, raiz)
    if md.is_file() and _ADULTA_TXT.search(md.read_text(encoding="utf-8")):
        return True
    return False


def _sem_ids_catalogo(txt: str) -> str:
    """Tira @PERS-menina-rosa etc. para não confundir o id com a palavra menina."""
    return re.sub(r"@?(?:PERS|FIG|ANIM|OBJ|AMB|SIT)-[a-z0-9-]+", " ", txt or "")


def _textos_prompt(c: CenaIndividual) -> str:
    bruto = " ".join([c.prompt_imagem, c.prompt_animacao, c.inicio, c.fim, c.movimento, c.expressao, c.cenario_encaixe])
    return _sem_ids_catalogo(bruto)


def validar_cena(c: CenaIndividual, catalogo: dict[str, FichaCatalogo], *, raiz: Path | str | None = None) -> None:
    """Levanta ValueError se a cena violar o fail-closed."""
    for r in c.refs:
        if r.startswith("ASSET_"):
            continue  # legado formal da CenaIndividual; não exige catálogo aberto
        if r not in catalogo:
            raise ValueError(f"cena {c.numero}: ref inexistente no catálogo: {r}")
    for r in c.refs:
        if not ID_PERSONAGEM.match(r):
            continue
        f = catalogo.get(r)
        if f is None:
            raise ValueError(f"cena {c.numero}: personagem {r} fora do catálogo")
        if not _STICKMAN.search(f.trava or ""):
            raise ValueError(f"cena {c.numero}: {r} sem trava stickman")
        if not _STICKMAN.search(c.prompt_imagem):
            raise ValueError(f"cena {c.numero}: prompt_imagem sem stickman (trava do personagem)")
        if _ficha_diz_adulta(f, raiz):
            txt = _textos_prompt(c)
            if _GIRL.search(txt):
                raise ValueError(f"cena {c.numero}: proibido girl para persona adulta ({r})")
            if r == "PERS-menina-rosa" and _MENINA_IDADE.search(txt):
                raise ValueError(f"cena {c.numero}: proibido menina como idade para PERS-menina-rosa adulta; use mulher jovem adulta")
            if not _ADULTA_TXT.search(c.prompt_imagem):
                raise ValueError(f"cena {c.numero}: ficha {r} é adulta e prompt_imagem não marca persona adulta")
        if r == "PERS-menina-rosa" and _GIRL.search(_textos_prompt(c)):
            raise ValueError(f"cena {c.numero}: nada de girl para PERS-menina-rosa")


def validar_lista(cenas: list[CenaIndividual], *, raiz: Path | str | None = None) -> None:
    cat = _fichas_por_id(raiz)
    if not cat:
        raise ValueError("catálogo vazio ou ausente")
    for c in cenas:
        validar_cena(c, cat, raiz=raiz)
