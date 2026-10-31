"""Uma única rodada PQBR-119; autorização Board real por snapshot GET, efeitos falsos."""
import asyncio, hashlib, json, time
from pathlib import Path
from temporalio import activity
from runtime_base_h3 import RuntimeBase, FalsosH3
from auth119 import canonical, require, IID, ISSUE, USER

class Falsos119(FalsosH3):
    @activity.defn(name='reler_confirmacao_canonica_falsa')
    async def reler_confirmacao(self, recebido: dict) -> dict:
        self.tentativas_validacao.append(activity.info().attempt)
        require(recebido==self.expected_receipt,'RECEIPT_DIVERGENTE')
        snapshot=json.loads(self.snapshot_path.read_text())
        require(snapshot==self.authorization,'SNAPSHOT_DIVERGENTE')
        require(recebido['authorizationSha256']==hashlib.sha256(canonical(snapshot).encode()).hexdigest(),'BINDING_DIVERGENTE')
        require(snapshot['status']=='accepted' and snapshot['outcome']=='accepted' and snapshot['resolvedByUserId']==USER,'AUTORIA_INVALIDA')
        require(snapshot['interactionId']==IID and snapshot['issueId']==ISSUE,'ID_DIVERGENTE')
        return dict(receipt=recebido,expira_em=self.expira_em)

class Prova119(RuntimeBase):
    async def test_unica_rodada(self):
        # Substituição apenas na nova fixture, antes de abrir qualquer Worker descartável.
        self.fake=Falsos119()
        self.fake.snapshot_path=Path(__file__).parent/'authorization-rechecked.json'
        self.fake.authorization=json.loads(self.fake.snapshot_path.read_text())
        require(json.loads((self.out/'system-info.json').read_text()).get('serverVersion')=='1.32.1','VERSAO_DIVERGENTE')
        h, paused, child=await self.preparar_duas_operacoes()
        # Este é o baseline imediatamente antes do consumo: primeira terminal, segunda aceita.
        (self.out/'estado-antes-consumo.json').write_text(json.dumps(paused,ensure_ascii=False,indent=2)+'\n')
        b=paused['bloqueio']
        scope=dict(supervisor_id=h.id,supervisor_run_id=(await h.describe()).run_id,revisao=paused['revisao'],falha_id=b['operacao_id'],filho_run_id=b['filho_run_id'],registro_falha_receipt=b['registro_id'],pendentes=['segunda'])
        receipt=dict(consumo_key='consumo:'+IID,decisao='accepted',escopo=scope,interaction_id=IID,issue_id=ISSUE,autor=USER,confirmacao_key=self.fake.authorization['idempotencyKey'],timestamp=self.fake.authorization['resolvedAt'],authorizationSha256=hashlib.sha256(canonical(self.fake.authorization).encode()).hexdigest())
        self.fake.expected_receipt=receipt
        self.fake.expira_em=int(time.time())+300
        (self.out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
        await h.signal('confirmar',receipt)
        await self.estado_ate(h,lambda s: list(s['resultados'])==['segunda'])
        # Reentrega do MESMO receipt, não uma segunda rodada/operação.
        await h.signal('confirmar',receipt)
        final=await self.estado_ate(h,lambda s:any(o['estado']=='consumo_duplicado_sem_efeito' for o in s['observacoes']))
        self.assertEqual(len(final['consumidos']),1)
        self.assertEqual(len(final['retomadas']),1)
        self.assertEqual(final['falhas'],paused['falhas'])
        self.assertEqual(final['pendentes'],[])
        self.assertEqual([c['passo'] for c in self.fake.calls],['primeira','segunda'])
        self.assertEqual([c['tentativa'] for c in self.fake.calls],[1,1])
        self.assertEqual(len(self.fake.registros),1)
        self.assertEqual(len(self.fake.eventos_falha),1)
        self.assertEqual(self.fake.tentativas_validacao,[1])
        self.assertEqual((await child.describe()).status.name,'FAILED')
        childhist=await child.fetch_history()
        self.assertEqual(sum(e.HasField('activity_task_failed_event_attributes') for e in childhist.events),1)
        self.assertFalse(any(e.HasField('workflow_execution_continued_as_new_event_attributes') for e in childhist.events))
        await h.signal('fechar')
        closed=await asyncio.wait_for(h.result(),30)
        self.assertEqual(len(closed['retomadas']),1)
        hist=await h.fetch_history()
        self.assertEqual(sum(e.HasField('start_child_workflow_execution_initiated_event_attributes') for e in hist.events),2)
        await self.capture(h)
        result=dict(status='PASS',ticket='PQBR-119',interactionId=IID,authorizationStatus='accepted',roundCount=1,receiptCount=1,receiptDeliveries=2,duplicateReceiptNoEffectCount=1,resumeCount=1,firstStatus='FAILED',firstAttemptCount=1,firstRerunCount=0,secondAttemptCount=1,secondFakeEffectCount=1,externalRealEffectCount=0,canonicalSnapshotValidationActivityAttempts=self.fake.tentativas_validacao,pendingCount=0,serverVersion='1.32.1',calls=self.fake.calls,finalState=closed,limits='GET real no host antes do runtime; Activity isolada valida snapshot/binding, não acessa Paperclip. Consumo no histórico Temporal e replay, sem crash injection, transação distribuída ou exactly-once externo.')
        (self.out/'resultado.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
