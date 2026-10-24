"""Preservação somente leitura fora da pasta D1; não abre documentos restritos."""
from pathlib import Path
import hashlib, json, subprocess, sys
ROOT=Path('/home/pc/Workspace/PQBR')
HERE=Path(__file__).resolve().parent
UNITS=('pqbr-temporal-worker.service','pqbr-camofox-worker.service','pqbr-notebooklm-worker.service','pqbr-episodio-worker.service')
def snapshot():
    paths=[]
    for name in ('src','tests','docs/sdd','templates','scripts'):
        for p in (ROOT/name).rglob('*'):
            if p.is_file() and HERE not in p.parents and '__pycache__' not in p.parts:
                paths.append(p)
    # Configuração e demais docs: só metadados; nenhum conteúdo ou credencial lido.
    metadata={}
    for name in ('config','docs'):
        for p in (ROOT/name).rglob('*'):
            if p.is_file() and HERE not in p.parents and p != ROOT/'docs/ROADMAP.md':
                s=p.stat();metadata[str(p)]=[s.st_size,s.st_mtime_ns,s.st_mode]
    workers={}
    for unit in UNITS:
        raw=subprocess.check_output(['systemctl','--user','show',unit,'--property=Id,ActiveState,SubState,MainPID,NRestarts,ExecMainStartTimestamp,FragmentPath'],text=True)
        props=dict(x.split('=',1) for x in raw.splitlines() if '=' in x)
        assert props['ActiveState']=='active',props
        workers[unit]=props
        paths.append(Path(props['FragmentPath']))
    return dict(hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))},metadata=metadata,workers=workers)
if __name__=='__main__':
    if sys.argv[1]=='antes':
        assert not (HERE/'baseline.json').exists()
        (HERE/'baseline.json').write_text(json.dumps(snapshot(),ensure_ascii=False,indent=2)+'\n')
        (HERE/'roadmap-antes.txt').write_bytes((ROOT/'docs/ROADMAP.md').read_bytes())
    else:
        before=json.loads((HERE/'baseline.json').read_text());after=snapshot()
        old=(HERE/'roadmap-antes.txt').read_text();new=(ROOT/'docs/ROADMAP.md').read_text()
        note=(HERE/'nota-roadmap.txt').read_text() if (HERE/'nota-roadmap.txt').exists() else ''
        check=dict(arquivos_hash_inalterados=before['hashes']==after['hashes'],metadados_inalterados=before['metadata']==after['metadata'],workers_pids_inicios_restarts_inalterados=before['workers']==after['workers'],somente_nota_roadmap=new.replace(note,'',1)==old if note else new==old,quantidade_hashes=len(before['hashes']),quantidade_metadados=len(before['metadata']),workers=after['workers'])
        (HERE/'preservacao.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n')
        assert all(check[k] for k in ('arquivos_hash_inalterados','metadados_inalterados','workers_pids_inicios_restarts_inalterados','somente_nota_roadmap')),check
        print(json.dumps(check,ensure_ascii=False,indent=2))
