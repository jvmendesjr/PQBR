"""D1: SOMENTE fixture sintética SQLite. Sem imports PQBR/Temporal, HTTP ou credenciais.
Hash = binding/integridade, NÃO autenticação/assinatura. Dois DBs, sem transação distribuída.
"""
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
import json
import signal
import sqlite3

NOW=2000000000
HUMAN='SYN:humano-ja-vinculado'
SCOPE_KEYS=('ticket','interaction','supervisor','supervisor_run','failure','failure_run','failure_receipt','revision','pending')

class Blocked(ValueError):
    pass

def require(ok, reason):
    if not ok:
        raise Blocked(reason)

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)

def digest(value):
    return sha256(canonical(value).encode()).hexdigest()

def confirmation_key(m):
    return 'D1:key:'+digest([m['ticket'],m['interaction']])

def scope(m):
    return {k:m[k] for k in SCOPE_KEYS}

def scope_id(m):
    # Escopo técnico é único mesmo com outra interação do mesmo ticket.
    return digest({k:m[k] for k in SCOPE_KEYS if k!='interaction'})

def fixture():
    return dict(ticket='SYN:ticket',interaction='SYN:interaction',supervisor='SYN:supervisor',supervisor_run='SYN:supervisor-run',failure='SYN:op-falha',failure_run='SYN:failure-run',failure_receipt='SYN:registro-terminal',revision=1,pending=['SYN:pendente-1','SYN:pendente-2'],actor=HUMAN,channel='board',timestamp=NOW,expires=NOW+3600,decision='accept',kind='request_confirmation',resolverPolicy='human_only',effectiveResolverPolicy='human_only',addresseeUserId=HUMAN,addresseeAgentId=None,continuationPolicy='none')

def validate(m, now=NOW):
    require(type(m) is dict and set(m)==set(fixture()),'campos_manifesto')
    for k in ('ticket','interaction','supervisor','supervisor_run','failure','failure_run','failure_receipt'):
        require(type(m[k]) is str and m[k].startswith('SYN:') and len(m[k])<=200,'id_sintetico')
    require(type(m['revision']) is int and m['revision']>0,'revision')
    require(type(m['pending']) is list and 0<len(m['pending'])<=20,'pending')
    require(all(type(x) is str and x.startswith('SYN:') for x in m['pending']),'pending_ids')
    require(len(set(m['pending']))==len(m['pending']) and m['failure'] not in m['pending'],'terminal_ou_duplicata')
    require(m['actor']==HUMAN and m['addresseeUserId']==HUMAN,'humano_vinculado')
    require(m['channel'] in ('board','discord-linked'),'canal')
    require(m['kind']=='request_confirmation' and m['resolverPolicy']=='human_only' and m['effectiveResolverPolicy']=='human_only','human_only')
    require(m['addresseeAgentId'] is None and m['continuationPolicy']=='none','sem_agente_ou_wake')
    require(m['decision'] in ('accept','reject'),'decisao')
    require(type(m['timestamp']) is int and type(m['expires']) is int and m['timestamp']<=now<m['expires'],'prazo')

def checkpoint(wanted, at):
    if wanted==at:
        print(canonical(dict(checkpoint=at)),flush=True)
        while True:
            signal.pause()  # Pai envia SIGKILL: não há cleanup Python/commit implícito.

def connect(base, which, readonly=False):
    base=Path(base).resolve()
    require(str(base).startswith('/tmp/pqbr-d1-') and (base/'.synthetic-d1').read_text()=='SYNTHETIC_ONLY\n','sandbox_fixture')
    require(which in ('source','receiver'),'db')
    path=base/(which+'.sqlite')
    require(not path.is_symlink(),'db_symlink')
    con=sqlite3.connect(path.as_uri()+('?mode=ro' if readonly else '?mode=rw'),uri=True,timeout=0.1,isolation_level=None)
    con.row_factory=sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    con.execute('PRAGMA synchronous=FULL')
    con.execute('PRAGMA busy_timeout=100')
    return con

@contextmanager
def transaction(con):
    con.execute('BEGIN IMMEDIATE')
    try:
        yield
        con.execute('COMMIT')
    except BaseException:
        if con.in_transaction:
            con.execute('ROLLBACK')
        raise

