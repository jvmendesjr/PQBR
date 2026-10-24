"""Verificação somente leitura dos arquivos anteriores e namespaces do teste."""
import hashlib
import json
import os
from pathlib import Path

root = Path('/home/pc/Workspace/PQBR')
out = root / 'docs/sdd/evidencias-f3-05-admissao-atomica-20261017'
before = json.loads((out / 'antes.json').read_text())
changed = [name for name, digest in before.items()
           if not (root / name).is_file()
           or hashlib.sha256((root / name).read_bytes()).hexdigest() != digest]
namespaces = {p.parent.name: p.read_text().strip() for p in out.glob('runtime-*/netns.txt')}
remaining = []
for process in Path('/proc').glob('[0-9]*'):
    try:
        ns = os.readlink(process / 'ns/net')
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        continue
    if ns in namespaces.values():
        remaining.append(dict(pid=int(process.name), namespace=ns))
summaries = [json.loads(p.read_text()) for p in (out / 'runtime-v2').glob('*.summary.json')]
new_files = [root / 'tests/workflows' / name for name in (
    'prototipo_admissao_atomica.py', 'test_f3_05_admissao_atomica_isolado.py',
    'run_f3_05_admissao_atomica_isolado.sh')]
result = dict(arquivos_anteriores_verificados=len(before), alterados=changed,
              namespaces=namespaces, processos_restantes=remaining,
              historicos_finais=len(summaries),
              replay_ok=sum(s['replay'] == 'ok' for s in summaries),
              estados={state: sum(s['estado'] == state for s in summaries)
                       for state in sorted({s['estado'] for s in summaries})},
              pending_activities=sum(s['pending_activities'] for s in summaries),
              novos_arquivos={str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in new_files})
(out / 'verificacao.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
assert not changed, 'Arquivo preexistente alterado'
assert not remaining, 'Processo de teste remanescente'
assert len(summaries) == 11 and all(s['replay'] == 'ok' for s in summaries)
assert result['pending_activities'] == 0
