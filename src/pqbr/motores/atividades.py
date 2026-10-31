"""Atividades das portas de motor (t513). `motor_consultar` roda na fila do motor (notebooklm-pqbr, concorrência 1)."""
from __future__ import annotations
from temporalio import activity
from . import PedidoMotor, motor_intelectual


@activity.defn
async def motor_consultar(pedido: dict) -> dict:
    p = PedidoMotor.model_validate(pedido)
    m = motor_intelectual()
    r = await m.aconsultar(p) if hasattr(m, "aconsultar") else m.consultar(p)
    activity.logger.info("motor_consultar motor=%s tarefa=%s sessao=%s", r.motor, p.tarefa, p.sessao)
    return r.model_dump()


ATIVIDADES_MOTORES = [motor_consultar]
