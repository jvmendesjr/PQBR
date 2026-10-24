"""Testes exclusivamente sintéticos; nenhuma chamada operacional ou rede."""
import unittest
from copy import deepcopy
from dataclasses import asdict, replace
from threading import Barrier, Thread
from adaptador_confirmacao import AdaptadorConfirmacao, corpo_confirmacao, projetar_receipt
from fakes import cenario
from modelos import Bloqueado, EventoVinculado, iso, json_canonico


class ConfirmacaoTests(unittest.TestCase):
    def setUp(self):
        (self.ctx, self.relogio, self.vinculo, self.pc, self.sup,
         self.ad, self.trilha) = cenario()
        self.iid = self.ad.abrir(self.ctx)

    def evento(self, decisao='accepted', **campos):
        e = EventoVinculado(self.vinculo.usuario, 'discord', self.ctx.issue_id, self.iid,
                           self.ctx.escopo.revisao, self.ctx.escopo, decisao, self.relogio.agora())
        return replace(e, **campos)

    def discord(self, evento=None, key='FAKE-evento', **origem):
        self.vinculo.registrar_fixture(key, evento or self.evento(), **origem)
        return self.ad.pelo_discord(self.ctx, self.iid, key)

    def aprovar(self):
        self.pc.painel_decidir_fixture(self.iid)

    def sem_efeito(self):
        self.assertEqual(self.sup.executados, [])
        self.assertEqual(self.sup.consumidos, {})
        self.assertTrue(self.sup.bloqueado)
        self.assertTrue(self.sup.admissao_fechada)
        self.assertIn(self.ctx.escopo.falha_id, self.sup.terminais)

    def test_payload_e_escopo_exatos_sem_wake_plan_ou_agente(self):
        r = self.pc.registros[self.iid]
        self.assertEqual(r['kind'], 'request_confirmation')
        self.assertEqual(r['continuationPolicy'], 'none')
        self.assertEqual(r['effectiveResolverPolicy'], 'human_only')
        self.assertEqual(r['addresseeUserId'], self.vinculo.usuario)
        self.assertIsNone(r['addresseeAgentId'])
        self.assertFalse(set(r['payload']) & {'target', 'toolAction', 'secretProposal'})
        self.assertIn(json_canonico(asdict(self.ctx.escopo)), r['payload']['detailsMarkdown'])
        self.assertFalse(hasattr(self.pc, 'criar_issue'))
        self.assertFalse(hasattr(self.vinculo, 'avisar'))
        self.sem_efeito()

    def test_abertura_duplicada_mesma_interacao_no_ticket_existente(self):
        self.assertEqual(self.ad.abrir(self.ctx), self.iid)
        self.assertEqual(len(self.pc.registros), 1)
        self.sem_efeito()

    def test_abertura_mesma_revisao_nao_renova_prazo(self):
        with self.assertRaises(Bloqueado):
            self.ad.abrir(replace(self.ctx, expira_em=self.ctx.expira_em + 60))
        self.assertEqual(len(self.pc.registros), 1)
        self.sem_efeito()

    def test_painel_persiste_rele_antes_retomar_sem_nova_resolucao(self):
        self.aprovar()
        resolucoes = self.pc.chamadas['resolver']
        self.assertEqual(self.ad.pelo_painel(self.ctx, self.iid), 'retomada_confirmada')
        self.assertEqual(self.pc.chamadas['resolver'], resolucoes)
        self.verificar_efeito_unico_e_receipt()
        self.verificar_ordem()

    def test_discord_persiste_rele_antes_retomar_mesma_interacao(self):
        self.assertEqual(self.discord(), 'retomada_confirmada')
        self.assertEqual(len(self.pc.registros), 1)
        self.verificar_efeito_unico_e_receipt()
        self.verificar_ordem()

    def verificar_efeito_unico_e_receipt(self):
        self.assertEqual(tuple(self.sup.executados), self.ctx.escopo.pendentes)
        self.assertNotIn(self.ctx.escopo.falha_id, self.sup.executados)
        self.assertNotIn('FAKE-ja-concluida', self.sup.executados)
        self.assertTrue(self.sup.admissao_fechada)
        self.assertEqual(len(self.sup.receipts), 1)
        receipt = next(iter(self.sup.receipts.values()))
        self.assertEqual((receipt.issue_id, receipt.interaction_id, receipt.autor,
                          receipt.decisao, receipt.timestamp, receipt.revisao, receipt.escopo),
                         (self.ctx.issue_id, self.iid, self.vinculo.usuario, 'accepted',
                          iso(self.relogio.agora()), self.ctx.escopo.revisao, self.ctx.escopo))
        self.assertTrue(receipt.registro_hash.startswith('FAKE-SNAPSHOT:'))

    def verificar_ordem(self):
        nomes = [x[0] for x in self.trilha]
        decisao = nomes.index('decisao_persistida')
        chamada = nomes.index('receptor_fake_chamado')
        efeito = nomes.index('pendentes_executados_fake')
        self.assertIn('registro_relido', nomes[decisao + 1:chamada])
        self.assertIn('registro_relido', nomes[chamada + 1:efeito])
        self.assertLess(decisao, chamada)
        self.assertLess(chamada, efeito)

    def test_painel_depois_discord_converge_mesmo_receipt(self):
        self.aprovar()
        self.ad.pelo_painel(self.ctx, self.iid)
        self.assertEqual(self.discord(), 'retomada_ja_confirmada')
        self.assertEqual(self.pc.chamadas['resolver'], 1)
        self.verificar_efeito_unico_e_receipt()

    def test_discord_depois_painel_converge_mesmo_receipt(self):
        self.discord()
        self.assertEqual(self.ad.pelo_painel(self.ctx, self.iid), 'retomada_ja_confirmada')
        self.verificar_efeito_unico_e_receipt()

    def test_replay_evento_e_evento_distinto_mesma_interacao(self):
        self.discord()
        self.assertEqual(self.ad.pelo_discord(self.ctx, self.iid, 'FAKE-evento'), 'retomada_ja_confirmada')
        self.assertEqual(self.discord(key='FAKE-evento-reentregue'), 'retomada_ja_confirmada')
        self.assertEqual(self.pc.chamadas['resolver'], 1)
        self.verificar_efeito_unico_e_receipt()

    def test_reconstruir_fachada_nao_depende_cache(self):
        self.discord()
        nova = AdaptadorConfirmacao(self.pc, self.vinculo, self.sup, self.relogio)
        self.assertEqual(nova.pelo_painel(self.ctx, self.iid), 'retomada_ja_confirmada')
        self.verificar_efeito_unico_e_receipt()

    def test_ack_perdido_sem_retry_automatico_reenvio_deduplica(self):
        self.sup.perder_ack = True
        with self.assertRaises(TimeoutError):
            self.discord()
        self.assertEqual(self.sup.chamadas['retomar'], 1)
        self.assertEqual(self.ad.pelo_painel(self.ctx, self.iid), 'retomada_ja_confirmada')
        self.verificar_efeito_unico_e_receipt()

    def test_resposta_decisao_perdida_nao_retoma_nesta_tentativa(self):
        self.pc.perder_resposta.add('resolver')
        with self.assertRaises(TimeoutError):
            self.discord()
        self.assertEqual(self.pc.chamadas['resolver'], 1)
        self.assertEqual(self.sup.chamadas['retomar'], 0)
        self.assertEqual(self.pc.registros[self.iid]['status'], 'accepted')
        self.sem_efeito()
        self.assertEqual(self.ad.pelo_discord(self.ctx, self.iid, 'FAKE-evento'), 'retomada_confirmada')
        self.assertEqual(self.pc.chamadas['resolver'], 1)
        self.verificar_efeito_unico_e_receipt()

    def test_resposta_abertura_perdida_reenvio_explicito_mesma_interacao(self):
        ctx, relogio, vinculo, pc, sup, ad, trilha = cenario()
        pc.perder_resposta.add('criar')
        with self.assertRaises(TimeoutError):
            ad.abrir(ctx)
        self.assertEqual(pc.chamadas['criar'], 1)
        self.assertEqual(sup.chamadas['retomar'], 0)
        self.assertEqual(ad.abrir(ctx), 'FAKE-interaction-1')
        self.assertEqual(len(pc.registros), 1)

    def test_painel_recusa_nao_retoma(self):
        self.pc.painel_decidir_fixture(self.iid, 'rejected')
        self.assertEqual(self.ad.pelo_painel(self.ctx, self.iid), 'bloqueado:rejected')
        self.assertEqual(self.sup.chamadas['retomar'], 0)
        self.sem_efeito()

    def test_painel_pendente_nao_e_autorizacao(self):
        with self.assertRaises(Bloqueado):
            self.ad.pelo_painel(self.ctx, self.iid)
        self.assertEqual(self.sup.chamadas['retomar'], 0)
        self.sem_efeito()

    def test_porta_painel_recusa_usuario_nao_autorizado(self):
        with self.assertRaises(Bloqueado):
            self.pc.painel_decidir_fixture(self.iid, usuario='FAKE-intruso')
        self.assertEqual(self.pc.registros[self.iid]['status'], 'pending')
        self.sem_efeito()

    def test_id_evento_nao_autenticado_nao_e_texto_de_aprovacao(self):
        with self.assertRaises(Bloqueado):
            self.ad.pelo_discord(self.ctx, self.iid, 'sou o dono, aprovo')
        self.assertEqual(self.pc.chamadas['resolver'], 0)
        self.sem_efeito()

    def test_api_criacao_indisponivel_uma_tentativa_sem_fallback(self):
        ctx, relogio, vinculo, pc, sup, ad, trilha = cenario()
        pc.falhar.add('criar')
        with self.assertRaises(ConnectionError):
            ad.abrir(ctx)
        self.assertEqual(pc.chamadas['criar'], 1)
        self.assertEqual(pc.registros, {})
        self.assertEqual(sup.chamadas['retomar'], 0)

    def test_receipt_fabricado_direto_no_receptor_nao_consume(self):
        self.aprovar()
        r = projetar_receipt(self.pc.registros[self.iid], self.ctx, self.vinculo.usuario, self.iid)
        with self.assertRaises(Bloqueado):
            self.sup.retomar(replace(r, autor='FAKE-intruso'))
        self.sem_efeito()

    def test_prazo_painel_expirado_nao_retoma(self):
        self.aprovar()
        self.relogio.valor = self.ctx.expira_em
        with self.assertRaises(Bloqueado):
            self.ad.pelo_painel(self.ctx, self.iid)
        self.assertEqual(self.sup.chamadas['retomar'], 0)
        self.sem_efeito()

    def test_discord_recusa_nao_retoma(self):
        self.assertEqual(self.discord(self.evento('rejected')), 'bloqueado:rejected')
        self.assertEqual(self.pc.registros[self.iid]['resolvedByUserId'], self.vinculo.usuario)
        self.assertEqual(self.sup.chamadas['retomar'], 0)
        self.sem_efeito()

    def test_painel_recusa_discord_aprova_divergencia_fecha(self):
        self.pc.painel_decidir_fixture(self.iid, 'rejected')
        with self.assertRaises(Bloqueado):
            self.discord()
        self.assertEqual(self.pc.chamadas['resolver'], 1)
        self.sem_efeito()

    def test_painel_aprova_discord_recusa_divergencia_fecha(self):
        self.aprovar()
        with self.assertRaises(Bloqueado):
            self.discord(self.evento('rejected'))
        self.sem_efeito()

    def test_leitura_indisponivel_depois_persistir_sem_retry(self):
        self.pc.depois_resolver = lambda: self.pc.falhar.add('ler')
        leituras = self.pc.chamadas['ler']
        with self.assertRaises(ConnectionError):
            self.discord()
        self.assertEqual(self.pc.chamadas['ler'], leituras + 2)
        self.assertEqual(self.sup.chamadas['retomar'], 0)
        self.sem_efeito()

    def test_receipt_incompleto_resposta_gravacao_nao_e_sucesso(self):
        original = self.pc.resolver_como_humano
        def incerto(evento):
            r = original(evento)
            r['resolvedAt'] = None
            return r
        self.pc.resolver_como_humano = incerto
        with self.assertRaises(Bloqueado):
            self.discord()
        self.assertEqual(self.sup.chamadas['retomar'], 0)
        self.sem_efeito()

    def test_receipt_relido_divergente_nao_retoma(self):
        original = self.pc.resolver_como_humano
        def divergente(evento):
            r = original(evento)
            self.pc.registros[self.iid]['updatedAt'] = iso(self.relogio.agora() + 1)
            return r
        self.pc.resolver_como_humano = divergente
        with self.assertRaisesRegex(Bloqueado, 'receipt_incerto'):
            self.discord()
        self.assertEqual(self.sup.chamadas['retomar'], 0)
        self.sem_efeito()

    def test_registro_muda_entre_fachada_e_receptor(self):
        self.aprovar()
        original = self.sup.retomar
        def adulterar(receipt):
            self.pc.registros[self.iid]['status'] = 'rejected'
            self.pc.registros[self.iid]['result']['outcome'] = 'rejected'
            return original(receipt)
        self.sup.retomar = adulterar
        with self.assertRaises(Bloqueado):
            self.ad.pelo_painel(self.ctx, self.iid)
        self.sem_efeito()

    def test_expira_no_cas_decisao(self):
        self.pc.antes_resolver = lambda: setattr(self.relogio, 'valor', self.ctx.expira_em)
        with self.assertRaises(Bloqueado):
            self.discord()
        self.assertEqual(self.pc.registros[self.iid]['status'], 'pending')
        self.sem_efeito()

    def test_expira_apos_gravar_antes_retomar(self):
        self.pc.depois_resolver = lambda: setattr(self.relogio, 'valor', self.ctx.expira_em)
        with self.assertRaises(Bloqueado):
            self.discord()
        self.assertEqual(self.sup.chamadas['retomar'], 0)
        self.sem_efeito()

    def test_expira_no_receptor(self):
        self.aprovar()
        original = self.sup.retomar
        def expirar(receipt):
            self.relogio.valor = self.ctx.expira_em
            return original(receipt)
        self.sup.retomar = expirar
        with self.assertRaises(Bloqueado):
            self.ad.pelo_painel(self.ctx, self.iid)
        self.sem_efeito()

    def test_pendentes_novos_falhos_ou_concluidos_nao_elegiveis(self):
        self.aprovar()
        self.sup.terminais.add(self.ctx.escopo.pendentes[0])
        with self.assertRaises(Bloqueado):
            self.ad.pelo_painel(self.ctx, self.iid)
        self.sem_efeito()

    def test_revisao_supervisor_stale_apos_decisao(self):
        self.aprovar()
        self.sup.atual = replace(self.ctx.escopo, revisao=self.ctx.escopo.revisao + 1)
        with self.assertRaises(Bloqueado):
            self.ad.pelo_painel(self.ctx, self.iid)
        self.sem_efeito()

    def test_escopo_muda_apos_gravar_nao_retoma(self):
        self.pc.depois_resolver = lambda: setattr(self.sup, 'atual', replace(self.ctx.escopo, pendentes=('FAKE-nova',)))
        with self.assertRaises(Bloqueado):
            self.discord()
        self.sem_efeito()

    def test_vinculo_revogado_apos_gravar_nao_retoma(self):
        self.pc.depois_resolver = lambda: setattr(self.vinculo, 'ativo', False)
        with self.assertRaises(Bloqueado):
            self.discord()
        self.sem_efeito()

    def test_corrida_recusa_painel_vence_antes_cas_discord(self):
        def recusar():
            self.pc.antes_resolver = None
            self.pc.painel_decidir_fixture(self.iid, 'rejected')
        self.pc.antes_resolver = recusar
        with self.assertRaises(Bloqueado):
            self.discord()
        self.assertEqual(self.pc.registros[self.iid]['status'], 'rejected')
        self.sem_efeito()

    def test_concorrencia_duas_aprovacoes_consumo_unico_em_memoria(self):
        self.aprovar()
        barreira, resultados = Barrier(3), []
        def despachar():
            barreira.wait()
            try:
                resultados.append(self.ad.pelo_painel(self.ctx, self.iid))
            except Exception as exc:
                resultados.append(type(exc).__name__)
        threads = [Thread(target=despachar) for _ in range(2)]
        for t in threads:
            t.start()
        barreira.wait()
        for t in threads:
            t.join(timeout=3)
            self.assertFalse(t.is_alive())
        self.assertCountEqual(resultados, ['retomada_confirmada', 'retomada_ja_confirmada'])
        self.verificar_efeito_unico_e_receipt()


