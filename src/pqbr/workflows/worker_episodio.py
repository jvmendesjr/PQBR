"""Worker da fila episodio-pqbr (FFmpeg, capa A9, Drive, publicação dry-run). Uso: python -m pqbr.workflows.worker_episodio"""
from __future__ import annotations
import asyncio
from temporalio.worker import Worker
from .worker import client, ADDR, NS
from .episodio import FILA_EPISODIO, EpisodioWorkflow, PublicacaoWorkflow, ATIVIDADES_EPISODIO


async def main() -> None:
    import logging
    from ..seguranca.barreira import instalar_no_logging
    logging.basicConfig(level=logging.INFO); instalar_no_logging()
    w = Worker(await client(), task_queue=FILA_EPISODIO, workflows=[EpisodioWorkflow, PublicacaoWorkflow],
               activities=ATIVIDADES_EPISODIO, max_concurrent_activities=1)
    print(f"worker episodio em {ADDR} ns={NS} fila={FILA_EPISODIO} (concorrência 1)", flush=True)
    await w.run()


if __name__ == "__main__":
    asyncio.run(main())