SOURCE_SCHEMA='''
CREATE TABLE live(id INTEGER PRIMARY KEY CHECK(id=1), body TEXT NOT NULL);
CREATE TABLE canonical_decision(
 key TEXT PRIMARY KEY, ticket TEXT NOT NULL, interaction TEXT NOT NULL,
 body TEXT NOT NULL, binding TEXT NOT NULL UNIQUE, receipt TEXT NOT NULL UNIQUE,
 UNIQUE(ticket, interaction));
CREATE TRIGGER immutable_decision_update BEFORE UPDATE ON canonical_decision BEGIN SELECT RAISE(ABORT,'immutable'); END;
CREATE TRIGGER immutable_decision_delete BEFORE DELETE ON canonical_decision BEGIN SELECT RAISE(ABORT,'immutable'); END;
CREATE TABLE consumption(receipt TEXT PRIMARY KEY REFERENCES canonical_decision(receipt), state TEXT NOT NULL CHECK(state IN ('pending','consumed')));
CREATE TRIGGER monotonic_consumption BEFORE UPDATE ON consumption WHEN OLD.state='consumed' AND NEW.state!='consumed' BEGIN SELECT RAISE(ABORT,'monotonic'); END;
CREATE TABLE outbox(receipt TEXT PRIMARY KEY REFERENCES consumption(receipt), scope TEXT NOT NULL UNIQUE, body TEXT NOT NULL, binding TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('pending','acked')), attempts INTEGER NOT NULL DEFAULT 0);
CREATE TRIGGER immutable_outbox BEFORE UPDATE ON outbox WHEN NEW.receipt!=OLD.receipt OR NEW.scope!=OLD.scope OR NEW.body!=OLD.body OR NEW.binding!=OLD.binding BEGIN SELECT RAISE(ABORT,'immutable'); END;
CREATE TRIGGER monotonic_ack BEFORE UPDATE ON outbox WHEN OLD.status='acked' AND NEW.status!='acked' BEGIN SELECT RAISE(ABORT,'monotonic'); END;
'''
RECEIVER_SCHEMA='''
CREATE TABLE live(id INTEGER PRIMARY KEY CHECK(id=1), body TEXT NOT NULL);
CREATE TABLE operations(id TEXT PRIMARY KEY, state TEXT NOT NULL CHECK(state IN ('terminal_failed','pending','completed')), executions INTEGER NOT NULL);
CREATE TRIGGER terminal_immutable BEFORE UPDATE ON operations WHEN OLD.state='terminal_failed' BEGIN SELECT RAISE(ABORT,'terminal'); END;
CREATE TABLE deliveries(receipt TEXT PRIMARY KEY, scope TEXT NOT NULL UNIQUE, body TEXT NOT NULL, binding TEXT NOT NULL, ack TEXT NOT NULL);
CREATE TRIGGER immutable_delivery_update BEFORE UPDATE ON deliveries BEGIN SELECT RAISE(ABORT,'immutable'); END;
CREATE TRIGGER immutable_delivery_delete BEFORE DELETE ON deliveries BEGIN SELECT RAISE(ABORT,'immutable'); END;
'''

def initialize(base):
    base=Path(base).resolve()
    require(str(base).startswith('/tmp/pqbr-d1-') and (base/'.synthetic-d1').read_text()=='SYNTHETIC_ONLY\n','sandbox_fixture')
    for name, schema in (('source',SOURCE_SCHEMA),('receiver',RECEIVER_SCHEMA)):
        p=base/(name+'.sqlite')
        require(not p.exists(),'db_ja_existe')
        with sqlite3.connect(p) as c:
            c.execute('PRAGMA journal_mode=DELETE')
            c.executescript(schema)
            m=fixture()
            c.execute('INSERT INTO live VALUES(1,?)',(canonical(scope(m)),))
            if name=='receiver':
                c.execute('INSERT INTO operations VALUES(?,?,?)',(m['failure'],'terminal_failed',1))
                c.executemany('INSERT INTO operations VALUES(?,?,0)',[(x,'pending') for x in m['pending']])
    return {'initialized':True}

