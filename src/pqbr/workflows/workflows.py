"""LEGADO (demo soak F05) — NÃO é o caminho oficial de produção.

Oficial: `src/pqbr/workflows/episodio.py` → EpisodioWorkflow na fila `episodio-pqbr`.
Este módulo permanece registrado no worker da fila `pqbr-episodio` só para testes/soak históricos.
Não remover o registro do worker sem OK do José. pt162u."""
from __future__ import annotations
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from pydantic import ValidationError
    from .contracts import (EpisodioInput, RoteiroShort, AprovacaoJose, PropostaAgente,
                            OutboxEvento, EstadoEpisodio)
    from .activities import gerar_roteiro, gravar_outbox
    from .ponte_atividades import pedir_aprovacao_telegram

JOSE_ID = "jose"  # identificador lógico; o ID real do Telegram fica na config, fora do git
RETRY = RetryPolicy(initial_interval=timedelta(seconds=1), backoff_coefficient=2.0,
                    maximum_interval=timedelta(seconds=30), maximum_attempts=0)


@workflow.defn
class EpisodioWorkflow:  # LEGADO — oficial em episodio.py
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
        else:
            await pedir_aprovacao_telegram("aguardando_aprovacao", f"episódio {inp.episodio_id}",
                                           f"PQBR — aprovar o roteiro do episódio {inp.episodio_id} ({inp.tema[:120]})?",
                                           timedelta(seconds=inp.espera_aprovacao_segundos))
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
    def etapa(self) -> str:
        """Usada pela ponte Telegram (t538) antes de sinalizar `aprovacao_jose`."""
        return self._e.get("etapa", "")

    @workflow.query
    def estado(self) -> dict:
        return {k: (v.model_dump(mode="json") if hasattr(v, "model_dump") else v) for k, v in self._e.items()}


with workflow.unsafe.imports_passed_through():
    from .contracts import PonteInput, ResultadoPonte
    from .paperclip import (PedidoIssue, Comentario, LeituraPropostas, abrir_issue_paperclip,
                            comentar_paperclip, ler_propostas_paperclip, concluir_issue_paperclip)
    from .activities import aplicar_proposta_stub

_PC = dict(start_to_close_timeout=timedelta(seconds=60),
           retry_policy=RetryPolicy(initial_interval=timedelta(seconds=2), maximum_interval=timedelta(seconds=60)))


@workflow.defn
class PonteTemporalPaperclipWorkflow:
    """Temporal abre issue no Paperclip → agente comenta proposta → validação Pydantic v2 →
    sinal de aprovação do José (stub) → aplica (stub) → comenta e conclui a issue."""

    def __init__(self) -> None:
        self._aprovacao: AprovacaoJose | None = None
        self._etapa = "inicio"
        self._rejeitadas = 0
        self._ignorados = 0

    @workflow.run
    async def run(self, inp: PonteInput) -> ResultadoPonte:
        wid = workflow.info().workflow_id
        issue = await workflow.execute_activity(abrir_issue_paperclip, PedidoIssue(
            company_id=inp.company_id, project_id=inp.project_id, marcador=f"[wf:{wid}]",
            titulo="TZ-04: proposta de teste", agente_id=inp.agente_id,
            descricao=("Issue aberta pelo Temporal (teste t334). O agente de teste responde com um bloco "
                       "```json``` no formato PropostaAgente. Nada é aplicado sem a aprovação do José.")), **_PC)
        await workflow.execute_activity(comentar_paperclip, Comentario(issue_id=issue, acordar_responsavel=True,
            corpo="[Temporal] Aguardando proposta do agente (bloco json PropostaAgente)."), **_PC)
        self._etapa = "aguardando_proposta"
        vistos: list[str] = []
        proposta: PropostaAgente | None = None
        prazo = workflow.now() + timedelta(seconds=inp.espera_proposta_segundos)
        while proposta is None:
            if workflow.now() >= prazo:
                self._etapa = "expirado_sem_proposta"
                return ResultadoPonte(issue_id=issue, etapa=self._etapa, propostas_rejeitadas=self._rejeitadas)
            novas = await workflow.execute_activity(ler_propostas_paperclip, LeituraPropostas(
                issue_id=issue, agente_id=inp.agente_id, ja_vistos=vistos), **_PC)
            for n in novas:
                vistos.append(n.comentario_id)
                try:
                    proposta = PropostaAgente.model_validate(n.dados or {})
                    break
                except ValidationError as e:
                    self._rejeitadas += 1
                    await workflow.execute_activity(comentar_paperclip, Comentario(issue_id=issue, corpo=(
                        f"[Temporal] Proposta rejeitada pela validação Pydantic v2 ({e.error_count()} erro(s)). "
                        "Nada foi aplicado.")), **_PC)
            if proposta is None:
                await workflow.sleep(timedelta(seconds=inp.intervalo_leitura_segundos))
        self._etapa = "aguardando_aprovacao"
        await workflow.execute_activity(comentar_paperclip, Comentario(issue_id=issue, corpo=(
            f"[Temporal] Proposta válida ({proposta.tipo}, risco {proposta.risco}): \"{proposta.resumo}\". "
            "Aguardando aprovação do José; nada aplicado ainda.")), **_PC)
        await pedir_aprovacao_telegram("aguardando_aprovacao", f"proposta {proposta.tipo} (issue {issue})",
                                       f"PQBR — aprovar proposta {proposta.tipo} (risco {proposta.risco}): {proposta.resumo[:600]}",
                                       timedelta(seconds=inp.espera_aprovacao_segundos))
        try:
            await workflow.wait_condition(lambda: self._aprovacao is not None,
                                          timeout=timedelta(seconds=inp.espera_aprovacao_segundos))
        except TimeoutError:
            self._etapa = "expirado_sem_aprovacao"
            return ResultadoPonte(issue_id=issue, etapa=self._etapa, propostas_rejeitadas=self._rejeitadas)
        if self._aprovacao.decisao == "negar":
            self._etapa = "negado"
            await workflow.execute_activity(comentar_paperclip, Comentario(issue_id=issue,
                corpo="[Temporal] José negou. Nada aplicado."), **_PC)
            return ResultadoPonte(issue_id=issue, etapa=self._etapa, propostas_rejeitadas=self._rejeitadas)
        await workflow.execute_activity(aplicar_proposta_stub, proposta, **_PC)
        await workflow.execute_activity(comentar_paperclip, Comentario(issue_id=issue,
            corpo="[Temporal] Aprovado pelo José; proposta aplicada (stub, sem efeito real)."), **_PC)
        await workflow.execute_activity(concluir_issue_paperclip, issue, **_PC)
        self._etapa = "aplicado"
        return ResultadoPonte(issue_id=issue, etapa=self._etapa, propostas_rejeitadas=self._rejeitadas,
                              proposta_aplicada=proposta)

    @workflow.signal
    def aprovacao_jose(self, a: AprovacaoJose) -> None:
        if a.remetente_id != JOSE_ID or self._aprovacao is not None or self._etapa != "aguardando_aprovacao":
            self._ignorados += 1
            return
        self._aprovacao = a

    @workflow.query
    def etapa(self) -> str:
        """Usada pela ponte Telegram (t538) antes de sinalizar `aprovacao_jose`."""
        return self._etapa

    @workflow.query
    def estado(self) -> dict:
        return {"etapa": self._etapa, "rejeitadas": self._rejeitadas, "sinais_ignorados": self._ignorados}
