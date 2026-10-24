"""t510: alerta de run Temporal preso (ADR-011). Lista workflows Running há mais de PQBR_PRESO_HORAS (padrão 6)
no namespace pqbr. Sem canal Telegram do bot pqbr ainda (token ausente): registra no journal (WARNING) e sai 1.
Timer: pqbr-runs-presos.timer (de hora em hora)."""
from __future__ import annotations
import asyncio, logging, os, sys
from datetime import datetime, timezone

log = logging.getLogger("pqbr.presos")
ISENTOS: set[str] = set()   # workflows longos por desenho (não alertar); ajustar aqui


async def presos(horas: float) -> list[tuple]:
    from temporalio.client import Client
    c = await Client.connect(os.environ.get("TEMPORAL_ADDRESS", "127.0.0.1:7233"), namespace=os.environ.get("TEMPORAL_NAMESPACE", "pqbr"))
    agora, out = datetime.now(timezone.utc), []
    async for w in c.list_workflows('ExecutionStatus="Running"'):
        h = (agora - w.start_time).total_seconds() / 3600
        if h > horas and w.workflow_type not in ISENTOS:
            out.append((w.workflow_type, w.id, w.run_id, round(h, 1)))
    return out


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    horas = float(os.environ.get("PQBR_PRESO_HORAS", "6"))
    ps = asyncio.run(presos(horas))
    for t, i, r, h in ps:
        log.warning("RUN PRESO %s id=%s run=%s há %sh (> %sh)", t, i, r, h, horas)
    if not ps: log.info("nenhum run preso (> %sh)", horas)
    return 1 if ps else 0


if __name__ == "__main__":
    sys.exit(main())
