"""Worker do PQBR. Uso: python -m pqbr.workflows.worker"""
from __future__ import annotations
import asyncio, os
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker
from .workflows import EpisodioWorkflow
from .activities import gerar_roteiro, gravar_outbox

ADDR = os.environ.get("TEMPORAL_ADDRESS", "127.0.0.1:7233")
NS = os.environ.get("TEMPORAL_NAMESPACE", "pqbr")
FILA = "pqbr-episodio"


async def client() -> Client:
    return await Client.connect(ADDR, namespace=NS, data_converter=pydantic_data_converter)


async def main() -> None:
    c = await client()
    w = Worker(c, task_queue=FILA, workflows=[EpisodioWorkflow], activities=[gerar_roteiro, gravar_outbox])
    print(f"worker em {ADDR} ns={NS} fila={FILA}", flush=True)
    await w.run()


if __name__ == "__main__":
    asyncio.run(main())
