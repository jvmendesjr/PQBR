"""Bot próprio do PQBR no Telegram (t538): adaptador DETERMINÍSTICO do Temporal; nenhum agente é dono.

- Saída (`RemetenteTelegram`): usada pela activity `enviar_telegram` (outbox `saida_telegram`):
  `sendMessage` ao José, com botões `pq:<a|n>:<ref>` quando é pedido de aprovação.
- Entrada (`ciclo_entrada` / `main --entrada`): long polling `getUpdates` (sem webhook, sem porta),
  offset persistido, valida `from.id`, deduplica em `entrada_telegram`, sinaliza o workflow,
  `answerCallbackQuery` e remove os botões depois da decisão.
- Segredo: token lido SÓ do ambiente (`PQBR_TELEGRAM_BOT_TOKEN`) no momento da chamada; nunca vai para
  log, exceção, repr ou retorno. Erros expõem só método + código.
- Ligado só por `config/ponte_telegram.json` (padrão: desligado)."""
from __future__ import annotations
import asyncio, json, logging, os, socket, tempfile, urllib.error, urllib.request
from pathlib import Path
from typing import Any, Awaitable, Callable, Protocol
from ..contratos.ponte_telegram import MensagemSaida
from .entrada_telegram import EnvelopeInvalido, callback_data, carregar_config, para_evento
from .ponte_telegram import EntregaIncerta, Repositorio, processar_callback

LOG = logging.getLogger("pqbr.telegram_bot")
ENV_TOKEN, ENV_JOSE = "PQBR_TELEGRAM_BOT_TOKEN", "PQBR_TELEGRAM_JOSE_ID"
API = "https://api.telegram.org"
_RESPOSTA = {"sinalizado": "Registrado.", "duplicado": "Já registrado.", "expirado": "Pedido expirado.",
             "estado_invalido": "Pedido não está mais aguardando.", "ticket": "Falha; aberto ticket."}
_REMOVE_BOTOES = {"sinalizado", "duplicado", "expirado", "estado_invalido"}


class TelegramErro(Exception):
    def __init__(self, metodo: str, codigo: int | str):
        super().__init__(f"telegram {metodo}: {codigo}"); self.metodo, self.codigo = metodo, codigo


Transporte = Callable[[str, dict], Awaitable[dict]]


def jose_id() -> str:
    v = os.environ.get(ENV_JOSE, "").strip()
    return v if v.isdigit() else ""          # vazio → fail-closed em processar_callback


def transporte_http(timeout_s: float = 60) -> Transporte:
    """POST JSON na Bot API; o token entra só na URL local desta função e nunca sai dela."""
    def _post(metodo: str, payload: dict) -> dict:
        cred = os.environ.get(ENV_TOKEN, "")
        if not cred: raise TelegramErro(metodo, "sem_token")
        req = urllib.request.Request(f"{API}/bot{cred}/{metodo}", data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as r:
                corpo = json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise TelegramErro(metodo, e.code) from None
        except (socket.timeout, TimeoutError):
            raise EntregaIncerta(f"telegram {metodo}: timeout") from None
        except urllib.error.URLError as e:
            if isinstance(e.reason, (socket.timeout, TimeoutError)):
                raise EntregaIncerta(f"telegram {metodo}: timeout") from None
            raise TelegramErro(metodo, "rede") from None
        if not corpo.get("ok"): raise TelegramErro(metodo, corpo.get("error_code", "?"))
        return corpo["result"]
    async def chamar(metodo: str, payload: dict) -> dict:
        return await asyncio.to_thread(_post, metodo, payload)
    return chamar


def teclado(ref: str) -> dict:
    return {"inline_keyboard": [[{"text": "Aprovar", "callback_data": callback_data("aprovar", ref)},
                                 {"text": "Negar", "callback_data": callback_data("negar", ref)}]]}


class RemetenteTelegram:
    """Porta `Remetente` da ponte (saída)."""
    def __init__(self, chamar: Transporte, destino: str | None = None):
        self._chamar, self._destino = chamar, destino

    async def enviar(self, m: MensagemSaida, reenvio: bool) -> int:
        dest = self._destino or jose_id()
        if not dest: raise TelegramErro("sendMessage", "sem_destino")
        p: dict[str, Any] = {"chat_id": int(dest), "text": ("(reenvio) " if reenvio else "") + m.texto,
                             "disable_web_page_preview": True}
        if m.ref_pedido: p["reply_markup"] = teclado(m.ref_pedido)
        return int((await self._chamar("sendMessage", p))["message_id"])


class Offset(Protocol):
    def ler(self) -> int: ...
    def gravar(self, v: int) -> None: ...


class OffsetArquivo:
    """Offset persistido (atômico, 600). A dedupe real é `entrada_telegram`; o offset só evita reprocessar."""
    def __init__(self, caminho: Path): self.p = caminho
    def ler(self) -> int:
        try: return int(self.p.read_text().strip() or 0)
        except FileNotFoundError: return 0
    def gravar(self, v: int) -> None:
        self.p.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.p.parent); os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as f: f.write(str(v))
        os.replace(tmp, self.p)


