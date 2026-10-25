"""Ligação dos workflows à ponte Telegram (t538). Activities finas sobre o `RepositorioPostgres` + helpers
DETERMINÍSTICOS para uso dentro de workflows (ref por `workflow.uuid4()`, chave derivada do workflow/run/etapa,
versionados por `workflow.patched` para não quebrar o replay de execuções antigas).
Config `saida` desligada → nada é enfileirado nem enviado (o aviso é melhor-esforço: falha nunca derruba o workflow)."""
from __future__ import annotations
import re
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError
from ..contratos.ponte_telegram import MensagemSaida, PedidoAprovacao, ReciboEntrega

PATCH_APROVACAO = "ponte-telegram-aprovacao-t538"
PATCH_AVISOS = "ponte-telegram-avisos-t538"
OPC = dict(start_to_close_timeout=timedelta(seconds=60),
           retry_policy=RetryPolicy(initial_interval=timedelta(seconds=2), maximum_interval=timedelta(seconds=30), maximum_attempts=3))


def _saida_ligada() -> bool:
    from .entrada_telegram import carregar_config
    return carregar_config().get("saida") == "telegram_bot"


def _repo():
    from .ponte_postgres import RepositorioPostgres
    return RepositorioPostgres()


@activity.defn(name="registrar_pedido_telegram")
async def registrar_pedido_telegram(p: PedidoAprovacao) -> None:
    _repo().registrar_pedido(p)                       # on conflict do nothing: idempotente


@activity.defn(name="enfileirar_telegram")
async def enfileirar_telegram(m: MensagemSaida) -> str:
    if not _saida_ligada(): return "desligado"
    return "novo" if _repo().enfileirar(m) else "existente"


@activity.defn(name="enfileirar_avisos_telegram")
async def enfileirar_avisos_telegram() -> list[str]:
    """F05-08: pedidos de acesso e avisos de `revisao_humana` → outbox (chave por item e janela de 6 h)."""
    if not _saida_ligada(): return []
    from ..storage.banco import conectar
    from .pedidos_telegram import enfileirar
    with conectar() as c:
        return enfileirar(c)


ATIVIDADES_PONTE = [registrar_pedido_telegram, enfileirar_telegram, enfileirar_avisos_telegram]


def chave_slug(s: str) -> str:
    return re.sub(r"[^a-z0-9_:.\-]", "-", s.lower())[:200]


async def pedir_aprovacao_telegram(etapa: str, tarefa: str, texto: str, espera: timedelta) -> str | None:
    """Dentro do workflow, ANTES de esperar `aprovacao_jose`. Devolve a chave da outbox ou None."""
    if not workflow.patched(PATCH_APROVACAO):
        return None
    info = workflow.info(); ref = workflow.uuid4().hex
    chave = chave_slug(f"aprov:{info.workflow_id}:{info.run_id[:8]}:{etapa}")
    try:
        await workflow.execute_activity("registrar_pedido_telegram", PedidoAprovacao(
            token=ref, workflow_id=info.workflow_id, etapa=etapa, tarefa=tarefa[:300], expira_em=workflow.now() + espera), **OPC)
        r = await workflow.execute_activity("enfileirar_telegram", MensagemSaida(
            chave=chave, classe="pedido_aprovacao", texto=texto[:3500], ref_pedido=ref), result_type=str, **OPC)
        if r == "desligado":
            return None
        await workflow.execute_activity("enviar_telegram", chave, result_type=ReciboEntrega, **OPC)
    except ActivityError as e:
        workflow.logger.warning("ponte telegram (aprovação) falhou: %s", type(e.cause).__name__)
        return None
    return chave


async def enviar_avisos_telegram() -> list[str]:
    """Dentro do workflow: enfileira e envia avisos/pedidos operacionais pendentes (F05-08)."""
    if not workflow.patched(PATCH_AVISOS):
        return []
    try:
        chaves = await workflow.execute_activity("enfileirar_avisos_telegram", result_type=list[str], **OPC)
        for k in chaves:
            await workflow.execute_activity("enviar_telegram", k, result_type=ReciboEntrega, **OPC)
    except ActivityError as e:
        workflow.logger.warning("ponte telegram (avisos) falhou: %s", type(e.cause).__name__)
        return []
    return chaves
