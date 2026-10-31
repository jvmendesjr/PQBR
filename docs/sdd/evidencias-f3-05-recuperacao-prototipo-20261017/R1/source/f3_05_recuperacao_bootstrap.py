"""Bootstrap exclusivo de containers sintéticos; sem conexão ao Temporal operacional."""
import asyncio
from datetime import timedelta
import json
import os
from pathlib import Path
from google.protobuf.json_format import MessageToDict
from temporalio.api.workflowservice.v1 import RegisterNamespaceRequest, DescribeNamespaceRequest
from temporalio.client import Client
from temporalio.service import RetryConfig
from tests.workflows.f3_05_candidate_bootstrap import main as preparar_candidata

async def main():
    await preparar_candidata()
    client = await Client.connect('127.0.0.1:7233', namespace='f3-05-recovery',
                                  retry_config=RetryConfig(max_retries=0))
    req = RegisterNamespaceRequest(namespace='f3-05-recovery',
        description='PROTOTIPO RECUPERACAO DESCARTAVEL; somente Activities sinteticas')
    req.workflow_execution_retention_period.FromTimedelta(timedelta(days=1))
    await client.workflow_service.register_namespace(req, retry=False, timeout=timedelta(seconds=10))
    ns = await client.workflow_service.describe_namespace(
        DescribeNamespaceRequest(namespace='f3-05-recovery'), retry=False, timeout=timedelta(seconds=10))
    (Path(os.environ['PQBR_CANDIDATE_OUT']) / 'namespace-recovery.json').write_text(
        json.dumps(MessageToDict(ns), ensure_ascii=False, indent=2) + '\n')
    print('Namespace sintético de recuperação criado.', flush=True)

if __name__ == '__main__':
    asyncio.run(main())
