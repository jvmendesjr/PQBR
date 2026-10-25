"""Leitura do catálogo de erros por papel (0019). Só leitura, com o papel de banco `pqbr_leitura`.
Use antes de gerar: `catalogo_erros_para_papel("auditor")` → lista de ErroCatalogo; `prevencoes_para_prompt`
devolve as instruções prontas para anexar ao prompt. A activity homônima expõe o mesmo ao Temporal."""
from __future__ import annotations
import json
from temporalio import activity
from ..contratos.catalogo_erros import ErroCatalogo, PapelInteressado

_ORDEM = "array_position(array['bloqueante','alta','media','baixa'], severidade), codigo"
SQL = ("select id, codigo, categoria, descricao, exemplo, prevencao, severidade, papeis_interessados, ativo, criado_em "
       f"from pqbr.catalogo_erros where ativo and %s = any(papeis_interessados) order by {_ORDEM}")


def _linha(r) -> ErroCatalogo:
    ex = r[4] if isinstance(r[4], dict) else json.loads(r[4] or "{}")
    return ErroCatalogo(id=r[0], codigo=r[1], categoria=r[2], descricao=r[3], exemplo=ex, prevencao=r[5],
                        severidade=r[6], papeis_interessados=list(r[7]), ativo=r[8], criado_em=r[9])


def catalogo_erros_para_papel(papel: PapelInteressado, conn=None) -> list[ErroCatalogo]:
    if conn is None:
        import os
        from ..storage.banco import conectar
        # pqbr_leitura quando a senha estiver no ambiente; senão pqbr_app em transação READ ONLY (só leitura igual).
        papel_db = "pqbr_leitura" if os.environ.get("PQBR_LEITURA_PASSWORD") else "pqbr_app"
        with conectar(papel_db) as c:
            c.execute("set transaction read only")
            return [_linha(r) for r in c.execute(SQL, (papel,)).fetchall()]
    return [_linha(r) for r in conn.execute(SQL, (papel,)).fetchall()]


def prevencoes_para_prompt(erros: list[ErroCatalogo]) -> str:
    return "\n".join(f"- [{e.codigo}/{e.severidade}] {e.prevencao}" for e in erros)


@activity.defn
async def catalogo_erros_consultar(papel: str) -> list[dict]:
    import asyncio
    return [e.model_dump(mode="json") for e in await asyncio.to_thread(catalogo_erros_para_papel, papel)]