class CanonicalFakeAPI:
    """A sessão/vínculo abaixo é fixture confiável, NÃO autenticação real.
    O token do cliente workflow nunca é sessão humana. Sem rede/endpoint real.
    """
    def __init__(self,base):
        self.base=base

    def persist(self,m,session='board-linked-human',pause=None,readonly=False):
        validate(m)
        trusted={'board-linked-human':('board',HUMAN),'discord-existing-link':('discord-linked',HUMAN)}
        require(session in trusted and trusted[session]==(m['channel'],m['actor']),'sessao_humana_obrigatoria_nunca_agente')
        key=confirmation_key(m)
        binding=digest(m);receipt='D1:'+binding
        with connect(self.base,'source',readonly) as c:
            with transaction(c):
                old=c.execute('SELECT * FROM canonical_decision WHERE key=?',(key,)).fetchone()
                if old:
                    require(old['body']==canonical(m) and old['binding']==binding,'conflito_mesma_chave')
                else:
                    c.execute('INSERT INTO canonical_decision VALUES(?,?,?,?,?,?)',(key,m['ticket'],m['interaction'],canonical(m),binding,receipt))
                    c.execute('INSERT INTO consumption VALUES(?,?)',(receipt,'pending'))
                checkpoint(pause,'decision_before_commit')
            checkpoint(pause,'decision_after_commit')
        return {'receipt':receipt}

    def read(self,receipt,now=NOW):
        with connect(self.base,'source',True) as c:
            r=c.execute('SELECT * FROM canonical_decision WHERE receipt=?',(receipt,)).fetchone()
            require(r is not None,'receipt_ausente')
            m=json.loads(r['body']);validate(m,now)
            require(r['binding']==digest(m) and receipt=='D1:'+digest(m),'binding_canonico')
            require(r['ticket']==m['ticket'] and r['interaction']==m['interaction'] and r['key']==confirmation_key(m),'binding_chaves')
            return m

def command(m,receipt):
    return dict(kind='SYN:resume-exact-pending',receipt=receipt,scope=scope_id(m),manifest=m,canonical_binding=digest(m))

def consume(base,receipt,expected=None,pause=None,readonly=False,fail_outbox=False,now=NOW,fail_full=False):
    api=CanonicalFakeAPI(base)
    with connect(base,'source',readonly) as c:
        with transaction(c):
            m=api.read(receipt,now)
            require(m['decision']=='accept','nao_aprovado')
            require(expected is None or canonical(expected)==canonical(scope(m)),'stale_esperado')
            live=json.loads(c.execute('SELECT body FROM live WHERE id=1').fetchone()[0])
            require(canonical(live)==canonical(scope(m)),'stale_live_origem')
            cmd=command(m,receipt)
            row=c.execute('SELECT state FROM consumption WHERE receipt=?',(receipt,)).fetchone()
            require(row is not None,'consumo_ausente')
            if row['state']=='pending':
                n=c.execute("UPDATE consumption SET state='consumed' WHERE receipt=? AND state='pending'",(receipt,)).rowcount
                require(n==1,'cas_perdido')
                if fail_full:
                    pages=c.execute('PRAGMA page_count').fetchone()[0]
                    c.execute('PRAGMA max_page_count='+str(pages))
                    c.execute('INSERT INTO synthetic_space VALUES(zeroblob(1048576))')
                if fail_outbox:
                    # Falha real SQLite depois do CAS; rollback deve desfazer o consumo.
                    c.execute("INSERT INTO outbox(receipt) VALUES(?)",(receipt,))
                c.execute('INSERT INTO outbox VALUES(?,?,?,?,?,0)',(receipt,cmd['scope'],canonical(cmd),digest(cmd),'pending'))
            else:
                old=c.execute('SELECT body,binding FROM outbox WHERE receipt=?',(receipt,)).fetchone()
                require(old is not None and old['body']==canonical(cmd) and old['binding']==digest(cmd),'consumido_sem_outbox_ou_conflito')
            checkpoint(pause,'consume_before_commit')
        checkpoint(pause,'consume_after_commit')
    return {'receipt':receipt,'state':'consumed'}

