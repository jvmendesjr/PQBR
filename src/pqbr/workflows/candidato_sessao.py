"""Candidata F3-05, exclusivamente local/testes; nenhum registro persistente.

Signal-With-Start confirma somente a RPC, não processamento/efeito. Deduplicação
pertence ao estado do ator: não oferece exactly-once nem fencing de efeitos externos.
As filas são obrigatoriamente experimentais; backends reais não são ligados aqui.
"""
from collections import deque
from datetime import timedelta
import hashlib

from temporalio import workflow
from temporalio.common import RetryPolicy, WorkflowIDConflictPolicy, WorkflowIDReusePolicy
from temporalio.exceptions import ApplicationError

with workflow.unsafe.imports_passed_through():
    from .correcao import (
        CAMOFOX_MIN_S, CAMOFOX_MAX_S, MAX_TENTATIVAS, PedidoCorrecao, Tentativa,
        triagem_jev, intervir_agente, verificar_jev, registrar_correcao,
    )
    from ..contratos import ResultadoCorrecao

VERSAO = 1
PREFIXO = 'teste-f3-05-candidato-'
PATCH_INTERVENCAO = 'f3-05-candidato-intervencao-id-v2'
_RT = RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=1))


def ator_id(sessao: str) -> str:
    if not isinstance(sessao, str) or not sessao:
        raise ValueError('sessão obrigatória')
    return PREFIXO + 'sessao-' + hashlib.sha256(sessao.encode('utf-8')).hexdigest()


def configuracao(sessao: str, fila_workflow: str, fila_camofox: str) -> dict:
    ator_id(sessao)
    if (not isinstance(fila_workflow, str) or not isinstance(fila_camofox, str)
            or not fila_workflow.startswith(PREFIXO + 'wf-')
            or not fila_camofox.startswith(PREFIXO + 'camofox-')
            or fila_workflow == fila_camofox):
        raise ValueError('somente filas experimentais separadas de workflow e Camofox')
    return dict(sessao=sessao, fila_workflow=fila_workflow, fila_camofox=fila_camofox)


def normalizar(pedido: dict, sessao: str) -> dict:
    p = PedidoCorrecao.model_validate(pedido)
    if p.sessao != sessao or p.ferramenta != 'camofox':
        raise ValueError('candidata restrita à sessão Camofox configurada')
    return p.model_dump(mode='json')


@workflow.defn(name='PQBRCorrecaoCandidata')
class CorrecaoCandidata:
    """Mesmo tratamento atual: triagem/verificação/registro 3; intervenção 1.

    Exceção técnica da intervenção propaga, sem reconciliação, retry, fallback,
    registro de sucesso ou tentativa de negócio seguinte. A candidata não redefine
    a política canônica. A escada de negócio só prossegue após resposta negativa.
    """
    def _opcoes_intervencao(self, n: int) -> dict:
        # Históricos anteriores ao patch conservam o ID automático original.
        if workflow.patched(PATCH_INTERVENCAO):
            return dict(activity_id=f'intervencao-{n}')
        return {}

    @workflow.run
    async def run(self, entrada: dict) -> dict:
        if entrada.get('versao', 1) != VERSAO:
            raise ApplicationError('versão candidata incompatível', non_retryable=True)
        config = configuracao(**entrada['config'])
        p = PedidoCorrecao.model_validate(normalizar(entrada['pedido'], config['sessao']))
        tri = await workflow.execute_activity(
            triagem_jev, p, task_queue=config['fila_workflow'],
            start_to_close_timeout=timedelta(minutes=2), retry_policy=_RT)
        if tri.classe != 'corrigivel':
            r = ResultadoCorrecao(resultado='sensivel', tentativas=0,
                                 motivo=f'{tri.classe}: {tri.motivo}', chamar_jose=True)
            return await self._registrar(r, config)
        for n in range(1, MAX_TENTATIVAS + 1):
            # Tipo novo, sem adoção de históricos do workflow persistente.
            if n > 1:
                await workflow.sleep(timedelta(seconds=workflow.random().randint(CAMOFOX_MIN_S, CAMOFOX_MAX_S)))
            limite = timedelta(seconds=workflow.random().randint(CAMOFOX_MIN_S, CAMOFOX_MAX_S))
            iv = await workflow.execute_activity(
                intervir_agente, Tentativa(pedido=p, n=n),
                task_queue=config['fila_camofox'], start_to_close_timeout=limite,
                retry_policy=RetryPolicy(maximum_attempts=1), **self._opcoes_intervencao(n))
            if not iv.conta_confere:
                r = ResultadoCorrecao(resultado='sensivel', tentativas=n,
                                     motivo='conta/sessão divergente', chamar_jose=True)
                return await self._registrar(r, config)
            if iv.resolvido:
                ver = await workflow.execute_activity(
                    verificar_jev, Tentativa(pedido=p, n=n), task_queue=config['fila_workflow'],
                    start_to_close_timeout=timedelta(minutes=2), retry_policy=_RT)
                if ver.ok:
                    r = ResultadoCorrecao(resultado='corrigido', tentativas=n,
                                         proposta_script=iv.proposta_script, chamar_jose=False)
                    return await self._registrar(r, config)
        r = ResultadoCorrecao(resultado='esgotado', tentativas=MAX_TENTATIVAS,
                             motivo='3 tentativas sem sucesso', chamar_jose=True)
        return await self._registrar(r, config)

    async def _registrar(self, resultado, config):
        await workflow.execute_activity(
            registrar_correcao, resultado, task_queue=config['fila_workflow'],
            start_to_close_timeout=timedelta(minutes=1), retry_policy=_RT)
        return resultado.model_dump(mode='json')


