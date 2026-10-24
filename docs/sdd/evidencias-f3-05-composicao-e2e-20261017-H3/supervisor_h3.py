"""F3-05: supervisor SINTÉTICO separado; não define política operacional.

Filho candidato inalterado. Só FalhaTecnicaFalsa é supervisionada; falha terminal
nunca é reaberta. Registro falso independente, uma tentativa, sem fallback.
Retomar correlaciona estado, NÃO autentica principal nem reconcilia efeito externo.
"""
from collections import deque
from datetime import timedelta
import hashlib
import os
from temporalio import workflow
from temporalio.common import RetryPolicy, WorkflowIDReusePolicy
from temporalio.exceptions import ApplicationError, ActivityError, ChildWorkflowError
with workflow.unsafe.imports_passed_through():
    from pqbr.workflows.candidato_sessao import configuracao, normalizar, CorrecaoCandidata

NAMESPACE = 'f3-05-supervisor'
PREFIXO = 'teste-f3-05-supervisor-'


def ator_id(sessao):
    if not isinstance(sessao, str) or not sessao:
        raise ValueError('sessão sintética obrigatória')
    return PREFIXO + hashlib.sha256(sessao.encode()).hexdigest()


def validar_config(config):
    value = configuracao(**config)
    if not all(value[k].endswith('-supervisor') for k in ('fila_workflow', 'fila_camofox')):
        raise ValueError('filas exclusivas do supervisor sintético')
    return value


