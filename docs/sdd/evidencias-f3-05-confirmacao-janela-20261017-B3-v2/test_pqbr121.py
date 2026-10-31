"""Uma prova única B3, sem imports de backends PQBR; somente Activities falsas."""
import asyncio, datetime, hashlib, json, os, pathlib, sqlite3, subprocess, sys, tempfile, time, unittest
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy, WorkflowIDReusePolicy
from temporalio.exceptions import ApplicationError, ChildWorkflowError, ActivityError
from temporalio.service import RetryConfig
from temporalio.worker import Worker, Replayer

NAMESPACE='f3-05-supervisor'
FIRST='first-B3-next-failed-v1'
SECOND='second-B3-next-accepted-v1'
SESSION='session-B3-next-disposable-v1'
SCOPE='scope-B3-next-once-v1'
KEY='pqbr-f3-05-B3-next-single-proof-v2'
IID='ee39501d-3787-470a-b871-7800669759b9'
ISSUE='730f420b-4d74-48be-894c-a79b13c035f2'
USER='eHIQgWDGucnmgW8xT19VvSsypXRdbTr7'
QUEUE='pqbr121-B3-disposable-only'
WIRE={'issueId':ISSUE,'interactionId':IID,'scopeId':SCOPE,'sessionId':SESSION,'operationId':SECOND,'idempotencyKey':KEY}

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def dbopen(path):
 db=sqlite3.connect(path,timeout=3,isolation_level=None)
 db.execute('PRAGMA foreign_keys=ON');db.execute('PRAGMA journal_mode=DELETE');db.execute('PRAGMA synchronous=FULL')
 return db
class Store:
 def __init__(self,path):
  self.path=str(path)
  with dbopen(self.path) as db:
   db.executescript('CREATE TABLE IF NOT EXISTS receipts(id TEXT PRIMARY KEY,idem TEXT UNIQUE,interaction TEXT UNIQUE,binding TEXT,wire TEXT,state TEXT,version INTEGER); CREATE TABLE IF NOT EXISTS outbox(receipt TEXT PRIMARY KEY REFERENCES receipts(id),wire TEXT,state TEXT,version INTEGER); CREATE TABLE IF NOT EXISTS effects(idem TEXT PRIMARY KEY,receipt TEXT,operation TEXT);')
 def issue_consume(self,receipt):
  db=dbopen(self.path)
  try:
   db.execute('BEGIN IMMEDIATE')
   row=db.execute('SELECT binding,state FROM receipts WHERE id=?',(receipt['id'],)).fetchone()
   if row is not None:
    assert row==(digest(receipt),'CONSUMED');db.rollback();return False
   db.execute('INSERT INTO receipts VALUES(?,?,?,?,?,\'ISSUED\',0)',(receipt['id'],KEY,IID,digest(receipt),canonical(WIRE)))
   n=db.execute('UPDATE receipts SET state=\'CONSUMED\',version=version+1 WHERE id=? AND state=\'ISSUED\' AND version=0',(receipt['id'],)).rowcount;assert n==1
   db.execute('INSERT INTO outbox VALUES(?,?,\'READY\',0)',(receipt['id'],canonical(WIRE)));db.commit();return True
  except BaseException:db.rollback();raise
  finally:db.close()
 def claim(self,rid):
  with dbopen(self.path) as db:
   n=db.execute('UPDATE outbox SET state=\'SENDING\',version=version+1 WHERE receipt=? AND state=\'READY\'',(rid,)).rowcount
   return n==1
 def ack(self,rid):
  with dbopen(self.path) as db:
   assert db.execute('UPDATE outbox SET state=\'ACKED\',version=version+1 WHERE receipt=? AND state=\'SENDING\'',(rid,)).rowcount==1
 def summary(self):
  with dbopen(self.path) as db:
   return {'receiptCount':db.execute('SELECT count(*) FROM receipts').fetchone()[0],'outboxCount':db.execute('SELECT count(*) FROM outbox').fetchone()[0],'effectCount':db.execute('SELECT count(*) FROM effects').fetchone()[0],'receiptStates':db.execute('SELECT state,version FROM receipts').fetchall(),'outboxStates':db.execute('SELECT state,version FROM outbox').fetchall()}