@workflow.defn(name='PQBRAtorSessaoCandidato')
class AtorSessaoCandidato:
    @workflow.init
    def __init__(self, entrada: dict):
        self.config = configuracao(**entrada['config'])
        self.versao = entrada.get('versao', 1)
        seed = entrada.get('seed', {})
        self.aceitos = dict(seed.get('aceitos', {}))
        self.resultados = dict(seed.get('resultados', {}))
        self.fila = deque()
        self.ativo = None
        self.fechando = False
        self.rolar = False
        self.observacoes = []
        self.geracao = entrada.get('geracao', 0)

    @workflow.signal
    def solicitar(self, envelope: dict):
        # Handler síncrono, sem await/efeito; somente o laço principal despacha.
        chave = envelope.get('operacao_id') if isinstance(envelope, dict) else None
        motivo = None
        pedido = None
        if not isinstance(envelope, dict) or type(envelope.get('versao', 1)) is not int or envelope.get('versao', 1) != VERSAO:
            motivo = 'versao_incompativel'
        elif envelope.get('config') != self.config:
            motivo = 'configuracao_divergente'
        elif not isinstance(chave, str) or not chave or len(chave) > 200:
            motivo = 'operacao_invalida'
        else:
            try:
                pedido = normalizar(envelope['pedido'], self.config['sessao'])
            except (ValueError, TypeError, KeyError):
                motivo = 'pedido_invalido'
        if motivo is None:
            if chave in self.aceitos:
                motivo = 'duplicado' if self.aceitos[chave] == pedido else 'payload_divergente'
            elif self.fechando:
                motivo = 'encerrando'
            elif len(self.aceitos) >= 1000:
                motivo = 'capacidade_experimental'
        if motivo:
            self.observacoes.append(dict(id=chave, estado=motivo))
            return
        self.aceitos[chave] = pedido
        self.fila.append(chave)
        self.observacoes.append(dict(id=chave, estado='aceito'))

    @workflow.signal
    def fechar(self):
        self.fechando = True

    @workflow.signal
    def continuar(self):
        # Sempre transfere dedup e resultados após drenagem, sem opção destrutiva.
        self.rolar = True

    @workflow.query
    def estado(self) -> dict:
        return dict(versao=self.versao, aceitos=list(self.aceitos), resultados=dict(self.resultados),
                    pendentes=list(self.fila), ativo=self.ativo, observacoes=list(self.observacoes),
                    geracao=self.geracao, fechando=self.fechando)

    @workflow.run
    async def run(self, entrada: dict) -> dict:
        if type(self.versao) is not int or self.versao != VERSAO or workflow.info().workflow_id != ator_id(self.config['sessao']):
            raise ApplicationError('identidade/versão candidata inválida', non_retryable=True)
        while True:
            await workflow.wait_condition(lambda: bool(self.fila) or self.fechando or self.rolar)
            if not self.fila:
                if self.fechando:
                    return self.estado()
                workflow.continue_as_new(dict(
                    versao=VERSAO, config=self.config, geracao=self.geracao + 1,
                    seed=dict(aceitos=self.aceitos, resultados=self.resultados)))
            chave = self.fila.popleft()
            self.ativo = chave
            # Await do filho inteiro: correções da mesma sessão não se intercalam.
            filho_id = workflow.info().workflow_id + '-op-' + hashlib.sha256(chave.encode('utf-8')).hexdigest()
            self.resultados[chave] = await workflow.execute_child_workflow(
                CorrecaoCandidata.run,
                dict(versao=VERSAO, config=self.config, pedido=self.aceitos[chave]),
                id=filho_id, task_queue=self.config['fila_workflow'],
                id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
                retry_policy=RetryPolicy(maximum_attempts=1))
            self.ativo = None


async def enviar_signal_with_start(client, sessao: str, fila_workflow: str,
                                   fila_camofox: str, operacao_id: str, pedido: dict):
    """Retorna handle do serviço, NÃO recibo de processamento/resultado de negócio.

    Sem retry de aplicação, fallback Start+Signal ou reabertura independente.
    REJECT_DUPLICATE não é memória após expirar a retenção do servidor.
    """
    config = configuracao(sessao, fila_workflow, fila_camofox)
    if not isinstance(operacao_id, str) or not operacao_id or len(operacao_id) > 200:
        raise ValueError('ID de operação obrigatório, até 200 caracteres')
    pedido = normalizar(pedido, sessao)
    return await client.start_workflow(
        AtorSessaoCandidato.run, dict(versao=VERSAO, config=config),
        id=ator_id(sessao), task_queue=fila_workflow,
        start_signal='solicitar',
        start_signal_args=[dict(versao=VERSAO, config=config, operacao_id=operacao_id, pedido=pedido)],
        id_conflict_policy=WorkflowIDConflictPolicy.USE_EXISTING,
        id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
        retry_policy=RetryPolicy(maximum_attempts=1), rpc_timeout=timedelta(seconds=10))
