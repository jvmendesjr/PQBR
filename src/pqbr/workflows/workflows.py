"""EpisodioWorkflow de demonstração: retries, timer durável, sinal de aprovação, outbox."""
from __future__ import annotations
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from pydantic import ValidationError
    from .contracts import (EpisodioInput, RoteiroShort, AprovacaoJose, PropostaAgente,
                            OutboxEvento, EstadoEpisodio)
    from .activities import gerar_roteiro, gravar_outbox

JOSE_ID = "jose"  # identificador lógico; o ID real do Telegram fica na config, fora do git
RETRY = RetryPolicy(initial_interval=timedelta(seconds=1), backoff_coefficient=2.0,
                    maximum_interval=timedelta(seconds=30), maximum_attempts=0)


@workflow.defn
class EpisodioWorkflow:
    def __init__(self) -> None:
        self._e: dict = {}
        self._aprovacao: AprovacaoJose | None = None

    def _set(self, **kw) -> None:
        self._e.update(kw)

    @workflow.run
    async def run(self, inp: EpisodioInput) -> EstadoEpisodio:
        self._e = dict(episodio_id=inp.episodio_id, etapa="roteiro", propostas_aceitas=0,
                       propostas_rejeitadas=0, sinais_ignorados=0, outbox_gravado=False)
        roteiro: RoteiroShort = await workflow.execute_activity(
            gerar_roteiro, inp, start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=1), maximum_attempts=10))
        self._set(roteiro=roteiro, etapa="timer")
        await workflow.sleep(timedelta(seconds=inp.timer_segundos))  # timer durável
        self._set(etapa="aguardando_aprovacao")
        if inp.aprovacao_automatica:
            self._aprovacao = AprovacaoJose(remetente_id=JOSE_ID, decisao="aprovar", motivo="soak")
        try:
            await workflow.wait_condition(lambda: self._aprovacao is not None,
                                          timeout=timedelta(seconds=inp.espera_aprovacao_segundos))
        except TimeoutError:
            self._set(etapa="expirado_sem_aprovacao")
            return EstadoEpisodio(**self._e)
        self._set(aprovacao=self._aprovacao)
        if self._aprovacao.decisao == "negar":
            self._set(etapa="negado")
            return EstadoEpisodio(**self._e)
        self._set(etapa="aguardando_outbox")
        ev = OutboxEvento(chave_idempotencia=f"{workflow.info().workflow_id}:{workflow.info().run_id}:episodio",
                          tabela="episodios", dados={"episodio_id": inp.episodio_id, "estado": "aprovado"},
                          criado_em=workflow.now())
        await workflow.execute_activity(gravar_outbox, ev, start_to_close_timeout=timedelta(seconds=15),
                                        retry_policy=RETRY)
        self._set(outbox_gravado=True, etapa="concluido")
        return EstadoEpisodio(**self._e)

    @workflow.signal
    def aprovacao_jose(self, a: AprovacaoJose) -> None:
        if a.remetente_id != JOSE_ID or self._aprovacao is not None:
            self._e["sinais_ignorados"] = self._e.get("sinais_ignorados", 0) + 1
            return
        self._aprovacao = a

    @workflow.signal
    def proposta_agente(self, bruto: dict) -> None:
        try:
            PropostaAgente.model_validate(bruto)
            self._e["propostas_aceitas"] = self._e.get("propostas_aceitas", 0) + 1
        except ValidationError:
            self._e["propostas_rejeitadas"] = self._e.get("propostas_rejeitadas", 0) + 1

    @workflow.query
    def estado(self) -> dict:
        return {k: (v.model_dump(mode="json") if hasattr(v, "model_dump") else v) for k, v in self._e.items()}
