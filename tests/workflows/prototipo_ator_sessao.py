"""Protótipo F3-05 exclusivamente sintético; não registrado em Workers reais."""
from collections import deque
from datetime import timedelta
import hashlib

from temporalio import workflow
from temporalio.common import RetryPolicy, WorkflowIDConflictPolicy, WorkflowIDReusePolicy
from temporalio.exceptions import ApplicationError


def ator_id(sessao: str) -> str:
    # Sem normalização implícita: igualdade exata UTF-8. Nunca usar hash() do Python.
    return "prototipo-ator-sessao-v1-" + hashlib.sha256(sessao.encode("utf-8")).hexdigest()


@workflow.defn
class AtorSessaoSintetico:
    @workflow.init
    def __init__(self, config: dict):
        self.sessao = config["sessao"]
        self.fila = deque()
        self.aceitos = {}
        self.concluidos = []
        self.fechando = False
        self.ativo = None

    @workflow.update
    def solicitar(self, pedido: dict) -> str:
        if pedido.get("sessao") != self.sessao:
            raise ApplicationError("sessao divergente", type="AdmissaoInvalida")
        chave = pedido.get("id")
        if not isinstance(chave, str) or not chave or set(pedido) != {"id", "sessao", "falhar"} or not isinstance(pedido["falhar"], bool):
            raise ApplicationError("pedido sintetico invalido", type="AdmissaoInvalida")
        if chave in self.aceitos:
            if self.aceitos[chave] != pedido:
                raise ApplicationError("id com payload divergente", type="AdmissaoInvalida")
            return "duplicado"
        if self.fechando:
            raise ApplicationError("ator encerrando", type="AdmissaoFechada")
        self.aceitos[chave] = dict(pedido)
        self.fila.append(dict(pedido))
        return "aceito"

    @workflow.signal
    def fechar(self):
        self.fechando = True

    @workflow.query
    def estado(self) -> dict:
        return dict(sessao=self.sessao, aceitos=list(self.aceitos),
                    pendentes=[p["id"] for p in self.fila], ativo=self.ativo,
                    concluidos=list(self.concluidos), fechando=self.fechando)

    @workflow.run
    async def run(self, config: dict) -> dict:
        self.sessao = config["sessao"]
        if workflow.info().workflow_id != ator_id(self.sessao):
            raise ApplicationError("identidade do ator invalida", type="IdentidadeInvalida", non_retryable=True)
        if not config["fila_camofox"].startswith("teste-camofox-ator-"):
            raise ApplicationError("apenas fila sintetica", type="ConfigInvalida", non_retryable=True)
        while True:
            await workflow.wait_condition(lambda: bool(self.fila) or self.fechando)
            if not self.fila:
                return self.estado()
            pedido = self.fila.popleft()
            self.ativo = pedido["id"]
            # Único lugar que inicia Activities. Updates não aguardam nem executam trabalho.
            # Erro técnico propaga: sem retry, fallback, registro final ou próximo pedido.
            await workflow.execute_activity(
                "intervir_camofox_sintetico_v1", pedido,
                task_queue=config["fila_camofox"],
                schedule_to_close_timeout=timedelta(seconds=config["prazo_s"]),
                start_to_close_timeout=timedelta(seconds=config["prazo_s"]),
                retry_policy=RetryPolicy(maximum_attempts=1),
            )
            self.concluidos.append(pedido["id"])
            self.ativo = None


async def obter_ator(client, sessao: str, fila_workflow: str, fila_camofox: str, prazo_s=10):
    # Protótipo de duas RPCs: criação e posterior update não formam admissão atômica.
    return await client.start_workflow(
        AtorSessaoSintetico.run,
        dict(sessao=sessao, fila_camofox=fila_camofox, prazo_s=prazo_s),
        id=ator_id(sessao), task_queue=fila_workflow,
        id_conflict_policy=WorkflowIDConflictPolicy.USE_EXISTING,
        id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
        execution_timeout=timedelta(minutes=2),
        retry_policy=RetryPolicy(maximum_attempts=1),
    )
