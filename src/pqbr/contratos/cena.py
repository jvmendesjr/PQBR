"""Cena individual (29/10/2026; rótulo unificado 31/10/2026 t168u).

Uma CenaIndividual numerada por cena, com prompt catalogado e rotulado, referência identificada,
norte, início e fim, e movimento bem definido no prompt. NÃO existe mais board: cada cena é criada,
validada e animada individualmente, uma por vez.
Rótulo canônico (José 31/10/2026): PQBR-EP####-S## — único do NotebookLM ao Flow/Drive/nome de arquivo.
Obrigatório antes de gerar imagem ou vídeo daquela cena. Deriva da antiga FichaCena (Storyboard 1.3.0, t150u):
`refs` aceitam os ids do catálogo visual aberto (`banco-fichas/`: PERS, FIG, ANIM, OBJ, AMB, SIT), até 6 por cena,
e o coadjuvante pode ser qualquer personagem do catálogo (o elenco varia)."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Literal
from pydantic import Field, model_validator
from . import Contrato
from .catalogo_visual import PROTAGONISTAS

VERSAO = "2.0.0"
ROTULO = re.compile(r"^PQBR-EP\d{4,}-S\d{2}$")          # ex.: PQBR-EP1003-S04
REF_ASSET = r"ASSET_[a-z]+_[a-z0-9-]+-v\d+"             # legado
REF_CATALOGO = r"(?:PERS|FIG|ANIM|OBJ|AMB|SIT)-[a-z0-9]+(?:-[a-z0-9]+)*"
REF = re.compile(rf"^(?:{REF_ASSET}|{REF_CATALOGO})$")
COADJUVANTE = r"^(?:masculino|feminino|PERS-[a-z0-9]+(?:-[a-z0-9]+)*)$"
PROIBIDO_FRAMING = re.compile(r"from the (chest|waist) up|do peito para cima|da cintura para cima", re.I)
FALA_NO_PROMPT = re.compile(r"[\"“”].{3,}[\"“”]|\b(speaks|says|talking|narrates|fala|diz|narra)\b", re.I)


def rotulo_cena(codigo: str, numero: int) -> str:
    """Formato canônico único (José 31/10/2026)."""
    if not re.match(r"^PQBR-EP\d{4,}$", codigo or ""):
        raise ValueError(f"código inválido: {codigo}")
    if numero < 1 or numero > 60:
        raise ValueError("numero de cena fora de 1..60")
    return f"{codigo}-S{numero:02d}"


def label_curto_flow(rotulo: str) -> str:
    """Sufixo S## para UI Flow / Collections."""
    if not ROTULO.match(rotulo or ""):
        raise ValueError(f"rótulo inválido: {rotulo}")
    return rotulo.rsplit("-", 1)[-1]


def validar_stem_rotulo(rotulo: str, caminho: str | Path) -> None:
    """Fail-closed: stem do arquivo (sem extensão) deve ser igual ao rótulo canônico."""
    if not ROTULO.match(rotulo or ""):
        raise ValueError(f"rótulo inválido: {rotulo}")
    stem = Path(caminho).stem
    if stem != rotulo:
        raise ValueError(f"stem do arquivo ({stem}) != rótulo ({rotulo})")


class CenaIndividual(Contrato):
    versao: Literal["2.0.0"] = VERSAO
    numero: int = Field(ge=1, le=60)
    rotulo: str = Field(pattern=ROTULO.pattern)
    fala: str = Field(min_length=3, max_length=400)
    norte: str = Field(min_length=10, max_length=300)
    inicio: str = Field(min_length=10, max_length=600)
    fim: str = Field(min_length=10, max_length=600)
    movimento: str = Field(min_length=5, max_length=300)
    enquadramento: Literal["plano_geral", "plano_medio", "plano_medio_curto", "close"]
    prompt_imagem: str = Field(min_length=20, max_length=2000)
    prompt_animacao: str = Field(min_length=10, max_length=1000)
    refs: list[str] = Field(min_length=1, max_length=6)
    epoca: Literal["presente", "passado"] = "presente"
    papel_personagem: Literal["observa", "participa"]
    figurino: Literal["epoca_local", "atual_variavel"]
    caracterizacao: str | None = Field(default=None, max_length=400)
    expressao: str = Field(min_length=5, max_length=300)
    cenario_encaixe: str = Field(min_length=10, max_length=400)
    coadjuvante: str | None = Field(default=None, pattern=COADJUVANTE)
    coadjuvante_justificativa: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def _regras(self):
        if not self.rotulo.endswith(f"-S{self.numero:02d}"):
            raise ValueError("rótulo não bate com o número da cena")
        # Prefixo do rótulo até antes de -S## deve ser um código PQBR-EP####
        codigo = self.rotulo[: self.rotulo.rfind("-S")]
        if not re.match(r"^PQBR-EP\d{4,}$", codigo):
            raise ValueError(f"código embutido no rótulo inválido: {codigo}")
        for r in self.refs:
            if not REF.match(r):
                raise ValueError(f"ref fora do catálogo: {r}")
        for campo in (self.prompt_imagem, self.prompt_animacao):
            if PROIBIDO_FRAMING.search(campo):
                raise ValueError("enquadramento descritivo corta cabeça/óculos; use o tipo de plano")
            if FALA_NO_PROMPT.search(campo):
                raise ValueError("fala ou verbo de fala no prompt faz a boca mexer; personagem nunca narra")
        if "lips closed" not in self.prompt_animacao.lower():
            raise ValueError("prompt_animacao deve fixar 'lips closed'")
        if self.papel_personagem == "participa" and self.figurino != "epoca_local":
            raise ValueError("participa do ambiente ⇒ figurino da época/local")
        if self.figurino == "epoca_local" and not self.caracterizacao:
            raise ValueError("figurino de época/local exige caracterizacao")
        if self.epoca == "presente" and self.figurino == "epoca_local" and self.papel_personagem == "observa":
            raise ValueError("observador no presente usa figurino atual")
        if self.coadjuvante and not (self.coadjuvante_justificativa and len(self.coadjuvante_justificativa) >= 10):
            raise ValueError("coadjuvante do elenco exige justificativa no roteiro")
        if FALA_NO_PROMPT.search(self.expressao) or re.search(
            r"\b(lábios? mexendo|mouthing|lip ?sync|articula)", self.expressao, re.I
        ):
            raise ValueError("expressão é reação (caras e bocas), nunca articulação de fala")
        return self


ELENCO = ("masculino", "feminino")


def elenco_alternado(codigo: str) -> str:
    """t78u: alterna por episódio pelo número do código (par = masculino, ímpar = feminino)."""
    return ELENCO[int(codigo.rsplit("EP", 1)[1]) % 2]


def protagonista_ref(elenco: str) -> str:
    """t150u: id do catálogo do protagonista do episódio."""
    return PROTAGONISTAS[elenco]