async def ciclo_entrada(chamar: Transporte, offset: Offset, repo: Repositorio, id_autorizado: str,
                        sinalizar, espera_s: int = 50) -> int:
    """Uma rodada de long polling; devolve quantos updates tratou."""
    ups = await chamar("getUpdates", {"offset": offset.ler(), "timeout": espera_s, "allowed_updates": ["callback_query"]})
    for u in ups:
        q = u.get("callback_query")
        if q:
            await _tratar_callback(chamar, u["update_id"], q, repo, id_autorizado, sinalizar)
        offset.gravar(int(u["update_id"]) + 1)      # depois de tratar: reprocessar é seguro (dedupe)
    return len(ups)


async def _tratar_callback(chamar, update_id, q, repo, id_autorizado, sinalizar) -> None:
    env = {"update_id": update_id, "from_id": (q.get("from") or {}).get("id"), "data": q.get("data")}
    msg = q.get("message") or {}
    if msg.get("chat"): env["chat_id"] = msg["chat"].get("id")
    try:
        status = (await processar_callback(repo, id_autorizado, para_evento(env), sinalizar)).status
    except EnvelopeInvalido:
        status = "envelope_invalido"
    LOG.info("callback update=%s status=%s", update_id, status)       # sem from.id, sem dados
    await _seguro(chamar, "answerCallbackQuery", {"callback_query_id": q["id"], "text": _RESPOSTA.get(status, "Recusado.")})
    if status in _REMOVE_BOTOES and msg.get("chat") and msg.get("message_id"):
        await _seguro(chamar, "editMessageReplyMarkup", {"chat_id": msg["chat"]["id"], "message_id": msg["message_id"],
                                                         "reply_markup": {"inline_keyboard": []}})


async def _seguro(chamar, metodo, payload) -> None:
    try: await chamar(metodo, payload)
    except Exception as e:  # noqa: BLE001 — cosmético; a decisão já foi registrada
        LOG.warning("telegram %s falhou: %s", metodo, type(e).__name__)


def sinalizar_temporal(cliente) -> Callable[..., Awaitable[str]]:
    """Lê a etapa (query `etapa`) e só sinaliza `aprovacao_jose` se for a esperada."""
    from .contracts import AprovacaoJose
    from .workflows import JOSE_ID
    async def _s(workflow_id: str, ref: str, decisao: str, etapa_esperada: str) -> str:
        h = cliente.get_workflow_handle(workflow_id)
        etapa = await h.query("etapa")
        if etapa == etapa_esperada:
            await h.signal("aprovacao_jose", AprovacaoJose(remetente_id=JOSE_ID, decisao=decisao, motivo=f"telegram:{ref[:8]}"))
        return etapa
    return _s


async def main_entrada() -> None:  # pragma: no cover — só roda com OK do José (unit em deploy/systemd)
    cfg = carregar_config()
    if cfg.get("entrada") != "telegram_long_polling":
        raise SystemExit("entrada desligada em config/ponte_telegram.json")
    raise SystemExit("EM CONSTRUÇÃO: repositório Postgres (0018) e query `etapa` nos workflows ainda não ligados")


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main_entrada())
