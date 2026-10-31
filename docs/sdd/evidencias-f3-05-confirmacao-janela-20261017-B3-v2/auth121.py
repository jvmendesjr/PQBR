import datetime, hashlib, json, os, pathlib, subprocess, time
ROOT=pathlib.Path('/home/pc/Workspace/PQBR')
E=ROOT/'docs/sdd/evidencias-f3-05-confirmacao-janela-20261017-B3-v2'
USER='eHIQgWDGucnmgW8xT19VvSsypXRdbTr7'
ISSUE='730f420b-4d74-48be-894c-a79b13c035f2'
IID='ee39501d-3787-470a-b871-7800669759b9'
KEY='pqbr-f3-05-B3-next-single-proof-v2'
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def require(ok,msg):
 if not ok:raise RuntimeError('BLOQUEIO: '+msg)
def durable(path,obj):
 temp=path.with_suffix(path.suffix+'.tmp')
 with temp.open('w') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(temp,path);fd=os.open(path.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
def read_authorization(activate=False):
 m=json.loads((E/'manifest.json').read_text());h=pathlib.Path.home()
 cli=[str(h/'.hermes/node/bin/node'),str(h/'.paperclip/cli/current/node_modules/paperclipai/dist/index.js')]
 def get(args):
  r=subprocess.run(cli+args+['--json'],capture_output=True,text=True,check=True,timeout=30);return json.loads(r.stdout)
 rows=get(['issue','interactions',ISSUE]);require(isinstance(rows,list),'Formato de interações')
 matches=[i for i in rows if i.get('id')==IID];require(len(matches)==1,'Interação não única');i=matches[0]
 t=get(['issue','get',ISSUE]);now=time.time()
 require(i.get('id')==m['interactionId']==IID and i.get('issueId')==m['issueId']==ISSUE,'IDs reais')
 require(i.get('companyId')==t.get('companyId')==m['companyId']=='be3980d6-51ae-4cee-b85f-923b4568188c','Empresa')
 require(i.get('kind')=='request_confirmation' and i.get('status')=='accepted','Status canônico')
 require(i.get('resolvedByUserId')==i.get('addresseeUserId')==i.get('createdByUserId')==m['board']['userId']==USER,'Humano destinatário/resolvedor')
 require(all(i.get(k) is None for k in ['createdByAgentId','addresseeAgentId','resolvedByAgentId','resolvedByRunId','sourceRunId']),'Agente/run')
 require(all(i.get(k)=='human_only' for k in ['requestedResolverPolicy','effectiveResolverPolicy','resolverPolicy']) and i.get('continuationPolicy')=='none','Políticas')
 require(i.get('idempotencyKey')==m['idempotencyKey']==KEY,'Idempotência')
 require(i.get('payload')==m['confirmation_payload_exact']==m['confirmation_request_exact']['payload'],'Payload literal')
 require(m['valid_from']=='2026-10-17T19:15:00-03:00' and m['valid_until']=='2026-10-18T19:15:00-03:00','Janela literal')
 start=int(datetime.datetime.fromisoformat(m['valid_from']).timestamp());end=int(datetime.datetime.fromisoformat(m['valid_until']).timestamp())
 require(m['valid_from_unix_utc']==start and m['valid_until_unix_utc']==end and start<=now<end,'Validade/relógio UTC')
 resolved=datetime.datetime.fromisoformat(i['resolvedAt'].replace('Z','+00:00')).timestamp();require(start<=resolved<=now,'Timestamp do aceite')
 require(m['scope']=={'scopeId':'scope-B3-next-once-v1','sessionId':'session-B3-next-disposable-v1','operationId':'second-B3-next-accepted-v1','idempotencyKey':KEY} and m['max_snapshot_age']==60,'Escopo/freshness')
 require(t.get('description')==m['issue_description_exact'] and t.get('identifier')==m['shortname']=='PQBR-121' and t.get('status')=='backlog','Ticket literal/estado')
 require(t.get('assigneeAgentId') is None and t.get('createdByAgentId') is None and t.get('createdByUserId')==USER,'Ticket humano/sem agente')
 # O contrato instalado usa result.outcome, não result.decision. Campo ausente não é pré-condição.
 result=i.get('result')
 require(result is None or isinstance(result,dict),'Shape contraditório de result')
 if isinstance(result,dict) and 'outcome' in result:require(result['outcome']=='accepted','Contradição em result.outcome')
 if activate:require(m['status']=='awaiting_paperclip_approval' and m['active'] is False,'Manifesto não pendente')
 else:require(m['status']=='active' and m['active'] is True,'Manifesto não ativo')
 projection={k:i.get(k) for k in ['id','issueId','companyId','kind','status','continuationPolicy','requestedResolverPolicy','effectiveResolverPolicy','resolverPolicy','resolverPolicyProvenance','effectiveResolverPolicySource','idempotencyKey','createdByAgentId','addresseeAgentId','addresseeUserId','createdByUserId','resolvedByAgentId','resolvedByRunId','resolvedByUserId','sourceRunId','resolvedAt','payload']}
 projection['result_outcome']=result.get('outcome') if isinstance(result,dict) else None
 snapshot={'interaction':projection,'issue':{k:t.get(k) for k in ['id','identifier','companyId','status','description','createdByUserId','assigneeAgentId']},'observed_at':now,'scope':m['scope'],'valid_from':start,'valid_until':end,'max_snapshot_age':60,'board':m['board']}
 if activate:
  require(not (E/'manifest-awaiting-original.json').exists(),'Ativação anterior já registrada')
  durable(E/'manifest-awaiting-original.json',m)
  m.update(status='active',active=True,approval_status='accepted',activated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),accepted_at_utc=i['resolvedAt'])
  durable(E/'manifest.json',m)
  durable(E/'approval-validation.json',{'validated':True,'shape':'status accepted; result.outcome accepted quando presente; result.decision não requerido','snapshot_projected':snapshot,'manifest_sha256':digest(m)})
 else:durable(E/'authorization-rechecked.json',snapshot)
 return snapshot
if __name__=='__main__':
 s=read_authorization(activate=True);print(json.dumps({'validated':True,'status':s['interaction']['status'],'outcome':s['interaction']['result_outcome'],'manifest_active':True,'observed_at':s['observed_at']},ensure_ascii=False))
