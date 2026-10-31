"""Registro experimental explícito, importado somente pela suíte candidata."""
import asyncio
import os
import time

from temporalio import activity, workflow
from temporalio.exceptions import ApplicationError
from temporalio.worker import Worker

from pqbr.contratos import TriagemCorrecao, ResultadoIntervencao, VerificacaoCorrecao, ResultadoCorrecao
from pqbr.workflows.correcao import PedidoCorrecao, Tentativa
from pqbr.workflows.candidato_sessao import AtorSessaoCandidato, CorrecaoCandidata


@workflow.defn(name='PQBRCorrecaoCandidata')
class CorrecaoCandidataV1(CorrecaoCandidata):
    """Fixture anterior ao patch; tipo e comandos reais, sem adulterar histórico."""
    def _opcoes_intervencao(self, n):
        return {}

    @workflow.run
    async def run(self, entrada: dict) -> dict:
        return await super().run(entrada)


class BackendsFalsos:
    def __init__(self):
        self.liberar = asyncio.Event()
        self.bloquear = False
        self.calls = []
        self.registros = []
        self.ativos = {}
        self.max_sessao = {}
        self.max_global = 0
        self.triagens = 0

    @activity.defn(name='triagem_jev')
    async def triagem(self, p: PedidoCorrecao) -> TriagemCorrecao:
        self.triagens += 1
        # Reusa a trava determinística atual, mas não liga backend real.
        from pqbr.workflows.correcao import triagem_jev
        return await triagem_jev(p)

    @activity.defn(name='intervir_agente')
    async def intervir(self, t: Tentativa) -> ResultadoIntervencao:
        s = t.pedido.sessao
        self.ativos[s] = self.ativos.get(s, 0) + 1
        self.max_sessao[s] = max(self.max_sessao.get(s, 0), self.ativos[s])
        self.max_global = max(self.max_global, sum(self.ativos.values()))
        chamada = dict(sessao=s, passo=t.pedido.passo, inicio=time.monotonic(), fim=None,
                       fila=activity.info().task_queue, tentativa=activity.info().attempt,
                       workflow_id=activity.info().workflow_id)
        self.calls.append(chamada)
        try:
            if self.bloquear:
                await self.liberar.wait()
            await asyncio.sleep(0.04)
            if t.pedido.erro == 'falha-tecnica':
                raise ApplicationError('falha técnica falsa', type='FalhaTecnicaFalsa')
            return ResultadoIntervencao(resolvido=True, conta_confere=t.pedido.simulacao.conta_confere,
                                       aprendizado='falso', proposta_script='proposta falsa')
        finally:
            chamada['fim'] = time.monotonic()
            self.ativos[s] -= 1

    @activity.defn(name='verificar_jev')
    async def verificar(self, t: Tentativa) -> VerificacaoCorrecao:
        return VerificacaoCorrecao(ok=True)

    @activity.defn(name='registrar_correcao')
    async def registrar(self, r: ResultadoCorrecao) -> None:
        self.registros.append(r.model_dump(mode='json'))


def workers_experimentais(client, config, falsos, *, legado=False):
    """A composição não roda nada ao importar; exige opt-in e namespace sintético."""
    if os.environ.get('PQBR_CANDIDATE_ISOLATED') != '1' or client.namespace != 'f3-05-candidate':
        raise RuntimeError('registro somente no ambiente descartável autorizado')
    return (
        Worker(client, task_queue=config['fila_workflow'],
               workflows=[AtorSessaoCandidato, CorrecaoCandidataV1 if legado else CorrecaoCandidata],
               activities=[falsos.triagem, falsos.verificar, falsos.registrar],
               max_concurrent_activities=8, max_cached_workflows=0),
        Worker(client, task_queue=config['fila_camofox'], activities=[falsos.intervir],
               max_concurrent_activities=8),
    )
