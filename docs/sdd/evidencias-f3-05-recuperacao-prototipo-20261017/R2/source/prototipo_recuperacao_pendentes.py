"""EXPERIMENTO SINTÉTICO F3-05. Não é política operacional nem recuperação de ator terminal.
Tipo/IDs novos; não adota históricos candidatos. Só captura FalhaTecnicaFalsa.
O filho continua falhando sem retry. Retomada não é reconciliação de efeito externo.
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

PREFIXO = 'teste-f3-05-recuperacao-'


def ator_id(sessao):
    if not isinstance(sessao, str) or not sessao:
        raise ValueError('sessão sintética obrigatória')
    return PREFIXO + hashlib.sha256(sessao.encode('utf-8')).hexdigest()


def validar_config(config):
    value = configuracao(**config)
    if not all(value[k].endswith('-recuperacao') for k in ('fila_workflow', 'fila_camofox')):
        raise ValueError('filas exclusivas do protótipo de recuperação')
    return value


@workflow.defn(name='PQBRPrototipoRecuperacaoPendentes')
class AtorRecuperacao:
    @workflow.init
    def __init__(self, entrada: dict):
        self.config = validar_config(entrada['config'])
        seed = entrada.get('seed', {})
        self.aceitos = dict(seed.get('aceitos', {}))
        self.resultados = dict(seed.get('resultados', {}))
        self.falhas = dict(seed.get('falhas', {}))
        self.fila = deque(seed.get('fila', []))
        self.bloqueio = seed.get('bloqueio')
        self.revisao = seed.get('revisao', 0)
        self.recuperacoes = list(seed.get('recuperacoes', []))
        self.observacoes = list(seed.get('observacoes', []))
        self.admissao_fechada = seed.get('admissao_fechada', False)
        self.fechando = seed.get('fechando', False)
        self.geracao = entrada.get('geracao', 0)
        self.ativo = None
        self.rolar = False

    @workflow.signal
    def solicitar(self, envelope: dict):
        chave = envelope.get('operacao_id') if isinstance(envelope, dict) else None
        motivo, pedido = None, None
        if not isinstance(envelope, dict) or type(envelope.get('versao', 1)) is not int or envelope.get('versao', 1) != 1:
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
        self.aceitos[chave] = pedido
        self.fila.append(chave)
        self.observacoes.append(dict(id=chave, estado='aceito'))

    @workflow.signal
    def recuperar(self, comando: dict):
        # Correlação sintética, NÃO autenticação/autorização de produção.
        esperado = None if self.bloqueio is None else dict(
            versao=1, decisao='retomar_somente_pendentes',
            revisao=self.revisao, falha_id=self.bloqueio['operacao_id'],
            filho_run_id=self.bloqueio['filho_run_id'])
        valido = (isinstance(comando, dict) and esperado is not None and comando == esperado
                  and type(comando.get('versao')) is int and type(comando.get('revisao')) is int)
        if not valido:
            self.observacoes.append(dict(estado='recuperacao_recusada'))
            return
        self.recuperacoes.append(dict(**esperado, pendentes=list(self.fila)))
        self.bloqueio = None
        self.observacoes.append(dict(estado='recuperacao_aceita'))

    @workflow.signal
    def fechar(self):
        self.admissao_fechada = True
        self.fechando = True

    @workflow.signal
    def continuar(self):
        self.rolar = True

    @workflow.query
    def estado(self) -> dict:
        return dict(versao=1, aceitos=dict(self.aceitos), resultados=dict(self.resultados),
                    falhas=dict(self.falhas), pendentes=list(self.fila), ativo=self.ativo,
                    bloqueio=self.bloqueio, revisao=self.revisao,
                    recuperacoes=list(self.recuperacoes), observacoes=list(self.observacoes),
                    admissao_fechada=self.admissao_fechada, fechando=self.fechando,
                    geracao=self.geracao)

    def _continuar(self):
        state = self.estado()
        state['fila'] = state.pop('pendentes')
        workflow.continue_as_new(dict(versao=1, somente_sintetico=True, config=self.config,
                                     geracao=self.geracao + 1, seed=state))

    @workflow.run
    async def run(self, entrada: dict) -> dict:
        if (entrada.get('somente_sintetico') is not True or type(entrada.get('versao')) is not int
                or entrada['versao'] != 1 or workflow.info().namespace != 'f3-05-recovery'
                or workflow.info().workflow_id != ator_id(self.config['sessao'])):
            raise ApplicationError('protótipo restrito ao ambiente sintético', non_retryable=True)
        while True:
            # Fechar NÃO libera bloqueio. Continue-As-New conserva toda a fila e a pausa.
            await workflow.wait_condition(lambda: self.rolar or (
                self.bloqueio is None and (bool(self.fila) or self.fechando)))
            if self.rolar:
                self._continuar()
            if not self.fila:
                return self.estado()
            chave = self.fila.popleft()
            self.ativo = chave
            filho_id = workflow.info().workflow_id + '-op-' + hashlib.sha256(chave.encode()).hexdigest()
            try:
                self.resultados[chave] = await workflow.execute_child_workflow(
                    CorrecaoCandidata.run,
                    dict(versao=1, config=self.config, pedido=self.aceitos[chave]),
                    id=filho_id, task_queue=self.config['fila_workflow'],
                    id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
                    retry_policy=RetryPolicy(maximum_attempts=1))
            except ChildWorkflowError as exc:
                # Nenhuma captura genérica de timeout/cancelamento/erros desconhecidos.
                act = exc.cause
                cause = act.cause if isinstance(act, ActivityError) else None
                if not isinstance(cause, ApplicationError) or cause.type != 'FalhaTecnicaFalsa':
                    raise
                self.revisao += 1
                self.bloqueio = dict(operacao_id=chave, filho_id=exc.workflow_id,
                                    filho_run_id=exc.run_id, revisao=self.revisao,
                                    estado='falha_tecnica_sintetica', resultado_efeito='nao_reconciliado')
                self.falhas[chave] = dict(self.bloqueio)
                self.admissao_fechada = True
                self.observacoes.append(dict(id=chave, estado='pausado_apos_falha'))
            finally:
                self.ativo = None


def workers_sinteticos(client, config, falsos):
    if (os.environ.get('PQBR_RECOVERY_ISOLATED') != '1'
            or os.environ.get('PQBR_CANDIDATE_ISOLATED') != '1'
            or client.namespace != 'f3-05-recovery'):
        raise RuntimeError('composição de recuperação somente no teste isolado')
    config = validar_config(config)
    from temporalio.worker import Worker
    return (
        Worker(client, task_queue=config['fila_workflow'],
               workflows=[AtorRecuperacao, CorrecaoCandidata],
               activities=[falsos.triagem, falsos.verificar, falsos.registrar],
               max_concurrent_activities=8, max_cached_workflows=0),
        Worker(client, task_queue=config['fila_camofox'], activities=[falsos.intervir],
               max_concurrent_activities=8),
    )
