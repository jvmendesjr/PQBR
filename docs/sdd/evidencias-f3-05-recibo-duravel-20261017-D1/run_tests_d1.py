"""Runner stdlib: saída nova obrigatória; nenhum container/Temporal ou integração real."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import json
import unittest
import platform
import sqlite3
import test_duravel_d1 as tests

class Result(unittest.TextTestResult):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw);self.outcomes=[]
    def addSuccess(self,t):
        super().addSuccess(t);self.outcomes.append(dict(test=t.id(),status='passed'))
    def addFailure(self,t,e):
        super().addFailure(t,e);self.outcomes.append(dict(test=t.id(),status='failed'))
    def addError(self,t,e):
        super().addError(t,e);self.outcomes.append(dict(test=t.id(),status='error'))

def guard(event,args):
    if event.startswith(('socket.','ctypes.')) or event in ('os.system','os.exec','os.spawn'):
        raise RuntimeError('D1: sem rede/shell')
    if event in ('subprocess.Popen','os.posix_spawn'):
        argv=args[1]
        expected=[sys.executable,'-I','-S','-B',str(Path(__file__).resolve().parent/'worker_d1.py')]
        if argv!=expected:
            raise RuntimeError('D1: apenas worker fixture em subprocesso')
sys.addaudithook(guard)

out=Path(sys.argv[1]).resolve()
out.mkdir(parents=False,exist_ok=False)
suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.DurabilityTests)
with (out/'testes.log').open('w') as log:
    result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Result).run(suite)
summary=dict(tests=result.testsRun,passed=sum(x['status']=='passed' for x in result.outcomes),failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),success=result.wasSuccessful(),python=platform.python_version(),sqlite=sqlite3.sqlite_version,outcomes=result.outcomes,subprocesses=len(tests.TRACE),killed_subprocesses=sum(e.get('signal')=='SIGKILL' for e in tests.TRACE),network='audit hook sem sockets; nao isolamento de kernel',synthetic_only=True,temporal_server=False)
(out/'resultado.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(out/'subprocessos.json').write_text(json.dumps(tests.TRACE,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='outcomes'},ensure_ascii=False))
if not result.wasSuccessful():
    print((out/'testes.log').read_text())
sys.exit(0 if result.wasSuccessful() else 1)
