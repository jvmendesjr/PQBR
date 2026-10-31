"""Experimento F3-05; sem importações PQBR ou registro em Worker operacional."""
from collections import deque
from datetime import timedelta
import hashlib
from temporalio import workflow
from temporalio.common import RetryPolicy, WorkflowIDConflictPolicy, WorkflowIDReusePolicy
from temporalio.exceptions import ApplicationError


def ator_id(sessao: str) -> str:
    return "prototipo-signal-start-v1-" + hashlib.sha256(sessao.encode("utf-8")).hexdigest()


@workflow.defn
class AtorSignalSintetico:
    @workflow.init
    def __init__(self, entrada: dict):
        self.config = entrada["config"]
        seed = entrada.get("seed", {})
        self.aceitos = dict(seed.get("aceitos", {}))
        self.concluidos = list(seed.get("concluidos", []))
        self.geracao = entrada.get("geracao", 0)
        self.fila = deque()
        self.observacoes = []
        self.ativo = None
        self.fechando = False
        self.rolar = None

    @workflow.signal
    def solicitar(self, envelope: dict):
        # Signal não tem retorno ao chamador. Rejeição é estado observável, não exceção RPC.
        pedido = envelope.get("pedido", {})
        chave = pedido.get("id")
        motivo = None
        if envelope.get("config") != self.config:
            motivo = "configuracao_divergente"
        elif (set(pedido) != {"id", "sessao", "falhar"} or not isinstance(chave, str)
              or not chave or type(pedido.get("falhar")) is not bool
              or pedido.get("sessao") != self.config["sessao"]):
            motivo = "pedido_invalido"
        elif chave in self.aceitos:
            motivo = "duplicado" if self.aceitos[chave] == pedido else "payload_divergente"
        elif self.fechando:
            motivo = "encerrando"
        if motivo:
            self.observacoes.append(dict(id=chave, estado=motivo))
            return
        self.aceitos[chave] = dict(pedido)
        self.fila.append(dict(pedido))
        self.observacoes.append(dict(id=chave, estado="aceito"))

    @workflow.signal
    def fechar(self):
        self.fechando = True

    @workflow.signal
    def continuar(self, preservar: bool):
        # Apenas experimento: drena a fila antes de Continue-As-New.
        self.rolar = preservar

    @workflow.query
    def estado(self) -> dict:
        return dict(aceitos=list(self.aceitos), concluidos=list(self.concluidos),
                    pendentes=[p["id"] for p in self.fila], ativo=self.ativo,
                    observacoes=list(self.observacoes), fechando=self.fechando,
                    geracao=self.geracao)

    @workflow.run
    async def run(self, entrada: dict) -> dict:
        config = self.config
        if workflow.info().workflow_id != ator_id(config["sessao"]):
            raise ApplicationError("identidade sintetica invalida", non_retryable=True)
        while True:
            await workflow.wait_condition(lambda: bool(self.fila) or self.fechando or self.rolar is not None)
            if not self.fila:
                if self.fechando:
                    return self.estado()
                seed = dict(aceitos=self.aceitos, concluidos=self.concluidos) if self.rolar else {}
                workflow.continue_as_new(dict(config=config, seed=seed, geracao=self.geracao + 1))
            pedido = self.fila.popleft()
            self.ativo = pedido["id"]
            # Único despachante. Falha técnica propaga sem retry/fallback/reconciliação.
            await workflow.execute_activity(
                "efeito_signal_sintetico_v1", pedido,
                task_queue=config["fila_activity"],
                schedule_to_close_timeout=timedelta(seconds=config["prazo_s"]),
                start_to_close_timeout=timedelta(seconds=config["prazo_s"]),
                retry_policy=RetryPolicy(maximum_attempts=1))
            self.concluidos.append(pedido["id"])
            self.ativo = None


def configuracao(sessao, fila_workflow, fila_activity, prazo_s=10):
    if not isinstance(sessao, str) or not sessao:
        raise ValueError("sessao sintetica obrigatoria")
    if not fila_workflow.startswith("teste-sws-wf-") or not fila_activity.startswith("teste-sws-act-"):
        raise ValueError("somente filas sinteticas")
    if type(prazo_s) is not int or not 1 <= prazo_s <= 30:
        raise ValueError("prazo sintetico entre 1 e 30")
    return dict(sessao=sessao, fila_workflow=fila_workflow, fila_activity=fila_activity, prazo_s=prazo_s)


async def enviar_signal_with_start(client, sessao, fila_workflow, fila_activity, pedido,
                                   prazo_s=10, reuse=WorkflowIDReusePolicy.REJECT_DUPLICATE):
    config = configuracao(sessao, fila_workflow, fila_activity, prazo_s)
    # start_signal aciona a RPC SignalWithStartWorkflowExecution do SDK Python.
    # O handle é resposta do serviço, NÃO confirmação de processamento do pedido.
    return await client.start_workflow(
        AtorSignalSintetico.run, dict(config=config), id=ator_id(sessao),
        task_queue=fila_workflow, start_signal="solicitar",
        start_signal_args=[dict(config=config, pedido=pedido)],
        id_conflict_policy=WorkflowIDConflictPolicy.USE_EXISTING,
        id_reuse_policy=reuse, execution_timeout=timedelta(minutes=2),
        retry_policy=RetryPolicy(maximum_attempts=1), rpc_timeout=timedelta(seconds=10))