# Casos de adulteração independentes, cada um com fixture nova.
def teste_registro(nome, alterar):
    def teste(self):
        self.aprovar()
        alterar(self.pc.registros[self.iid], self)
        with self.assertRaises((Bloqueado, ConnectionError, TimeoutError)):
            self.ad.pelo_painel(self.ctx, self.iid)
        self.assertEqual(self.sup.chamadas['retomar'], 0)
        self.sem_efeito()
    setattr(ConfirmacaoTests, 'test_registro_' + nome, teste)


for nome, campo, valor in (
    ('wake_assignee', 'continuationPolicy', 'wake_assignee'),
    ('wake_on_accept', 'continuationPolicy', 'wake_assignee_on_accept'),
    ('continuacao_ausente', 'continuationPolicy', None),
    ('agente_destinatario', 'addresseeAgentId', 'FAKE-agente'),
    ('usuario_destinatario_invalido', 'addresseeUserId', 'FAKE-intruso'),
    ('politica_efetiva_anyone', 'effectiveResolverPolicy', 'anyone'),
    ('politica_solicitada_anyone', 'requestedResolverPolicy', 'anyone'),
    ('resolver_agente', 'resolvedByAgentId', 'FAKE-agente'),
    ('resolver_run', 'resolvedByRunId', 'FAKE-run'),
    ('autor_invalido', 'resolvedByUserId', 'FAKE-intruso'),
    ('autor_ausente', 'resolvedByUserId', None),
    ('timestamp_ausente', 'resolvedAt', None),
    ('timestamp_invalido', 'resolvedAt', 'ontem'),
    ('timestamp_sem_timezone', 'resolvedAt', '2027-01-15T08:00:00'),
    ('resultado_ausente', 'result', None),
    ('resultado_divergente', 'result', {'version': 1, 'outcome': 'rejected'}),
    ('resultado_versao_bool', 'result', {'version': True, 'outcome': 'accepted'}),
    ('resultado_com_wake_falhou', 'result', {'version': 1, 'outcome': 'accepted', 'resumeFailure': {'status': 'retrying'}}),
    ('ticket_divergente', 'issueId', 'FAKE-outro-ticket'),
    ('interacao_divergente', 'id', 'FAKE-outra-interacao'),
    ('kind_divergente', 'kind', 'ask_user_questions'),
    ('chave_divergente', 'idempotencyKey', 'FAKE-outra-chave'),
    ('status_desconhecido', 'status', 'unknown'),
):
    teste_registro(nome, lambda r, s, k=campo, v=valor: r.__setitem__(k, deepcopy(v)))


