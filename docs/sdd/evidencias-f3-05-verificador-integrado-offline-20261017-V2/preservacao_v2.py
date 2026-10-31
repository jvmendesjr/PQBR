"""Proveniência V2: somente arquivos autorizados e consultas Git offline."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SDD = HERE.parent
HISTORY = SDD / 'evidencias-f3-05-confirmacao-janela-20261017-B3-v2'
V1 = SDD / 'evidencias-f3-05-verificador-offline-20261017-V1'
CANONICAL = [ROOT / 'docs' / (name + '.md') for name in ('REGRAS', 'SPEC', 'ARQUITETURA', 'TESTES', 'ROADMAP')]
ALLOWED_DIFF = ['src', 'tests', 'scripts', 'config', 'infra', 'docker', 'templates'] + [str(p.relative_to(ROOT)) for p in CANONICAL]


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def capture():
    paths = sorted(p for base in (HISTORY, V1) for p in base.rglob('*') if p.is_file()) + CANONICAL
    return {'hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'git_status': git('status', '--short').decode(),
            'allowed_tracked_diff_sha256': hashlib.sha256(git('diff', '--', *ALLOWED_DIFF)).hexdigest(),
            'historical_orchestrator_exit': json.loads((HISTORY / 'final-result.json').read_text())['orchestratorExitCode'],
            'manifest_reuse_prohibited': json.loads((HISTORY / 'manifest.json').read_text())['reuse_prohibited']}


def main():
    if sys.argv[1:] == ['before']:
        with (HERE / 'preservacao-before.json').open('x') as stream:
            json.dump(capture(), stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    elif sys.argv[1:] == ['after']:
        before = json.loads((HERE / 'preservacao-before.json').read_text())
        after = capture()
        new_line = '?? ' + str(HERE.relative_to(ROOT)) + '/'
        def status_without_new(value):
            return [x for x in value.splitlines() if x != new_line]
        checks = {
            'historical_v1_and_canonical_hashes_unchanged': before['hashes'] == after['hashes'],
            'preexisting_status_unchanged': status_without_new(before['git_status']) == status_without_new(after['git_status']),
            'allowed_tracked_diff_unchanged': before['allowed_tracked_diff_sha256'] == after['allowed_tracked_diff_sha256'],
            'historical_exit_still_1': after['historical_orchestrator_exit'] == 1,
            'manifest_still_non_reusable': after['manifest_reuse_prohibited'] is True}
        report = {'status': 'PASS' if all(checks.values()) else 'FAIL', 'checks': checks,
                  'file_count': len(before['hashes']), 'after_git_status': after['git_status'], 'g4': 'OPEN'}
        with (HERE / 'preservacao-after.json').open('x') as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        print(json.dumps({k: value for k, value in report.items() if k != 'after_git_status'}, ensure_ascii=False))
        return 0 if all(checks.values()) else 1
    else:
        raise SystemExit('Use before ou after; somente arquivos locais.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