@workflow.defn(name='PQBRComposicaoCanonicaH3')
class SupervisorSessao:
    @workflow.init
    def __init__(self, entrada: dict):
        self.config = validar_config(entrada['config'])
        self.aceitos = {}
        self.fila = deque()
        self.resultados = {}
        self.falhas = {}
        self.bloqueio = None
        self.ativo = None
        self.revisao = 0
        self.retomadas = []
        self.autorizacoes = deque()
        self.consumidos = {}
        self.recibos_rejeitados = 0
        self.observacoes = []
        self.admissao_fechada = False
        self.fechando = False

    @workflow.signal
    def solicitar(self, envelope: dict):
        chave = envelope.get('operacao_id') if isinstance(envelope, dict) else None
        motivo, pedido = None, None
        if not isinstance(envelope, dict) or type(envelope.get('versao')) is not int or envelope['versao'] != 1:
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
                motivo = 'duplicado' if pedido == self.aceitos[chave] else 'payload_divergente'
            elif self.admissao_fechada or self.fechando:
                motivo = 'admissao_fechada'
            elif len(self.aceitos) >= 1000:
                motivo = 'capacidade_experimental'
        if motivo:
            self.observacoes.append(dict(id=chave, estado=motivo))
            return
        if (not self.config['sessao'].startswith('FAKE-H3-') or chave not in ('primeira', 'segunda')
                or pedido['passo'] != chave or pedido['erro'] not in ('falha-tecnica', 'falha falsa')
                or pedido.get('simulacao') is None):
            self.observacoes.append(dict(id=chave, estado='fora_allowlist_fixture'))
            return
        self.aceitos[chave] = pedido
        self.fila.append(chave)
        self.observacoes.append(dict(id=chave, estado='aceito'))

    @workflow.signal
    def retomar(self, comando: dict):
        # O comando correlacionado antigo sozinho NÃO é autorização.
        self.observacoes.append(dict(estado='retomada_crua_recusada'))
    @workflow.signal
    def confirmar(self, receipt: dict):
        # Signal não autentica: só o laço principal valida a leitura canônica.
        if isinstance(receipt, dict) and len(self.autorizacoes) < 32:
            self.autorizacoes.append(receipt)
        else:
            self.recibos_rejeitados += 1
    def escopo_atual(self):
        b = self.bloqueio
        if b is None:
            return None
        return dict(supervisor_id=workflow.info().workflow_id,
                    supervisor_run_id=workflow.info().run_id,
                    revisao=self.revisao, falha_id=b['operacao_id'],
                    filho_run_id=b['filho_run_id'], registro_falha_receipt=b['registro_id'],
                    pendentes=list(self.fila))
    async def processar_confirmacao(self, receipt):
        key = receipt.get('consumo_key')
        if isinstance(key, str) and key in self.consumidos:
            if self.consumidos[key] != receipt:
                self.recibos_rejeitados += 1
            else:
                self.observacoes.append(dict(estado='consumo_duplicado_sem_efeito'))
            return
        escopo = self.escopo_atual()
        if (escopo is None or self.bloqueio['registro'] != 'confirmado'
                or receipt.get('escopo') != escopo or receipt.get('decisao') != 'accepted'):
            self.recibos_rejeitados += 1
            return
        try:
            validado = await workflow.execute_activity(
                'reler_confirmacao_canonica_falsa', receipt, result_type=dict,
                task_queue=self.config['fila_workflow'],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=1))
        except ActivityError:
            self.recibos_rejeitados += 1
            return
        # Revalida depois do await. Estado/consumo entram no histórico antes de despachar filho.
        if (not isinstance(validado, dict) or validado.get('receipt') != receipt
                or type(validado.get('expira_em')) is not int
                or workflow.now().timestamp() >= validado['expira_em']
                or self.escopo_atual() != escopo
                or not isinstance(key, str) or not key.startswith('consumo:')):
            self.recibos_rejeitados += 1
            return
        self.consumidos[key] = receipt
        self.retomadas.append(dict(receipt=receipt, pendentes=list(self.fila)))
        self.bloqueio = None
        self.observacoes.append(dict(estado='retomada_canonica_aceita'))
    @workflow.signal
    def fechar(self):
        # Não ignora a pausa, mesmo após pedido de encerramento.
        self.admissao_fechada = True
        self.fechando = True

    @workflow.query
    def estado(self) -> dict:
        return dict(versao=1, aceitos=dict(self.aceitos), pendentes=list(self.fila),
                    resultados=dict(self.resultados), falhas=dict(self.falhas),
                    bloqueio=self.bloqueio, ativo=self.ativo, revisao=self.revisao,
                    retomadas=list(self.retomadas), observacoes=list(self.observacoes),
                    consumidos=dict(self.consumidos), recibos_rejeitados=self.recibos_rejeitados,
                    admissao_fechada=self.admissao_fechada, fechando=self.fechando)

    @workflow.run
    async def run(self, entrada: dict) -> dict:
        if (entrada.get('somente_sintetico') is not True or type(entrada.get('versao')) is not int
                or entrada['versao'] != 1 or workflow.info().namespace != NAMESPACE
                or workflow.info().workflow_id != ator_id(self.config['sessao'])):
            raise ApplicationError('supervisor restrito ao teste sintético', non_retryable=True)
        while True:
            await workflow.wait_condition(lambda: bool(self.autorizacoes) or (self.bloqueio is None and (bool(self.fila) or self.fechando)))
            if self.autorizacoes:
                await self.processar_confirmacao(self.autorizacoes.popleft())
                continue
            if not self.fila:
                return self.estado()
            chave = self.fila.popleft()
            self.ativo = chave
            filho_id = workflow.info().workflow_id + '-op-' + hashlib.sha256(chave.encode()).hexdigest()
            try:
                self.resultados[chave] = await workflow.execute_child_workflow(
                    CorrecaoCandidata.run, dict(versao=1, config=self.config, pedido=self.aceitos[chave]),
                    id=filho_id, task_queue=self.config['fila_workflow'],
                    id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
                    retry_policy=RetryPolicy(maximum_attempts=1))
            except ChildWorkflowError as exc:
                act = exc.cause
                cause = act.cause if isinstance(act, ActivityError) else None
                # Não adota timeout, cancelamento ou erro desconhecido como falha recuperável.
                if not isinstance(cause, ApplicationError) or cause.type != 'FalhaTecnicaFalsa':
                    raise
                self.revisao += 1
                registro_id = workflow.info().workflow_id + ':' + exc.run_id + ':' + chave
                falha = dict(operacao_id=chave, filho_id=exc.workflow_id, filho_run_id=exc.run_id,
                             revisao=self.revisao, estado='falha_tecnica_terminal',
                             resultado_efeito='nao_reconciliado', registro='pendente', registro_id=registro_id)
                self.falhas[chave] = falha
                self.bloqueio = falha
                self.admissao_fechada = True
                # Sem mensagem crua, payload, segredo ou escrita em banco real.
                evento = dict(versao=1, registro_id=registro_id, sessao=self.config['sessao'],
                              operacao_id=chave, filho_id=exc.workflow_id, filho_run_id=exc.run_id,
                              estado='falha_tecnica_terminal', tipo='FalhaTecnicaFalsa',
                              resultado_efeito='nao_reconciliado')
                try:
                    recibo = await workflow.execute_activity(
                        'registrar_falha_supervisor_falsa', evento,
                        task_queue=self.config['fila_workflow'], result_type=dict,
                        activity_id=f'registro-falha-{self.revisao}',
                        start_to_close_timeout=timedelta(seconds=10),
                        retry_policy=RetryPolicy(maximum_attempts=1))
                    falha['registro'] = 'confirmado' if recibo == dict(registro_id=registro_id) else 'recibo_invalido'
                except ActivityError:
                    # Falha do registro também não ganha retry/fallback: permanece bloqueado.
                    falha['registro'] = 'falhou'
                self.observacoes.append(dict(id=chave, estado='pausado_apos_falha'))
            finally:
                self.ativo = None


def workers_sinteticos(client, config, falsos):
    if (os.environ.get('PQBR_SUPERVISOR_ISOLATED') != '1'
            or os.environ.get('PQBR_CANDIDATE_ISOLATED') != '1' or os.environ.get('PQBR_H3_ISOLATED') != '1' or client.namespace != NAMESPACE):
        raise RuntimeError('supervisor somente no Temporal sintético isolado')
    config = validar_config(config)
    from temporalio.worker import Worker
    return (
        Worker(client, task_queue=config['fila_workflow'], workflows=[SupervisorSessao, CorrecaoCandidata],
               activities=[falsos.triagem, falsos.verificar, falsos.registrar, falsos.registrar_falha, falsos.reler_confirmacao],
               max_concurrent_activities=8, max_cached_workflows=0),
        Worker(client, task_queue=config['fila_camofox'], activities=[falsos.intervir], max_concurrent_activities=8),
    )
