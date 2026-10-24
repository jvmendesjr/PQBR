"""APENAS FAKES em memória. Não há cliente HTTP, notificações, comandos ou durabilidade real."""
from collections import Counter
from copy import deepcopy
from dataclasses import replace
import json
from threading import RLock
from modelos import (Contexto, Escopo, EventoVinculado, exigir, iso, timestamp)
from adaptador_confirmacao import projetar_receipt


class RelogioFake:
    def __init__(self):
        self.valor = 1_800_000_000

    def agora(self):
        return self.valor


class VinculoExistenteFake:
    """Fixture do vínculo JÁ existente. Não configura usuário, bot ou credenciais reais."""
    def __init__(self):
        self.usuario = 'FAKE-paperclip-owner'
        self.conta_discord = 'FAKE-discord-ja-vinculada'
        self.canal_permitido = 'FAKE-canal-privado'
        self.eventos = {}
        self.ativo = True
        self.chamadas = Counter()

    def autorizador(self):
        self.chamadas['autorizador'] += 1
        exigir(self.ativo and bool(self.usuario), 'vinculo_indisponivel')
        return self.usuario

    def registrar_fixture(self, evento_id, evento, conta=None, canal=None, tipo='decisao'):
        self.eventos[evento_id] = (evento, self.conta_discord if conta is None else conta,
                                   self.canal_permitido if canal is None else canal, tipo)

    def evento(self, evento_id, canal):
        self.chamadas['evento'] += 1
        exigir(self.ativo and canal == 'discord' and evento_id in self.eventos, 'evento_inexistente')
        evento, conta, recurso, tipo = self.eventos[evento_id]
        exigir(conta == self.conta_discord and recurso == self.canal_permitido
               and tipo == 'decisao', 'origem_sem_decisao_autenticada')
        exigir(evento.usuario_paperclip == self.usuario, 'vinculo_usuario_divergente')
        return evento


class PaperclipFake:
    """Um ticket preexistente, uma interação canônica. Não tem porta criar ticket/avisar."""
    def __init__(self, ctx, vinculo, relogio, trilha):
        self.ctx, self.vinculo, self.relogio, self.trilha = ctx, vinculo, relogio, trilha
        self.registros, self.chaves = {}, {}
        self.chamadas = Counter()
        self.falhar, self.perder_resposta = set(), set()
        self.antes_resolver, self.depois_resolver, self.antes_ler = None, None, None
        self.lock = RLock()

    def _inicio(self, op):
        self.chamadas[op] += 1
        self.trilha.append(['paperclip:' + op])
        if op in self.falhar:
            raise ConnectionError('API FAKE indisponivel:' + op)

    def _resposta(self, op, valor):
        if op in self.perder_resposta:
            self.perder_resposta.remove(op)
            raise TimeoutError('resposta FAKE perdida:' + op)
        return deepcopy(valor)

    def criar_interacao(self, issue_id, corpo):
        with self.lock:
            self._inicio('criar')
            exigir(issue_id == self.ctx.issue_id, 'ticket_fake_ausente')
            k = (issue_id, corpo['idempotencyKey'])
            if k in self.chaves:
                r = self.registros[self.chaves[k]]
                for campo, valor in corpo.items():
                    if campo == 'resolverPolicy':
                        exigir(r['requestedResolverPolicy'] == valor, 'chave_divergente')
                    else:
                        exigir(r.get(campo) == valor, 'chave_divergente')
                return self._resposta('criar', r)
            exigir(corpo['kind'] == 'request_confirmation' and corpo['resolverPolicy'] == 'human_only'
                   and corpo['continuationPolicy'] == 'none' and corpo['addresseeAgentId'] is None
                   and corpo['addresseeUserId'] == self.vinculo.autorizador(), 'criacao_insegura')
            exigir(not any(k in corpo['payload'] for k in ('target', 'toolAction', 'secretProposal')),
                   'alvo_ativo_inadmissivel')
            r = deepcopy(corpo)
            r.pop('resolverPolicy')
            r.update(id='FAKE-interaction-' + str(len(self.registros) + 1), issueId=issue_id,
                     status='pending', requestedResolverPolicy='human_only',
                     effectiveResolverPolicy='human_only', resolvedByUserId=None,
                     resolvedByAgentId=None, resolvedByRunId=None, resolvedAt=None,
                     result=None, createdAt=iso(self.relogio.agora()), updatedAt=iso(self.relogio.agora()))
            self.registros[r['id']] = r
            self.chaves[k] = r['id']
            self.trilha.append(['interacao_persistida', issue_id, r['id']])
            return self._resposta('criar', r)

    def listar_interacoes(self, issue_id):
        with self.lock:
            self._inicio('ler')
            if self.antes_ler:
                self.antes_ler()
            exigir(issue_id == self.ctx.issue_id, 'ticket_fake_ausente')
            registros = [r for r in self.registros.values() if r['issueId'] == issue_id]
            self.trilha.append(['registro_relido', issue_id])
            return self._resposta('ler', registros)

    def resolver_como_humano(self, evento):
        with self.lock:
            self._inicio('resolver')
            if self.antes_resolver:
                self.antes_resolver()
            exigir(evento.usuario_paperclip == self.vinculo.autorizador(), 'somente_humano_vinculado')
            exigir(evento.issue_id == self.ctx.issue_id and evento.interaction_id in self.registros,
                   'correlacao_invalida')
            r = self.registros[evento.interaction_id]
            manifesto = json.loads(r['payload']['detailsMarkdown'].split('\n', 1)[1])
            exigir(evento.escopo == self.ctx.escopo and evento.revisao == manifesto['escopo']['revisao'],
                   'cas_revisao')
            exigir(self.relogio.agora() < manifesto['expiraEm'], 'cas_expiracao')
            exigir(r['effectiveResolverPolicy'] == 'human_only' and r['continuationPolicy'] == 'none'
                   and r['addresseeAgentId'] is None, 'cas_politica')
            exigir(evento.decisao in ('accepted', 'rejected'), 'decisao_invalida')
            if r['status'] != 'pending':
                exigir(r['status'] == evento.decisao and r['resolvedByUserId'] == evento.usuario_paperclip,
                       'cas_decisao_conflitante')
                return self._resposta('resolver', r)
            r.update(status=evento.decisao, result={'version': 1, 'outcome': evento.decisao},
                     resolvedByUserId=evento.usuario_paperclip,
                     resolvedAt=iso(self.relogio.agora()), updatedAt=iso(self.relogio.agora()))
            self.trilha.append(['decisao_persistida', r['issueId'], r['id'], evento.decisao])
            if self.depois_resolver:
                self.depois_resolver()
            return self._resposta('resolver', r)

    def painel_decidir_fixture(self, interaction_id, decisao='accepted', usuario=None):
        return self.resolver_como_humano(EventoVinculado(
            self.vinculo.usuario if usuario is None else usuario, 'paperclip', self.ctx.issue_id,
            interaction_id, self.ctx.escopo.revisao, self.ctx.escopo, decisao, self.relogio.agora()))


