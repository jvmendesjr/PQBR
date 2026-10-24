"""Somente leitura: hashes de código/evidências permitidas e propriedades systemd.
Não abre configuração, credenciais nem documentos restritos.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
ROOT=Path('/home/pc/Workspace/PQBR')
HERE=Path(__file__).resolve().parent
UNITS=('pqbr-temporal-worker.service','pqbr-camofox-worker.service',
       'pqbr-notebooklm-worker.service','pqbr-episodio-worker.service')

def snapshot():
    paths=[]
    for name in ('src','tests','docs/sdd','templates'):
        for p in (ROOT/name).rglob('*'):
            if p.is_file() and HERE not in p.parents and '__pycache__' not in p.parts:
                paths.append(p)
    workers={}
    for unit in UNITS:
        value=subprocess.check_output(['systemctl','--user','show',unit,
            '--property=Id,ActiveState,SubState,MainPID,NRestarts,ExecMainStartTimestamp,FragmentPath'],text=True)
        props=dict(x.split('=',1) for x in value.splitlines() if '=' in x)
        assert props['ActiveState']=='active',props
        workers[unit]=props
        paths.append(Path(props['FragmentPath']))
    return dict(hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))},workers=workers)

mode=sys.argv[1]
if mode=='antes':
    dest=HERE/'baseline.json'
    assert not dest.exists()
    dest.write_text(json.dumps(snapshot(),ensure_ascii=False,indent=2)+'\n')
    (HERE/'roadmap-antes.txt').write_bytes((ROOT/'docs/ROADMAP.md').read_bytes())
else:
    before=json.loads((HERE/'baseline.json').read_text());after=snapshot()
    old=(HERE/'roadmap-antes.txt').read_text();new=(ROOT/'docs/ROADMAP.md').read_text()
    note=(HERE/'nota-roadmap.txt').read_text() if (HERE/'nota-roadmap.txt').exists() else ''
    check=dict(arquivos_preexistentes_inalterados=before['hashes']==after['hashes'],
               workers_mesmos_pids_inicios_restarts=before['workers']==after['workers'],
               somente_nota_roadmap=new.replace(note,'',1)==old if note else new==old,
               quantidade_arquivos=len(before['hashes']),workers=after['workers'])
    (HERE/'preservacao.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n')
    assert all(check[k] for k in ('arquivos_preexistentes_inalterados','workers_mesmos_pids_inicios_restarts','somente_nota_roadmap')),check
    print(json.dumps(check,ensure_ascii=False,indent=2))
