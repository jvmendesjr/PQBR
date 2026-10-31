"""Consumo por modelo (F3-06, RF-47) e retenção (F3-07, RF-49; t358/t369: bruto 90 d, resumo 25 meses, 04:15).
Senhas no ambiente do worker (EnvironmentFile ~/.pqbr/worker.env, 600)."""
from __future__ import annotations
import json
from datetime import timedelta, timezone
from pydantic import BaseModel, ConfigDict, Field
from temporalio import activity, workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from ..contratos import RegistroConsumo

FUSO = timezone(timedelta(hours=-3))  # America/Fortaleza não tem horário de verão
BRUTO_DIAS, RESUMO_MESES = 90, 25


class PedidoRetencao(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    hoje: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    bruto_dias: int = Field(default=BRUTO_DIAS, ge=1)
    resumo_meses: int = Field(default=RESUMO_MESES, ge=1)


class ResultadoRetencao(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    corte_bruto: str
    corte_resumo: str
    grupos_resumidos: int
    brutas_apagadas: int
    resumo_apagado: int


@activity.defn
async def registrar_consumo(r: RegistroConsumo) -> None:
    from ..storage.consumo import gravar
    gravar(r)


@activity.defn
async def reter_consumo(p: PedidoRetencao) -> ResultadoRetencao:
    from ..storage.banco import conectar
    with conectar("pqbr_manutencao") as c, c.cursor() as cur:
        cur.execute("select pqbr.reter_consumo(%s::date, %s, %s)::text", (p.hoje, p.bruto_dias, p.resumo_meses))
        r = json.loads(cur.fetchone()[0])
        c.commit()
    return ResultadoRetencao(**{k: str(v) if k.startswith("corte") else int(v) for k, v in r.items()})


@workflow.defn
class RetencaoConsumoWorkflow:
    @workflow.run
    async def run(self, p: PedidoRetencao | None = None) -> ResultadoRetencao:
        if p is None:  # disparo do Schedule: "hoje" é o dia do disparo em Fortaleza
            hoje = workflow.now().astimezone(FUSO).date().isoformat()
            p = PedidoRetencao(hoje=hoje)
        return await workflow.execute_activity(reter_consumo, p, start_to_close_timeout=timedelta(minutes=10),
                                               retry_policy=RetryPolicy(maximum_attempts=3, initial_interval=timedelta(minutes=1)))


def secao_consumo(hoje: list[dict], semana: list[dict]) -> str:
    """Seção "Consumo" do relatório diário (por template): por modelo, por tipo de ação, falhas,
    custo estimado e variação vs. média dos 7 dias anteriores. Linhas = `pqbr.consumo_diario`."""
    def tot(ls, k): return sum((x.get(k) or 0) for x in ls)
    def agrup(ls, k):
        g: dict = {}
        for x in ls:
            a = g.setdefault(x[k], {"chamadas": 0, "falhas": 0, "tokens": 0, "custo": 0})
            a["chamadas"] += x.get("chamadas") or 0; a["falhas"] += x.get("falhas") or 0
            a["tokens"] += (x.get("tokens_entrada") or 0) + (x.get("tokens_saida") or 0)
            a["custo"] += x.get("custo_estimado_micro_usd") or 0
        return g
    media7 = tot(semana, "chamadas") / 7 if semana else 0
    var = f"{(tot(hoje, 'chamadas') / media7 - 1) * 100:+.0f}%" if media7 else "sem base"
    out = [f"Consumo: {tot(hoje, 'chamadas')} chamadas, {tot(hoje, 'falhas')} falhas, "
           f"US$ {tot(hoje, 'custo_estimado_micro_usd') / 1e6:.2f} estimados (vs. média 7 dias: {var})"]
    for titulo, k in (("Por modelo", "modelo"), ("Por tipo de ação", "tipo_acao")):
        out.append(f"{titulo}:")
        for nome, a in sorted(agrup(hoje, k).items(), key=lambda kv: -kv[1]["chamadas"]):
            out.append(f"- {nome}: {a['chamadas']} chamadas, {a['falhas']} falhas, {a['tokens']} tokens, US$ {a['custo'] / 1e6:.2f}")
    return "\n".join(out)
