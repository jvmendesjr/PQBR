#!/usr/bin/env python3
"""D2: GET Paperclip -> recibo SQLite local; nenhum despacho operacional."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone

ISSUE = '61ca182f-7342-4dd3-8827-0464ee541fff'
INTERACTION = 'db924b2d-3be6-4c6e-8d77-b2519fcbf4a3'
USER = 'eHIQgWDGucnmgW8xT19VvSsypXRdbTr7'
PROMPT = 'Autoriza somente registrar a decisão desta confirmação de teste? Nenhuma operação será retomada.'
SCOPE = 'Fixture de teste aprovada por José. Ticket PQBR-118. Verifica somente a autoria humana e a gravação da decisão da confirmação. Não chama Temporal, não retoma nenhuma fila ou operação e não ativa produção. Sem aviso Discord.'
ROOT = Path('/home/pc/Workspace/PQBR')
OUT = ROOT / 'docs/sdd/evidencias-f3-05-integracao-local-20261017-D2'

def require(condition, label):
    if not condition:
        raise RuntimeError(label)

def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def read_receipt():
    # Único comando de serviço permitido. stdout raw só existe transitoriamente em memória.
    p = subprocess.run([str(Path.home()/'.hermes/node/bin/node'), str(Path.home()/'.paperclip/cli/current/node_modules/paperclipai/dist/index.js'), 'issue', 'interactions', ISSUE, '--json'], capture_output=True, text=True, timeout=60)
    require(p.returncode == 0, 'CLI_GET_FAILED')
    data = json.loads(p.stdout)
    if isinstance(data, dict):
        data = data.get('interactions', data.get('data'))
    require(isinstance(data, list), 'INVALID_ENVELOPE')
    rows = [x for x in data if x.get('id') == INTERACTION]
    require(len(rows) == 1, 'INTERACTION_COUNT_MISMATCH')
    v = rows[0]
    expected = {'id': INTERACTION, 'issueId': ISSUE, 'companyId': 'be3980d6-51ae-4cee-b85f-923b4568188c', 'kind': 'request_confirmation', 'status': 'accepted', 'addresseeUserId': USER, 'resolvedByUserId': USER, 'continuationPolicy': 'none', 'requestedResolverPolicy': 'human_only', 'effectiveResolverPolicy': 'human_only', 'resolverPolicy': 'human_only'}
    for key, value in expected.items():
        require(v.get(key) == value, 'MISMATCH_' + key)
    for key in ['addresseeAgentId', 'resolvedByAgentId', 'resolvedByRunId', 'sourceRunId']:
        require(v.get(key) is None, 'UNEXPECTED_' + key)
    require(v.get('result', {}).get('outcome') == 'accepted', 'RESULT_MISMATCH')
    payload = v.get('payload', {})
    require(payload.get('version') == 1 and payload.get('prompt') == PROMPT and payload.get('detailsMarkdown') == SCOPE, 'SCOPE_MISMATCH')
    require(isinstance(v.get('idempotencyKey'), str) and bool(v['idempotencyKey']), 'MISSING_IDEMPOTENCY_KEY')
    stamp = v.get('resolvedAt')
    require(isinstance(stamp, str) and datetime.fromisoformat(stamp.replace('Z', '+00:00')).utcoffset() is not None, 'INVALID_TIMESTAMP')
    # Whitelist: nunca gravar resposta raw, título, comentários, credenciais ou perfil CLI.
    return {'actionType': 'record_authorization_only', 'ticket': 'PQBR-118', 'issueId': ISSUE, 'interactionId': INTERACTION, 'userId': USER, 'status': v['status'], 'timestamp': stamp, 'scope': {'prompt': PROMPT, 'detailsMarkdown': SCOPE}, 'continuationPolicy': 'none', 'requestedResolverPolicy': 'human_only', 'effectiveResolverPolicy': 'human_only', 'idempotencyKey': v['idempotencyKey'], 'pendingCount': 0, 'resumeCount': 0, 'effectCount': 0}

def worker(db_path):
    def audit(event, args):
        if event.startswith('socket.') or event in ('subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.fork', 'os.exec'):
            raise RuntimeError('WORKER_EXTERNAL_EFFECT_BLOCKED')
    sys.addaudithook(audit)
    receipt = json.load(sys.stdin)
    require(receipt['actionType'] == 'record_authorization_only' and all(receipt[k] == 0 for k in ['pendingCount', 'resumeCount', 'effectCount']), 'NON_AUDIT_RECEIPT')
    body = canonical(receipt)
    digest = hashlib.sha256(body.encode()).hexdigest()
    db = sqlite3.connect(db_path, timeout=30, isolation_level=None)
    db.execute('PRAGMA journal_mode=DELETE')
    db.execute('PRAGMA synchronous=FULL')
    db.execute('BEGIN IMMEDIATE')
    db.execute('CREATE TABLE IF NOT EXISTS receipts (idempotency_key TEXT PRIMARY KEY, interaction_id TEXT NOT NULL UNIQUE, issue_id TEXT NOT NULL, action_type TEXT NOT NULL CHECK(action_type="record_authorization_only"), status TEXT NOT NULL CHECK(status="accepted"), pending_count INTEGER NOT NULL CHECK(pending_count=0), resume_count INTEGER NOT NULL CHECK(resume_count=0), effect_count INTEGER NOT NULL CHECK(effect_count=0), digest TEXT NOT NULL, body TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS effects (id INTEGER PRIMARY KEY)')
    db.execute('CREATE TRIGGER IF NOT EXISTS forbid_effects BEFORE INSERT ON effects BEGIN SELECT RAISE(ABORT, "audit only"); END')
    old = db.execute('SELECT digest, body FROM receipts WHERE idempotency_key=? OR interaction_id=?', (receipt['idempotencyKey'], receipt['interactionId'])).fetchall()
    if old:
        require(len(old) == 1 and old[0] == (digest, body), 'RECEIPT_CONFLICT')
        result = 'duplicate'
    else:
        db.execute('INSERT INTO receipts VALUES (?,?,?,?,?,?,?,?,?,?)', (receipt['idempotencyKey'], receipt['interactionId'], receipt['issueId'], receipt['actionType'], receipt['status'], 0, 0, 0, digest, body))
        result = 'inserted'
    db.execute('COMMIT')
    db.close()
    print(json.dumps({'result': result}))

def run_worker(receipt):
    p = subprocess.run(['/usr/bin/python3', '-I', '-S', '-B', str(Path(__file__).resolve()), 'worker', str(OUT/'audit.sqlite3')], input=canonical(receipt), capture_output=True, text=True, env={'PATH': '/usr/bin:/bin', 'HOME': '/tmp', 'LANG': 'C.UTF-8'}, timeout=60)
    require(p.returncode == 0, 'LOCAL_WORKER_FAILED')
    return json.loads(p.stdout)['result']

def main():
    require(not OUT.exists(), 'OUTPUT_ALREADY_EXISTS')
    roadmap = ROOT/'docs/ROADMAP.md'
    before = roadmap.read_bytes()
    receipt = read_receipt()  # CLI processo 1 encerra antes de persistir.
    OUT.mkdir(mode=0o700)
    os.umask(0o077)
    require(run_worker(receipt) == 'inserted', 'INITIAL_INSERT_FAILED')
    # Processo gravador já terminou; novo processo CLI e novas conexões SQLite.
    again = read_receipt()
    require(again == receipt, 'CANONICAL_AUTHORIZATION_CHANGED')
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        outcomes = list(pool.map(lambda _: run_worker(again), range(16)))
    require(outcomes == ['duplicate']*16, 'CONCURRENT_DEDUP_FAILED')
    db = sqlite3.connect(f'file:{OUT / "audit.sqlite3"}?mode=ro', uri=True)
    rows = db.execute('SELECT body, pending_count, resume_count, effect_count FROM receipts').fetchall()
    effects = db.execute('SELECT COUNT(*) FROM effects').fetchone()[0]
    integrity = db.execute('PRAGMA integrity_check').fetchone()[0]
    db.close()
    require(len(rows) == 1 and rows[0] == (canonical(receipt), 0, 0, 0) and effects == 0 and integrity == 'ok', 'FINAL_AUDIT_FAILED')
    result = {'test': 'D2_board_authorization_audit_only', 'verifiedAt': datetime.now(timezone.utc).isoformat(), 'ticket': 'PQBR-118', 'interactionId': INTERACTION, 'initialInsertCount': 1, 'concurrentResubmissions': 16, 'durableDuplicates': outcomes.count('duplicate'), 'receiptCount': len(rows), 'pendingCount': 0, 'resumeCount': 0, 'effectCount': effects, 'sqliteIntegrity': integrity, 'cliGetCalls': 2, 'freshCliProcesses': 2, 'localWriterProcesses': 17, 'roadmapBeforeSha256': hashlib.sha256(before).hexdigest(), 'identityEvidence': 'Board decision attributed by Paperclip to expected tutibom userId; no Discord authentication claim'}
    (OUT/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    (OUT/'resultado.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    note = '  - Integração mínima local D2, 2026-10-17: duas releituras exclusivamente GET via CLI Paperclip atual autenticado confirmaram a interação `db924b2d-3be6-4c6e-8d77-b2519fcbf4a3` do **PQBR-118**, `accepted`, autoria Board do perfil **tutibom** (`resolvedByUserId` igual ao destinatário humano esperado), `human_only`, `continuationPolicy=none`, sem agente/run. Escopo canônico: somente registrar autoria/decisão, sem retomada. Recibo mínimo `record_authorization_only` em SQLite novo: processo gravador encerrado, cliente CLI reconstruído, banco reaberto por processos novos e **16 reenvios concorrentes deduplicados duravelmente; 1 recibo, pendingCount=0, resumeCount=0, effectCount=0**. [Evidência, código e limites](sdd/evidencias-f3-05-integracao-local-20261017-D2/README.md). **Não prova autenticação de decisão via Discord, crash safety real Paperclip/Temporal, transação distribuída, fencing ou exactly-once externo**; encerramento normal de processo não equivale a teste de crash. Sem endpoints mutáveis, criação/edição/comentário de ticket/interação, Discord, Temporal, publicação, alteração/restart de Workers, commit/push ou documentos restritos; resposta raw não armazenada, logs por whitelist. **F3-05/G4 permanece aberto; política operacional intacta; F05-06 no-arm; F7-02/G7 e PQBR-114 pausados.**\n'
    marker = '  - [ ] **Revisão futura da política de exceção técnica na intervenção'
    text = before.decode()
    require(text.count(marker) == 1, 'ROADMAP_ANCHOR_MISMATCH')
    require(roadmap.read_bytes() == before, 'ROADMAP_CONCURRENT_CHANGE')
    after = text.replace(marker, note + marker, 1)
    require(after.replace(note, '', 1) == text, 'ROADMAP_PRESERVATION_FAILED')
    roadmap.write_text(after)
    (OUT/'nota-roadmap.txt').write_text(note)
    (OUT/'README.md').write_text('# D2 — decisão Board real, recibo exclusivamente local\n\nA interação aprovada do PQBR-118 foi relida duas vezes com `issue interactions <issueId> --json`, no CLI atual e perfil já autenticado, sem abrir credenciais. IDs de organização/ticket/interação/ator/destinatário, status, outcome, políticas solicitada/efetiva, ausência de agente/run e escopo exato foram conferidos antes da gravação. A idempotencyKey original foi preservada e conferida na releitura. O timestamp é o resolvedAt canônico. Nenhuma resposta raw completa foi persistida.\n\n## Resultado\n\n1 inserção em processo separado, encerrado normalmente; novo cliente CLI, novas conexões SQLite e 16 reenvios concorrentes em processos distintos produziram 16 duplicatas e exatamente 1 recibo. pendingCount=0, resumeCount=0, effectCount=0; integrity_check=ok. O SQLite usa BEGIN IMMEDIATE, chave única para idempotência/interação, journal DELETE e synchronous FULL; corpo divergente falha fechado. Workers locais têm ambiente mínimo e audit hook bloqueando sockets/subprocessos; não é isolamento de kernel. Só o runner faz o GET autorizado.\n\n## Limites\n\nProva atribuição da decisão Board pelo Paperclip ao userId esperado, que o proprietário autorizou como perfil tutibom neste teste. Não usa aprovação do chat como decisão no ticket e não demonstra autenticação via Discord, posse de credenciais ou uma assinatura independente. Deduplicação persiste após encerramento normal/reabertura do SQLite local; não é teste de SIGKILL, queda do host ou crash safety Paperclip/Temporal real, transação distribuída, fencing ou exactly-once externo. Não há pendentes, dispatcher, outbox ou integração operacional. Efeito e resume são literalmente zero.\n\nA única alteração preexistente autorizada é a nota F3-05; demais arquivos são preservados. Nenhum endpoint mutável, comentário, aviso Discord, chamada Temporal, alteração de Worker, publicação, commit/push ou documento restrito. F3-05/G4 segue aberto; demais gates/pausas e política operacional intactos.\n\n## Artefatos\n\n- `receipt.json`: whitelist do recibo; `audit.sqlite3`: a mesma decisão persistida.\n- `resultado.json`: contagens e hash anterior do roadmap.\n- `test_integracao_d2.py`: ensaio reproduzível; o diretório de saída deve ser novo.\n- `nota-roadmap.txt`: inserção exata no roadmap.\n')
    result['roadmapAfterSha256'] = hashlib.sha256(roadmap.read_bytes()).hexdigest()
    result['roadmapInsertionOnlyVerified'] = True
    (OUT/'resultado.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    try:
        if len(sys.argv) == 3 and sys.argv[1] == 'worker':
            worker(sys.argv[2])
        else:
            main()
    except Exception as e:
        # Apenas classe/label controlada, nunca stderr/raw remoto ou secrets.
        print(json.dumps({'status': 'aborted', 'errorType': type(e).__name__, 'label': str(e) if isinstance(e, RuntimeError) else 'LOCAL_VALIDATION_OR_IO_ERROR'}))
        raise SystemExit(1)
