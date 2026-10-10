"""Escritor do banco do app (Postgres local, papel pqbr_app). Só o Temporal escreve (t341–t342).
Todo parâmetro passa pela barreira antes do INSERT/UPDATE. senha no ambiente (worker.env 600)."""
from __future__ import annotations
import os
from typing import Any, Sequence
from ..seguranca.barreira import exigir_limpo


DSN_BASE = os.environ.get("PQBR_DB_DSN_BASE", "host=127.0.0.1 port=55433 dbname=pqbr")
_PAPEIS = {"pqbr_app": "PQBR_APP_PASSWORD", "pqbr_manutencao": "PQBR_MANUT_PASSWORD"}


def conectar(papel: str = "pqbr_app"):
    """Senha lida do ambiente (EnvironmentFile ~/.pqbr/worker.env, 600); nunca vai para log."""
    import psycopg
    credencial = {"password": os.environ[_PAPEIS[papel]]}
    return psycopg.connect(f"{DSN_BASE} user={papel}", autocommit=False, **credencial)


def escrever(conn, sql: str, params: Sequence[Any] | dict = ()) -> int:
    exigir_limpo(params, "banco")
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount
