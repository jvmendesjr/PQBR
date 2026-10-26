"""Storyboard 'fábrica em série' (t75u/t76u/t77u): uma FichaCena numerada por cena, com prompt catalogado e rotulado,
referência identificada, norte, início e fim. Obrigatório antes de gerar imagem ou vídeo. Base: docs/pesquisas/flow-storyboard-por-cena.md."""
from __future__ import annotations
import re
from typing import Literal
from pydantic import Field, model_validator
from . import Contrato

VERSAO = "1.0.0"
ROTULO = re.compile(r"^PQBR-EP\d{4,}_c\d{2}$")          # ex.: PQBR-EP1003_c04
REF = re.compile(r"^ASSET_[a-z]+_[a-z0-9-]+-v\d+$")     # ex.: ASSET_personagem_pqbr-v1
PROIBIDO_FRAMING = re.compile(r"from the (chest|waist) up|do peito para cima|da cintura para cima", re.I)
FALA_NO_PROMPT = re.compile(r"[\"“”].{3,}[\"“”]|\b(speaks|says|talking|narrates|fala|diz|narra)\b", re.I)


class FichaCena(Contrato):
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
    refs: list[str] = Field(min_length=1, max_length=4)            # imagem de referência identificada
    epoca: Literal["presente", "passado"] = "presente"
    papel_personagem: Literal["protagonista", "observador_escondido", "caracterizado_epoca", "ausente"]
    caracterizacao: str | None = None                              # roupa e traços da época, se for caracterizado_epoca

    @model_validator(mode="after")
    def _regras(self):
        if not self.rotulo.endswith(f"_c{self.numero:02d}"): raise ValueError("rótulo não bate com o número da cena")
        for r in self.refs:
            if not REF.match(r): raise ValueError(f"ref fora do catálogo: {r}")
        for campo in (self.prompt_imagem, self.prompt_animacao):
            if PROIBIDO_FRAMING.search(campo): raise ValueError("enquadramento descritivo corta cabeça/óculos; use o tipo de plano")
            if FALA_NO_PROMPT.search(campo): raise ValueError("fala ou verbo de fala no prompt faz a boca mexer; personagem nunca narra")
        if "lips closed" not in self.prompt_animacao.lower(): raise ValueError("prompt_animacao deve fixar 'lips closed'")
        if self.epoca == "passado" and self.papel_personagem == "protagonista":
            raise ValueError("no passado o personagem observa escondido ou vai caracterizado da época")
        if self.papel_personagem == "caracterizado_epoca" and not self.caracterizacao:
            raise ValueError("caracterizado_epoca exige caracterizacao")
        return self


class Storyboard(Contrato):
    versao: Literal["1.0.0"] = VERSAO
    codigo: str = Field(pattern=r"^PQBR-EP\d{4,}$")
    norte_geral: str = Field(min_length=20, max_length=600)
    bloco_estilo: str = Field(min_length=20, max_length=1500)
    ficha_personagem: str = Field(min_length=20, max_length=800)
    cenas: list[FichaCena] = Field(min_length=3, max_length=60)
    imagens_revisadas: bool = False                                # True só depois da revisão das imagens, antes do vídeo

    @model_validator(mode="after")
    def _ordem(self):
        if [c.numero for c in self.cenas] != list(range(1, len(self.cenas) + 1)): raise ValueError("cenas fora de ordem")
        if any(not c.rotulo.startswith(self.codigo + "_") for c in self.cenas): raise ValueError("rótulo de outro episódio")
        return self

    def pode_gerar_video(self) -> bool:
        return self.imagens_revisadas
