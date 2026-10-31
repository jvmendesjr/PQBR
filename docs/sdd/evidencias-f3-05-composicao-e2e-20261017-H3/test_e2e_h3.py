"""E2E H3 opt-in; todas as identidades e efeitos são fixtures sintéticas."""
import asyncio
from copy import deepcopy
from dataclasses import replace
import json
import time
from temporalio import activity
from pqbr.contratos import TriagemCorrecao, ResultadoIntervencao
from pqbr.workflows.correcao import PedidoCorrecao, Tentativa
from runtime_base_h3 import RuntimeBase
from modelos import Escopo, Contexto, EventoVinculado, Bloqueado, exigir
from adaptador_confirmacao import AdaptadorConfirmacao
from fakes import RelogioFake, VinculoExistenteFake, PaperclipFake
from ponte_h3 import PortaSupervisorTemporal, ValidadorCanonico


class ComposicaoH3(RuntimeBase):
    async def preparar(self, canal='discord'):
        h, paused, child = await self.preparar_duas_operacoes()
        self.h, self.paused, self.child = h, paused, child
        self.trilha = []
        self.relogio = RelogioFake()
        self.relogio.valor = int(time.time())
        self.vinculo = VinculoExistenteFake()
        b = paused['bloqueio']
        run = (await h.describe()).run_id
        escopo = Escopo(h.id, run, paused['revisao'], b['operacao_id'], b['filho_run_id'],
                        b['registro_id'], tuple(paused['pendentes']))
        self.ctx = Contexto('FAKE-ticket-existente-H3', escopo,
                            self.relogio.agora(), self.relogio.agora()+600)
        self.paperclip = PaperclipFake(self.ctx, self.vinculo, self.relogio, self.trilha)
        self.porta = PortaSupervisorTemporal(self.ctx, self.trilha)
        self.adapter = AdaptadorConfirmacao(self.paperclip, self.vinculo, self.porta, self.relogio)
        self.fake.ctx, self.fake.paperclip, self.fake.vinculo = self.ctx, self.paperclip, self.vinculo
        self.fake.relogio, self.fake.trilha = self.relogio, self.trilha
        self.iid = self.adapter.abrir(self.ctx)
        self.assertEqual(self.adapter.abrir(self.ctx), self.iid)
        self.assertEqual(len(self.paperclip.registros), 1)
        record = self.paperclip.registros[self.iid]
        self.assertEqual(record['continuationPolicy'], 'none')
        self.assertEqual(record['effectiveResolverPolicy'], 'human_only')
        self.assertEqual(record['kind'], 'request_confirmation')
        self.assertIsNone(record['addresseeAgentId'])
        self.assertNotIn('target', record['payload'])
        await self.seguro()
        return h

    def evento(self, decisao='accepted', **alteracoes):
        e = EventoVinculado(self.vinculo.usuario, 'discord', self.ctx.issue_id, self.iid,
                            self.ctx.escopo.revisao, self.ctx.escopo, decisao, self.relogio.agora())
        e = replace(e, **alteracoes)
        self.vinculo.registrar_fixture('FAKE-evento', e)
        return e

    def decidir(self, canal='discord', decisao='accepted'):
        if canal == 'painel':
            self.paperclip.painel_decidir_fixture(self.iid, decisao)
            return self.adapter.pelo_painel(self.ctx, self.iid)
        self.evento(decisao)
        return self.adapter.pelo_discord(self.ctx, self.iid, 'FAKE-evento')

    async def seguro(self):
        # Query prova processamento; sleep sozinho não serve como ACK.
        state = await self.h.query('estado')
        self.assertEqual(state['pendentes'], ['segunda'])
        self.assertEqual(state['resultados'], {})
        self.assertEqual(state['consumidos'], {})
        self.assertEqual(state['retomadas'], [])
        self.assertEqual(state['falhas'], self.paused['falhas'])
        self.assertTrue(state['admissao_fechada'])
        self.assertIsNotNone(state['bloqueio'])
        self.assertEqual([c['passo'] for c in self.fake.calls], ['primeira'])
        self.assertEqual((await self.child.describe()).status.name, 'FAILED')
        return state

    async def entregar(self, receipt=None, rejeitado=False, perder_ack=False):
        r = deepcopy(receipt if receipt is not None else self.porta.saida[-1])
        old = await self.h.query('estado')
        await self.h.signal('confirmar', r)
        if rejeitado:
            state = await self.estado_ate(self.h, lambda s: s['recibos_rejeitados'] > old['recibos_rejeitados'])
            await self.seguro()
        else:
            state = await self.estado_ate(self.h, lambda s: r['consumo_key'] in s['consumidos'])
            self.assertEqual(state['consumidos'][r['consumo_key']], r)
            if perder_ack:
                self.trilha.append(['ACK_perdido_depois_consumo', r['consumo_key']])
                raise TimeoutError('ACK FAKE perdido; resultado consultável no workflow')
        return state

    async def aprovado(self, canal, ack=False):
        await self.preparar(canal)
        # Nem comando legado correlacionado nem interação pending liberam a fila.
        await self.h.signal('retomar', self.comando(self.paused))
        await self.estado_ate(self.h, lambda s: any(o['estado']=='retomada_crua_recusada' for o in s['observacoes']))
        with self.assertRaises(Bloqueado):
            self.adapter.pelo_painel(self.ctx, self.iid)
        await self.seguro()
        # Recria SOMENTE workers sintéticos enquanto pausado.
        await self.stack.aclose()
        await self.abrir_workers()
        await self.seguro()
        self.assertEqual(self.decidir(canal), 'enfileirado_sem_ack')
        # Decisão gravada/relida ainda não é execução: ponte não envia automaticamente.
        await self.seguro()
        persisted = next(i for i,e in enumerate(self.trilha) if e[0]=='decisao_persistida')
        queued = next(i for i,e in enumerate(self.trilha) if e[0]=='receipt_enfileirado_sem_ack')
        self.assertTrue(any(e[0]=='registro_relido' for e in self.trilha[persisted+1:queued]))
        if ack:
            with self.assertRaises(TimeoutError):
                await self.entregar(perder_ack=True)
        else:
            await self.entregar()
        final = await self.estado_ate(self.h, lambda s: list(s['resultados']) == ['segunda'])
        # Reconstrução só do adaptador + entrega por outro canal converge à mesma interação.
        self.adapter = AdaptadorConfirmacao(self.paperclip, self.vinculo, self.porta, self.relogio)
        self.decidir('painel' if canal == 'discord' else 'discord')
        await asyncio.gather(*(self.h.signal('confirmar', self.porta.saida[-1]) for _ in range(3)))
        await self.estado_ate(self.h, lambda s: sum(o['estado']=='consumo_duplicado_sem_efeito' for o in s['observacoes'])>=3)
        await self.stack.aclose()
        await self.abrir_workers()
        await self.entregar()  # ACK correlacionado sobre estado reconstruído do histórico.
        await self.h.signal('solicitar', self.envelope('primeira', 'falha-tecnica'))
        await self.h.signal('solicitar', self.envelope('segunda', 'falha falsa'))
        await self.h.signal('fechar')
        result = await asyncio.wait_for(self.h.result(), 30)
        self.assertEqual(len(result['consumidos']), 1)
        self.assertEqual(len(result['retomadas']), 1)
        self.assertEqual(result['pendentes'], [])
        self.assertEqual(result['falhas'], self.paused['falhas'])
        self.assertEqual([c['passo'] for c in self.fake.calls], ['primeira','segunda'])
        self.assertTrue(all(c['tentativa']==1 for c in self.fake.calls))
        self.assertEqual(len(self.fake.eventos_falha), 1)
        self.assertEqual(len(self.fake.registros), 1)
        self.assertEqual(self.fake.max_sessao[self.sessao], 1)
        self.assertEqual((await self.child.describe()).status.name, 'FAILED')
        hist = await self.h.fetch_history()
        self.assertEqual(sum(e.HasField('start_child_workflow_execution_initiated_event_attributes') for e in hist.events), 2)
        self.assertEqual(self.fake.tentativas_validacao, [1])
        self.assertEqual(len(self.paperclip.registros), 1)
        await self.capture(self.h)
        self.evidencia(canal=canal, resultado=result, ack_perdido=ack)

    def evidencia(self, **dados):
        (self.out/(self._testMethodName+'.e2e.json')).write_text(json.dumps(dict(
            **dados, trilha=self.trilha, interacoes=self.paperclip.registros,
            chamadas=self.fake.calls, tentativas_validacao=self.fake.tentativas_validacao),
            ensure_ascii=False, indent=2)+'\n')

    async def test_01_painel(self):
        await self.aprovado('painel')

    async def test_02_discord_ack_perdido_replay(self):
        await self.aprovado('discord', ack=True)

    async def test_03_negativa(self):
        await self.preparar()
        self.assertEqual(self.decidir(decisao='rejected'), 'bloqueado:rejected')
        self.assertEqual(self.porta.saida, [])
        self.evidencia(estado=await self.seguro())

    async def test_04_identidade_nao_autorizada(self):
        await self.preparar()
        self.evento(usuario_paperclip='FAKE-intruso')
        with self.assertRaises(Bloqueado):
            self.adapter.pelo_discord(self.ctx,self.iid,'FAKE-evento')
        self.assertEqual(self.porta.saida, [])
        self.evidencia(estado=await self.seguro())

    async def test_05_ticket_stale(self):
        await self.preparar()
        self.evento(issue_id='FAKE-outro-ticket')
        with self.assertRaises(Bloqueado):
            self.adapter.pelo_discord(self.ctx,self.iid,'FAKE-evento')
        self.evidencia(estado=await self.seguro())

    async def test_06_revisao_stale(self):
        await self.preparar()
        self.evento(revisao=self.ctx.escopo.revisao+1)
        with self.assertRaises(Bloqueado):
            self.adapter.pelo_discord(self.ctx,self.iid,'FAKE-evento')
        self.evidencia(estado=await self.seguro())

    async def test_07_escopo_stale(self):
        await self.preparar()
        self.evento(escopo=replace(self.ctx.escopo, pendentes=('FAKE-nova',)))
        with self.assertRaises(Bloqueado):
            self.adapter.pelo_discord(self.ctx,self.iid,'FAKE-evento')
        self.evidencia(estado=await self.seguro())

    async def test_08_receipt_incerto(self):
        await self.preparar()
        self.paperclip.perder_resposta.add('resolver')
        with self.assertRaises(TimeoutError):
            self.decidir()
        self.assertEqual(self.porta.saida, [])
        self.assertEqual(self.paperclip.registros[self.iid]['status'], 'accepted')
        self.evidencia(estado=await self.seguro())

    async def test_09_persistencia_decisao_falha(self):
        await self.preparar()
        self.paperclip.falhar.add('resolver')
        with self.assertRaises(ConnectionError):
            self.decidir()
        self.assertEqual(self.paperclip.registros[self.iid]['status'], 'pending')
        self.evidencia(estado=await self.seguro())

    async def test_10_registro_falha_indisponivel(self):
        self.fake.falhar_registro = True
        await self.preparar()
        self.decidir()
        await self.entregar(rejeitado=True)
        self.assertEqual(self.fake.tentativas_validacao, [])
        self.assertEqual(len(self.fake.tentativas_registro), 1)
        self.evidencia(estado=await self.seguro())

    async def test_11_receipt_registro_invalido(self):
        self.fake.recibo_invalido = True
        await self.preparar()
        self.decidir()
        await self.entregar(rejeitado=True)
        self.evidencia(estado=await self.seguro())

    async def test_12_receipt_forjado_no_transporte(self):
        await self.preparar()
        self.decidir()
        r = deepcopy(self.porta.saida[-1]); r['autor']='FAKE-intruso'
        await self.entregar(r,rejeitado=True)
        self.assertEqual(self.fake.tentativas_validacao,[1])
        self.evidencia(estado=await self.seguro())

    async def test_13_releitura_receptor_falha(self):
        await self.preparar()
        self.decidir()
        self.paperclip.falhar.add('ler')
        await self.entregar(rejeitado=True)
        self.assertEqual(self.fake.tentativas_validacao,[1])
        self.evidencia(estado=await self.seguro())

    async def test_14_receipt_ambiguo(self):
        await self.preparar()
        self.decidir()
        self.paperclip.registros['FAKE-duplicado']=deepcopy(self.paperclip.registros[self.iid])
        await self.entregar(rejeitado=True)
        self.evidencia(estado=await self.seguro())

    async def test_15_escopo_stale_transporte(self):
        await self.preparar()
        self.decidir()
        r=deepcopy(self.porta.saida[-1]); r['escopo']['pendentes']=['primeira','segunda']
        await self.entregar(r,rejeitado=True)
        self.assertEqual(self.fake.tentativas_validacao,[])
        self.evidencia(estado=await self.seguro())

    async def test_16_expirado(self):
        await self.preparar()
        self.decidir()
        self.relogio.valor=self.ctx.expira_em
        await self.entregar(rejeitado=True)
        self.evidencia(estado=await self.seguro())

    async def test_17_persistencia_receptor_falha(self):
        await self.preparar()
        self.decidir()
        self.fake.falhar_validacao=True
        await self.entregar(rejeitado=True)
        self.assertEqual(self.fake.tentativas_validacao,[1])
        self.evidencia(estado=await self.seguro())

    async def test_18_mesma_chave_receipt_divergente_apos_consumo(self):
        await self.preparar()
        self.decidir()
        await self.entregar()
        await self.estado_ate(self.h, lambda s: 'segunda' in s['resultados'])
        r=deepcopy(self.porta.saida[-1]);r['registro_hash']='FAKE-adulterado'
        before=await self.h.query('estado')
        await self.h.signal('confirmar',r)
        state=await self.estado_ate(self.h,lambda s:s['recibos_rejeitados']>before['recibos_rejeitados'])
        self.assertEqual(len(state['retomadas']),1)
        self.assertEqual([c['passo'] for c in self.fake.calls],['primeira','segunda'])
        self.evidencia(estado=state)
