"""F5-02: GradeDiariaWorkflow, EpisodioProducaoWorkflow e VigiaJanelaWorkflow (RF-01, RF-06, RF-17, RNF-10).

Nesta fase **só testes**: NotebookLM, auditor e publicação reais não estão ligados. Sem `simulacao`,
as Activities falham sem repetir (`EmConstrucao`/`PublicacaoDesligada`) — nada é publicado e a conta
de produção não é tocada. Schedules nascem PAUSADOS (scripts/temporal/schedules.py)."""
from __future__ import annotations
import asyncio
from datetime import date, datetime, timedelta, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from temporalio import activity, workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

with workflow.unsafe.imports_passed_through():
    from ..contratos import GradeDiaria, ItemGrade, VereditoAuditor, RoteiroShort, CTA, BlocoVisual, CenaVisual, PUBLICAVEL, VereditoTipo
    from ..pipeline.grade import Candidato, montar_grade

FUSO = timezone(timedelta(hours=-3))
MARGEM_PRONTO = timedelta(minutes=30)   # PROPOSTA: vídeo agendado até 30 min antes da janela
_RT = RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=2))


class SimProducao(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    candidatos: list[tuple[str, Literal["em_alta", "perene"]]] = Field(default_factory=list)
    publicados: list[str] = Field(default_factory=list)
    veredito: VereditoTipo = "aprova"
    atraso_producao_s: int = 0
    tem_reserva: bool = True


class PedidoGrade(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    dia: date | None = None
    simulacao: SimProducao | None = None


class PedidoEpisodio(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    item: ItemGrade
    codigo: str = Field(pattern=r"^PQBR-EP\d{4}$")
    simulacao: SimProducao | None = None


class ResultadoEpisodio(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    codigo: str
    estado: Literal["agendado", "reprovado", "aguardando_jose", "cancelado", "reserva_usada"]
    motivo: str = ""


def _sim(s: SimProducao | None, oque: str) -> SimProducao:
    if s is None:
        raise ApplicationError(f"{oque} real EM CONSTRUÇÃO nesta fase", type="EmConstrucao", non_retryable=True)
    return s


@activity.defn
async def coletar_candidatos(p: PedidoGrade) -> list[tuple[str, str]]:
    return list(_sim(p.simulacao, "coleta (Data API/NotebookLM)").candidatos)


@activity.defn
async def temas_usados(p: PedidoGrade) -> list[str]:
    return list(_sim(p.simulacao, "leitura de temas do banco").publicados)


@activity.defn
async def gravar_grade(g: GradeDiaria) -> int:
    """Real: grava em pqbr.grade pelo outbox (índice R10 no banco = 3ª barreira). Aqui: só valida."""
    return len(g.itens)


@activity.defn
async def gerar_roteiro_nb(p: PedidoEpisodio) -> RoteiroShort:
    _sim(p.simulacao, "NotebookLM (conta de produção)")
    falas = [f"{p.item.tema}"] + ["E a explicação é mais lógica do que parece, e a gente nem percebe no dia a dia."] * 6 + [CTA]
    bloco = BlocoVisual(estilo="Ilustração 2D plana de cartum, traço preto, cores chapadas (simulado)",
                        personagem="adulto de uns 35 anos, camiseta verde, bigode (simulado)",
                        cenas=[CenaVisual(fala=f, acao="personagem reage", enquadramento="plano médio",
                                          ambiente="cozinha brasileira") for f in falas[:2]])
    return RoteiroShort(episodio_id=p.codigo.lower(), titulo=p.item.tema[:100], falas=falas, entidades_cena=["cena"],
                        bloco_visual=bloco)


@activity.defn
async def auditar(p: PedidoEpisodio) -> VereditoAuditor:
    s = _sim(p.simulacao, "auditor")
    return VereditoAuditor(veredito=s.veredito, motivos=[] if s.veredito == "aprova" else ["simulado"], rodadas=1)


@activity.defn
async def agendar_publicacao(p: PedidoEpisodio) -> str:
    """Trava dura: nesta fase NUNCA publica. Simulação devolve um ID falso."""
    _sim(p.simulacao, "publicação")
    return "SIMULADO000"


@workflow.defn
class GradeDiariaWorkflow:
    @workflow.run
    async def run(self, p: PedidoGrade | None = None) -> GradeDiaria:
        p = p or PedidoGrade()
        dia = p.dia or workflow.now().astimezone(FUSO).date()   # grade do dia D só a partir de D
        p = PedidoGrade(dia=dia, simulacao=p.simulacao)
        cands = await workflow.execute_activity(coletar_candidatos, p, start_to_close_timeout=timedelta(minutes=30), retry_policy=_RT)
        usados = await workflow.execute_activity(temas_usados, p, start_to_close_timeout=timedelta(minutes=2), retry_policy=_RT)
        grade, _recusas = montar_grade(dia, [Candidato(t, f) for t, f in cands], usados)
        await workflow.execute_activity(gravar_grade, grade, start_to_close_timeout=timedelta(minutes=2), retry_policy=_RT)
        return grade


@workflow.defn
class EpisodioProducaoWorkflow:
    """Um episódio: roteiro → auditor → agenda na janela, com vigia de prazo (RF-17: horário sem
    reserva é cancelado; vídeo reprovado nunca é publicado; polêmica > 75 espera o José)."""
    @workflow.run
    async def run(self, p: PedidoEpisodio) -> ResultadoEpisodio:
        if p.item.status == "aguardando_jose":
            return ResultadoEpisodio(codigo=p.codigo, estado="aguardando_jose", motivo="polêmica > 75")
        h, m = map(int, p.item.janela.split(":"))
        janela = datetime(p.item.data.year, p.item.data.month, p.item.data.day, h, m, tzinfo=FUSO)
        prazo = janela - MARGEM_PRONTO
        try:
            return await asyncio.wait_for(self._produzir(p), timeout=max(0.0, (prazo - workflow.now()).total_seconds()))
        except asyncio.TimeoutError:
            s = p.simulacao
            if s and s.tem_reserva:
                return ResultadoEpisodio(codigo=p.codigo, estado="reserva_usada", motivo="prazo vencido; reserva assumiu")
            return ResultadoEpisodio(codigo=p.codigo, estado="cancelado", motivo="prazo vencido e sem reserva")

    async def _produzir(self, p: PedidoEpisodio) -> ResultadoEpisodio:
        if p.simulacao and p.simulacao.atraso_producao_s:
            await workflow.sleep(p.simulacao.atraso_producao_s)
        await workflow.execute_activity(gerar_roteiro_nb, p, start_to_close_timeout=timedelta(minutes=20), retry_policy=_RT)
        v = await workflow.execute_activity(auditar, p, start_to_close_timeout=timedelta(minutes=20), retry_policy=_RT)
        if v.veredito not in PUBLICAVEL:
            return ResultadoEpisodio(codigo=p.codigo, estado="reprovado", motivo=v.veredito)
        await workflow.execute_activity(agendar_publicacao, p, start_to_close_timeout=timedelta(minutes=20),
                                        retry_policy=RetryPolicy(maximum_attempts=1))  # não reenvia sem consultar
        return ResultadoEpisodio(codigo=p.codigo, estado="agendado")


ATIVIDADES = [coletar_candidatos, temas_usados, gravar_grade, gerar_roteiro_nb, auditar, agendar_publicacao]
