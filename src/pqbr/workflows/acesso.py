"""Acessos que só o José pode renovar (José 12/10 17:17/17:18): o fluxo confere sozinho e, se cair, PEDE pelo Telegram/painel.
Nada aqui faz login. Pedido = linha em pqbr.revisao_humana (o Hermes `pqbr` lê e avisa no Telegram) — idempotente por item_ref.
Google: a sessão vive no Camofox PQBR (9387, userId pqbr). notebooklm-py roda com NOTEBOOKLM_DISABLE_KEEPALIVE_POKE=1
(a rotação de cookies fora do Camofox derrubou a sessão em 12/10 ~16:15)."""
from __future__ import annotations
import asyncio, json, os, re, subprocess, time, urllib.request
from datetime import timedelta
from typing import Literal
from pydantic import BaseModel, ConfigDict
from temporalio import activity, workflow
from temporalio.common import RetryPolicy

FILA_CAMOFOX = "camofox-pqbr"; FILA_NLM = "notebooklm-pqbr"; FILA_REG = "episodio-pqbr"
Servico = Literal["google_camofox", "notebooklm", "paperclip_cli"]
SINAL_DESLOGADO = re.compile(r'Sign in|Fazer login|link "Entrar"|button "Entrar"')
ACAO_JOSE = {
    "google_camofox": "Login Google (juniormoedavirtual) no Camofox PQBR. Responda OK que eu abro a tela (scripts/camofox/vnc-mostrar.sh start) no pc.",
    "notebooklm": "NotebookLM sem sessão: em geral volta sozinho quando o Google do Camofox volta. Se persistir, login no Camofox PQBR.",
    "paperclip_cli": "Ponte Paperclip sem credencial: rode `node …/paperclipai/dist/index.js auth login --api-base http://<ip-tailnet>:3101` no pc.",
}


class EstadoAcesso(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    servico: Servico
    ok: bool
    motivo: str


class PedidoJose(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    servico: Servico
    motivo: str
    acao_jose: str
    caminhos_tentados: list[str] = []


def deslogado(snapshot: str) -> bool:
    """Puro; testado. Página Google mostrando 'Sign in/Fazer login' = sessão do navegador caiu."""
    return bool(SINAL_DESLOGADO.search(snapshot or ""))


@activity.defn
async def acesso_google_camofox() -> EstadoAcesso:
    from .auditor_gemini import _api, _snap
    def run():
        tab = _api("POST", "/tabs", {"userId": "pqbr", "sessionKey": "acesso", "url": "https://gemini.google.com/app"})["tabId"]
        try:
            time.sleep(6); return _snap(tab)
        finally:
            try: _api("DELETE", f"/tabs/{tab}?userId=pqbr")
            except Exception: pass
    s = await asyncio.to_thread(run)
    return EstadoAcesso(servico="google_camofox", ok=not deslogado(s), motivo="Gemini mostra 'Sign in'" if deslogado(s) else "logado")


@activity.defn
async def acesso_notebooklm() -> EstadoAcesso:
    from .notebooklm import CLI, HOME, PERFIL
    env = {**os.environ, "NOTEBOOKLM_HOME": str(HOME), "NOTEBOOKLM_DISABLE_KEEPALIVE_POKE": "1"}
    r = await asyncio.to_thread(subprocess.run, [CLI, "-p", PERFIL, "--quiet", "list", "--json"], capture_output=True, text=True, timeout=120, env=env)
    return EstadoAcesso(servico="notebooklm", ok=r.returncode == 0, motivo="ok" if r.returncode == 0 else (r.stderr or r.stdout)[-200:])


@activity.defn
async def acesso_paperclip() -> EstadoAcesso:
    from .paperclip import _cli
    try:
        await _cli("company", "list"); return EstadoAcesso(servico="paperclip_cli", ok=True, motivo="ok")
    except Exception as e:  # noqa: BLE001
        return EstadoAcesso(servico="paperclip_cli", ok=False, motivo=str(e)[-200:])


@activity.defn
async def pedir_jose(p: PedidoJose) -> int:
    """Idempotente: um pedido pendente por serviço. O Hermes `pqbr` lê revisao_humana e avisa no Telegram; o painel mostra."""
    from .pacote import _banco
    ref = f"acesso:{p.servico}"
    with _banco() as c:
        r = c.execute("select id from pqbr.revisao_humana where item_ref = %s and status = 'pendente'", (ref,)).fetchone()
        if r: return r[0]
        i = c.execute("insert into pqbr.revisao_humana (canal_id, item_tipo, item_ref, caminhos_tentados, status, observacao_jose)"
                      " values ('pqbr', 'outro', %s, %s, 'pendente', %s) returning id",
                      (ref, json.dumps({"motivo": p.motivo, "tentado": p.caminhos_tentados}, ensure_ascii=False), p.acao_jose)).fetchone()[0]
        c.commit(); return i


@activity.defn
async def acesso_resolvido(servico: str) -> int:
    from .pacote import _banco
    with _banco() as c:
        n = c.execute("update pqbr.revisao_humana set status = 'executado', determinacao = 'corrigir', decidido_em = now()"
                      " where item_ref = %s and status = 'pendente'", (f"acesso:{servico}",)).rowcount
        c.commit(); return n


@workflow.defn
class AcessosWorkflow:
    """Agenda pqbr-acessos (de hora em hora): confere Google/Camofox, NotebookLM e ponte Paperclip; pede ao José o que cair."""
    @workflow.run
    async def run(self) -> list[dict]:
        r = dict(start_to_close_timeout=timedelta(minutes=3), retry_policy=RetryPolicy(maximum_attempts=2))
        estados = [await workflow.execute_activity(acesso_google_camofox, task_queue=FILA_CAMOFOX, **r),
                   await workflow.execute_activity(acesso_notebooklm, task_queue=FILA_NLM, **r),
                   await workflow.execute_activity(acesso_paperclip, task_queue=FILA_REG, **r)]
        for e in estados:
            if e.ok:
                await workflow.execute_activity(acesso_resolvido, e.servico, task_queue=FILA_REG, **r)
            else:
                await workflow.execute_activity(pedir_jose, PedidoJose(servico=e.servico, motivo=e.motivo, acao_jose=ACAO_JOSE[e.servico],
                                                caminhos_tentados=["conferência automática"]), task_queue=FILA_REG, **r)
        return [e.model_dump() for e in estados]
