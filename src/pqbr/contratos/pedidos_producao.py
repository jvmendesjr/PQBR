"""Pedidos versionados da produção E2E (pt162u): registrados em VERSOES 1.0.0.

Oficial: EpisodioWorkflow (episodio.py) e NotebookLMWorkflow.
O EpisodioWorkflow em workflows.py é legado e NÃO usa estes contratos.
"""
from __future__ import annotations
import re
from typing import Literal
from pydantic import Field
from . import Contrato

VERSAO = "1.0.0"
CODIGO = re.compile(r"^PQBR-EP[0-9]{4,}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,60}$")
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


class PedidoEpisodioE2E(Contrato):
    """Entrada do EpisodioWorkflow oficial (fila episodio-pqbr)."""
    versao: Literal["1.0.0"] = VERSAO
    slug: str = Field(pattern=SLUG.pattern)
    codigo: str = Field(pattern=CODIGO.pattern)
    roteiro_texto: str = Field(min_length=50)
    n_cenas: int = Field(ge=2, le=60)
    titulo: str | None = Field(default=None, min_length=5, max_length=100)
    descricao: str | None = Field(default=None, min_length=10, max_length=5000)
    roteirizar: bool = False
    tema: str | None = Field(default=None, max_length=300)
    tema_id: int | None = None
    tags: list[str] = Field(default_factory=list, max_length=15)
    dry_run: bool = True
    steering: str | None = Field(default=None, max_length=4000)
    espera_veredito_h: float = Field(default=24, ge=0.01, le=72)


class PedidoNotebookLM(Contrato):
    """Entrada do NotebookLMWorkflow (fila notebooklm-pqbr)."""
    versao: Literal["1.0.0"] = VERSAO
    tipo: Literal["pesquisa", "roteiro", "seo", "contexto", "short"]
    slug: str = Field(pattern=SLUG.pattern)
    fonte: str = Field(min_length=20, max_length=200_000)
    pergunta: str | None = Field(default=None, max_length=4000)
    perguntas: list[str] | None = Field(default=None, max_length=3)
    pesquisa_web: list[str] | None = Field(default=None, max_length=3)
    solicitante: str = "kit"
    episodio: str | None = Field(default=None, pattern=CODIGO.pattern)
    caderno_registrado: str | None = Field(default=None, pattern=UUID.pattern)
    pacote_fonte: str | None = None
    pacote_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    steering: str | None = Field(default=None, max_length=4000)
    roteirizar: bool = False
    tema: str | None = Field(default=None, max_length=300)
