"""Entrada exclusivamente para subprocessos da suíte sintética D1."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import json
import sqlite3
import duravel_d1 as d

def guard(event,args):
    if event.startswith(('socket.','subprocess.','ctypes.')) or event in ('os.system','os.exec','os.posix_spawn','os.spawn'):
        raise RuntimeError('D1: rede/execucao externa proibida no worker fake')
sys.addaudithook(guard)

def main():
    request=json.load(sys.stdin)
    base=request['base'];action=request['action'];pause=request.get('pause')
    if action=='init':
        out=d.initialize(base)
    elif action=='decide':
        out=d.CanonicalFakeAPI(base).persist(request.get('manifest',d.fixture()),request.get('session','board-linked-human'),pause,request.get('readonly',False))
    elif action=='consume':
        out=d.consume(base,request['receipt'],request.get('expected'),pause,request.get('readonly',False),request.get('fail_outbox',False),request.get('now',d.NOW),request.get('fail_full',False))
    elif action=='dispatch':
        out=d.dispatch(base,pause,request.get('receiver_readonly',False),request.get('source_readonly',False),request.get('now',d.NOW),request.get('ack_readonly',False))
    elif action=='receive':
        out=d.receive(base,request['command'],pause,request.get('readonly',False),request.get('now',d.NOW))
    elif action=='inspect':
        out=d.inspect(base)
    else:
        raise d.Blocked('acao_desconhecida')
    print(d.canonical(dict(ok=True,result=out)),flush=True)
try:
    main()
except (d.Blocked,sqlite3.Error) as e:
    print(d.canonical(dict(ok=False,error=type(e).__name__,reason=str(e),sqlite_code=getattr(e,'sqlite_errorname',None))),flush=True)
    sys.exit(3)
