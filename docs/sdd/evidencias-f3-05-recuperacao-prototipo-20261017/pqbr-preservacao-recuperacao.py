"""Somente hashes de código/testes e documentos permitidos; nenhuma leitura de segredos/restritos."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT = Path('/home/pc/Workspace/PQBR')
OUT = Path(sys.argv[2])
services = ['pqbr-camofox-worker.service', 'pqbr-episodio-worker.service',
            'pqbr-notebooklm-worker.service', 'pqbr-temporal-worker.service', 'pqbr-camofox.service']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def state():
    result = {}
    for name in services:
        p = subprocess.run(['systemctl', '--user', 'show', name, '--property=Id,ActiveState,SubState,MainPID,ExecMainStartTimestampMonotonic,NRestarts,Restart,FragmentPath'],
                           check=True, text=True, capture_output=True)
        data = dict(line.split('=', 1) for line in p.stdout.splitlines() if '=' in line)
        fragment = Path(data['FragmentPath']) if data.get('FragmentPath') else None
        if fragment and fragment.is_file():
            data['unit_sha256'] = sha(fragment)
        result[name] = data
    return result

if sys.argv[1] == 'antes':
    OUT.mkdir(exist_ok=False)
    paths = [p for folder in ('src', 'tests') for p in (ROOT / folder).rglob('*.py') if '.venv' not in p.parts]
    paths += [ROOT / name for name in ('AGENTS.md', 'docs/README.md', 'docs/REGRAS.md',
              'docs/SPEC.md', 'docs/ARQUITETURA.md', 'docs/TESTES.md', 'docs/ROADMAP.md',
              'docs/sdd/f3-05-integracao-candidata-20261017.md')]
    data = dict(hashes={str(p.relative_to(ROOT)): sha(p) for p in paths}, services=state())
    data['git_status'] = subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain'], text=True)
    (OUT / 'baseline.json').write_text(json.dumps(data, indent=2) + '\n')
    print('Baseline criado; arquivos permitidos:', len(data['hashes']))
else:
    before = json.loads((OUT / 'baseline.json').read_text())
    changed = [name for name, digest in before['hashes'].items() if sha(ROOT / name) != digest]
    after = state()
    result = dict(arquivos_preexistentes_alterados=changed,
                  servicos_inalterados=after == before['services'],
                  servicos_antes=before['services'], servicos_depois=after,
                  git_status_depois=subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain'], text=True))
    (OUT / 'preservation-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('arquivos_preexistentes_alterados', 'servicos_inalterados')}))
    if changed or not result['servicos_inalterados']:
        sys.exit(1)