@workflow.defn(name='PQBR121B3SyntheticOperation')
class Operation:
 @workflow.run
 async def run(self,p:dict)->dict:
  if p['operation'] not in (FIRST,SECOND) or p['sessionId']!=SESSION:raise ApplicationError('outside fake allowlist',non_retryable=True)
  return await workflow.execute_activity('pqbr121_fake_intervention',p,start_to_close_timeout=timedelta(seconds=10),retry_policy=RetryPolicy(maximum_attempts=1))

@workflow.defn(name='PQBR121B3SyntheticSupervisor')
class Supervisor:
 def __init__(self):
  self.pending=[SECOND];self.accepted=[FIRST,SECOND];self.queue=[];self.consumed={};self.resumes=0;self.duplicates=0;self.first_status='NOT_STARTED';self.second_status='PENDING';self.phase='STARTING';self.close=False
 @workflow.signal
 def confirm(self,r:dict):self.queue.append(r)
 @workflow.signal
 def finish(self):self.close=True
 @workflow.query
 def state(self)->dict:return {'pending':self.pending,'accepted':self.accepted,'consumed':self.consumed,'resumes':self.resumes,'duplicates':self.duplicates,'firstStatus':self.first_status,'secondStatus':self.second_status,'phase':self.phase}
 @workflow.run
 async def run(self,p:dict)->dict:
  if p!=WIRE or workflow.info().namespace!=NAMESPACE or workflow.info().workflow_id!=SESSION:raise ApplicationError('scope mismatch',non_retryable=True)
  try:
   await workflow.execute_child_workflow(Operation.run,{'operation':FIRST,'sessionId':SESSION},id=FIRST,task_queue=QUEUE,retry_policy=RetryPolicy(maximum_attempts=1),id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE)
   raise ApplicationError('first must fail',non_retryable=True)
  except ChildWorkflowError as exc:
   if not isinstance(exc.cause,ActivityError) or not isinstance(exc.cause.cause,ApplicationError) or exc.cause.cause.type!='SyntheticTechnicalFailure':raise
   self.first_status='FAILED'
  await workflow.execute_activity('pqbr121_fake_failure_record',{'operation':FIRST,'status':'FAILED'},start_to_close_timeout=timedelta(seconds=10),retry_policy=RetryPolicy(maximum_attempts=1))
  self.phase='PAUSED'
  while True:
   await workflow.wait_condition(lambda:bool(self.queue) or self.close)
   if not self.queue:
    if self.close and self.second_status=='COMPLETED':return self.state()
    raise ApplicationError('closed while blocked',non_retryable=True)
   r=self.queue.pop(0)
   if r['id'] in self.consumed:
    if self.consumed[r['id']]!=r:raise ApplicationError('duplicate mismatch',non_retryable=True)
    self.duplicates+=1;continue
   if self.second_status!='PENDING' or self.first_status!='FAILED' or r['wire']!=WIRE:raise ApplicationError('resume mismatch',non_retryable=True)
   await workflow.execute_activity('pqbr121_validate_local_receipt',r,start_to_close_timeout=timedelta(seconds=10),retry_policy=RetryPolicy(maximum_attempts=1))
   self.consumed[r['id']]=r;self.resumes+=1;self.phase='RESUMING'
   await workflow.execute_child_workflow(Operation.run,{'operation':SECOND,'sessionId':SESSION,'receiptId':r['id']},id=SECOND,task_queue=QUEUE,retry_policy=RetryPolicy(maximum_attempts=1),id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE)
   self.pending=[];self.second_status='COMPLETED';self.phase='DONE'

