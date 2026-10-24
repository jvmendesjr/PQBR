"""Escritor do banco do app (Postgres local, papel pqbr_app). Só o Temporal escreve (t341–t342).
Todo parâmetro passa pela barreira antes do INSERT/UPDATE. senha no ambiente (worker.env 600)."""
from __future__ import annotations
import os
from typing import Any, Sequence
from ..seguranca.barreira import exigir_limpo


DSN_BASE = os.environ.get("PQBR_DB_DSN_BASE", "host=127.0.0.1 port=55433 dbname=pqbr")
_PAPEIS = {"pqbr_app": "PQBR_APP_PASSWORD", "pqbr_manutencao": "PQBR_MANUT_PASSWORD"}


def _validar(sql, params, contexto=None):
    # psycopg.sql.Composable deve ser renderizado, não inspecionado pelo repr.
    texto = sql.as_string(contexto) if hasattr(sql, "as_string") else sql
    exigir_limpo({"sql": texto, "params": params}, "banco")


class CursorProtegido:
    """Proxy restrito aos métodos de cursor usados pela aplicação."""
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, params=None, **kwargs):
        _validar(sql, params, self._cursor)
        self._cursor.execute(sql, params, **kwargs)
        return self

    def executemany(self, sql, params_seq, **kwargs):
        params_seq = list(params_seq)
        # Valida o lote inteiro antes da primeira gravação.
        for params in params_seq:
            _validar(sql, params, self._cursor)
        self._cursor.executemany(sql, params_seq, **kwargs)
        return self

    def copy(self, *args, **kwargs):
        raise ValueError("COPY não suportado pelo escritor protegido")

    def __enter__(self):
        self._cursor.__enter__()
        return self

    def __exit__(self, *args):
        return self._cursor.__exit__(*args)

    def __iter__(self):
        return iter(self._cursor)

    def __getattr__(self, nome):
        return getattr(self._cursor, nome)


class ConexaoProtegida:
    """Cobre também os escritores existentes que usam c.execute diretamente."""
    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=None, **kwargs):
        _validar(sql, params, self._conn)
        return CursorProtegido(self._conn.execute(sql, params, **kwargs))

    def cursor(self, *args, **kwargs):
        return CursorProtegido(self._conn.cursor(*args, **kwargs))

    def __enter__(self):
        self._conn.__enter__()
        return self

    def __exit__(self, *args):
        return self._conn.__exit__(*args)

    def __getattr__(self, nome):
        return getattr(self._conn, nome)


def conectar(papel: str = "pqbr_app"):
    """Senha lida do ambiente (EnvironmentFile ~/.pqbr/worker.env, 600); nunca vai para log."""
    import psycopg
    credencial = {}
    credencial["password"] = os.environ[_PAPEIS[papel]]
    return ConexaoProtegida(psycopg.connect(f"{DSN_BASE} user={papel}", autocommit=False, **credencial))


def escrever(conn, sql: str, params: Sequence[Any] | dict = ()) -> int:
    exigir_limpo({"sql": sql, "params": params}, "banco")
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount
