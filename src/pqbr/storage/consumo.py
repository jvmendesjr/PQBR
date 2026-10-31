"""Escrita em `pqbr.consumo_modelos` (RF-47). Usada pela activity `registrar_consumo` e pela porta `decide()` do Jev."""
from __future__ import annotations

from ..contratos import RegistroConsumo


def sql_insercao(r: RegistroConsumo) -> tuple[str, list]:
    campos = r.model_dump()
    colunas = ", ".join(campos)
    marcas = ", ".join(["%s"] * len(campos))
    return f"insert into pqbr.consumo_modelos ({colunas}) values ({marcas})", list(campos.values())


def gravar(r: RegistroConsumo) -> None:
    from .banco import conectar, escrever
    sql, params = sql_insercao(r)
    with conectar("pqbr_app") as c:
        escrever(c, sql, params)
        c.commit()