teste_registro('timestamp_futuro', lambda r, s: r.__setitem__('resolvedAt', iso(s.relogio.agora() + 1)))
teste_registro('timestamp_antigo', lambda r, s: r.__setitem__('resolvedAt', iso(s.ctx.criado_em - 1)))
teste_registro('timestamp_expirado', lambda r, s: r.__setitem__('resolvedAt', iso(s.ctx.expira_em)))
teste_registro('payload_plan', lambda r, s: r['payload'].__setitem__('target', {'kind': 'plan'}))
teste_registro('payload_toolaction', lambda r, s: r['payload'].__setitem__('toolAction', {}))
teste_registro('payload_version_bool', lambda r, s: r['payload'].__setitem__('version', True))
teste_registro('payload_escopo_stale', lambda r, s: r['payload'].__setitem__('detailsMarkdown', r['payload']['detailsMarkdown'].replace('"revisao":7', '"revisao":6')))
teste_registro('payload_pendente_extra', lambda r, s: r['payload'].__setitem__('detailsMarkdown', r['payload']['detailsMarkdown'].replace('"FAKE-pendente-2"', '"FAKE-pendente-2","FAKE-nova"')))
teste_registro('campo_agente_ausente', lambda r, s: r.pop('resolvedByAgentId'))
teste_registro('resultado_toolaction_vazio', lambda r, s: r['result'].__setitem__('toolAction', {}))
teste_registro('resultado_resume_nulo', lambda r, s: r['result'].__setitem__('resumeFailure', None))
teste_registro('interacao_ambigua', lambda r, s: s.pc.registros.__setitem__('FAKE-duplicata', deepcopy(r)))
teste_registro('api_indisponivel', lambda r, s: s.pc.falhar.add('ler'))
teste_registro('leitura_resposta_perdida', lambda r, s: s.pc.perder_resposta.add('ler'))


