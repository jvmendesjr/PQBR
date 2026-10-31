"""Captura/compara somente arquivos autorizados; não coleta serviços."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HISTORY = HERE.parent / 'evidencias-f3-05-confirmacao-janela-20261017-B3-v2'
CANONICAL = [ROOT / 'docs' / (name + '.md') for name in ('REGRAS', 'SPEC', 'ARQUITETURA', 'TESTES', 'ROADMAP')]


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True)


def capture():
    paths = sorted(p for p in HISTORY.rglob('*') if p.is_file()) + CANONICAL
    return {'hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'git_status': git('status', '--short'),
            'git_numstat_allowed': git('diff', '--numstat', '--', 'src', 'tests', 'scripts', 'config', 'infra', 'docker', 'templates'),
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
        old_status = before['git_status'].splitlines()
        new_status = after['git_status'].splitlines()
        clean_status = lambda rows: [x for x in rows if x != new_line]
        checks = {'historical_and_canonical_hashes_unchanged': before['hashes'] == after['hashes'],
                  'preexisting_status_unchanged': clean_status(old_status) == clean_status(new_status),
                  'allowed_tracked_diff_numstat_unchanged': before['git_numstat_allowed'] == after['git_numstat_allowed'],
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
