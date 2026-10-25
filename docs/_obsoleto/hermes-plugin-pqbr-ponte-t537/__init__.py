"""Plugin Hermes (perfil pqbr) — RASCUNHO, NÃO INSTALADO (t537).
Registra um CallbackQueryHandler com pattern ^pq: (não engole os fluxos do core: ea:/sc:/cl:/mp:…),
lê from_user.id do próprio update e repassa um envelope JSON ao socket Unix da PQBR.
Sem token, sem chat_id em código; resposta ao usuário só com o status curto."""
import asyncio, json, os

SOCK = os.environ.get("PQBR_PONTE_SOCK", "/run/user/1000/pqbr/ponte-telegram.sock")
_TXT = {"sinalizado": "Registrado.", "duplicado": "Já registrado."}


async def _repassar(update, context):
    q = update.callback_query
    env = {"update_id": update.update_id, "from_id": q.from_user.id,
           "chat_id": q.message.chat_id if q.message else 0, "data": q.data}
    try:
        r, w = await asyncio.wait_for(asyncio.open_unix_connection(SOCK), 3)
        w.write((json.dumps(env) + "\n").encode()); await w.drain()
        resp = json.loads(await asyncio.wait_for(r.readline(), 10)); w.close()
        await q.answer(text=_TXT.get(resp.get("status"), "Recusado."))
    except Exception:  # fail-closed: sem resposta do PQBR = nada aprovado
        await q.answer(text="PQBR indisponível; nada foi registrado.")


def register(ctx):
    from telegram.ext import CallbackQueryHandler
    ctx.register_telegram_handler(lambda *a, **k: CallbackQueryHandler(_repassar, pattern=r"^pq:"))
