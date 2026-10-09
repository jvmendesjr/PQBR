"""Driver dos testes TZ (Fase 0.5). Uso: python scripts/tz/tz.py <comando> [...]"""
from __future__ import annotations
import asyncio, json, sys
from datetime import timedelta
from temporalio.client import (Schedule, ScheduleActionStartWorkflow, ScheduleSpec, ScheduleIntervalSpec,
                               SchedulePolicy, ScheduleOverlapPolicy)
from pqbr.workflows.worker import client, FILA
from pqbr.workflows.workflows import EpisodioWorkflow
from pqbr.workflows.contracts import EpisodioInput, AprovacaoJose


async def main(cmd: str, *a: str) -> None:
    c = await client()
    if cmd == "start":  # start <id> <timer_s> <falhas>
        inp = EpisodioInput(episodio_id=a[0], tema="teste do motor", timer_segundos=int(a[1]), falhas_simuladas=int(a[2]))
        h = await c.start_workflow(EpisodioWorkflow.run, inp, id=a[0], task_queue=FILA)
        print("iniciado", h.id, h.result_run_id)
    elif cmd == "query":
        print(json.dumps(await c.get_workflow_handle(a[0]).query(EpisodioWorkflow.estado), ensure_ascii=False))
    elif cmd == "aprovar":  # aprovar <id> <remetente>
        await c.get_workflow_handle(a[0]).signal(EpisodioWorkflow.aprovacao_jose,
                                                 AprovacaoJose(remetente_id=a[1], decisao="aprovar"))
        print("sinal enviado")
    elif cmd == "proposta":  # proposta <id> <json>
        await c.get_workflow_handle(a[0]).signal(EpisodioWorkflow.proposta_agente, json.loads(a[1]))
        print("proposta enviada")
    elif cmd == "result":
        r = await asyncio.wait_for(c.get_workflow_handle_for(EpisodioWorkflow.run, a[0]).result(), timeout=float(a[1]) if len(a) > 1 else 120)
        print(r.model_dump_json())
    elif cmd == "carga":  # carga <n>
        hs = [await c.start_workflow(EpisodioWorkflow.run,
              EpisodioInput(episodio_id=f"carga-{i:03d}", tema="carga", timer_segundos=5, falhas_simuladas=1,
                            aprovacao_automatica=True), id=f"carga-{a[1]}-{i:03d}", task_queue=FILA)
              for i in range(int(a[0]))]
        rs = await asyncio.gather(*(h.result() for h in hs))
        print("concluidos", sum(r.etapa == "concluido" for r in rs), "de", len(rs))
    elif cmd == "soak-schedule":  # cria Schedule a cada 10 min por 24 h
        await c.create_schedule("pqbr-soak-24h", Schedule(
            action=ScheduleActionStartWorkflow(EpisodioWorkflow.run,
                EpisodioInput(episodio_id="soak", tema="soak 24h", timer_segundos=60, falhas_simuladas=1,
                              aprovacao_automatica=True), id="pqbr-soak", task_queue=FILA),
            spec=ScheduleSpec(intervals=[ScheduleIntervalSpec(every=timedelta(minutes=10))]),
            policy=SchedulePolicy(overlap=ScheduleOverlapPolicy.SKIP)))
        print("schedule criado")
    else:
        sys.exit(f"comando desconhecido: {cmd}")


if __name__ == "__main__":
    asyncio.run(main(*sys.argv[1:]))
