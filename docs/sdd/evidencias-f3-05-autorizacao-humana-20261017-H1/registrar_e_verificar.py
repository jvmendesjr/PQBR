"""Executar somente no PC, após testes. Única edição preexistente: nota F3-05."""
import hashlib
import json
from pathlib import Path
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
assert ROOT == Path('/home/pc/Workspace/PQBR'), ROOT
baseline = json.loads((BASE / 'baseline.json').read_text())
roadmap = ROOT / 'docs/ROADMAP.md'
original = roadmap.read_bytes()
sha = lambda data: hashlib.sha256(data).hexdigest()
if sha(original) != baseline['files']['docs/ROADMAP.md']:
    raise SystemExit('Roadmap mudou desde baseline; nenhuma escrita realizada')
result = json.loads((BASE / 'execucao-pc/resultado.json').read_text())
assert result['sucesso'] and result['testes'] == 57 and not result['sdk_temporal_importado']
nota = ('  - Autorização humana em protótipo offline separado, 2026-10-17: **57/57 testes E2E com fake Paperclip, fake Discord e fake supervisor Temporal**, sem servidor/SDK Temporal nem efeito externo. Ticket como registro canônico; despacho autenticado sintético por painel ou Discord com allowlist configurável por canal, decisão/ator/timestamp/revisão/idempotência e receipt persistidos antes do resume. Recusa/expiração, identidade ausente/não autorizada, ticket/receipt ausente ou divergente, revisão/falha/pendentes stale e operações novas/falhas/concluídas não liberam retomada. Retry explícito após resposta perdida deduplica decisão e consumo dos pendentes; aviso Discord indisponível não inventa aprovação. [Código, evidência e limites](sdd/evidencias-f3-05-autorizacao-humana-20261017-H1/README.md) · [resultado no PC](sdd/evidencias-f3-05-autorizacao-humana-20261017-H1/execucao-pc/resultado.json). **Limites:** apenas memória/fakes, sem autenticação real, durabilidade após crash, integração, replay Temporal, fencing ou exactly-once externo; nenhuma identidade real presumida e nada ligado aos Workers persistentes. Política operacional e arquivos preexistentes preservados, exceto esta nota; sem tickets/avisos reais, restart, deploy, publicação, commit/push. **F3-05/G4 aberto; F7-02/G7 e PQBR-114 pausados; F05-06 no-arm.**\n').encode()
marker = '  - [ ] **Revisão futura da política de exceção técnica na intervenção'.encode()
assert original.count(marker) == 1
updated = original.replace(marker, nota + marker, 1)
roadmap.write_bytes(updated)
(BASE / 'nota-roadmap.txt').write_bytes(nota)

changed, missing = [], []
for path, expected in baseline['files'].items():
    file = ROOT / path
    if not file.is_file():
        missing.append(path)
    elif path == 'docs/ROADMAP.md':
        assert file.read_bytes() == updated
        assert file.read_bytes().replace(nota, b'', 1) == original
    elif sha(file.read_bytes()) != expected:
        changed.append(path)
props = ['MainPID','ActiveState','SubState','NRestarts','Restart',
         'ExecMainStartTimestamp','FragmentPath','DropInPaths']
workers = {s: subprocess.check_output(['systemctl','--user','show',s] +
           ['--property=' + p for p in props]).decode() for s in baseline['workers']}
unit_changes = [path for path, expected in baseline['units'].items()
                if not Path(path).is_file() or sha(Path(path).read_bytes()) != expected]
files = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],
                                cwd=ROOT).decode().split('\0')
added = sorted(set(p for p in files if p) - set(baseline['files']))
allowed = str(BASE.relative_to(ROOT)) + '/'
unexpected = [p for p in added if not p.startswith(allowed)]
check = subprocess.run(['git','diff','--check','--','docs/ROADMAP.md'], cwd=ROOT,
                       capture_output=True, text=True)
report = {
    'arquivos_preexistentes_verificados': len(baseline['files']),
    'alterados_fora_roadmap': changed, 'ausentes': missing,
    'roadmap_apenas_insercao_exata': roadmap.read_bytes().replace(nota, b'', 1) == original,
    'roadmap_hash_antes': sha(original), 'roadmap_hash_depois': sha(updated),
    'workers_antes': baseline['workers'], 'workers_depois': workers,
    'workers_mesmos_pids_inicio_restarts_estado_e_restart': workers == baseline['workers'],
    'quatro_workers_ativos_restart_always': len(workers) == 4 and all(
        'ActiveState=active\n' in text and 'Restart=always\n' in text for text in workers.values()),
    'units_alteradas': unit_changes,
    'adicoes_fora_pasta_evidencia': unexpected,
    'git_diff_check_roadmap': {'codigo': check.returncode, 'saida': check.stdout + check.stderr},
    'somente_systemctl_show_leitura': True,
}
report['sucesso'] = (not changed and not missing and not unit_changes and not unexpected
                     and report['roadmap_apenas_insercao_exata']
                     and report['workers_mesmos_pids_inicio_restarts_estado_e_restart']
                     and report['quatro_workers_ativos_restart_always'] and check.returncode == 0)
(BASE / 'preservacao.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if not k.startswith('workers_')}, indent=2))
raise SystemExit(0 if report['sucesso'] else 1)
