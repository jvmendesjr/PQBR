"""Catálogo de erros de produção (migração 0019; José 25/10/2026). Versão do contrato: CATALOGO_ERROS_VERSAO.

Agentes internos só LEEM (papel de banco `pqbr_leitura`) e consultam antes de gerar; quem cadastra é o
agente externo (t538-P). Sem delete: um erro superado vira `ativo=false`."""
from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import Field
from . import Contrato

CATALOGO_ERROS_VERSAO = "1.0.0"
CategoriaErro = Literal["estilo", "personagem", "roteiro", "montagem", "texto_na_imagem", "compliance", "custo"]
Severidade = Literal["baixa", "media", "alta", "bloqueante"]
PapelInteressado = Literal["diretor", "lider-editorial", "pesquisador-origem", "auditor", "lider-compliance",
                           "guardiao-seguranca", "observador", "dev"]


class ExemploErro(Contrato):
    tema: str | None = Field(default=None, max_length=300)
    caminho: str | None = Field(default=None, max_length=300)


class ErroCatalogo(Contrato):
    versao: Literal["1.0.0"] = CATALOGO_ERROS_VERSAO
    id: int | None = None
    codigo: str = Field(pattern=r"^ERR-[A-Z]{3}-[0-9]{2}$")
    categoria: CategoriaErro
    descricao: str = Field(min_length=10, max_length=1000)
    exemplo: ExemploErro = Field(default_factory=ExemploErro)
    prevencao: str = Field(min_length=10, max_length=2000)
    severidade: Severidade
    papeis_interessados: list[PapelInteressado] = Field(min_length=1)
    ativo: bool = True
    criado_em: datetime | None = None
