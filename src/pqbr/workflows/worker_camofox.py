"""Worker da fila camofox-pqbr (concorrência 1). Uso: python -m pqbr.workflows.worker_camofox"""
from __future__ import annotations
import asyncio
from temporalio.worker import Worker
from .worker import client, ADDR, NS
from .camofox import FILA_CAMOFOX, CamofoxSaudeWorkflow, camofox_saude, camofox_acao_stub


async def main() -> None:
    c = await client()
    w = Worker(c, task_queue=FILA_CAMOFOX, workflows=[CamofoxSaudeWorkflow],
               activities=[camofox_saude, camofox_acao_stub], max_concurrent_activities=1)
    print(f"worker camofox em {ADDR} ns={NS} fila={FILA_CAMOFOX} (concorrência 1)", flush=True)
    await w.run()


if __name__ == "__main__":
    asyncio.run(main())
