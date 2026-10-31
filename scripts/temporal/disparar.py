"""Dispara uma agenda Temporal agora (uso: disparar.py <schedule-id>). Usado pelo keepalive quando a sessão Google cai."""
import asyncio, sys
from pqbr.workflows.worker import client
async def m(): await (await client()).get_schedule_handle(sys.argv[1]).trigger(); print("disparado", sys.argv[1])
asyncio.run(m())