def receive(base,cmd,pause=None,readonly=False,now=NOW):
    require(type(cmd) is dict and set(cmd)=={'kind','receipt','scope','manifest','canonical_binding'},'command_fields')
    # Releitura canônica obrigatória; o comando sozinho NÃO é autorização.
    # Duplicatas já aceitas podem receber ACK após expiração, sem novo efeito.
    with connect(base,'receiver',readonly) as c:
        with transaction(c):
            old=c.execute('SELECT * FROM deliveries WHERE receipt=? OR scope=?',(cmd['receipt'],cmd['scope'])).fetchall()
            if old:
                require(len(old)==1 and old[0]['receipt']==cmd['receipt'] and old[0]['scope']==cmd['scope'] and old[0]['body']==canonical(cmd) and old[0]['binding']==digest(cmd),'conflito_dedup_persistente')
                # A entrega original já guardou o comando validado na mesma TX dos efeitos.
                return {'ack':old[0]['ack'],'duplicate':True}
            m=CanonicalFakeAPI(base).read(cmd['receipt'],now)
            require(m['decision']=='accept','nao_aprovado')
            require(canonical(cmd)==canonical(command(m,cmd['receipt'])),'binding_comando')
            # Só comando admitido na outbox após consumo atômico pode ser entregue.
            with connect(base,'source',True) as s:
                admitted=s.execute('SELECT o.body,o.binding,c.state FROM outbox o JOIN consumption c USING(receipt) WHERE receipt=?',(cmd['receipt'],)).fetchone()
                require(admitted is not None and admitted['state']=='consumed' and admitted['body']==canonical(cmd) and admitted['binding']==digest(cmd),'sem_consumo_outbox')
            live=json.loads(c.execute('SELECT body FROM live WHERE id=1').fetchone()[0])
            require(canonical(live)==canonical(scope(m)),'stale_live_receptor')
            pending=[r[0] for r in c.execute("SELECT id FROM operations WHERE state='pending' ORDER BY id")]
            require(set(pending)==set(m['pending']) and len(pending)==len(m['pending']),'pendentes_exatas')
            terminal=c.execute('SELECT state,executions FROM operations WHERE id=?',(m['failure'],)).fetchone()
            require(terminal is not None and tuple(terminal)==('terminal_failed',1),'falha_terminal')
            ack='SYN:ack:'+digest(cmd)
            c.execute('INSERT INTO deliveries VALUES(?,?,?,?,?)',(cmd['receipt'],cmd['scope'],canonical(cmd),digest(cmd),ack))
            for op in m['pending']:
                n=c.execute("UPDATE operations SET state='completed',executions=executions+1 WHERE id=? AND state='pending' AND executions=0",(op,)).rowcount
                require(n==1,'cas_operacao')
            live['pending']=[]
            c.execute('UPDATE live SET body=? WHERE id=1',(canonical(live),))
            checkpoint(pause,'receiver_before_commit')
        checkpoint(pause,'receiver_after_commit')
    return {'ack':ack,'duplicate':False}

def dispatch(base,pause=None,receiver_readonly=False,source_readonly=False,now=NOW,ack_readonly=False):
    results=[]
    with connect(base,'source',True) as c:
        rows=c.execute("SELECT * FROM outbox WHERE status='pending' ORDER BY receipt").fetchall()
    for row in rows:
        cmd=json.loads(row['body'])
        require(digest(cmd)==row['binding'],'binding_outbox')
        with connect(base,'source',source_readonly) as c:
            with transaction(c):
                c.execute('UPDATE outbox SET attempts=attempts+1 WHERE receipt=?',(row['receipt'],))
        result=receive(base,cmd,pause,receiver_readonly,now)
        checkpoint(pause,'accepted_before_ack')
        require(result['ack']=='SYN:ack:'+digest(cmd),'ack_invalido')
        with connect(base,'source',source_readonly or ack_readonly) as c:
            with transaction(c):
                n=c.execute("UPDATE outbox SET status='acked' WHERE receipt=? AND status='pending'",(row['receipt'],)).rowcount
                require(n in (0,1),'ack_cas')
            checkpoint(pause,'ack_after_commit')
        results.append(result)
    return {'delivered':len(results),'results':results}

def inspect(base):
    result={}
    for name,tables in (('source',('live','canonical_decision','consumption','outbox')),('receiver',('live','operations','deliveries'))):
        with connect(base,name,True) as c:
            result[name]={t:[dict(r) for r in c.execute('SELECT * FROM '+t)] for t in tables}
            result[name]['integrity_check']=c.execute('PRAGMA integrity_check').fetchone()[0]
    return result