class Fakes:
 def __init__(self,path,snapshot,manifest):self.path=str(path);self.snapshot=snapshot;self.manifest=manifest;self.calls=[];self.failure_records=[];self.validation_attempts=[]
 @activity.defn(name='pqbr121_fake_intervention')
 async def intervention(self,p:dict)->dict:
  assert p['sessionId']==SESSION and p['operation'] in (FIRST,SECOND)
  self.calls.append({'operation':p['operation'],'attempt':activity.info().attempt})
  if p['operation']==FIRST:raise ApplicationError('intentional synthetic failure',type='SyntheticTechnicalFailure',non_retryable=True)
  with dbopen(self.path) as db:
   db.execute('BEGIN IMMEDIATE')
   db.execute('INSERT INTO effects VALUES(?,?,?)',(KEY,p['receiptId'],SECOND));db.commit()
  return {'fakeEffect':True,'operation':SECOND}
 @activity.defn(name='pqbr121_fake_failure_record')
 async def record(self,p:dict)->dict:self.failure_records.append(p);return {'recorded_fake':True}
 @activity.defn(name='pqbr121_validate_local_receipt')
 async def validate(self,r:dict)->dict:
  self.validation_attempts.append(activity.info().attempt)
  assert r['wire']==WIRE and r['snapshotHash']==digest(self.snapshot) and r['manifestHash']==digest(self.manifest)
  i=self.snapshot['interaction'];assert i['status']=='accepted' and i['resolvedByUserId']==i['addresseeUserId']==USER
  assert self.manifest['active'] is True and self.manifest['status']=='active'
  now=time.time();assert 0<=now-self.snapshot['observed_at']<=60 and self.snapshot['valid_from']<=now<self.snapshot['valid_until']
  with dbopen(self.path) as db:
   assert db.execute('SELECT binding,state FROM receipts WHERE id=?',(r['id'],)).fetchone()==(digest(r),'CONSUMED')
   assert db.execute('SELECT wire,state FROM outbox WHERE receipt=?',(r['id'],)).fetchone()==(canonical(WIRE),'SENDING')
  return {'valid':True}

