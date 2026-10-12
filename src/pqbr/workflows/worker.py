"""Worker do PQBR. Uso: python -m pqbr.workflows.worker"""
from __future__ import annotations
import asyncio, os
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker
from .workflows import EpisodioWorkflow, PonteTemporalPaperclipWorkflow
from .activities import gerar_roteiro, gravar_outbox, aplicar_proposta_stub
from .correcao import (CorrecaoAutonomaWorkflow, triagem_jev, intervir_agente, verificar_jev,
                       registrar_correcao)
from .manutencao import RetencaoConsumoWorkflow, reter_consumo, registrar_consumo
from .producao import GradeDiariaWorkflow, EpisodioProducaoWorkflow, ATIVIDADES as ATIV_PRODUCAO
from .temas import ReposicaoTemasWorkflow, ATIVIDADES_TEMAS
from .acesso import AcessosWorkflow
from .paperclip import (abrir_issue_paperclip, comentar_paperclip, ler_propostas_paperclip,
                        concluir_issue_paperclip)

ADDR = os.environ.get("TEMPORAL_ADDRESS", "127.0.0.1:7233")
NS = os.environ.get("TEMPORAL_NAMESPACE", "pqbr")
FILA = "pqbr-episodio"


async def client() -> Client:
    return await Client.connect(ADDR, namespace=NS, data_converter=pydantic_data_converter)


async def main() -> None:
    import logging
    from ..seguranca.barreira import instalar_no_logging
    logging.basicConfig(level=logging.INFO)
    instalar_no_logging()
    c = await client()
    w = Worker(c, task_queue=FILA, workflows=[EpisodioWorkflow, PonteTemporalPaperclipWorkflow, CorrecaoAutonomaWorkflow, AcessosWorkflow,
                          RetencaoConsumoWorkflow, GradeDiariaWorkflow, EpisodioProducaoWorkflow, ReposicaoTemasWorkflow],
               activities=[gerar_roteiro, gravar_outbox, aplicar_proposta_stub, abrir_issue_paperclip,
                           comentar_paperclip, ler_propostas_paperclip, concluir_issue_paperclip,
                           triagem_jev, intervir_agente, verificar_jev, registrar_correcao,
                           reter_consumo, registrar_consumo, *ATIV_PRODUCAO, *ATIVIDADES_TEMAS])
    print(f"worker em {ADDR} ns={NS} fila={FILA}", flush=True)
    await w.run()


if __name__ == "__main__":
    asyncio.run(main())
