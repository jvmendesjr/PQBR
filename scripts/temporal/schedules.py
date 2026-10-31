"""Cria/atualiza os Schedules da PQBR no Temporal (namespace pqbr). Idempotente.
- pqbr-retencao-consumo: diário 04:15 Fortaleza, ATIVO (t369 aprovou prazos e horário).
- pqbr-grade-diaria (01:00) e pqbr-lote-producao (05:00): PAUSADOS (F5-02; horários PROPOSTA; liberar = G5 do José).
Uso: PYTHONPATH=src .venv/bin/python scripts/temporal/schedules.py [--listar]"""
import asyncio, sys
from temporalio.client import (Schedule, ScheduleActionStartWorkflow, ScheduleSpec, ScheduleCalendarSpec,
                               ScheduleRange, ScheduleState, SchedulePolicy, ScheduleOverlapPolicy)
from pqbr.workflows.worker import client, FILA

FUSO = "America/Fortaleza"
AGENDA = [  # id, workflow, hora, minuto, pausado, nota
    ("pqbr-retencao-consumo", "RetencaoConsumoWorkflow", 4, 15, False, "F3-07 t369: bruto 90 d, resumo 25 meses"),
    ("pqbr-reposicao-temas", "ReposicaoTemasWorkflow", 0, 30, False, "t465 José 14:00: 7 dias de temas abertos (Líder Editorial)"),
    ("pqbr-acessos", "AcessosWorkflow", None, 10, False, "José 17:18: confere Google/NotebookLM/Paperclip de hora em hora e pede login pelo Telegram/painel"),
    ("pqbr-grade-diaria", "GradeDiariaWorkflow", 1, 0, True, "F5-02 PAUSADO: coleta real EM CONSTRUÇÃO; liberar = G5"),
    ("pqbr-lote-producao", "EpisodioProducaoWorkflow", 5, 0, True, "F5-02 PAUSADO: sem NotebookLM/publicação reais; liberar = G5"),
]


async def main() -> None:
    c = await client()
    existentes = {s.id async for s in await c.list_schedules()}
    for sid, wf, h, m, pausado, nota in AGENDA:
        if sid in existentes:
            print(f"já existe: {sid}"); continue
        await c.create_schedule(sid, Schedule(
            action=ScheduleActionStartWorkflow(wf, id=f"{sid}-wf", task_queue=FILA),
            spec=ScheduleSpec(calendars=[ScheduleCalendarSpec(hour=[ScheduleRange(0, 23) if h is None else ScheduleRange(h)], minute=[ScheduleRange(m)])], time_zone_name=FUSO),
            policy=SchedulePolicy(overlap=ScheduleOverlapPolicy.SKIP),
            state=ScheduleState(paused=pausado, note=nota)))
        print(f"criado: {sid} {'hh' if h is None else f'{h:02d}'}:{m:02d} {'PAUSADO' if pausado else 'ativo'}")
    # t517: vigia de atualizações do Dev — semanal, sexta 08:00 Fortaleza (só leitura; relatório no Postgres + log)
    if "pqbr-vigia-atualizacoes" not in existentes:
        await c.create_schedule("pqbr-vigia-atualizacoes", Schedule(
            action=ScheduleActionStartWorkflow("VigiaAtualizacoesWorkflow", id="pqbr-vigia-atualizacoes-wf", task_queue=FILA),
            spec=ScheduleSpec(calendars=[ScheduleCalendarSpec(day_of_week=[ScheduleRange(5)], hour=[ScheduleRange(8)], minute=[ScheduleRange(0)])],
                              time_zone_name=FUSO),
            policy=SchedulePolicy(overlap=ScheduleOverlapPolicy.SKIP),
            state=ScheduleState(paused=False, note="t517 José: vigia semanal de atualizações (Dev), sexta 08:00; nunca aplica")))
        print("criado: pqbr-vigia-atualizacoes sex 08:00 ativo")
    if "--listar" in sys.argv or True:
        async for s in await c.list_schedules():
            if s.id.startswith("pqbr-"):
                d = await c.get_schedule_handle(s.id).describe()
                print(s.id, "PAUSADO" if d.schedule.state.paused else "ativo", d.info.next_action_times[:1])


asyncio.run(main())
