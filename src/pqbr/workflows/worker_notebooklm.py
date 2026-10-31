"""Worker da fila notebooklm-pqbr (concorrência 1; um pedido por vez). Uso: python -m pqbr.workflows.worker_notebooklm"""
from __future__ import annotations
import asyncio
from temporalio.worker import Worker
from .acesso import acesso_notebooklm
from .worker import client, ADDR, NS
from .notebooklm import FILA_NOTEBOOKLM, NotebookLMWorkflow, ATIVIDADES
from .pacote import ATIVIDADES_NLM_CICLO
from ..motores.atividades import ATIVIDADES_MOTORES


async def main() -> None:
    import logging
    from ..seguranca.barreira import instalar_no_logging
    logging.basicConfig(level=logging.INFO)
    instalar_no_logging()
    c = await client()
    w = Worker(c, task_queue=FILA_NOTEBOOKLM, workflows=[NotebookLMWorkflow], activities=[*ATIVIDADES, *ATIVIDADES_NLM_CICLO, *ATIVIDADES_MOTORES, acesso_notebooklm],
               max_concurrent_activities=1, max_concurrent_workflow_tasks=1)
    logging.getLogger(__name__).info(f"worker notebooklm em {ADDR} ns={NS} fila={FILA_NOTEBOOKLM} (concorrência 1)")
    await w.run()


if __name__ == "__main__":
    asyncio.run(main())
