"""CorrecaoAutonomaWorkflow (F3-05; RF-44..RF-46; REGRAS §3.1; t355–t357).

Jev faz a triagem → agente com LLM intervém (até 3 tentativas; 5–15 min sorteados no Camofox;
confere conta/sessão antes de agir) → Jev verifica → registra (banco via Temporal) e aprende
(Hindsight, sanitizado) → propõe ajuste de script (ticket, 2 aprovações do José).
No Camofox, há também espera sorteada de 5–15 min entre intervenções (REGRAS §0, item 8),
independente do timeout da Activity; timer e sorteio pertencem ao workflow Temporal.
Resultado: corrigido | esgotado | sensivel; só os dois últimos chamam o José.

Backends reais (Jev, agente no Paperclip) ainda não estão ligados: sem `simulacao`, as Activities
falham sem repetir com `EmConstrucao` — nada é executado às cegas."""
from __future__ import annotations
from datetime import timedelta
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from temporalio import activity, workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

with workflow.unsafe.imports_passed_through():
    from ..contratos import (TriagemCorrecao, ResultadoIntervencao, VerificacaoCorrecao, ResultadoCorrecao)

MAX_TENTATIVAS = 3
CAMOFOX_MIN_S, CAMOFOX_MAX_S = 5 * 60, 15 * 60
SENSIVEIS = ("login", "2fa", "senha", "excluir", "apagar", "pagamento", "publicar_fora", "cookies")


class Simulacao(BaseModel):
    """Só para teste: roteiro do que cada backend devolveria."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    triagem: Literal["corrigivel", "sensivel", "fora_de_escopo"] = "corrigivel"
    intervencoes: list[bool] = Field(default_factory=lambda: [True], min_length=1)  # resolveu? por tentativa
    verificacoes: list[bool] = Field(default_factory=lambda: [True], min_length=1)
    conta_confere: bool = True


class PedidoCorrecao(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    ferramenta: Literal["camofox", "notebooklm", "youtube_api", "drive", "banco", "temporal", "paperclip"]
    sessao: str = "pqbr"
    passo: str = Field(min_length=3, max_length=200)
    erro: str = Field(min_length=3, max_length=2000)
    episodio: str | None = None
    simulacao: Simulacao | None = None


class Tentativa(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    pedido: PedidoCorrecao
    n: int = Field(ge=1, le=MAX_TENTATIVAS)


def _sim(p: PedidoCorrecao) -> Simulacao:
    if p.simulacao is None:
        raise ApplicationError("backend real EM CONSTRUÇÃO (Jev/agente no Paperclip)", type="EmConstrucao", non_retryable=True)
    return p.simulacao


@activity.defn
async def triagem_jev(p: PedidoCorrecao) -> TriagemCorrecao:
    if any(s in p.passo.lower() for s in SENSIVEIS):
        return TriagemCorrecao(classe="sensivel", motivo=f"passo sensível: {p.passo}")  # trava dura, antes do Jev
    s = _sim(p)
    return TriagemCorrecao(classe=s.triagem, motivo="simulado")


@activity.defn
async def intervir_agente(t: Tentativa) -> ResultadoIntervencao:
    s = _sim(t.pedido)
    ok = s.intervencoes[min(t.n - 1, len(s.intervencoes) - 1)]
    return ResultadoIntervencao(resolvido=ok, conta_confere=s.conta_confere,
                                aprendizado="seletor do botão mudou" if ok else "",
                                proposta_script="trocar seletor X por Y" if ok else None)


@activity.defn
async def verificar_jev(t: Tentativa) -> VerificacaoCorrecao:
    s = _sim(t.pedido)
    return VerificacaoCorrecao(ok=s.verificacoes[min(t.n - 1, len(s.verificacoes) - 1)])


@activity.defn
async def registrar_correcao(r: ResultadoCorrecao) -> None:
    """Registro em pqbr.acoes pelo outbox e aprendizado no Hindsight (com barreira). Stub até F3-05b."""
    from ..seguranca.barreira import exigir_limpo
    exigir_limpo(r, "banco")


_RT = RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=1))


@workflow.defn
class CorrecaoAutonomaWorkflow:
    @workflow.run
    async def run(self, p: PedidoCorrecao) -> ResultadoCorrecao:
        tri = await workflow.execute_activity(triagem_jev, p, start_to_close_timeout=timedelta(minutes=2), retry_policy=_RT)
        if tri.classe != "corrigivel":
            r = ResultadoCorrecao(resultado="sensivel", tentativas=0, motivo=f"{tri.classe}: {tri.motivo}", chamar_jose=True)
            await self._registrar(r); return r
        for n in range(1, MAX_TENTATIVAS + 1):
            # Sem espera antes da primeira nem após a última/saídas antecipadas.
            # O patch preserva comandos e sorteios dos históricos sem esse timer.
            if (p.ferramenta == "camofox" and n > 1
                    and workflow.patched("f3-05-camofox-intervalo-v1")):
                espera = workflow.random().randint(CAMOFOX_MIN_S, CAMOFOX_MAX_S)
                await workflow.sleep(timedelta(seconds=espera))
            limite = (timedelta(seconds=workflow.random().randint(CAMOFOX_MIN_S, CAMOFOX_MAX_S))
                      if p.ferramenta == "camofox" else timedelta(minutes=10))
            t = Tentativa(pedido=p, n=n)
            # uma tentativa = uma execução (a escada de 3 é deste laço; a Activity não repete sozinha)
            iv = await workflow.execute_activity(intervir_agente, t, start_to_close_timeout=limite,
                                                 retry_policy=RetryPolicy(maximum_attempts=1))
            if not iv.conta_confere:
                r = ResultadoCorrecao(resultado="sensivel", tentativas=n, motivo="conta/sessão divergente", chamar_jose=True)
                await self._registrar(r); return r
            if iv.resolvido:
                ver = await workflow.execute_activity(verificar_jev, t, start_to_close_timeout=timedelta(minutes=2), retry_policy=_RT)
                if ver.ok:
                    r = ResultadoCorrecao(resultado="corrigido", tentativas=n, proposta_script=iv.proposta_script, chamar_jose=False)
                    await self._registrar(r); return r
        r = ResultadoCorrecao(resultado="esgotado", tentativas=MAX_TENTATIVAS, motivo="3 tentativas sem sucesso", chamar_jose=True)
        await self._registrar(r); return r

    async def _registrar(self, r: ResultadoCorrecao) -> None:
        await workflow.execute_activity(registrar_correcao, r, start_to_close_timeout=timedelta(minutes=1), retry_policy=_RT)