@unittest.skipUnless(os.environ.get('PQBR_121_ISOLATED')=='1','opt-in + isolated namespace required')
class Prova121(unittest.IsolatedAsyncioTestCase):
 async def test_unique_B3(self):
  out=pathlib.Path(os.environ['PQBR_CANDIDATE_OUT']);e=pathlib.Path(__file__).parent
  assert json.loads((out.parent/'isolation-gate.json').read_text())['passed']
  assert json.loads((out/'system-info.json').read_text())['serverVersion']=='1.32.1'
  for family in ('-4','-6'):assert not any(x.get('dst')=='default' for x in json.loads(subprocess.check_output(['/usr/bin/ip','-j',family,'route'])))
  snapshot=json.loads((e/'authorization-rechecked.json').read_text());manifest=json.loads((e/'manifest.json').read_text())
  assert time.time()-snapshot['observed_at']<=60
  client=await Client.connect('127.0.0.1:7233',namespace=NAMESPACE,retry_config=RetryConfig(max_retries=0))
  async def until(h,pred):
   async def loop():
    while True:
     s=await h.query('state')
     if pred(s):return s
     await asyncio.sleep(.03)
   return await asyncio.wait_for(loop(),30)
  with tempfile.TemporaryDirectory(prefix='pqbr121-b3-local-') as tmp:
   dbpath=pathlib.Path(tmp)/'receipt-outbox.sqlite';store=Store(dbpath);fake=Fakes(dbpath,snapshot,manifest)
   async with Worker(client,task_queue=QUEUE,workflows=[Supervisor,Operation],activities=[fake.intervention,fake.record,fake.validate],max_cached_workflows=0):
    h=await client.start_workflow(Supervisor.run,WIRE,id=SESSION,task_queue=QUEUE,retry_policy=RetryPolicy(maximum_attempts=1),id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE)
    paused=await until(h,lambda s:s['phase']=='PAUSED');assert paused['pending']==[SECOND] and paused['firstStatus']=='FAILED'
    (out/'state-before-consumption.json').write_text(json.dumps(paused,indent=2)+'\n')
    receipt={'id':'receipt:'+IID,'wire':WIRE,'snapshotHash':digest(snapshot),'manifestHash':digest(manifest),'acceptedBy':USER,'resolvedAt':snapshot['interaction']['resolvedAt']}
    assert store.issue_consume(receipt) is True
    store=Store(dbpath);assert store.issue_consume(receipt) is False
    assert store.claim(receipt['id']) is True and Store(dbpath).claim(receipt['id']) is False
    # Novo processo abre o SQLite após commit. Não é outra execução do ensaio.
    before=json.loads(subprocess.check_output([sys.executable,'-I','-B','-c','import sqlite3,json,sys; c=sqlite3.connect(sys.argv[1]); print(json.dumps([c.execute("SELECT count(*) FROM receipts").fetchone()[0],c.execute("SELECT count(*) FROM outbox").fetchone()[0],c.execute("SELECT state FROM outbox").fetchone()[0]]))',str(dbpath)]))
    assert before==[1,1,'SENDING']
    await h.signal('confirm',receipt)
    completed=await until(h,lambda s:s['phase']=='DONE');assert completed['resumes']==1
    store.ack(receipt['id']);assert Store(dbpath).issue_consume(receipt) is False and Store(dbpath).claim(receipt['id']) is False
    # Reentrega idêntica no MESMO run para provar dedup, não nova operação/rodada.
    await h.signal('confirm',receipt);final=await until(h,lambda s:s['duplicates']==1)
    assert final['resumes']==1 and len(final['consumed'])==1 and final['pending']==[]
    assert fake.calls==[{'operation':FIRST,'attempt':1},{'operation':SECOND,'attempt':1}] and len(fake.failure_records)==1 and fake.validation_attempts==[1]
    await h.signal('finish');closed=await asyncio.wait_for(h.result(),30)
    histories=[]
    for wid in (SESSION,FIRST,SECOND):
     handle=client.get_workflow_handle(wid);desc=await handle.describe();hist=await handle.fetch_history()
     if wid==FIRST:assert desc.status.name=='FAILED' and sum(ev.HasField('activity_task_failed_event_attributes') for ev in hist.events)==1
     else:assert desc.status.name=='COMPLETED'
     assert not any(ev.HasField('workflow_execution_continued_as_new_event_attributes') for ev in hist.events)
     (out/(wid+'.history.json')).write_text(hist.to_json()+'\n')
     await Replayer(workflows=[Supervisor,Operation],namespace=NAMESPACE).replay_workflow(hist,raise_on_replay_failure=True)
     histories.append({'workflowId':wid,'status':desc.status.name,'events':len(hist.events),'replay':'ok'})
    summary=Store(dbpath).summary();assert summary['receiptCount']==summary['outboxCount']==summary['effectCount']==1
    assert summary['outboxStates']==[('ACKED',2)]
    result={'status':'PASS','ticket':'PQBR-121','interactionId':IID,'roundCount':1,'firstStatus':'FAILED','firstAttemptCount':1,'firstRerunCount':0,'secondAttemptCount':1,'secondFakeEffectCount':1,'resumeCount':1,'receiptDeliveries':2,'duplicateReceiptNoEffectCount':1,'externalRealEffectCount':0,'serverVersion':'1.32.1','scope':WIRE,'durableLocal':summary,'newProcessReadAfterCommit':before,'calls':fake.calls,'histories':histories,'finalState':closed,'limits':'GET Board real no host; snapshot com freshness 60s validado em Activity fake; receipt/outbox SQLite FULL local e dedup no histórico Temporal descartável. Sem crash injection, atomicidade distribuída, fencing ou exactly-once externo. Harness novo separado, sem mudar candidatas/produção.'}
    (out/'resultado.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  assert not dbpath.exists()
  (out/'temporary-storage-cleaned.json').write_text(json.dumps({'sqliteTemporaryDirectoryRemoved':True})+'\n')
