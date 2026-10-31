"""Briefing emitido pelo Caderno Mestre para um caderno efêmero (José 31/10/2026, t168u).

O mestre NUNCA gera mídia. Ele indica persona, prompts por etapa, refs, consulta de pesquisa
do tema (executada no efêmero) e fontes/URLs. Validado fail-closed antes de abrir o efêmero."""
from __future__ import annotations
import re
from typing import Literal
from pydantic import Field, model_validator
from . import Contrato

VERSAO = "1.0.0"
CODIGO = re.compile(r"^PQBR-EP[0-9]{4,}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,60}$")
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
URL = re.compile(r"^https?://", re.I)


class BriefingEfemerico(Contrato):
    """Saída canônica do pedido de briefing ao caderno mestre."""
    versao: Literal["1.0.0"] = VERSAO
    tema: str = Field(min_length=3, max_length=300)
    codigo: str | None = Field(default=None, pattern=CODIGO.pattern)
    slug: str | None = Field(default=None, pattern=SLUG.pattern)
    n_cenas: int | None = Field(default=None, ge=2, le=60)
    caderno_mestre_id: str = Field(pattern=UUID.pattern)
    persona_efemero: str = Field(min_length=50, max_length=10000)
    prompt_pesquisa: str = Field(min_length=10, max_length=2000)
    modo_pesquisa: Literal["fast", "deep"] = "fast"
    # Pesquisa do tema é obrigatória no efêmero (José): consulta + pelo menos uma URL sugerida ou lista explícita.
    pesquisa_obrigatoria: bool = True
    urls_pesquisa: list[str] = Field(min_length=1, max_length=20)
    fontes_mestre_a_copiar: list[str] = Field(default_factory=list, max_length=30)
    refs_catalogo_sugeridas: list[str] = Field(default_factory=list, max_length=20)
    prompt_roteiro: str = Field(min_length=20, max_length=4000)
    prompt_seo: str = Field(min_length=20, max_length=2000)
    prompt_direcao_cenas: str = Field(min_length=20, max_length=4000)
    prompt_compliance: str | None = Field(default=None, max_length=2000)
    riscos_compliance: list[str] = Field(default_factory=list, max_length=15)
    modelo_sugerido: str = Field(default="notebooklm-chat", max_length=80)
    rotulo_episodio_prefix: str | None = Field(default=None, max_length=40)
    nota_salva: bool = False  # se a resposta útil foi persistida como note no mestre

    @model_validator(mode="after")
    def _pesquisa_e_urls(self):
        if self.pesquisa_obrigatoria and not (self.prompt_pesquisa and self.prompt_pesquisa.strip()):
            raise ValueError("pesquisa_obrigatoria exige prompt_pesquisa")
        if self.pesquisa_obrigatoria and len(self.urls_pesquisa) < 1:
            raise ValueError("pesquisa_obrigatoria exige ao menos 1 URL em urls_pesquisa")
        for u in self.urls_pesquisa:
            if not URL.match(u.strip()):
                raise ValueError(f"URL de pesquisa inválida: {u[:80]}")
        if self.codigo and self.rotulo_episodio_prefix and not self.rotulo_episodio_prefix.startswith(self.codigo):
            raise ValueError("rotulo_episodio_prefix deve começar com o código do episódio")
        return self


class PedidoBriefingMestre(Contrato):
    """Entrada do pedido de briefing ao mestre (activity/workflow)."""
    versao: Literal["1.0.0"] = VERSAO
    tema: str = Field(min_length=3, max_length=300)
    codigo: str | None = Field(default=None, pattern=CODIGO.pattern)
    slug: str | None = Field(default=None, pattern=SLUG.pattern)
    n_cenas: int | None = Field(default=None, ge=2, le=60)
    caderno_mestre_id: str | None = Field(default=None, pattern=UUID.pattern)
    limpar_chat_apos: bool = True
    salvar_nota: bool = True
