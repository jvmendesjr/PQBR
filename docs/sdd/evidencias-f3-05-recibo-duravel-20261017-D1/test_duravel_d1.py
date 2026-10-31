"""D1: testes usam processos novos e SIGKILL real, não recriação de objetos."""
from pathlib import Path
import copy
import json
import os
import select
import signal
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import duravel_d1 as d

HERE=Path(__file__).resolve().parent
TRACE=[]

class DurabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='pqbr-d1-')
        self.base=Path(self.tmp.name)
        (self.base/'.synthetic-d1').write_text('SYNTHETIC_ONLY\n')
        self.run_worker('init')

    def spawn(self,action,**kw):
        request=dict(base=str(self.base),action=action,**kw)
        p=subprocess.Popen([sys.executable,'-I','-S','-B',str(HERE/'worker_d1.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env={'PATH':'/usr/bin:/bin','HOME':'/nonexistent','PYTHONDONTWRITEBYTECODE':'1'})
        return p,request

    def finish(self,p,request,expect=True):
        stdout,stderr=p.communicate(d.canonical(request) if p.stdin is not None else None,timeout=15)
        self.assertFalse(stderr,stderr)
        self.assertIn(p.returncode,(0,3),(p.returncode,stdout))
        output=json.loads(stdout)
        TRACE.append(dict(test=self.id(),action=request['action'],pid=p.pid,exit=p.returncode,result=output))
        if expect is not None:
            self.assertEqual(output['ok'],expect,output)
        return output

    def run_worker(self,action,expect=True,**kw):
        p,request=self.spawn(action,**kw)
        return self.finish(p,request,expect)

    def crash(self,action,pause,**kw):
        p,request=self.spawn(action,pause=pause,**kw)
        p.stdin.write(d.canonical(request));p.stdin.close();p.stdin=None
        try:
            ready,_,_=select.select([p.stdout],[],[],12)
            self.assertTrue(ready,'checkpoint nao atingido')
            line=p.stdout.readline()
            self.assertEqual(json.loads(line),{'checkpoint':pause})
            p.kill()
            stdout,stderr=p.communicate(timeout=10)
            self.assertEqual(p.returncode,-signal.SIGKILL)
            self.assertFalse(stderr,stderr)
            TRACE.append(dict(test=self.id(),action=action,pid=p.pid,checkpoint=pause,exit=p.returncode,signal='SIGKILL'))
        finally:
            if p.poll() is None:
                p.kill();p.communicate()

    def decide(self,**kw):
        return self.run_worker('decide',**kw)['result']['receipt']

    def ready(self):
        receipt=self.decide()
        self.run_worker('consume',receipt=receipt)
        return receipt

    def state(self):
        return self.run_worker('inspect')['result']

    def assert_effects(self,state,done):
        ops={r['id']:r for r in state['receiver']['operations']}
        self.assertEqual(ops['SYN:op-falha'],dict(id='SYN:op-falha',state='terminal_failed',executions=1))
        for op in d.fixture()['pending']:
            self.assertEqual(ops[op]['executions'],int(done))
            self.assertEqual(ops[op]['state'],'completed' if done else 'pending')
        self.assertEqual(len(state['receiver']['deliveries']),int(done))

    def assert_pending_outbox(self,state,attempts=None):
        self.assertEqual(len(state['source']['outbox']),1)
        self.assertEqual(state['source']['outbox'][0]['status'],'pending')
        if attempts is not None:
            self.assertEqual(state['source']['outbox'][0]['attempts'],attempts)

    def complete(self):
        self.run_worker('dispatch')
        state=self.state();self.assert_effects(state,True)
        self.assertEqual(state['source']['outbox'][0]['status'],'acked')
        self.run_worker('dispatch')
        self.assert_effects(self.state(),True)

    def sql(self,which,statement,args=()):
        with sqlite3.connect(self.base/(which+'.sqlite')) as c:
            return c.execute(statement,args).fetchall()

    def change_live(self,which,key,value):
        m=json.loads(self.sql(which,'SELECT body FROM live')[0][0]);m[key]=value
        self.sql(which,'UPDATE live SET body=?',(d.canonical(m),))

    def tearDown(self):
        try:
            s=self.state()
            for name in ('source','receiver'):
                self.assertEqual(s[name]['integrity_check'],'ok')
            for op in s['receiver']['operations']:
                self.assertLessEqual(op['executions'],1)
                if op['id']=='SYN:op-falha':
                    self.assertEqual((op['state'],op['executions']),('terminal_failed',1))
            out={r['receipt'] for r in s['source']['outbox']}
            consumed={r['receipt'] for r in s['source']['consumption'] if r['state']=='consumed'}
            self.assertEqual(out,consumed,'consumo e outbox nao podem separar')
        finally:
            self.tmp.cleanup()

    def test_01_kill_decision_before_commit(self):
        self.crash('decide','decision_before_commit')
        s=self.state()
        self.assertEqual(s['source']['canonical_decision'],[])
        self.assertEqual(s['source']['consumption'],[])
        self.assert_effects(s,False)
        r=self.decide();self.run_worker('consume',receipt=r);self.complete()

    def test_02_kill_decision_after_commit_restart_pending(self):
        self.crash('decide','decision_after_commit')
        s=self.state();self.assertEqual(s['source']['consumption'][0]['state'],'pending')
        self.assertEqual(s['source']['outbox'],[]);self.assert_effects(s,False)
        r=self.decide();self.run_worker('consume',receipt=r);self.complete()

    def test_03_kill_consume_before_commit(self):
        r=self.decide();self.crash('consume','consume_before_commit',receipt=r)
        s=self.state();self.assertEqual(s['source']['consumption'][0]['state'],'pending')
        self.assertEqual(s['source']['outbox'],[]);self.assert_effects(s,False)
        self.run_worker('consume',receipt=r);self.complete()

    def test_04_kill_consume_after_commit_before_resume(self):
        r=self.decide();self.crash('consume','consume_after_commit',receipt=r)
        s=self.state();self.assertEqual(s['source']['consumption'][0]['state'],'consumed')
        self.assert_pending_outbox(s,0);self.assert_effects(s,False)
        self.run_worker('consume',receipt=r);self.complete()

    def test_05_kill_receiver_before_commit(self):
        self.ready();self.crash('dispatch','receiver_before_commit')
        s=self.state();self.assert_pending_outbox(s,1);self.assert_effects(s,False)
        self.complete()

    def test_06_kill_receiver_after_commit_before_reply(self):
        self.ready();self.crash('dispatch','receiver_after_commit')
        s=self.state();self.assert_pending_outbox(s,1);self.assert_effects(s,True)
        self.complete();self.assertEqual(self.state()['source']['outbox'][0]['attempts'],2)

    def test_07_kill_after_accept_before_storing_ack(self):
        self.ready();self.crash('dispatch','accepted_before_ack')
        s=self.state();self.assert_pending_outbox(s,1);self.assert_effects(s,True)
        self.complete();self.assertEqual(self.state()['source']['outbox'][0]['attempts'],2)

    def test_08_kill_after_ack_restart(self):
        self.ready();self.crash('dispatch','ack_after_commit')
        s=self.state();self.assertEqual(s['source']['outbox'][0]['status'],'acked')
        self.assert_effects(s,True);self.complete()
        self.assertEqual(self.state()['source']['outbox'][0]['attempts'],1)

    def test_09_sequential_replay_after_full_process_restart(self):
        r=self.ready();cmd=d.command(d.fixture(),r)
        self.complete()
        for _ in range(3):
            result=self.run_worker('receive',command=cmd)['result']
            self.assertTrue(result['duplicate'])
        self.assert_effects(self.state(),True)

    def test_10_concurrent_decision_and_consumption_unique(self):
        jobs=[self.spawn('decide') for _ in range(8)]
        # Iniciar todos antes de coletar: stdin submetido para todos.
        for p,req in jobs:
            p.stdin.write(d.canonical(req));p.stdin.close();p.stdin=None
        receipts=[]
        for p,req in jobs:
            out=self.finish(p,req,None)
            if out['ok']:
                receipts.append(out['result']['receipt'])
            else:
                self.assertEqual(out['sqlite_code'],'SQLITE_BUSY',out)
        self.assertTrue(receipts);self.assertEqual(len(set(receipts)),1)
        r=receipts[0]
        jobs=[self.spawn('consume',receipt=r) for _ in range(8)]
        for p,req in jobs:
            p.stdin.write(d.canonical(req));p.stdin.close();p.stdin=None
        for p,req in jobs:
            out=self.finish(p,req,None)
            if not out['ok']:
                self.assertEqual(out['sqlite_code'],'SQLITE_BUSY',out)
        s=self.state();self.assertEqual(len(s['source']['canonical_decision']),1)
        self.assertEqual(len(s['source']['outbox']),1);self.complete()

    def test_11_concurrent_receiver_persistent_dedup(self):
        r=self.ready();cmd=d.command(d.fixture(),r)
        jobs=[self.spawn('receive',command=cmd) for _ in range(10)]
        for p,req in jobs:
            p.stdin.write(d.canonical(req));p.stdin.close();p.stdin=None
        successful=[]
        for p,req in jobs:
            out=self.finish(p,req,None)
            if out['ok']:
                successful.append(out['result'])
            else:
                self.assertEqual(out['sqlite_code'],'SQLITE_BUSY',out)
        self.assertTrue(successful)
        self.assertEqual(sum(not x['duplicate'] for x in successful),1)
        self.assert_effects(self.state(),True);self.complete()

    def test_12_concurrent_dispatch(self):
        self.ready()
        jobs=[self.spawn('dispatch') for _ in range(8)]
        for p,req in jobs:
            p.stdin.write(d.canonical(req));p.stdin.close();p.stdin=None
        for p,req in jobs:
            out=self.finish(p,req,None)
            if not out['ok']:
                self.assertEqual(out['sqlite_code'],'SQLITE_BUSY',out)
        self.complete()

    def test_13_same_decision_key_conflicting_payload(self):
        self.decide();m=d.fixture();m['decision']='reject'
        out=self.run_worker('decide',manifest=m,expect=False)
        self.assertEqual(out['reason'],'conflito_mesma_chave')
        self.assertEqual(len(self.state()['source']['canonical_decision']),1)

    def test_14_same_receipt_conflicting_payload_after_accept(self):
        r=self.ready();self.complete();cmd=d.command(d.fixture(),r)
        cmd['manifest']['pending'].append('SYN:extra')
        self.run_worker('receive',command=cmd,expect=False)
        self.assert_effects(self.state(),True)

    def test_15_same_scope_new_receipt_conflict(self):
        r=self.ready();self.complete();m=d.fixture();m['interaction']='SYN:other-interaction'
        cmd=d.command(m,'D1:'+d.digest(m))
        self.assertEqual(cmd['scope'],d.scope_id(d.fixture()))
        self.run_worker('receive',command=cmd,expect=False)
        self.assert_effects(self.state(),True)

    def test_16_stale_unknown_receipt(self):
        self.decide();self.run_worker('consume',receipt='D1:stale',expect=False)
        self.assertEqual(self.state()['source']['outbox'],[])

    def test_17_stale_ticket(self):
        r=self.decide();self.change_live('source','ticket','SYN:old-ticket')
        self.run_worker('consume',receipt=r,expect=False)
        self.assertEqual(self.state()['source']['outbox'],[])

    def test_18_stale_revision(self):
        r=self.decide();self.change_live('source','revision',2)
        self.run_worker('consume',receipt=r,expect=False)
        self.assertEqual(self.state()['source']['outbox'],[])

    def test_19_stale_pending_extra_missing_reordered_terminal(self):
        r=self.decide()
        for pending in (['SYN:pendente-1'],['SYN:pendente-1','SYN:pendente-2','SYN:new'],list(reversed(d.fixture()['pending'])),['SYN:op-falha']):
            self.change_live('source','pending',pending)
            self.run_worker('consume',receipt=r,expect=False)
            self.assertEqual(self.state()['source']['outbox'],[])

    def test_20_stale_receiver_after_consumption(self):
        self.ready()
        for key,val in (('ticket','SYN:stale'),('revision',2),('pending',['SYN:pendente-1']),('failure','SYN:other-failure'),('interaction','SYN:stale-interaction')):
            original=d.scope(d.fixture())
            self.sql('receiver','UPDATE live SET body=?',(d.canonical(original),))
            self.change_live('receiver',key,val)
            self.run_worker('dispatch',expect=False)
            s=self.state();self.assert_pending_outbox(s);self.assert_effects(s,False)

    def test_21_workflow_agent_token_never_human(self):
        for session in ('workflow-agent-token','agent','board','discord','SYN:humano-ja-vinculado'):
            out=self.run_worker('decide',session=session,expect=False)
            self.assertEqual(out['reason'],'sessao_humana_obrigatoria_nunca_agente')
        self.assertEqual(self.state()['source']['canonical_decision'],[])

    def test_22_discord_existing_link_fake(self):
        m=d.fixture();m['channel']='discord-linked'
        r=self.decide(manifest=m,session='discord-existing-link')
        self.run_worker('consume',receipt=r);self.complete()

    def test_23_human_only_bound_recipient_and_no_continuation(self):
        for key,value in (('resolverPolicy','any'),('effectiveResolverPolicy','agent'),('addresseeUserId','SYN:unlinked'),('addresseeAgentId','SYN:agent'),('continuationPolicy','resume'),('actor','SYN:unlinked'),('target','plan'),('revision',True)):
            m=d.fixture();m[key]=value
            self.run_worker('decide',manifest=m,expect=False)
        self.assertEqual(self.state()['source']['canonical_decision'],[])

    def test_24_rejection_does_not_resume(self):
        m=d.fixture();m['decision']='reject';r=self.decide(manifest=m)
        self.run_worker('consume',receipt=r,expect=False)
        self.assertEqual(self.state()['source']['outbox'],[])

    def test_25_expiration_blocks_first_delivery(self):
        r=self.ready()
        self.run_worker('dispatch',now=d.NOW+3600,expect=False)
        self.assert_effects(self.state(),False)
        self.assert_pending_outbox(self.state())

    def test_26_expired_already_delivered_duplicate_only_ack(self):
        r=self.ready();self.crash('dispatch','accepted_before_ack')
        out=self.run_worker('dispatch',now=d.NOW+3600)['result']
        self.assertTrue(out['results'][0]['duplicate']);self.assert_effects(self.state(),True)

    def test_27_readonly_decision_storage_failure(self):
        out=self.run_worker('decide',readonly=True,expect=False)
        self.assertEqual(out['sqlite_code'],'SQLITE_READONLY')
        self.assertEqual(self.state()['source']['canonical_decision'],[])

    def test_28_readonly_consume_storage_failure(self):
        r=self.decide();out=self.run_worker('consume',receipt=r,readonly=True,expect=False)
        self.assertEqual(out['sqlite_code'],'SQLITE_READONLY')
        s=self.state();self.assertEqual(s['source']['consumption'][0]['state'],'pending')
        self.assertEqual(s['source']['outbox'],[])

    def test_29_outbox_failure_rolls_back_cas(self):
        r=self.decide();out=self.run_worker('consume',receipt=r,fail_outbox=True,expect=False)
        self.assertEqual(out['error'],'IntegrityError')
        s=self.state();self.assertEqual(s['source']['consumption'][0]['state'],'pending')
        self.assertEqual(s['source']['outbox'],[])
        self.run_worker('consume',receipt=r);self.complete()

    def test_30_receiver_readonly_storage_failure(self):
        self.ready();out=self.run_worker('dispatch',receiver_readonly=True,expect=False)
        self.assertEqual(out['sqlite_code'],'SQLITE_READONLY')
        s=self.state();self.assert_pending_outbox(s);self.assert_effects(s,False)
        self.complete()

    def test_31_source_busy_real_lock(self):
        r=self.decide()
        with sqlite3.connect(self.base/'source.sqlite') as lock:
            lock.execute('BEGIN IMMEDIATE')
            out=self.run_worker('consume',receipt=r,expect=False)
            self.assertEqual(out['sqlite_code'],'SQLITE_BUSY')
            lock.rollback()
        s=self.state();self.assertEqual(s['source']['consumption'][0]['state'],'pending')
        self.assertEqual(s['source']['outbox'],[])
        self.run_worker('consume',receipt=r);self.complete()

    def test_32_receiver_busy_real_lock(self):
        self.ready()
        with sqlite3.connect(self.base/'receiver.sqlite') as lock:
            lock.execute('BEGIN IMMEDIATE')
            out=self.run_worker('dispatch',expect=False)
            self.assertEqual(out['sqlite_code'],'SQLITE_BUSY')
            lock.rollback()
        s=self.state();self.assert_pending_outbox(s);self.assert_effects(s,False)
        self.complete()

    def test_33_immutable_manifest_and_monotonic_state(self):
        r=self.ready()
        for stmt in ('UPDATE canonical_decision SET body=body','DELETE FROM canonical_decision',"UPDATE consumption SET state='pending'",'UPDATE outbox SET body=body||\'x\''):
            with self.assertRaises(sqlite3.IntegrityError):
                self.sql('source',stmt)
        self.complete()
        with self.assertRaises(sqlite3.IntegrityError):
            self.sql('source',"UPDATE outbox SET status='pending'")
        with self.assertRaises(sqlite3.IntegrityError):
            self.sql('receiver',"UPDATE operations SET state='pending' WHERE id='SYN:op-falha'")

    def test_34_receipt_without_consumption_not_authorization(self):
        r=self.decide();cmd=d.command(d.fixture(),r)
        out=self.run_worker('receive',command=cmd,expect=False)
        self.assertEqual(out['reason'],'sem_consumo_outbox')
        self.assert_effects(self.state(),False)

    def test_35_tampered_command_binding(self):
        r=self.ready()
        for key,value in (('receipt','D1:forged'),('scope','forged'),('canonical_binding','forged')):
            cmd=d.command(d.fixture(),r);cmd[key]=value
            self.run_worker('receive',command=cmd,expect=False)
        self.assert_effects(self.state(),False)

    def test_36_expected_scope_stale(self):
        r=self.decide();s=d.scope(d.fixture());s['revision']=2
        self.run_worker('consume',receipt=r,expected=s,expect=False)
        self.assertEqual(self.state()['source']['outbox'],[])

    def test_37_unlisted_new_operation_blocks(self):
        self.ready()
        self.sql('receiver','INSERT INTO operations VALUES(?,?,0)',('SYN:new','pending'))
        self.run_worker('dispatch',expect=False)
        self.assert_effects(self.state(),False)
        self.assertEqual(self.sql('receiver',"SELECT executions FROM operations WHERE id='SYN:new'")[0][0],0)

    def test_38_receiver_constraint_failure_rolls_back_dedup_and_effect(self):
        self.ready()
        self.sql('receiver',"CREATE TRIGGER synthetic_storage_failure BEFORE UPDATE ON operations WHEN NEW.id='SYN:pendente-2' BEGIN SELECT RAISE(ABORT,'synthetic storage failure'); END")
        out=self.run_worker('dispatch',expect=False)
        self.assertEqual(out['error'],'IntegrityError')
        self.assert_effects(self.state(),False)
        self.sql('receiver','DROP TRIGGER synthetic_storage_failure')
        self.complete()

    def test_39_ack_storage_failure_after_receiver_commit(self):
        self.ready()
        out=self.run_worker('dispatch',ack_readonly=True,expect=False)
        self.assertEqual(out['sqlite_code'],'SQLITE_READONLY')
        s=self.state();self.assert_pending_outbox(s,1);self.assert_effects(s,True)
        out=self.run_worker('dispatch')['result']
        self.assertTrue(out['results'][0]['duplicate'])
        self.assertEqual(self.state()['source']['outbox'][0]['status'],'acked')
        self.assert_effects(self.state(),True)

    def test_40_sqlite_full_after_cas_rolls_back(self):
        r=self.decide()
        self.sql('source','CREATE TABLE synthetic_space(data BLOB)')
        out=self.run_worker('consume',receipt=r,fail_full=True,expect=False)
        self.assertEqual(out['sqlite_code'],'SQLITE_FULL')
        s=self.state();self.assertEqual(s['source']['consumption'][0]['state'],'pending')
        self.assertEqual(s['source']['outbox'],[]);self.assert_effects(s,False)
        self.run_worker('consume',receipt=r);self.complete()

    def test_41_stale_supervisor_failure_and_interaction(self):
        r=self.decide()
        for key in ('supervisor','supervisor_run','failure','failure_run','failure_receipt','interaction'):
            self.sql('source','UPDATE live SET body=?',(d.canonical(d.scope(d.fixture())),))
            self.change_live('source',key,'SYN:stale')
            self.run_worker('consume',receipt=r,expect=False)
            self.assertEqual(self.state()['source']['outbox'],[])

    def test_42_expired_authorization_before_consume(self):
        r=self.decide()
        self.run_worker('consume',receipt=r,now=d.NOW+3600,expect=False)
        s=self.state();self.assertEqual(s['source']['consumption'][0]['state'],'pending')
        self.assertEqual(s['source']['outbox'],[]);self.assert_effects(s,False)

    def test_43_first_delivery_conflicting_pending_payload(self):
        r=self.ready();m=d.fixture();m['pending']=['SYN:op-falha']
        cmd=d.command(m,r)
        self.run_worker('receive',command=cmd,expect=False)
        self.assert_effects(self.state(),False)
        self.complete()

    def test_44_compound_key_unambiguous(self):
        a=d.fixture();a['ticket']='SYN:a/SYN:b';a['interaction']='SYN:c'
        b=d.fixture();b['ticket']='SYN:a';b['interaction']='SYN:b/SYN:c'
        self.assertEqual(a['ticket']+'/'+a['interaction'],b['ticket']+'/'+b['interaction'])
        self.assertNotEqual(d.confirmation_key(a),d.confirmation_key(b))
        r1=self.decide(manifest=a);r2=self.decide(manifest=b)
        self.assertNotEqual(r1,r2)
        self.assertEqual(len(self.state()['source']['canonical_decision']),2)