def teste_evento(nome, alterar, origem=None):
    def teste(self):
        evento = alterar(self.evento(), self)
        with self.assertRaises((Bloqueado, ConnectionError, TimeoutError)):
            self.discord(evento, **(origem or {}))
        self.assertEqual(self.pc.chamadas['resolver'], 0)
        self.assertEqual(self.sup.chamadas['retomar'], 0)
        self.sem_efeito()
    setattr(ConfirmacaoTests, 'test_evento_' + nome, teste)


for nome, campo, valor in (
    ('ator_nao_autorizado', 'usuario_paperclip', 'FAKE-intruso'),
    ('ator_ausente', 'usuario_paperclip', ''),
    ('canal_divergente', 'canal', 'paperclip'),
    ('ticket_divergente', 'issue_id', 'FAKE-outro'),
    ('interacao_divergente', 'interaction_id', 'FAKE-outra'),
    ('revisao_stale', 'revisao', 6),
    ('revisao_float', 'revisao', 7.0),
    ('decisao_invalida', 'decisao', 'sim'),
):
    teste_evento(nome, lambda e, s, k=campo, v=valor: replace(e, **{k: v}))
for nome, campo, valor in (
    ('supervisor', 'supervisor_id', 'FAKE-outro'),
    ('supervisor_run', 'supervisor_run_id', 'FAKE-outro-run'),
    ('falha', 'falha_id', 'FAKE-outra-falha'),
    ('filho_run', 'filho_run_id', 'FAKE-outro-filho-run'),
    ('receipt_falha', 'registro_falha_receipt', 'FAKE-outro-recibo'),
    ('pendentes_extra', 'pendentes', ('FAKE-pendente-1', 'FAKE-pendente-2', 'FAKE-nova')),
    ('pendentes_subconjunto', 'pendentes', ('FAKE-pendente-1',)),
    ('pendentes_ordem', 'pendentes', ('FAKE-pendente-2', 'FAKE-pendente-1')),
    ('terminal_na_fila', 'pendentes', ('FAKE-terminal',)),
    ('concluido_na_fila', 'pendentes', ('FAKE-ja-concluida',)),
):
    teste_evento(nome, lambda e, s, k=campo, v=valor: replace(e, escopo=replace(e.escopo, **{k: v})))
