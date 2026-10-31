"""Somente unittest/stdlib e leitura de JSON histórico. Nunca importa o runner."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import socket
import subprocess
import unittest
from unittest.mock import patch

import verificador_offline as v

HERE = Path(__file__).resolve().parent
HISTORY = HERE.parent / 'evidencias-f3-05-confirmacao-janela-20261017-B3-v2'
A, B = 'a' * 64, 'b' * 64


def raw(cid=A, name='/fixture-ONLY'):
    return {'Id': cid, 'Name': name, 'State': {'Status': 'running', 'Pid': 123,
            'StartedAt': '2026-10-17T20:39:06.140919400Z'}}


def inv():
    return {'containers': [A], 'networks': ['fixture-network'], 'volumes': []}


def prot():
    # Valores sintéticos, NÃO estado observado do PC.
    return {'hashes': {'fixture.py': 'f' * 64}, 'services': {
        name: {'Id': name, 'ActiveState': 'active', 'SubState': 'running',
               'MainPID': '123', 'NRestarts': '0', 'ExecMainStartTimestamp': 'fixture-start',
               'Restart': 'always', 'FragmentPath': '/fixture/' + name}
        for name in ('pqbr-temporal-worker.service', 'pqbr-camofox-worker.service',
                     'pqbr-notebooklm-worker.service', 'pqbr-episodio-worker.service')}}


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.guard_process = patch.object(subprocess, 'Popen', side_effect=AssertionError('subprocess proibido'))
        self.guard_socket = patch.object(socket, 'socket', side_effect=AssertionError('rede proibida'))
        self.guard_process.start()
        self.guard_socket.start()
        self.addCleanup(self.guard_process.stop)
        self.addCleanup(self.guard_socket.stop)

    def final(self, before=None, before_protected=None, overrides=None, runtime=0):
        self.calls = []
        outputs = {'inventory': inv(), 'operational': [raw()], 'protected': prot(), 'cleanup': True}
        if overrides:
            outputs.update(overrides)
        def callback(name):
            def collect():
                self.calls.append(name)
                value = outputs[name]
                if isinstance(value, Exception):
                    raise value
                return deepcopy(value)
            return collect
        return v.verify_final(v.snapshot_resources(inv(), [raw()], [A]) if before is None else before,
                              prot() if before_protected is None else before_protected, [A],
                              runtime_exit_code=runtime, collect_inventory=callback('inventory'),
                              collect_operational=callback('operational'),
                              collect_protected=callback('protected'), check_cleanup=callback('cleanup'))

    def test_producer_consumer_pass(self):
        report = self.final()
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['exit_code'], 0)
        self.assertEqual(report['g4'], 'OPEN')

    def test_projection_uses_observed_fields_only(self):
        source = raw()
        source['unrelated'] = 'ignored'
        projection = v.project_inspects([source], [A])
        self.assertEqual(set(projection[0]), v.FIELDS)
        self.assertEqual(projection[0]['pid'], 123)
        self.assertNotIn('operational_states', inv())

    def test_order_is_deterministic_no_input_mutation(self):
        records = [raw(B, '/fixture-B'), raw(A, '/fixture-A')]
        original = deepcopy(records)
        first = v.snapshot_resources({'containers': [B, A], 'networks': [], 'volumes': []}, records, [B, A])
        second = v.snapshot_resources({'containers': [A, B], 'networks': [], 'volumes': []}, records[::-1], [A, B])
        self.assertEqual(first, second)
        self.assertEqual(records, original)

    def test_missing_operational_baseline_never_default_pass(self):
        report = self.final(before=inv())
        self.assertEqual(report['checks']['operational']['status'], 'INCONCLUSIVE')
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(self.calls, ['inventory', 'operational', 'protected', 'cleanup'])
        self.assertEqual(report['checks']['protected']['status'], 'PASS')

    def test_each_callback_failure_does_not_skip_other_checks(self):
        for name in ('inventory', 'operational', 'protected', 'cleanup'):
            with self.subTest(name=name):
                report = self.final(overrides={name: OSError('simulated')})
                self.assertEqual(report['checks'][name]['status'], 'INCONCLUSIVE')
                self.assertEqual(report['exit_code'], 2)
                self.assertEqual(len(self.calls), 4)
                self.assertEqual(sum(x['status'] == 'PASS' for x in report['checks'].values()), 3)

    def test_operational_change_detected(self):
        for key, value in (('Pid', 124), ('StartedAt', '2026-10-17T21:00:00Z'), ('Status', 'paused')):
            with self.subTest(key=key):
                changed = raw()
                changed['State'][key] = value
                report = self.final(overrides={'operational': [changed]})
                self.assertEqual(report['checks']['operational']['status'], 'FAIL')
                self.assertEqual(report['status'], 'FAIL')

    def test_inventory_added_removed_detected(self):
        for containers in ([], [A, B]):
            with self.subTest(containers=containers):
                changed = inv()
                changed['containers'] = containers
                self.assertEqual(self.final(overrides={'inventory': changed})['checks']['inventory']['status'], 'FAIL')

    def test_protected_hash_and_worker_changes(self):
        for key in ('hash', 'MainPID', 'NRestarts', 'ExecMainStartTimestamp'):
            with self.subTest(key=key):
                changed = prot()
                if key == 'hash':
                    changed['hashes']['fixture.py'] = 'e' * 64
                else:
                    changed['services']['pqbr-temporal-worker.service'][key] = 'changed'
                self.assertEqual(self.final(overrides={'protected': changed})['checks']['protected']['status'], 'FAIL')

    def test_cleanup_not_truthiness(self):
        self.assertEqual(self.final(overrides={'cleanup': False})['checks']['cleanup']['status'], 'FAIL')
        for value in (None, {}, [], 1, 'PASS'):
            with self.subTest(value=value):
                self.assertEqual(self.final(overrides={'cleanup': value})['checks']['cleanup']['status'], 'INCONCLUSIVE')

    def test_runtime_failure_cannot_be_overwritten(self):
        for code in (1, 2, None, False, '0'):
            with self.subTest(code=code):
                report = self.final(runtime=code)
                self.assertEqual(report['status'], 'FAIL')
                self.assertEqual(report['runtime_exit_code'], code)

    def test_malformed_projection_rejected(self):
        good = v.project_inspects([raw()], [A])[0]
        variants = [None, [], {}, [good, good]]
        for key, value in (('id', 'abc'), ('name', ''), ('pid', True), ('pid', -1),
                           ('pid', 0), ('status', 'unknown'), ('startedAt', 'invalid'),
                           ('startedAt', '2026-10-17T21:00:00')):
            item = dict(good)
            item[key] = value
            variants.append([item])
        for key in good:
            item = dict(good)
            del item[key]
            variants.append([item])
        for rows in variants:
            with self.subTest(rows=rows):
                with self.assertRaises(v.ContractError):
                    v.operational_projection(rows, [A])

    def test_expected_ids_explicit_complete_unique(self):
        for expected in ([], None, [A, A], ['a' * 12], [B]):
            with self.subTest(expected=expected):
                with self.assertRaises(v.ContractError):
                    v.project_inspects([raw()], expected)

    def test_missing_inspect_fields_no_defaults(self):
        for record in ({}, {'Id': A, 'Name': '/fixture', 'State': {}}, {'Id': A, 'Name': '/fixture', 'State': None}):
            with self.subTest(record=record):
                with self.assertRaises(v.ContractError):
                    v.project_inspects([record], [A])

    def test_missing_or_duplicate_inventory_rejected(self):
        for value in ({}, {'containers': [], 'networks': []}, {'containers': [A, A], 'networks': [], 'volumes': []}):
            with self.subTest(value=value):
                with self.assertRaises(v.ContractError):
                    v.inventory(value)

    def test_operational_must_be_in_inventory(self):
        empty = inv()
        empty['containers'] = []
        with self.assertRaises(v.ContractError):
            v.snapshot_resources(empty, [raw()], [A])

    def test_protected_missing_data_not_equal_empty(self):
        for value in ({}, {'hashes': {}, 'services': {}}, {'hashes': {'a': 'f'*64}, 'services': {'unit': {}}}):
            with self.subTest(value=value):
                report = self.final(before_protected=value, overrides={'protected': value})
                self.assertEqual(report['checks']['protected']['status'], 'INCONCLUSIVE')
                self.assertEqual(report['status'], 'FAIL')

    def test_real_historical_inventory_remains_inconclusive(self):
        baseline = json.loads((HISTORY / 'runtime-run-B3121/resources-before.json').read_text())
        self.assertEqual(set(baseline), set(v.KINDS))
        report = self.final(before=baseline, overrides={'inventory': baseline})
        self.assertEqual(report['checks']['operational']['status'], 'INCONCLUSIVE')
        self.assertEqual(report['checks']['protected']['status'], 'PASS')
        self.assertEqual(report['status'], 'FAIL')

    def test_real_inspect_shape_without_claiming_operational_baseline(self):
        # Inspect é DESCARTÁVEL histórico: valida somente formato, não preservação.
        record = json.loads((HISTORY / 'runtime-run-B3121/inspect-final-pqbr-f305-B3121-server.json').read_text())
        projection = v.project_inspects([record], [record['Id']])
        self.assertEqual(projection[0]['startedAt'], record['State']['StartedAt'])
        self.assertEqual(projection[0]['name'], record['Name'])
        self.assertEqual(projection[0]['pid'], record['State']['Pid'])

    def test_real_protected_shape(self):
        snapshot = json.loads((HISTORY / 'runtime-run-B3121/protected-before.json').read_text())
        self.assertEqual(v.protected(snapshot), snapshot)
        self.assertEqual(len(snapshot['services']), 4)

    def test_static_no_effect_imports_or_top_level_calls(self):
        tree = ast.parse((HERE / 'verificador_offline.py').read_text())
        for node in tree.body:
            self.assertIsInstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.ClassDef, ast.FunctionDef, ast.Expr))
            if isinstance(node, ast.Import):
                self.assertEqual([x.name for x in node.names], ['re'])
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.module, 'datetime')
            elif isinstance(node, ast.Expr):
                self.assertIsInstance(node.value, ast.Constant)
            elif isinstance(node, ast.Assign):
                self.assertFalse(any(isinstance(x, ast.Call) for x in ast.walk(node)))
        self.assertNotIn('run_pqbr121', (HERE / 'verificador_offline.py').read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
