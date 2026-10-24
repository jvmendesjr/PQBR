"""Testes offline da integração V2: somente fixtures sintéticas e arquivos locais."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import verificador_integrado as integrated
import verificador_offline as core
from test_verificador_offline import raw, inv, prot, A, B

HERE = Path(__file__).resolve().parent


class IntegratedTests(unittest.TestCase):
    def setUp(self):
        self.guard_process = patch.object(subprocess, 'Popen', side_effect=AssertionError('subprocess proibido'))
        self.guard_socket = patch.object(socket, 'socket', side_effect=AssertionError('rede proibida'))
        self.guard_process.start()
        self.guard_socket.start()
        self.addCleanup(self.guard_process.stop)
        self.addCleanup(self.guard_socket.stop)

    def baseline(self):
        return integrated.prepare_baseline(inv(), [raw()], prot(), [A])

    def callbacks(self, overrides=None):
        values = {'inventory': inv(), 'inspects': [raw()], 'protected': prot(), 'cleanup': True}
        values.update(overrides or {})
        calls = []
        def cb(name):
            def call():
                calls.append(name)
                value = values[name]
                if isinstance(value, Exception):
                    raise value
                return deepcopy(value)
            return call
        return calls, dict(read_inventory=cb('inventory'), read_inspects=cb('inspects'),
                            read_protected=cb('protected'), read_cleanup=cb('cleanup'))

    def test_prepare_baseline_roundtrip_does_not_mutate_inputs(self):
        inventories, inspects, protection = inv(), [raw()], prot()
        original = deepcopy((inventories, inspects, protection))
        result = integrated.prepare_baseline(inventories, inspects, protection, [A])
        self.assertEqual((inventories, inspects, protection), original)
        self.assertEqual(result['resources']['containers'], [A])
        self.assertEqual(result['protected'], protection)
        result['protected']['hashes']['fixture.py'] = 'e' * 64
        self.assertEqual(protection, original[2])

    def test_prepare_baseline_strict_failure(self):
        for args in (({}, [raw()], prot(), [A]), (inv(), [], prot(), [A]),
                     (inv(), [raw()], {}, [A])):
            with self.subTest(args=args):
                with self.assertRaises(core.ContractError):
                    integrated.prepare_baseline(*deepcopy(args))

    def test_file_json_roundtrip_pass_synthetic_only(self):
        baseline = self.baseline()
        with tempfile.TemporaryDirectory() as td:
            paths = {}
            data = {'resources': baseline['resources'], 'protected': baseline['protected'],
                    'inventory': inv(), 'inspects': [raw()], 'after_protected': prot(), 'cleanup': True}
            for name, value in data.items():
                path = Path(td) / (name + '.json')
                path.write_text(json.dumps(value), encoding='utf-8')
                paths[name] = path
            report = integrated.verify_files(baseline_resources=paths['resources'],
                baseline_protected=paths['protected'], after_inventory=paths['inventory'],
                after_inspects=paths['inspects'], after_protected=paths['after_protected'],
                cleanup_result=paths['cleanup'], expected_ids=[A], runtime_exit_code=0)
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['checks']['snapshot_contract']['status'], 'PASS')
        self.assertEqual(report['mode'], 'OFFLINE_ONLY')

    def test_missing_and_malformed_baselines_inconclusive_independent_checks_run(self):
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / 'missing.json'
            malformed = Path(td) / 'bad.json'
            malformed.write_text('{broken', encoding='utf-8')
            files = self._write_after(td)
            for resources, protected in ((missing, missing), (malformed, malformed)):
                report = integrated.verify_files(baseline_resources=resources, baseline_protected=protected,
                    after_inventory=files['inventory'], after_inspects=files['inspects'],
                    after_protected=files['protected'], cleanup_result=files['cleanup'],
                    expected_ids=[A], runtime_exit_code=0)
                self.assertEqual(report['checks']['inventory']['status'], 'INCONCLUSIVE')
                self.assertEqual(report['checks']['operational']['status'], 'INCONCLUSIVE')
                self.assertEqual(report['checks']['protected']['status'], 'INCONCLUSIVE')
                self.assertEqual(report['checks']['cleanup']['status'], 'PASS')
                self.assertEqual(report['checks']['snapshot_contract']['status'], 'PASS')
                self.assertEqual(report['status'], 'FAIL')
                self.assertEqual(set(report['baseline_acquisition']), {'baseline_resources', 'baseline_protected'})

    def _write_after(self, td):
        values = {'inventory': inv(), 'inspects': [raw()], 'protected': prot(), 'cleanup': True}
        paths = {}
        for name, value in values.items():
            path = Path(td) / ('after-' + name + '.json')
            path.write_text(json.dumps(value), encoding='utf-8')
            paths[name] = path
        return paths

    def test_each_read_callback_exception_attempts_all_four(self):
        for failed in ('inventory', 'inspects', 'protected', 'cleanup'):
            with self.subTest(failed=failed):
                calls, callbacks = self.callbacks({failed: OSError('synthetic')})
                baseline = self.baseline()
                report = integrated.verify_inputs(baseline['resources'], baseline['protected'], [A],
                                                  runtime_exit_code=0, **callbacks)
                self.assertEqual(calls, ['inventory', 'inspects', 'protected', 'cleanup'])
                self.assertEqual(report['checks'][failed if failed not in ('inspects',) else 'operational']['status'], 'INCONCLUSIVE')
                self.assertEqual(report['checks']['snapshot_contract']['status'], 'INCONCLUSIVE' if failed in ('inventory', 'inspects') else 'PASS')

    def test_invalid_or_missing_after_files_by_category(self):
        baseline = self.baseline()
        categories = {'inventory': 'after_inventory', 'inspects': 'after_inspects',
                      'protected': 'after_protected', 'cleanup': 'cleanup_result'}
        with tempfile.TemporaryDirectory() as td:
            for category, parameter in categories.items():
                for invalid in (True, False):
                    with self.subTest(category=category, invalid=invalid):
                        paths = self._write_after(td)
                        path = Path(td) / (category + ('-bad' if invalid else '-missing') + '.json')
                        if invalid:
                            path.write_text('{', encoding='utf-8')
                        else:
                            path.unlink(missing_ok=True)
                        values = {'after_inventory': paths['inventory'], 'after_inspects': paths['inspects'],
                                  'after_protected': paths['protected'], 'cleanup_result': paths['cleanup']}
                        values[parameter] = path
                        report = integrated.verify_files(baseline_resources=self._write_baseline(td, baseline, 'r'),
                            baseline_protected=self._write_baseline(td, baseline, 'p'), **values,
                            expected_ids=[A], runtime_exit_code=0)
                        check = {'inventory':'inventory','inspects':'operational','protected':'protected','cleanup':'cleanup'}[category]
                        self.assertEqual(report['checks'][check]['status'], 'INCONCLUSIVE')
                        self.assertEqual(report['status'], 'FAIL')
                        self.assertEqual(report['checks']['snapshot_contract']['status'],
                                         'INCONCLUSIVE' if category in ('inventory', 'inspects') else 'PASS')

    def _write_baseline(self, td, baseline, suffix):
        path = Path(td) / ('baseline-' + suffix + '.json')
        path.write_text(json.dumps(baseline['resources' if suffix == 'r' else 'protected']), encoding='utf-8')
        return path

    def test_runtime_exit_one_never_passes(self):
        baseline = self.baseline()
        calls, callbacks = self.callbacks()
        report = integrated.verify_inputs(baseline['resources'], baseline['protected'], [A],
                                          runtime_exit_code=1, **callbacks)
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(report['exit_code'], 2)
        self.assertEqual(calls, ['inventory', 'inspects', 'protected', 'cleanup'])

    def test_operational_baseline_missing_invalid_never_passes(self):
        for state in ('absent', None, [], {}, [{'id': A}]):
            with self.subTest(state=state):
                baseline = self.baseline()
                if state == 'absent':
                    del baseline['resources']['operational_states']
                else:
                    baseline['resources']['operational_states'] = state
                calls, callbacks = self.callbacks()
                report = integrated.verify_inputs(baseline['resources'], baseline['protected'], [A],
                                                  runtime_exit_code=0, **callbacks)
                self.assertEqual(report['checks']['operational']['status'], 'INCONCLUSIVE')
                self.assertEqual(report['checks']['protected']['status'], 'PASS')
                self.assertEqual(report['checks']['cleanup']['status'], 'PASS')
                self.assertEqual(report['status'], 'FAIL')
                self.assertEqual(calls, ['inventory', 'inspects', 'protected', 'cleanup'])

    def test_simultaneous_callback_errors_all_recorded(self):
        baseline = self.baseline()
        calls, callbacks = self.callbacks({name: OSError('fixture')
                                          for name in ('inventory', 'inspects', 'protected', 'cleanup')})
        report = integrated.verify_inputs(baseline['resources'], baseline['protected'], [A],
                                          runtime_exit_code=0, **callbacks)
        self.assertEqual(calls, ['inventory', 'inspects', 'protected', 'cleanup'])
        self.assertTrue(all(check['status'] == 'INCONCLUSIVE' for check in report['checks'].values()))
        self.assertEqual(report['status'], 'FAIL')
        self.assertNotIn('after_snapshot', report)

    def test_historical_resources_not_reconstructed(self):
        history = HERE.parent / 'evidencias-f3-05-confirmacao-janela-20261017-B3-v2'
        baseline = json.loads((history / 'runtime-run-B3121/resources-before.json').read_text())
        original = deepcopy(baseline)
        calls, callbacks = self.callbacks({'inventory': baseline})
        report = integrated.verify_inputs(baseline, prot(), [A], runtime_exit_code=1, **callbacks)
        self.assertEqual(report['checks']['operational']['status'], 'INCONCLUSIVE')
        self.assertEqual(report['checks']['protected']['status'], 'PASS')
        self.assertEqual(report['runtime_exit_code'], 1)
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(baseline, original)
        self.assertNotIn('operational_states', baseline)

    def test_snapshot_contract_requires_expected_ids_in_after_inventory(self):
        baseline = self.baseline()
        changed = inv()
        changed['containers'] = [B]
        calls, callbacks = self.callbacks({'inventory': changed})
        report = integrated.verify_inputs(baseline['resources'], baseline['protected'], [A],
                                          runtime_exit_code=0, **callbacks)
        self.assertEqual(report['checks']['snapshot_contract']['status'], 'INCONCLUSIVE')
        self.assertNotIn('after_snapshot', report)
        self.assertEqual(calls, ['inventory', 'inspects', 'protected', 'cleanup'])

    def test_malformed_post_snapshot_never_emits_empty_after_snapshot(self):
        baseline = self.baseline()
        for overrides in ({'inspects': []}, {'inventory': {'containers': [A], 'networks': []}}):
            with self.subTest(overrides=overrides):
                calls, callbacks = self.callbacks(overrides)
                report = integrated.verify_inputs(baseline['resources'], baseline['protected'], [A],
                                                  runtime_exit_code=0, **callbacks)
                self.assertEqual(report['checks']['snapshot_contract']['status'], 'INCONCLUSIVE')
                self.assertNotIn('after_snapshot', report)

    def test_static_module_has_no_cli_runtime_imports_or_top_level_calls(self):
        source = (HERE / 'verificador_integrado.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        forbidden = {'argparse', 'subprocess', 'socket', 'docker', 'run_pqbr121'}
        for node in tree.body:
            self.assertIsInstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.FunctionDef, ast.Expr))
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = ([alias.name for alias in node.names] if isinstance(node, ast.Import)
                         else [node.module or ''])
                self.assertFalse(any(any(term in name.lower() for term in forbidden) for name in names))
            if isinstance(node, ast.Expr):
                self.assertIsInstance(node.value, ast.Constant)
            if isinstance(node, ast.Assign):
                self.assertFalse(any(isinstance(child, ast.Call) for child in ast.walk(node)))
        self.assertNotIn('run_pqbr121', source)


if __name__ == '__main__':
    unittest.main(verbosity=2)