class SupervisorFake:
    def __init__(self, ctx, paperclip, vinculo, relogio, trilha):
        self.ctx, self.paperclip, self.vinculo, self.relogio = ctx, paperclip, vinculo, relogio
        self.trilha = trilha
        self.atual = ctx.escopo
        self.elegiveis_na_falha = frozenset(ctx.escopo.pendentes)
        self.aceitos = self.elegiveis_na_falha | {ctx.escopo.falha_id, 'FAKE-ja-concluida'}
        self.terminais = {ctx.escopo.falha_id, 'FAKE-ja-concluida'}
        self.consumidos, self.executados, self.receipts = {}, [], {}
        self.chamadas = Counter()
        self.bloqueado, self.admissao_fechada = True, True
        self.falhar, self.perder_ack = False, False
        self.lock = RLock()

    def consultar(self):
        self.chamadas['consultar'] += 1
        exigir(self.bloqueado, 'supervisor_nao_bloqueado')
        return self.atual

    def retomar(self, receipt):
        with self.lock:
            self.chamadas['retomar'] += 1
            self.trilha.append(['receptor_fake_chamado', receipt.interaction_id])
            if self.falhar:
                raise ConnectionError('supervisor FAKE indisponivel')
            registros = self.paperclip.listar_interacoes(receipt.issue_id)
            candidatos = [r for r in registros if r['id'] == receipt.interaction_id
                          or r['idempotencyKey'] == receipt.confirmacao_key]
            exigir(len(candidatos) == 1, 'receipt_ambiguo_no_receptor')
            canonico = projetar_receipt(candidatos[0], self.ctx, self.vinculo.autorizador(), receipt.interaction_id)
            exigir(receipt == canonico and receipt.decisao == 'accepted', 'receipt_divergente_no_receptor')
            exigir(timestamp(receipt.timestamp) <= self.relogio.agora() < self.ctx.expira_em,
                   'receipt_expirado_no_receptor')
            if receipt.consumo_key in self.consumidos:
                exigir(self.consumidos[receipt.consumo_key] == receipt, 'consumo_divergente')
                return 'retomada_ja_confirmada'
            exigir(self.bloqueado and self.atual == receipt.escopo == self.ctx.escopo, 'escopo_stale_no_receptor')
            receipt.escopo.validar()
            ids = frozenset(receipt.escopo.pendentes)
            exigir(ids == self.elegiveis_na_falha and ids <= self.aceitos and not ids & self.terminais,
                   'operacao_nao_elegivel')
            # SOMENTE seção crítica em memória: não prova transação/durabilidade/crash safety.
            self.receipts[receipt.consumo_key] = receipt
            self.consumidos[receipt.consumo_key] = receipt
            self.executados.extend(receipt.escopo.pendentes)
            self.terminais.update(ids)
            self.bloqueado = False
            self.trilha.append(['pendentes_executados_fake', *receipt.escopo.pendentes])
            if self.perder_ack:
                self.perder_ack = False
                raise TimeoutError('ACK FAKE perdido')
            return 'retomada_confirmada'


def cenario():
    from adaptador_confirmacao import AdaptadorConfirmacao
    relogio, vinculo, trilha = RelogioFake(), VinculoExistenteFake(), []
    escopo = Escopo('FAKE-supervisor', 'FAKE-supervisor-run', 7, 'FAKE-terminal',
                    'FAKE-filho-run', 'FAKE-registro-falha', ('FAKE-pendente-1', 'FAKE-pendente-2'))
    ctx = Contexto('FAKE-ticket-existente', escopo, relogio.agora(), relogio.agora() + 600)
    paperclip = PaperclipFake(ctx, vinculo, relogio, trilha)
    supervisor = SupervisorFake(ctx, paperclip, vinculo, relogio, trilha)
    adaptador = AdaptadorConfirmacao(paperclip, vinculo, supervisor, relogio)
    return ctx, relogio, vinculo, paperclip, supervisor, adaptador, trilha
