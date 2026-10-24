import json, subprocess, hashlib
from datetime import datetime, timezone
from pathlib import Path
ISSUE='d3b2eb41-63e5-4e7e-8cb7-06672e3ddab9'
IID='815e9e44-cf90-45b4-86a2-23aafd45d0fc'
USER='eHIQgWDGucnmgW8xT19VvSsypXRdbTr7'
COMPANY='be3980d6-51ae-4cee-b85f-923b4568188c'
DESCRIPTION='Teste E2E único autorizado para o supervisor de sessão. Escopo: primeira já está em falha terminal e nunca deve ser repetida; segunda já foi aceita e pode retomar uma única vez após confirmação. Execução em Temporal Server 1.32.1 efêmero, rede interna sem saída, sem Workers persistentes, usando Activities falsas e armazenamento temporário. Nenhuma ação externa, integração real com Camofox/Hindsight, publicação ou produção. Aprovar autoriza somente essa execução única.'
PROMPT='Autoriza executar uma única vez o teste descrito neste ticket, apenas no Temporal descartável e com operações sintéticas?'
DETAILS='Ticket PQBR-119. Primeira: operação sintética já em falha terminal; não repetir. Segunda: operação sintética já aceita e pendente; após aprovação, retomar exatamente uma vez. Temporal Server 1.32.1 efêmero, rede interna sem saída, Activities falsas e armazenamento temporário. Sem Workers persistentes, ação externa, Camofox/Hindsight reais, publicação ou produção. Aprovação autoriza somente esta execução única.'
def require(ok, label):
    if not ok: raise RuntimeError(label)
def canonical(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def get(*args):
    p=subprocess.run(['/home/pc/.hermes/node/bin/node','/home/pc/.paperclip/cli/current/node_modules/paperclipai/dist/index.js','issue',*args,'--json'],capture_output=True,text=True,timeout=60)
    require(p.returncode==0,'GET_CLI_FALHOU')
    return json.loads(p.stdout)
def read_authorization():
    ticket=get('get',ISSUE)
    for k,v in dict(id=ISSUE,companyId=COMPANY,identifier='PQBR-119',status='backlog',createdByUserId=USER,responsibleUserId=USER,description=DESCRIPTION).items(): require(ticket.get(k)==v,'TICKET_DIVERGENTE_'+k)
    for k in ('createdByAgentId','executionRunId','checkoutRunId','executionLockedAt','completedAt','cancelledAt'): require(ticket.get(k) is None,'TICKET_USADO_OU_AUTOR_DIVERGENTE_'+k)
    rows=get('interactions',ISSUE)
    require(isinstance(rows,list),'ENVELOPE_INVALIDO')
    require(len(rows)==1 and rows[0].get('id')==IID,'INTERACAO_DIVERGENTE')
    r=rows[0]
    for k,v in dict(id=IID,issueId=ISSUE,companyId=COMPANY,kind='request_confirmation',status='accepted',continuationPolicy='none',requestedResolverPolicy='human_only',effectiveResolverPolicy='human_only',resolverPolicy='human_only',resolverPolicyProvenance='explicit',effectiveResolverPolicySource='requested',addresseeUserId=USER,createdByUserId=USER,resolvedByUserId=USER,idempotencyKey='pqbr-f3-05-pqbr-119-synthetic-e2e-20261017-v1').items(): require(r.get(k)==v,'INTERACAO_DIVERGENTE_'+k)
    for k in ('createdByAgentId','addresseeAgentId','resolvedByAgentId','resolvedByRunId','sourceRunId'): require(r.get(k) is None,'AGENTE_OU_RUN_INESPERADO_'+k)
    require(r.get('result')=={'version':1,'outcome':'accepted'},'ACEITE_FALSO')
    require(r.get('payload')==dict(version=1,prompt=PROMPT,acceptLabel='Autorizar execução única',rejectLabel='Não autorizar',allowDeclineReason=True,detailsMarkdown=DETAILS,supersedeOnUserComment=False),'ESCOPO_DIVERGENTE')
    require(datetime.fromisoformat(r['resolvedAt'].replace('Z','+00:00')).utcoffset() is not None,'TIMESTAMP_INVALIDO')
    return dict(ticket='PQBR-119',issueId=ISSUE,interactionId=IID,companyId=COMPANY,userId=USER,resolvedByUserId=USER,resolvedByAgentId=None,resolvedByRunId=None,status='accepted',outcome='accepted',requestedResolverPolicy='human_only',effectiveResolverPolicy='human_only',continuationPolicy='none',idempotencyKey=r['idempotencyKey'],resolvedAt=r['resolvedAt'],description=DESCRIPTION,prompt=PROMPT,detailsMarkdown=DETAILS)
