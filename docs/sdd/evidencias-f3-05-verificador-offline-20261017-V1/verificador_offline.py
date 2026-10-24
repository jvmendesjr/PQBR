"""Candidata offline V1. Sem coleta real, CLI, efeitos ou import do runner B3."""
from datetime import datetime
import re

KINDS = ('containers', 'networks', 'volumes')
FIELDS = {'id', 'name', 'status', 'pid', 'startedAt'}
STATES = {'created', 'running', 'paused', 'restarting', 'removing', 'exited', 'dead'}


class ContractError(ValueError):
    """Evidência ausente/inválida: nunca equivale a preservação comprovada."""


def require(ok, field):
    if not ok:
        raise ContractError(field)


def identifier(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def expected_set(expected_ids):
    require(isinstance(expected_ids, (list, tuple)), 'expected_ids: lista explícita')
    require(bool(expected_ids) and all(identifier(x) for x in expected_ids), 'expected_ids: IDs completos')
    require(len(set(expected_ids)) == len(expected_ids), 'expected_ids: duplicata')
    return set(expected_ids)


def inventory(value):
    require(isinstance(value, dict), 'inventory: objeto')
    result = {}
    for kind in KINDS:
        require(kind in value and isinstance(value[kind], list), kind + ': ausente/lista')
        rows = value[kind]
        require(all(isinstance(x, str) and bool(x.strip()) for x in rows), kind + ': identificador')
        require(len(set(rows)) == len(rows), kind + ': duplicata')
        result[kind] = sorted(rows)
    return result


def operational_projection(rows, expected_ids):
    expected = expected_set(expected_ids)
    require(isinstance(rows, list) and bool(rows), 'operational_states: lista não vazia')
    output = []
    for row in rows:
        require(isinstance(row, dict) and set(row) == FIELDS, 'operational_states: campos exatos')
        require(identifier(row['id']), 'operational_states.id')
        require(isinstance(row['name'], str) and row['name'].startswith('/') and len(row['name']) > 1, 'operational_states.name')
        require(isinstance(row['status'], str) and row['status'] in STATES, 'operational_states.status')
        require(type(row['pid']) is int and row['pid'] >= 0, 'operational_states.pid')
        require(row['status'] != 'running' or row['pid'] > 0, 'operational_states.running.pid')
        require(isinstance(row['startedAt'], str) and bool(row['startedAt']), 'operational_states.startedAt')
        try:
            stamp = datetime.fromisoformat(row['startedAt'].replace('Z', '+00:00'))
        except ValueError as exc:
            raise ContractError('operational_states.startedAt: ISO inválido') from exc
        require(stamp.tzinfo is not None, 'operational_states.startedAt: timezone')
        output.append(dict(row))
    require(len({x['id'] for x in output}) == len(output), 'operational_states: ID duplicado')
    require(len({x['name'] for x in output}) == len(output), 'operational_states: nome duplicado')
    require({x['id'] for x in output} == expected, 'operational_states: conjunto protegido divergente')
    return sorted(output, key=lambda row: row['id'])


def project_inspects(records, expected_ids):
    """Projeta apenas campos observados em inspect histórico; não chama Docker."""
    require(isinstance(records, list), 'inspect: lista')
    output = []
    for record in records:
        require(isinstance(record, dict) and all(k in record for k in ('Id', 'Name', 'State')), 'inspect: campos ausentes')
        state = record['State']
        require(isinstance(state, dict) and all(k in state for k in ('Status', 'Pid', 'StartedAt')), 'inspect.State: campos ausentes')
        output.append({'id': record['Id'], 'name': record['Name'], 'status': state['Status'],
                       'pid': state['Pid'], 'startedAt': state['StartedAt']})
    return operational_projection(output, expected_ids)


def snapshot_resources(inventories, inspect_records, expected_ids):
    """Produtor puro para futura integração, não instalada nesta etapa."""
    result = inventory(inventories)
    result['operational_states'] = project_inspects(inspect_records, expected_ids)
    require(expected_set(expected_ids) <= set(result['containers']), 'operacionais ausentes do inventário')
    return result


def protected(value):
    require(isinstance(value, dict) and set(value) == {'hashes', 'services'}, 'protected: hashes/services')
    require(isinstance(value['hashes'], dict) and bool(value['hashes']), 'protected.hashes: não vazio')
    require(all(isinstance(k, str) and k and identifier(v) for k, v in value['hashes'].items()), 'protected.hashes: formato')
    require(isinstance(value['services'], dict) and bool(value['services']), 'protected.services: não vazio')
    required = {'Id', 'ActiveState', 'SubState', 'MainPID', 'NRestarts', 'ExecMainStartTimestamp', 'Restart', 'FragmentPath'}
    for unit, props in value['services'].items():
        require(isinstance(unit, str) and unit and isinstance(props, dict) and required <= set(props), 'protected.services: campos')
        require(all(isinstance(props[k], str) and props[k] for k in required), 'protected.services: valores')
    return value


def verify_final(before_resources, before_protected, expected_ids, *, runtime_exit_code,
                 collect_inventory, collect_operational, collect_protected, check_cleanup):
    """Executa TODOS os checks independentes; callbacks nesta candidata são fakes.

    Ausência/erro => INCONCLUSIVE; diferença => FAIL; somente todos PASS e
    runtime_exit_code inteiro zero => PASS. Não reclassifica evidência histórica.
    """
    checks = {}

    def check(name, callback, validate):
        try:
            observed = callback()
            passed = validate(observed)
            require(type(passed) is bool, 'check: retorno booleano obrigatório')
            checks[name] = {'status': 'PASS' if passed else 'FAIL'}
        except Exception as exc:
            checks[name] = {'status': 'INCONCLUSIVE', 'error_type': type(exc).__name__}

    def same_inventory(after):
        return inventory(before_resources) == inventory(after)

    def same_operational(after):
        observed = project_inspects(after, expected_ids)
        require(isinstance(before_resources, dict) and 'operational_states' in before_resources,
                'baseline operacional ausente; não reconstruir retroativamente')
        baseline = operational_projection(before_resources['operational_states'], expected_ids)
        require(expected_set(expected_ids) <= set(inventory(before_resources)['containers']), 'baseline inventário operacional')
        return baseline == observed

    def same_protected(after):
        return protected(before_protected) == protected(after)

    def cleanup(value):
        require(type(value) is bool, 'cleanup: booleano obrigatório')
        return value

    check('inventory', collect_inventory, same_inventory)
    check('operational', collect_operational, same_operational)
    check('protected', collect_protected, same_protected)
    check('cleanup', check_cleanup, cleanup)
    runtime_ok = type(runtime_exit_code) is int and runtime_exit_code == 0
    passed = runtime_ok and all(x['status'] == 'PASS' for x in checks.values())
    return {'status': 'PASS' if passed else 'FAIL', 'exit_code': 0 if passed else 2,
            'runtime_exit_code': runtime_exit_code, 'checks': checks, 'g4': 'OPEN'}
