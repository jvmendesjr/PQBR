"""Somente no PC: verifica preservação e insere UMA nota F3-05; nenhuma chamada de integração."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
if ROOT != Path('/home/pc/Workspace/PQBR'):
    raise SystemExit('Verificador restrito ao checkout autorizado')
baseline = json.loads((BASE / 'baseline.json').read_text())
resultado = json.loads((BASE / 'execucao-pc/resultado.json').read_text())
if not (resultado['sucesso'] and resultado['testes'] == 104 and resultado['falhas'] == 0
        and resultado['erros'] == 0 and resultado['pulados'] == 0
        and not resultado['pqbr_ou_temporal_importado']):
    raise SystemExit('Resultado offline ausente ou divergente; roadmap intacto')

sha = lambda b: sha256(b).hexdigest()
roadmap = ROOT / 'docs/ROADMAP.md'
original = roadmap.read_bytes()
if sha(original) != baseline['sha256']['docs/ROADMAP.md']:
    raise SystemExit('Roadmap mudou desde baseline; preservar alteração e não escrever')

alterados, ausentes = [], []
for nome, esperado in baseline['sha256'].items():
    p = ROOT / nome
    if not p.is_file():
        ausentes.append(nome)
    elif sha(p.read_bytes()) != esperado:
        alterados.append(nome)
if alterados or ausentes:
    raise SystemExit('Preexistentes divergentes; nenhuma nota escrita: ' + repr((alterados, ausentes)))

workers_antes = json.loads((BASE / 'workers-antes.json').read_text())
props = ['MainPID', 'ActiveState', 'SubState', 'NRestarts', 'ExecMainStartTimestamp',
         'FragmentPath', 'DropInPaths']
workers_depois = {s: subprocess.check_output(['systemctl', '--user', 'show', s]
                  + ['--property=' + p for p in props], text=True) for s in workers_antes}
if workers_antes != workers_depois:
    raise SystemExit('Estado de Worker mudou; nenhuma nota escrita')

status = subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True)
prefixo = str(BASE.relative_to(ROOT))
def status_sem_evidencia(texto):
    return sorted(linha for linha in texto.splitlines() if linha[3:].rstrip('/') != prefixo
                  and not linha[3:].startswith(prefixo + '/'))
if status_sem_evidencia(status) != status_sem_evidencia(baseline['git_status']):
    raise SystemExit('Status externo à evidência mudou; preservar e não escrever')

nota = ('  - Adaptador isolado da confirmação canônica Paperclip, 2026-10-17: **104/104 testes com portas fake Paperclip, Discord/vínculo existente e supervisor**, sem HTTP, CLI mutável, ticket/aviso ou comando Temporal real. `request_confirmation` no ticket existente, `human_only` solicitado/efetivo, destinatário humano pelo vínculo já aprovado, `continuationPolicy="none"`, sem destinatário agente e sem alvo `plan`; decisão de painel e Discord converge à mesma interação/ticket. Revisão e pendentes exatos no manifesto; decisão canônica gravada e relida antes do consumo, receipt local com autor/decisão/timestamp/revisão/escopo, dedup de replay/duplicata/ACK perdido em memória. Identidade inválida, stale/divergência, recusa/expiração, política incorreta, API indisponível e receipt incerto bloqueiam; sem retries/fallback automáticos nem reexecução terminal. [Código, evidência e limites](sdd/evidencias-f3-05-confirmacao-canonica-20261017-H2/README.md) · [resultado no PC](sdd/evidencias-f3-05-confirmacao-canonica-20261017-H2/execucao-pc/resultado.json). **Limites:** todas as portas são fakes; sem autenticação/integração reais, durabilidade/crash safety, replay Temporal, fencing ou exactly-once externo provados. Não redefine o autorizador nem a integração já aprovada. Política de exceção, candidatas, supervisores anteriores, Workers persistentes, configuração/credenciais e serviços preservados; nada conectado aos Workers; sem restart/deploy/commit/push. **F3-05/G4 aberto; F7-02/G7 e PQBR-114 pausados; F05-06 no-arm.**\n').encode()
marcador = '  - [ ] **Revisão futura da política de exceção técnica na intervenção'.encode()
if original.count(marcador) != 1 or nota in original:
    raise SystemExit('Marcador ausente/ambíguo ou nota já presente; nenhuma escrita')
atualizado = original.replace(marcador, nota + marcador, 1)
roadmap.write_bytes(atualizado)
(BASE / 'nota-roadmap.txt').write_bytes(nota)

check = subprocess.run(['git', 'diff', '--check', '--', 'docs/ROADMAP.md'],
                       cwd=ROOT, capture_output=True, text=True)
report = {
    'arquivos_preexistentes_verificados': len(baseline['sha256']),
    'escopo_baseline': 'src, tests, evidência H1 e docs/ROADMAP.md; sem abrir configurações/credenciais/units',
    'alterados_fora_roadmap': alterados, 'ausentes': ausentes,
    'roadmap_apenas_insercao_exata': roadmap.read_bytes().replace(nota, b'', 1) == original,
    'roadmap_sha256_antes': sha(original), 'roadmap_sha256_depois': sha(atualizado),
    'status_externo_preservado': True,
    'workers_antes': workers_antes, 'workers_depois': workers_depois,
    'workers_mesmos_pids_inicio_restarts_estado': workers_antes == workers_depois,
    'somente_systemctl_show_leitura': True,
    'git_diff_check_roadmap': {'codigo': check.returncode, 'saida': check.stdout + check.stderr},
    'portas_fakes': True, 'crash_safety_durabilidade_real': 'NAO PROVADAS',
}
report['sucesso'] = (not alterados and not ausentes and report['roadmap_apenas_insercao_exata']
                     and report['workers_mesmos_pids_inicio_restarts_estado'] and check.returncode == 0)
(BASE / 'preservacao.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({k: v for k, v in report.items() if k not in ('workers_antes', 'workers_depois')},
                 indent=2, ensure_ascii=False))
raise SystemExit(0 if report['sucesso'] else 1)
