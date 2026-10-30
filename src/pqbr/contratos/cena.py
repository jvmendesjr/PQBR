"""Cena individual (29/10/2026, ordem do José: storyboard REMOVIDO definitivamente).

Uma CenaIndividual numerada por cena, com prompt catalogado e rotulado, referência identificada,
norte, início e fim, e movimento bem definido no prompt. NÃO existe mais board: cada cena é criada,
validada e animada individualmente, uma por vez — um encarte só com muitas cenas facilitava o erro do agente.
Obrigatório antes de gerar imagem ou vídeo daquela cena. Deriva da antiga FichaCena (Storyboard 1.3.0, t150u):
`refs` aceitam os ids do catálogo visual aberto (`banco-fichas/`: PERS, FIG, ANIM, OBJ, AMB, SIT), até 6 por cena,
e o coadjuvante pode ser qualquer personagem do catálogo (o elenco varia)."""
from __future__ import annotations
import re
from typing import Literal
from pydantic import Field, model_validator
from . import Contrato
from .catalogo_visual import PROTAGONISTAS

VERSAO = "1.0.0"
ROTULO = re.compile(r"^PQBR-EP\d{4,}_c\d{2}$")          # ex.: PQBR-EP1003_c04
REF_ASSET = r"ASSET_[a-z]+_[a-z0-9-]+-v\d+"             # legado (1.0.0 a 1.2.0), ex.: ASSET_personagem_pqbr-v1
REF_CATALOGO = r"(?:PERS|FIG|ANIM|OBJ|AMB|SIT)-[a-z0-9]+(?:-[a-z0-9]+)*"   # ex.: PERS-menina-rosa, SIT-pensando
REF = re.compile(rf"^(?:{REF_ASSET}|{REF_CATALOGO})$")
COADJUVANTE = r"^(?:masculino|feminino|PERS-[a-z0-9]+(?:-[a-z0-9]+)*)$"   # gênero do elenco (legado) ou id de personagem do catálogo
PROIBIDO_FRAMING = re.compile(r"from the (chest|waist) up|do peito para cima|da cintura para cima", re.I)
FALA_NO_PROMPT = re.compile(r"[\"“”].{3,}[\"“”]|\b(speaks|says|talking|narrates|fala|diz|narra)\b", re.I)


class CenaIndividual(Contrato):
    versao: Literal["1.0.0"] = VERSAO
    numero: int = Field(ge=1, le=60)
    rotulo: str = Field(pattern=ROTULO.pattern)
    fala: str = Field(min_length=3, max_length=400)               # narração em off; nunca vai no prompt
    norte: str = Field(min_length=10, max_length=300)              # intenção da cena: o que o espectador entende
    inicio: str = Field(min_length=10, max_length=600)             # frame inicial descrito como foto parada
    fim: str = Field(min_length=10, max_length=600)                # frame final, mesma câmera e mesma luz
    movimento: str = Field(min_length=5, max_length=300)           # uma ação + um movimento de câmera
    enquadramento: Literal["plano_geral", "plano_medio", "plano_medio_curto", "close"]
    prompt_imagem: str = Field(min_length=20, max_length=2000)     # bloco de estilo completo + ação
    prompt_animacao: str = Field(min_length=10, max_length=1000)
    refs: list[str] = Field(min_length=1, max_length=6)            # ids do catálogo visual (protagonista, coadjuvante, ambiente, objeto, situação); ASSET_* só no legado
    epoca: Literal["presente", "passado"] = "presente"
    # t78u: participa ⇒ figurino da época/local. t133u: atual_variavel é o visual cotidiano travado da ficha, não roupa nova a cada vídeo.
    papel_personagem: Literal["observa", "participa"]
    figurino: Literal["epoca_local", "atual_variavel"]
    caracterizacao: str | None = Field(default=None, max_length=400)   # roupa/traços da época ou local, ou a roupa atual escolhida
    expressao: str = Field(min_length=5, max_length=300)           # caras e bocas ligadas à situação; reação, nunca articulação de fala
    cenario_encaixe: str = Field(min_length=10, max_length=400)    # onde e como o personagem está no cenário (escondido, ao fundo, no meio)
    # t79u: outro personagem pode contracenar com o protagonista quando o roteiro pedir (com justificativa).
    # t150u: pode ser qualquer personagem do catálogo (PERS-*), não só o outro gênero do elenco; o elenco varia.
    coadjuvante: str | None = Field(default=None, pattern=COADJUVANTE)
    coadjuvante_justificativa: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def _regras(self):
        if not self.rotulo.endswith(f"_c{self.numero:02d}"): raise ValueError("rótulo não bate com o número da cena")
        for r in self.refs:
            if not REF.match(r): raise ValueError(f"ref fora do catálogo: {r}")
        for campo in (self.prompt_imagem, self.prompt_animacao):
            if PROIBIDO_FRAMING.search(campo): raise ValueError("enquadramento descritivo corta cabeça/óculos; use o tipo de plano")
            if FALA_NO_PROMPT.search(campo): raise ValueError("fala ou verbo de fala no prompt faz a boca mexer; personagem nunca narra")
        if "lips closed" not in self.prompt_animacao.lower(): raise ValueError("prompt_animacao deve fixar 'lips closed'")
        if self.papel_personagem == "participa" and self.figurino != "epoca_local":
            raise ValueError("participa do ambiente ⇒ figurino da época/local")
        if self.figurino == "epoca_local" and not self.caracterizacao:
            raise ValueError("figurino de época/local exige caracterizacao")
        if self.epoca == "presente" and self.figurino == "epoca_local" and self.papel_personagem == "observa":
            raise ValueError("observador no presente usa figurino atual")
        if self.coadjuvante and not (self.coadjuvante_justificativa and len(self.coadjuvante_justificativa) >= 10):
            raise ValueError("coadjuvante do elenco exige justificativa no roteiro")
        if FALA_NO_PROMPT.search(self.expressao) or re.search(r"\b(lábios? mexendo|mouthing|lip ?sync|articula)", self.expressao, re.I):
            raise ValueError("expressão é reação (caras e bocas), nunca articulação de fala")
        return self


ELENCO = ("masculino", "feminino")


def elenco_alternado(codigo: str) -> str:
    """t78u: alterna por episódio pelo número do código (par = masculino, ímpar = feminino)."""
    return ELENCO[int(codigo.rsplit("EP", 1)[1]) % 2]


def protagonista_ref(elenco: str) -> str:
    """t150u: id do catálogo do protagonista do episódio (José: nº 1 = masculino, nº 2 = feminino)."""
    return PROTAGONISTAS[elenco]


