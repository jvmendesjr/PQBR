"""Reproduz evidência sintética já capturada, sem cliente/servidor/Activities."""
import asyncio
import inspect
import json
from pathlib import Path
import sys
from temporalio.client import WorkflowHistory
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Replayer
from pqbr.workflows.candidato_sessao import CorrecaoCandidata, AtorSessaoCandidato
from tests.workflows.prototipo_recuperacao_pendentes import AtorRecuperacao
from tests.workflows.test_f3_05_recuperacao_runtime import RecuperacaoRuntime

async def main():
    root = Path(sys.argv[1])
    names = [n for n, _ in inspect.getmembers(RecuperacaoRuntime) if n.startswith('test_')]
    results = []
    for path in sorted((root / 'runtime').glob('*.history.json')):
        recovery = any(path.name.startswith(n + '.') for n in names)
        ns = 'f3-05-recovery' if recovery else 'f3-05-candidate'
        data = json.loads(path.read_text())
        h = WorkflowHistory.from_json('replay-offline', data)
        # O workflow ID efetivo é o original; a guarda do ator o valida.
        first = h.events[0].workflow_execution_started_event_attributes
        # Históricos não carregam workflow_id no evento de início; extrair do
        # resumo quando disponível ou da configuração sintética original.
        summary = path.with_name(path.name.replace('.history.json', '.summary.json'))
        if summary.exists():
            workflow_id = json.loads(summary.read_text())['workflow_id']
        else:
            from temporalio.converter import PayloadConverter
            from tests.workflows.prototipo_recuperacao_pendentes import ator_id
            payload = first.input.payloads[0]
            entrada = json.loads(payload.data)
            workflow_id = ator_id(entrada['config']['sessao'])
        h = WorkflowHistory.from_json(workflow_id, data)
        await Replayer(workflows=[AtorRecuperacao, AtorSessaoCandidato, CorrecaoCandidata],
            namespace=ns, data_converter=pydantic_data_converter).replay_workflow(h, raise_on_replay_failure=True)
        results.append(dict(arquivo=path.name, namespace=ns, replay='ok'))
    (root / 'offline-replay-correct-namespace.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Históricos reproduzidos no namespace correto:', len(results))

if __name__ == '__main__':
    asyncio.run(main())
