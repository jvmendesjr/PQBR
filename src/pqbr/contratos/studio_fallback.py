"""Base residual do fallback de publicação no Studio (t125u) — v0.1.0.

Espelha as funções que a API faz hoje: subir privado, agendar (`publishAt`) e mudar a
privacidade. É resíduo: pode estar desatualizada. Seletor de tela fica vazio até uma
observação com data. Clique ao vivo não entra neste contrato. Atualização conhecida da
API ou da tela: subir a versão, os passos e o teste no mesmo commit.
"""
from __future__ import annotations
from typing import Literal
from pydantic import Field, model_validator
from . import Contrato

VERSAO_BASE = "0.1.0"
OBSERVADA_EM = "2026-10-26"
AVISO = ("Base residual da API em 26/10/2026 (0.1.0). Pode estar desatualizada. "
         "Atualização conhecida: subir a versão do contrato, os passos e o teste.")
Funcao = Literal["subir_privado", "agendar", "tornar_publico", "tornar_privado"]
Acao = Literal["abrir", "anexar", "preencher", "marcar", "escolher", "conferir"]


class PassoBase(Contrato):
    versao: Literal["0.1.0"] = VERSAO_BASE
    funcao: Funcao
    ordem: int = Field(ge=1, le=20)
    acao: Acao
    alvo: str = Field(min_length=3, max_length=160)
    campo_api: str = Field(pattern=r"^[A-Za-z0-9_.]+$")
    seletor: str | None = Field(default=None, max_length=200)
    observado_em: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")

    @model_validator(mode="after")
    def _par(self):
        if (self.seletor is None) != (self.observado_em is None):
            raise ValueError("seletor e observado_em andam juntos")
        return self


class PassoEnsaio(Contrato):
    funcao: Funcao
    ordem: int
    acao: Acao
    alvo: str
    campo_api: str
    valor: str = Field(max_length=5000)
    clicavel: bool
    base_ok: bool
    motivo: str = Field(max_length=200)


class EnsaioCliques(Contrato):
    versao_base: Literal["0.1.0"] = VERSAO_BASE
    funcoes: tuple[Funcao, ...]
    ok: bool
    clicavel: bool
    passos: tuple[PassoEnsaio, ...]
    aviso: str = AVISO


def _p(funcao: Funcao, ordem: int, acao: Acao, alvo: str, campo: str) -> PassoBase:
    return PassoBase(funcao=funcao, ordem=ordem, acao=acao, alvo=alvo, campo_api=campo)


BASE_PASSOS: tuple[PassoBase, ...] = (
    _p("subir_privado", 1, "abrir", "tela de envio do Studio", "status.privacyStatus"),
    _p("subir_privado", 2, "anexar", "arquivo de vídeo", "_arquivo"),
    _p("subir_privado", 3, "preencher", "título", "snippet.title"),
    _p("subir_privado", 4, "preencher", "descrição com o código", "snippet.description"),
    _p("subir_privado", 5, "preencher", "etiqueta do código", "snippet.tags"),
    _p("subir_privado", 6, "marcar", "não é feito para crianças", "status.selfDeclaredMadeForKids"),
    _p("subir_privado", 7, "marcar", "conteúdo alterado ou sintético", "status.containsSyntheticMedia"),
    _p("subir_privado", 8, "escolher", "visibilidade privada", "status.privacyStatus"),
    _p("agendar", 9, "preencher", "data e hora da janela", "status.publishAt"),
    _p("tornar_publico", 1, "escolher", "visibilidade pública", "status.privacyStatus"),
    _p("tornar_privado", 1, "escolher", "visibilidade privada", "status.privacyStatus"),
)
