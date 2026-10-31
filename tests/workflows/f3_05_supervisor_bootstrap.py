"""Bootstrap do Temporal descartavel para o teste candidato; dados sinteticos."""
import asyncio
from datetime import timedelta
import json
import os
from pathlib import Path
import time
from google.protobuf.json_format import MessageToDict
from temporalio.api.workflowservice.v1 import (
    GetSystemInfoRequest,
    RegisterNamespaceRequest,
    DescribeNamespaceRequest,
)
from temporalio.client import Client
from temporalio.service import RetryConfig


async def main():
    out = Path(os.environ['PQBR_CANDIDATE_OUT'])
    observacoes = []
    prazo = time.monotonic() + 180
    while True:
        try:
            cliente = await Client.connect(
                '127.0.0.1:7233', namespace='f3-05-supervisor',
                retry_config=RetryConfig(max_retries=0),
            )
            info = await cliente.workflow_service.get_system_info(
                GetSystemInfoRequest(), retry=False, timeout=timedelta(seconds=2)
            )
            break
        except Exception as exc:
            observacoes.append({
                'fase': 'prontidao', 'tipo': type(exc).__name__, 'mensagem': str(exc)
            })
            if time.monotonic() > prazo:
                (out / 'readiness.json').write_text(
                    json.dumps(observacoes, ensure_ascii=False, indent=2) + '\n'
                )
                raise
            await asyncio.sleep(1)
    (out / 'system-info.json').write_text(
        json.dumps(MessageToDict(info), ensure_ascii=False, indent=2) + '\n'
    )
    pedido = RegisterNamespaceRequest(
        namespace='f3-05-supervisor',
        description='TESTE SUPERVISOR DESCARTAVEL; somente dados sinteticos',
    )
    pedido.workflow_execution_retention_period.FromTimedelta(timedelta(days=1))
    await cliente.workflow_service.register_namespace(
        pedido, retry=False, timeout=timedelta(seconds=10)
    )
    descricao = await cliente.workflow_service.describe_namespace(
        DescribeNamespaceRequest(namespace='f3-05-supervisor'), retry=False,
        timeout=timedelta(seconds=10),
    )
    (out / 'namespace.json').write_text(
        json.dumps(MessageToDict(descricao), ensure_ascii=False, indent=2) + '\n'
    )
    (out / 'readiness.json').write_text(
        json.dumps(observacoes, ensure_ascii=False, indent=2) + '\n'
    )
    print('Servidor pronto; namespace sintetico candidato criado.', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
