"""Ponte durável Telegram ↔ Temporal (rascunho F05-06/F05-08, t536). Sem efeito real neste rascunho:
o envio é uma porta (`Remetente`) e o banco é uma porta (`Repositorio`); o adaptador Postgres segue a
migração 0018 e o adaptador Telegram depende do token do bot `pqbr` (decisão pendente do José).

Regras:
- Saída: enfileira → reivindica (claim com prazo) → envia → confirma. `avisado_em`/`enviado` só depois
  da confirmação. Erro claro → `falhou` (retenta). Resposta ambígua (timeout após enviar) → `incerto`:
  não reenvia às cegas; reenvio só marcado "(reenvio)" e seguro porque a decisão é deduplicada pelo token.
- Entrada: fail-closed. Sem ID autorizado configurado, remetente diferente, token desconhecido,
  expirado, decisão já registrada ou etapa errada → nenhum sinal. Uma decisão por token (único no banco).
- Sinal: `aprovacao_jose` com o token; o workflow ignora token repetido, então repetir o sinal após
  resposta ambígua é seguro. Três falhas do Temporal → ticket de manutenção (uma vez, pela chave)."""
from __future__ import annotations
import secrets
from datetime import datetime, timezone
from typing import Awaitable, Callable, Protocol
from ..contratos.ponte_telegram import (EventoCallbackTelegram, MensagemSaida, PedidoAprovacao,
                                        ReciboEntrega, ResultadoDecisao)

MAX_TENTATIVAS = 3


class EntregaIncerta(Exception):
    """O transporte pode ter entregue (timeout depois do envio)."""


class Remetente(Protocol):
    async def enviar(self, m: MensagemSaida, reenvio: bool) -> int: ...      # devolve message_id


class Repositorio(Protocol):
    def enfileirar(self, m: MensagemSaida) -> bool: ...                      # False se a chave já existe
    def reivindicar(self, chave: str) -> tuple[str, int, bool] | None: ...   # (claim, tentativa, reenvio)
    def confirmar(self, chave: str, claim: str, mensagem_id: int) -> None: ...
    def marcar(self, chave: str, claim: str, estado: str, motivo: str) -> None: ...
    def mensagem(self, chave: str) -> MensagemSaida: ...
    def recibo(self, chave: str) -> ReciboEntrega: ...
    def registrar_pedido(self, p: PedidoAprovacao) -> None: ...
    def pedido(self, token: str) -> PedidoAprovacao | None: ...
    def registrar_entrada(self, e: EventoCallbackTelegram) -> str: ...       # "novo" | "update_repetido" | "token_decidido"
    def atualizar_entrada(self, token: str, status: str, tentativas: int, motivo: str) -> None: ...
    def abrir_ticket(self, chave: str, resumo: str) -> None: ...             # idempotente pela chave


def novo_token() -> str:
    return secrets.token_urlsafe(24)


async def enviar_idempotente(repo: Repositorio, rem: Remetente, chave: str) -> ReciboEntrega:
    """Corpo da activity `enviar_telegram` (retries do Temporal desligados aqui; a escada é nossa)."""
    claim = repo.reivindicar(chave)
    if claim is None:                       # já enviado, incerto aguardando decisão, ou outro worker com o claim
        return repo.recibo(chave)
    ref, tentativa, reenvio = claim
    try:
        mid = await rem.enviar(repo.mensagem(chave), reenvio)
    except EntregaIncerta as e:
        repo.marcar(chave, ref, "incerto", _limpo(e))
    except Exception as e:  # noqa: BLE001 — erro claro: não entregou
        repo.marcar(chave, ref, "ticket" if tentativa >= MAX_TENTATIVAS else "falhou", _limpo(e))
        if tentativa >= MAX_TENTATIVAS:
            repo.abrir_ticket(f"ticket:{chave}", f"envio Telegram falhou {tentativa}x: {_limpo(e)}")
    else:
        repo.confirmar(chave, ref, mid)
    return repo.recibo(chave)


