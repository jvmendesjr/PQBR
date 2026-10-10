"""Escritor do banco do app (Postgres local, papel pqbr_app). Só o Temporal escreve (t341–t342).
Todo parâmetro passa pela barreira antes do INSERT/UPDATE. DSN em PQBR_DB_DSN (vem do .env 600)."""
from __future__ import annotations
import os
from typing import Any, Sequence
from ..seguranca.barreira import exigir_limpo


def conectar(dsn: str | None = None):
    import psycopg
    return psycopg.connect(dsn or os.environ["PQBR_DB_DSN"], autocommit=False)


def escrever(conn, sql: str, params: Sequence[Any] | dict = ()) -> int:
    exigir_limpo(params, "banco")
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount
