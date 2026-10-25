"""Adaptador de ENTRADA da ponte Telegram → Temporal (t537): o gateway Hermes (perfil pqbr) repassa o
callback; nada de bot próprio. Porta `FonteCallback` escolhida por `config/ponte_telegram.json`.

Envelope repassado (JSON, uma linha): {"update_id": int, "from_id": int|str, "chat_id": int|str, "data": str}
`data` = "pq:<a|n>:<ref_pedido>" (≤ 64 bytes, limite do Telegram). O `from_id` vem do objeto
`CallbackQuery.from_user.id` lido pelo plugin dentro do gateway — nunca de texto do usuário.
Transporte: socket Unix local (0600) — sem porta TCP, sem mudança de rede/exposição."""
from __future__ import annotations
import asyncio, json, os
from pathlib import Path
from typing import Awaitable, Callable
from pydantic import ValidationError
from ..contratos.ponte_telegram import EventoCallbackTelegram, ResultadoDecisao
from .ponte_telegram import Repositorio, processar_callback

PREFIXO = "pq:"
_DECISAO = {"a": "aprovar", "n": "negar"}
CONFIG = Path(__file__).resolve().parents[3] / "config" / "ponte_telegram.json"


class EnvelopeInvalido(ValueError):
    pass


def carregar_config(p: Path = CONFIG) -> dict:
    c = json.loads(p.read_text())
    if c.get("adaptador_entrada") not in ("hermes_plugin_unix", "desligado"):
        raise ValueError("adaptador_entrada desconhecido")
    return c


def callback_data(decisao: str, ref: str) -> str:
    d = {"aprovar": "a", "negar": "n"}[decisao]; s = f"{PREFIXO}{d}:{ref}"
    if len(s.encode()) > 64: raise ValueError("callback_data > 64 bytes")
    return s


def para_evento(env: dict) -> EventoCallbackTelegram:
    """Fail-closed: qualquer campo estranho/ausente → EnvelopeInvalido (sem eco do conteúdo)."""
    if not isinstance(env, dict) or set(env) - {"update_id", "from_id", "chat_id", "data"}:
        raise EnvelopeInvalido("campos")
    data = env.get("data")
    if not isinstance(data, str) or not data.startswith(PREFIXO):
        raise EnvelopeInvalido("prefixo")
    partes = data.split(":", 2)
    if len(partes) != 3 or partes[1] not in _DECISAO:
        raise EnvelopeInvalido("formato")
    fid = env.get("from_id")
    if isinstance(fid, bool) or not isinstance(fid, (int, str)):
        raise EnvelopeInvalido("from_id")
    try:
        return EventoCallbackTelegram(update_id=env.get("update_id"), remetente_id=str(fid),
                                      ref_pedido=partes[2], decisao=_DECISAO[partes[1]])
    except ValidationError as e:
        raise EnvelopeInvalido("contrato") from e


async def tratar_envelope(linha: bytes, repo: Repositorio, id_autorizado: str,
                          sinalizar: Callable[[str, str, str], Awaitable[str]]) -> dict:
    """Resposta curta ao plugin (texto do `answerCallbackQuery`); nunca devolve IDs nem erro bruto."""
    try:
        ev = para_evento(json.loads(linha))
    except (EnvelopeInvalido, json.JSONDecodeError, UnicodeDecodeError) as e:
        return {"ok": False, "status": "envelope_invalido", "motivo": str(e) if isinstance(e, EnvelopeInvalido) else "json"}
    r: ResultadoDecisao = await processar_callback(repo, id_autorizado, ev, sinalizar)
    return {"ok": r.status == "sinalizado", "status": r.status}


async def servir_unix(caminho: str, repo: Repositorio, id_autorizado: str, sinalizar) -> asyncio.AbstractServer:
    """Recebedor local. Não é iniciado por nenhum serviço neste rascunho."""
    async def conn(reader, writer):
        try:
            linha = await asyncio.wait_for(reader.readline(), 5)
            resp = await tratar_envelope(linha[:2048], repo, id_autorizado, sinalizar)
            writer.write((json.dumps(resp) + "\n").encode()); await writer.drain()
        finally:
            writer.close()
    old = os.umask(0o177)
    try:
        srv = await asyncio.start_unix_server(conn, path=caminho)
    finally:
        os.umask(old)
    os.chmod(caminho, 0o600)
    return srv
