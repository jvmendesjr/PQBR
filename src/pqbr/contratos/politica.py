"""Política por papel (t84u–t85u): um bank Hindsight (`pqbr`) e um índice de código, com limites por papel.
Fonte única: config/politica_papeis.json. Papel desconhecido, tag ou caminho fora da lista => negado (fail-closed)."""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path
from pydantic import Field, model_validator
from . import Contrato

ARQ = Path(__file__).resolve().parents[3] / "config" / "politica_papeis.json"


class AcessoNegado(PermissionError):
    pass


class PoliticaPapel(Contrato):
    leitura: tuple[str, ...] = ()
    escrita: tuple[str, ...] = ()
    codigo: tuple[str, ...] = ()        # prefixos de caminho visíveis no índice de código ("" = repo todo)
    ferramentas: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _sem_curinga(self):
        for t in (*self.leitura, *self.escrita):
            if not t or "*" in t:
                raise ValueError("tag vazia ou curinga não é permitida")
        if any(p.startswith("/") or ".." in p for p in self.codigo):
            raise ValueError("caminho deve ser relativo ao repo, sem ..")
        return self


class PoliticaPapeis(Contrato):
    versao: str
    bank: str = Field(pattern=r"^pqbr$")
    nota: str = ""
    papeis: dict[str, PoliticaPapel]

    def de(self, papel: str | None) -> PoliticaPapel:
        if not papel or papel not in self.papeis:
            raise AcessoNegado(f"papel desconhecido: {papel!r}")
        return self.papeis[papel]

    def tags_leitura(self, papel: str) -> tuple[str, ...]:
        t = self.de(papel).leitura
        if not t:
            raise AcessoNegado(f"{papel} não lê memória")
        return t

    def exigir_escrita(self, papel: str, tags: list[str] | tuple[str, ...]) -> None:
        pode = set(self.de(papel).escrita)
        if not tags or not set(tags) <= pode:
            raise AcessoNegado(f"{papel} não escreve tags {sorted(set(tags) - pode) or tags}")

    def ve_caminho(self, papel: str, caminho: str | None) -> bool:
        if not caminho:
            return False
        c = caminho.lstrip("./")
        return any(c.startswith(p) for p in self.de(papel).codigo)

    def exigir_ferramenta(self, papel: str, nome: str) -> None:
        if nome not in self.de(papel).ferramentas:
            raise AcessoNegado(f"{papel} não usa {nome}")


@lru_cache(maxsize=1)
def carregar(arq: str | None = None) -> PoliticaPapeis:
    return PoliticaPapeis.model_validate(json.loads(Path(arq or ARQ).read_text(encoding="utf-8")))
