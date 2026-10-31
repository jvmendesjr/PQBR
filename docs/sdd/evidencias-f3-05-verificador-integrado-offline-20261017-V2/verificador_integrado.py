"""Integração V2 offline: JSONs locais/dados fornecidos, sem coletor operacional.

Não é runner B3. Não importa autorizações, workflows ou ferramentas de runtime.
Nenhuma função escreve arquivos. O chamador é responsável por fornecer capturas
anteriores legítimas; esta API não autentica dados nem reconstrói o passado.
"""
from copy import deepcopy
import json
from pathlib import Path

import verificador_offline as core


def prepare_baseline(inventories, inspect_records, protected_payload, expected_ids):
    """Conecta produtor explícito e proteção; falha sem fabricar baseline parcial.

    Só utilizar com capturas próprias da etapa que vier a ser autorizada. Nunca
    alimentar esta função com dados posteriores para reparar uma rodada passada.
    """
    resources = core.snapshot_resources(inventories, inspect_records, expected_ids)
    protection = core.protected(protected_payload)
    return {'resources': resources, 'protected': deepcopy(protection)}


def verify_inputs(before_resources, before_protected, expected_ids, *, runtime_exit_code,
                  read_inventory, read_inspects, read_protected, read_cleanup):
    """Integra os checks V1 e o produtor pós-snapshot sem acoplar as coletas.

    Cada callback devolve dados já decodificados. Todos os checks são tentados
    antes da validação cruzada do snapshot produzido. Não há saída de runtime.
    """
    captured = {}

    def inventory():
        value = read_inventory()
        captured['inventory'] = deepcopy(value)
        return value

    def inspects():
        value = read_inspects()
        captured['inspects'] = deepcopy(value)
        return value

    report = core.verify_final(
        before_resources, before_protected, expected_ids,
        runtime_exit_code=runtime_exit_code,
        collect_inventory=inventory, collect_operational=inspects,
        collect_protected=read_protected, check_cleanup=read_cleanup)

    # A falha de coleta/projeção não impede proteção/limpeza: elas já foram
    # verificadas. Não há default vazio para qualquer parte faltante.
    try:
        core.require('inventory' in captured and 'inspects' in captured,
                     'snapshot posterior: captura incompleta')
        after = core.snapshot_resources(captured['inventory'], captured['inspects'], expected_ids)
        report['after_snapshot'] = after
        report['checks']['snapshot_contract'] = {'status': 'PASS'}
    except Exception as exc:
        report['checks']['snapshot_contract'] = {
            'status': 'INCONCLUSIVE', 'error_type': type(exc).__name__}

    passed = (type(runtime_exit_code) is int and runtime_exit_code == 0
              and all(check['status'] == 'PASS' for check in report['checks'].values()))
    report['status'] = 'PASS' if passed else 'FAIL'
    report['exit_code'] = 0 if passed else 2
    report['mode'] = 'OFFLINE_ONLY'
    report['integration_version'] = 'V2'
    return report


def read_json(path):
    """Somente leitura do arquivo explicitamente fornecido; não segue referências."""
    return json.loads(Path(path).read_text(encoding='utf-8'))


def verify_files(*, baseline_resources, baseline_protected, after_inventory,
                 after_inspects, after_protected, cleanup_result,
                 expected_ids, runtime_exit_code):
    """Ponto de entrada offline integrado, sem CLI nem execução no import.

    Erros de leitura dos baselines não abortam as verificações independentes.
    O código do runtime é somente dado fornecido, nunca resultado reexecutado.
    """
    acquisition = {}

    def baseline(name, path):
        try:
            value = read_json(path)
            acquisition[name] = {'status': 'READ'}
            return value
        except Exception as exc:
            acquisition[name] = {'status': 'INCONCLUSIVE', 'error_type': type(exc).__name__}
            return None  # Evidência explicitamente ausente, não snapshot vazio.

    before_resources = baseline('baseline_resources', baseline_resources)
    before_protected = baseline('baseline_protected', baseline_protected)
    report = verify_inputs(
        before_resources, before_protected, expected_ids,
        runtime_exit_code=runtime_exit_code,
        read_inventory=lambda: read_json(after_inventory),
        read_inspects=lambda: read_json(after_inspects),
        read_protected=lambda: read_json(after_protected),
        read_cleanup=lambda: read_json(cleanup_result))
    report['baseline_acquisition'] = acquisition
    return report
