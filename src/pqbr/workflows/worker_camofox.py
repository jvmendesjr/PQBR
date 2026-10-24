"""Worker da fila camofox-pqbr (concorrência 1). Uso: python -m pqbr.workflows.worker_camofox"""
from __future__ import annotations
import asyncio
from temporalio.worker import Worker
from .worker import client, ADDR, NS
from .camofox import FILA_CAMOFOX, CamofoxSaudeWorkflow, camofox_saude, camofox_acao_stub
from .acesso import acesso_google_camofox, restaurar_sessao_camofox
from .auditor_gemini import auditor_gemini


async def main() -> None:
    import logging
    from ..seguranca.barreira import instalar_no_logging
    logging.basicConfig(level=logging.INFO)
    instalar_no_logging()
    c = await client()
    w = Worker(c, task_queue=FILA_CAMOFOX, workflows=[CamofoxSaudeWorkflow],
               activities=[camofox_saude, camofox_acao_stub, acesso_google_camofox, restaurar_sessao_camofox, auditor_gemini], max_concurrent_activities=1)
    logging.getLogger(__name__).info(f"worker camofox em {ADDR} ns={NS} fila={FILA_CAMOFOX} (concorrência 1)")
    await w.run()


if __name__ == "__main__":
    asyncio.run(main())