for nome, origem in (
    ('discord_nao_vinculado', {'conta': 'FAKE-nao-vinculada'}),
    ('canal_fora_allowlist', {'canal': 'FAKE-publico'}),
    ('dm', {'canal': 'FAKE-DM'}),
    ('round_trip_nao_e_decisao', {'tipo': 'mensagem_thread'}),
):
    teste_evento(nome, lambda e, s: e, origem)
teste_evento('antigo', lambda e, s: (setattr(s.relogio, 'valor', s.relogio.agora() + 301) or e))
teste_evento('futuro', lambda e, s: replace(e, timestamp=s.relogio.agora() + 1))
teste_evento('antes_criacao', lambda e, s: replace(e, timestamp=s.ctx.criado_em - 1))
teste_evento('expirado', lambda e, s: (setattr(s.relogio, 'valor', s.ctx.expira_em) or e))


def teste_falha(nome, alvo, operacao):
    def teste(self):
        getattr(self, alvo).falhar.add(operacao) if alvo == 'pc' else setattr(self.sup, 'falhar', True)
        with self.assertRaises(ConnectionError):
            self.discord()
        if alvo == 'pc':
            self.assertEqual(self.pc.chamadas[operacao], 1 if operacao == 'resolver' else 2)
        else:
            self.assertEqual(self.sup.chamadas['retomar'], 1)
        self.sem_efeito()
    setattr(ConfirmacaoTests, 'test_sem_retry_' + nome, teste)


teste_falha('api_resolver', 'pc', 'resolver')
teste_falha('api_ler', 'pc', 'ler')
teste_falha('supervisor', 'sup', 'retomar')


def estado_final_teste(estado):
    def teste(self):
        self.pc.registros[self.iid]['status'] = estado
        self.assertEqual(self.ad.pelo_painel(self.ctx, self.iid), 'bloqueado:' + estado)
        self.assertEqual(self.sup.chamadas['retomar'], 0)
        self.sem_efeito()
    setattr(ConfirmacaoTests, 'test_estado_' + estado + '_nao_retoma', teste)


for estado in ('expired', 'cancelled', 'failed'):
    estado_final_teste(estado)


if __name__ == '__main__':
    unittest.main()