async def processar_callback(repo: Repositorio, id_autorizado: str, e: EventoCallbackTelegram,
                             sinalizar: Callable[[str, str, str], Awaitable[str]],
                             agora: datetime | None = None) -> ResultadoDecisao:
    """`sinalizar(workflow_id, token, decisao)` envia o sinal e devolve a etapa lida do workflow."""
    agora = agora or datetime.now(timezone.utc)
    def r(s, wf=None, n=0, m=""):
        return ResultadoDecisao.model_validate({"status": s, "ref_pedido": e.ref_pedido, "workflow_id": wf, "tentativas": n, "motivo": m})
    if not id_autorizado:
        return r("config_ausente")
    if e.remetente_id != id_autorizado:
        return r("remetente_recusado")
    p = repo.pedido(e.ref_pedido)
    if p is None:
        return r("pedido_desconhecido")
    if p.expira_em <= agora:
        return r("expirado", p.workflow_id)
    reg = repo.registrar_entrada(e)
    if reg != "novo":
        return r("duplicado", p.workflow_id, m=reg)
    ultimo = ""
    for n in range(1, MAX_TENTATIVAS + 1):
        try:
            etapa = await sinalizar(p.workflow_id, e.ref_pedido, e.decisao)
        except Exception as ex:  # noqa: BLE001
            ultimo = _limpo(ex)
            continue
        if etapa != p.etapa:
            repo.atualizar_entrada(e.ref_pedido, "estado_invalido", n, etapa[:60])
            return r("estado_invalido", p.workflow_id, n, etapa[:60])
        repo.atualizar_entrada(e.ref_pedido, "sinalizado", n, "")
        return r("sinalizado", p.workflow_id, n)
    repo.atualizar_entrada(e.ref_pedido, "ticket", MAX_TENTATIVAS, ultimo)
    repo.abrir_ticket(f"ticket:sinal:{e.ref_pedido}", f"sinal aprovacao_jose falhou {MAX_TENTATIVAS}x: {ultimo}")
    return r("ticket", p.workflow_id, MAX_TENTATIVAS, ultimo)


def _limpo(e: Exception) -> str:
    return type(e).__name__  # nunca o texto bruto (pode conter URL com token ou chat_id)


class RepositorioMemoria:
    """Implementação em memória com a MESMA semântica das restrições da migração 0018 (testes)."""

    def __init__(self) -> None:
        self.saida: dict[str, dict] = {}; self.pedidos: dict[str, PedidoAprovacao] = {}
        self.updates: set[int] = set(); self.entradas: dict[str, dict] = {}; self.tickets: dict[str, str] = {}

    def enfileirar(self, m):
        if m.chave in self.saida: return False
        self.saida[m.chave] = {"m": m, "estado": "pendente", "tent": 0, "claim": None, "mid": None, "motivo": ""}; return True

    def reivindicar(self, chave):
        s = self.saida[chave]
        if s["estado"] not in ("pendente", "falhou"): return None
        s["estado"], s["tent"], s["claim"] = "enviando", s["tent"] + 1, novo_token()
        return s["claim"], s["tent"], s["tent"] > 1

    def reenviar_incerto(self, chave):     # decisão explícita (humana/Observador) após `incerto`
        s = self.saida[chave]
        if s["estado"] == "incerto": s["estado"] = "falhou"

    def confirmar(self, chave, claim, mid):
        s = self.saida[chave]
        if s["claim"] == claim: s.update(estado="enviado", mid=mid, claim=None)

    def marcar(self, chave, claim, estado, motivo):
        s = self.saida[chave]
        if s["claim"] == claim: s.update(estado=estado, motivo=motivo, claim=None)

    def mensagem(self, chave): return self.saida[chave]["m"]

    def recibo(self, chave):
        s = self.saida[chave]
        return ReciboEntrega(chave=chave, estado=s["estado"], tentativas=s["tent"], mensagem_id=s["mid"], motivo=s["motivo"])

    def registrar_pedido(self, p): self.pedidos.setdefault(p.token, p)
    def pedido(self, token): return self.pedidos.get(token)

    def registrar_entrada(self, e):
        if e.update_id in self.updates: return "update_repetido"
        self.updates.add(e.update_id)
        if e.ref_pedido in self.entradas: return "token_decidido"
        self.entradas[e.ref_pedido] = {"decisao": e.decisao, "status": "recebido", "tent": 0}; return "novo"

    def atualizar_entrada(self, token, status, tentativas, motivo):
        self.entradas[token].update(status=status, tent=tentativas, motivo=motivo)

    def abrir_ticket(self, chave, resumo): self.tickets.setdefault(chave, resumo)
