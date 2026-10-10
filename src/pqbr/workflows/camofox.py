"""Fila `camofox-pqbr` (F4C-03, t375): Activities do Camofox isolado da PQBR (127.0.0.1:9387).
Concorrência 1 por sessão: o worker desta fila roda com max_concurrent_activities=1 (uma sessão `pqbr`).
Só scripts e, depois (F4C-08), a Activity de agente chamam o Camofox; ninguém fala direto com a porta."""
from __future__ import annotations
import asyncio, json, os, time, urllib.request
from datetime import timedelta
from pydantic import BaseModel
from temporalio import activity, workflow

FILA_CAMOFOX = "camofox-pqbr"
BASE = os.environ.get("PQBR_CAMOFOX_URL", "http://127.0.0.1:9387")
ENV = os.environ.get("PQBR_CAMOFOX_ENV", "/home/pc/.pqbr/camofox/.env")


def _chave() -> str:
    for linha in open(ENV, encoding="utf-8"):
        if linha.startswith("CAMOFOX_API_KEY="):
            return linha.split("=", 1)[1].strip()
    raise RuntimeError("sem chave do Camofox da PQBR")


class SaudeCamofox(BaseModel):
    ok: bool
    navegador: bool
    sessoes: int
    rss_mb: int | None = None
    autenticado: bool
    inicio: float
    fim: float


@activity.defn
async def camofox_saude(espera_s: float = 0.0) -> SaudeCamofox:
    ini = time.time()
    def _get(path: str, auth: bool):
        h = {"Authorization": "Bearer " + _chave()} if auth else {}
        with urllib.request.urlopen(urllib.request.Request(BASE + path, headers=h), timeout=15) as r:
            return r.status, json.load(r)
    _, h = await asyncio.to_thread(_get, "/health", False)
    st, _ = await asyncio.to_thread(_get, "/tabs?userId=pqbr", True)
    if espera_s:
        await asyncio.sleep(espera_s)   # usado só no teste de serialização
    return SaudeCamofox(ok=bool(h.get("ok")), navegador=bool(h.get("browserConnected")),
                        sessoes=int(h.get("activeSessions", 0)), rss_mb=(h.get("memory") or {}).get("rssMb"),
                        autenticado=(st == 200), inicio=ini, fim=time.time())


@activity.defn
async def camofox_acao_stub(acao: str) -> str:
    """Stub: as ações reais (navegar, clicar, digitar, upload) entram na F4C-05/F4C-08, sem login nem cookies."""
    return f"stub: {acao} não executada (F4C-03)"


@workflow.defn
class CamofoxSaudeWorkflow:
    @workflow.run
    async def run(self, espera_s: float = 0.0) -> SaudeCamofox:
        return await workflow.execute_activity(camofox_saude, espera_s, start_to_close_timeout=timedelta(seconds=60))
