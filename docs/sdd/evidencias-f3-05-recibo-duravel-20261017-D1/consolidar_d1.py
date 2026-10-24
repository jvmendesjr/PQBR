"""Consolidação D1: única alteração fora desta pasta é a nota F3-05 autorizada."""
from pathlib import Path
import hashlib
import json
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=Path('/home/pc/Workspace/PQBR')
result=json.loads((HERE/'execucao-final/resultado.json').read_text())
repeat=json.loads((HERE/'execucao-v3/resultado.json').read_text())
assert result['success'] and repeat['success']
assert result['tests']==repeat['tests']==44
assert result['subprocesses']==repeat['subprocesses']==409
assert result['killed_subprocesses']==repeat['killed_subprocesses']==9
note='  - Recibo durável sintético D1, 2026-10-17: **44/44 testes stdlib aprovados em duas rodadas finais**, cada uma com **409 subprocessos e 9 SIGKILL reais**, sem servidor/SDK Temporal ou containers. Dois bancos SQLite temporários separados: API canônica fake grava decisão + manifesto imutável + receipt em transação; consumo por chave única e CAS `pending→consumed` + outbox na mesma transação; receptor Temporal fake relê autorização, confere escopo e persiste dedup por receipt/escopo junto aos efeitos sintéticos. Quedas antes/depois dos commits, antes/depois do aceite/ACK, restart pendente/consumido, replay/concorrência, conflito de payload, receipt/ticket/revisão/pendentes stale, recusa/expiração, `SQLITE_READONLY`, `SQLITE_FULL` e lock real `SQLITE_BUSY` não repetem a terminal nem ampliam as pendentes autorizadas. Token de agente workflow nunca é sessão humana; board/vínculo Discord são fixtures confiáveis, com `human_only`, destinatário sintético já vinculado e `continuationPolicy=none`. [Código, resultados, reprodução e limites](sdd/evidencias-f3-05-recibo-duravel-20261017-D1/README.md) · [resultado](sdd/evidencias-f3-05-recibo-duravel-20261017-D1/execucao-final/resultado.json). **Limites:** hash é binding, não assinatura/auth; durabilidade observada contra queda de processo SQLite local não valida Postgres/Paperclip, queda de host, autenticação real ou receptor Temporal real; outbox pode reentregar e não há transação distribuída, fencing nem exactly-once de efeitos externos. 1.471 hashes preexistentes e quatro Workers/units/PIDs/inícios/restarts preservados; H2/H3, candidatas, supervisores, configuração e política de exceção técnica intactos. **F3-05/G4 aberto; F05-06 no-arm; F7-02/G7 e PQBR-114 pausados.** Sem credenciais, ticket/aviso/HTTP/CLI de integração real, restart/deploy/commit/push ou documentos restritos.\n'
roadmap=ROOT/'docs/ROADMAP.md'
old=(HERE/'roadmap-antes.txt').read_text()
assert roadmap.read_text()==old,'Roadmap mudou desde baseline; não sobrescrever'
anchor='  - [ ] **Revisão futura da política de exceção técnica na intervenção'
assert old.count(anchor)==1
(HERE/'nota-roadmap.txt').write_text(note)
roadmap.write_text(old.replace(anchor,note+anchor,1))
subprocess.run(['python3','-B',str(HERE/'preservar_d1.py'),'depois'],check=True)
# Nenhum processo worker de teste deve sobreviver às suítes.
probe=subprocess.run(['pgrep','-af','^/usr/bin/python3 -I -S -B .*/worker_d1.py$'],capture_output=True,text=True)
assert probe.returncode==1,probe.stdout
scratch=[str(p) for p in Path('/tmp').glob('pqbr-d1-*') if p.is_dir() and (p/'.synthetic-d1').exists()]
assert not scratch,scratch
summary=dict(synthetic_only=True,final=result,repeated_run=repeat['success'],preservation=json.loads((HERE/'preservacao.json').read_text()),test_workers_remaining=0,temporary_fixture_directories_remaining=0,roadmap_only_inserted_note=True,temporal_or_containers_started=False,auth_real=False,external_effects=False,production_enabled=False,g4='aberto',exception_policy='intacta',f05_06='no-arm',f7_02_g7='pausado',pqbr_114='pausado')
(HERE/'manifesto-final.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
paths=sorted(p for p in HERE.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts)
(HERE/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(HERE))+'\n' for p in paths))
print(json.dumps(dict(result='D1 consolidado',files=len(paths),readme=str(HERE/'README.md'),manifest=str(HERE/'manifesto-final.json')),ensure_ascii=False))
