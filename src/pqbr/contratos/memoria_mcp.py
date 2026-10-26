"""Contratos da escrita de memória pelo MCP (t95u/t96u). Agente externo registra o que implementou;
o servidor valida papel, tags (política + hindsight_tags) e commit antes de chamar storage.hindsight.reter."""
from __future__ import annotations
import re
from typing import Literal
from pydantic import Field, field_validator
from . import Contrato

VERSAO = "1.0.0"
_COMMIT = r"^[0-9a-f]{7,40}$"


def _caminho_ok(p: str) -> str:
    if not p or p.startswith("/") or ".." in p.split("/") or len(p) > 200:
        raise ValueError("caminho deve ser relativo ao repo, sem ..")
    return p


class RegistroMemoriaEntrada(Contrato):
    versao: Literal["1.0.0"] = VERSAO
    conteudo: str = Field(min_length=20, max_length=4000)
    tags: tuple[str, ...] = ()                    # vazio ⇒ derivadas por hindsight_tags dentro do que o papel escreve
    arquivos: tuple[str, ...] = Field(default=(), max_length=30)
    commit: str | None = Field(default=None, pattern=_COMMIT)

    @field_validator("arquivos")
    @classmethod
    def _arquivos(cls, v):
        return tuple(_caminho_ok(p) for p in v)

    @field_validator("tags")
    @classmethod
    def _tags(cls, v):
        if any(not re.fullmatch(r"[a-z_]{2,30}", t) for t in v):
            raise ValueError("tag inválida")
        return v


class RegistroAlteracaoEntrada(RegistroMemoriaEntrada):
    commit: str = Field(pattern=_COMMIT)          # obrigatório: a alteração precisa existir no repo


class RegistroMemoriaSaida(Contrato):
    versao: Literal["1.0.0"] = VERSAO
    ok: bool
    autor: str
    papel: str
    tags: tuple[str, ...]
    commit: str | None = None
    commit_verificado: bool = False
