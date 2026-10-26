"""Worker da fila episodio-pqbr (FFmpeg, capa A9, Drive, publicação dry-run). Uso: python -m pqbr.workflows.worker_episodio"""
from __future__ import annotations
import asyncio
from temporalio.worker import Worker
from .acesso import pedir_jose, acesso_resolvido, acesso_paperclip, registrar_evento, avisar_jose
from .worker import client, ADDR, NS
from .episodio import FILA_EPISODIO, EpisodioWorkflow, PublicacaoWorkflow, ATIVIDADES_EPISODIO
from .pacote import ApagarCadernoWorkflow
from .publicacao import PublicacaoAgendadaWorkflow, ControlePublicacaoWorkflow, ATIVIDADES_PUBLICACAO, FILA_PUBLICACAO
from .descarte import DescartarCadernoTesteWorkflow, ATIVIDADES_DESCARTE


async def main() -> None:
    import logging
    from ..seguranca.barreira import instalar_no_logging
    logging.basicConfig(level=logging.INFO); instalar_no_logging()
    assert FILA_PUBLICACAO == FILA_EPISODIO   # t69s317: publicação agendada no worker do episódio
    w = Worker(await client(), task_queue=FILA_EPISODIO, workflows=[EpisodioWorkflow, PublicacaoWorkflow, ApagarCadernoWorkflow, DescartarCadernoTesteWorkflow,
                                                                     PublicacaoAgendadaWorkflow, ControlePublicacaoWorkflow],
               activities=[*ATIVIDADES_EPISODIO, pedir_jose, acesso_resolvido, acesso_paperclip, registrar_evento, avisar_jose, *ATIVIDADES_DESCARTE, *ATIVIDADES_PUBLICACAO], max_concurrent_activities=1)
    logging.getLogger(__name__).info(f"worker episodio em {ADDR} ns={NS} fila={FILA_EPISODIO} (concorrência 1)")
    await w.run()


if __name__ == "__main__":
    asyncio.run(main())
