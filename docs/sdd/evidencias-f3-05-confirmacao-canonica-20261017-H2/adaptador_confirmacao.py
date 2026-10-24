"""Adaptador isolado H2. Portas injetadas; sem HTTP, SDK, CLI, aviso ou registro de Worker.
Os nomes de campos vêm do contrato instalado. Receipt é projeção local, não campo novo na API.
"""
from dataclasses import asdict
from modelos import (Contexto, EventoVinculado, Receipt, exigir, digest,
                     json_canonico, timestamp, PaperclipPort, VinculoExistentePort,
                     SupervisorPort)


def chave(ctx, usuario):
    # Sem canal/evento e sem prazo renovável: não abre confirmação paralela no Discord.
    return 'pqbr-f3-05:' + digest([ctx.issue_id, asdict(ctx.escopo), usuario])


def corpo_confirmacao(ctx, usuario):
    ctx.validar()
    exigir(type(usuario) is str and bool(usuario), 'vinculo_ausente')
    manifesto = {'version': 1, 'issueId': ctx.issue_id,
                 'escopo': asdict(ctx.escopo), 'criadoEm': ctx.criado_em,
                 'expiraEm': ctx.expira_em}
    details = 'PQBR-F3-05/v1\n' + json_canonico(manifesto)
    exigir(len(details) <= 20000, 'escopo_excede_limite')
    return {
        'kind': 'request_confirmation', 'idempotencyKey': chave(ctx, usuario),
        'resolverPolicy': 'human_only', 'addresseeUserId': usuario,
        'addresseeAgentId': None, 'continuationPolicy': 'none',
        'title': 'Autorizar somente pendentes já aceitos',
        'payload': {
            'version': 1,
            'prompt': 'Autoriza retomar somente os pendentes desta revisão, sem repetir a operação terminal?',
            'acceptLabel': 'Autorizar pendentes', 'rejectLabel': 'Não autorizar',
            'supersedeOnUserComment': False, 'detailsMarkdown': details,
        },
    }


def validar_registro(registro, ctx, usuario, interaction_id=None):
    exigir(type(registro) is dict, 'registro_ausente')
    esperado = corpo_confirmacao(ctx, usuario)
    obrigatorios = {'id', 'issueId', 'kind', 'status', 'continuationPolicy',
                    'requestedResolverPolicy', 'effectiveResolverPolicy',
                    'addresseeUserId', 'addresseeAgentId', 'resolvedByUserId',
                    'resolvedByAgentId', 'resolvedByRunId', 'resolvedAt',
                    'result', 'createdAt', 'updatedAt', 'payload', 'idempotencyKey'}
    exigir(obrigatorios <= registro.keys(), 'registro_incompleto')
    exigir(type(registro.get('id')) is str and bool(registro['id']), 'interacao_ausente')
    exigir(interaction_id is None or registro['id'] == interaction_id, 'interacao_divergente')
    exigir(registro.get('issueId') == ctx.issue_id, 'ticket_divergente')
    for campo in ('kind', 'idempotencyKey', 'addresseeUserId', 'title', 'payload',
                  'addresseeAgentId', 'continuationPolicy'):
        exigir(campo in registro and json_canonico(registro[campo]) == json_canonico(esperado[campo]),
               'registro_divergente:' + campo)
    exigir(registro.get('requestedResolverPolicy') == 'human_only'
           and registro.get('effectiveResolverPolicy') == 'human_only', 'politica_humana_incorreta')
    # Payload exato também rejeita target=plan, toolAction, secretProposal e escopo ampliado.
    exigir(registro.get('resolvedByAgentId') is None
           and registro.get('resolvedByRunId') is None, 'resolucao_por_agente')
    exigir(ctx.criado_em <= timestamp(registro.get('createdAt')) < ctx.expira_em,
           'criacao_fora_janela')
    estado = registro.get('status')
    if estado == 'pending':
        exigir(all(registro.get(k) is None for k in ('result', 'resolvedByUserId', 'resolvedAt')),
               'pendente_com_decisao')
    elif estado in ('accepted', 'rejected'):
        exigir(registro.get('resolvedByUserId') == usuario, 'autor_nao_autorizado')
        resultado = registro.get('result')
        exigir(type(resultado) is dict and type(resultado.get('version')) is int
               and resultado['version'] == 1 and resultado.get('outcome') == estado,
               'receipt_incompleto_ou_divergente')
        exigir(not any(k in resultado for k in ('resumeFailure', 'toolAction', 'secretProposal')),
               'efeito_automatico_inadmissivel')
        exigir(timestamp(registro['createdAt']) <= timestamp(registro.get('resolvedAt'))
               < ctx.expira_em, 'decisao_fora_janela')
    else:
        exigir(estado in ('expired', 'cancelled', 'failed'), 'estado_desconhecido')
    return registro


def projetar_receipt(registro, ctx, usuario, interaction_id):
    validar_registro(registro, ctx, usuario, interaction_id)
    exigir(registro['status'] in ('accepted', 'rejected'), 'sem_decisao_final')
    return Receipt(ctx.issue_id, registro['id'], registro['resolvedByUserId'],
                   registro['result']['outcome'], registro['resolvedAt'],
                   ctx.escopo.revisao, ctx.escopo, 'FAKE-SNAPSHOT:' + digest(registro),
                   registro['idempotencyKey'])


class AdaptadorConfirmacao:
    def __init__(self, paperclip: PaperclipPort, vinculo: VinculoExistentePort,
                 supervisor: SupervisorPort, relogio):
        self.paperclip, self.vinculo = paperclip, vinculo
        self.supervisor, self.relogio = supervisor, relogio

    def _ler(self, ctx, interaction_id):
        usuario = self.vinculo.autorizador()
        registros = self.paperclip.listar_interacoes(ctx.issue_id)
        exigir(type(registros) is list, 'leitura_incerta')
        # Mesmo ID duplicado ou mesma chave em mais de uma interação: ambiguidade fecha.
        candidatos = [r for r in registros if isinstance(r, dict) and
                      (r.get('id') == interaction_id or r.get('idempotencyKey') == chave(ctx, usuario))]
        exigir(len(candidatos) == 1, 'interacao_ausente_ou_ambigua')
        return validar_registro(candidatos[0], ctx, usuario, interaction_id)

    def abrir(self, ctx: Contexto):
        ctx.validar()
        exigir(ctx.criado_em <= self.relogio.agora() < ctx.expira_em, 'pedido_expirado')
        exigir(self.supervisor.consultar() == ctx.escopo, 'supervisor_stale')
        usuario = self.vinculo.autorizador()
        # Abre somente interação NO ticket existente; não há porta criar_issue/avisar.
        criado = self.paperclip.criar_interacao(ctx.issue_id, corpo_confirmacao(ctx, usuario))
        validar_registro(criado, ctx, usuario)
        relido = self._ler(ctx, criado['id'])
        exigir(criado == relido, 'criacao_incerta')
        return relido['id']

    def pelo_painel(self, ctx: Contexto, interaction_id: str):
        # O painel já resolveu no Paperclip. Não grava uma segunda decisão.
        registro = self._ler(ctx, interaction_id)
        return self._encaminhar(ctx, interaction_id, registro)

    def pelo_discord(self, ctx: Contexto, interaction_id: str, evento_id: str):
        evento = self.vinculo.evento(evento_id, 'discord')
        exigir(type(evento) is EventoVinculado and evento.canal == 'discord', 'evento_nao_confiavel')
        exigir(evento.usuario_paperclip == self.vinculo.autorizador(), 'identidade_invalida')
        evento.escopo.validar()
        exigir(type(evento.revisao) is int, 'revisao_evento_invalida')
        exigir((evento.issue_id, evento.interaction_id, evento.revisao, evento.escopo) ==
               (ctx.issue_id, interaction_id, ctx.escopo.revisao, ctx.escopo), 'evento_stale_ou_divergente')
        exigir(evento.decisao in ('accepted', 'rejected'), 'decisao_invalida')
        agora = self.relogio.agora()
        exigir(type(evento.timestamp) is int and ctx.criado_em <= evento.timestamp <= agora
               and agora < ctx.expira_em and agora - evento.timestamp <= 300, 'evento_expirado')
        registro = self._ler(ctx, interaction_id)
        if registro['status'] == 'pending':
            exigir(self.supervisor.consultar() == ctx.escopo, 'supervisor_stale')
            # A porta age na sessão humana vinculada. Não simula autor em corpo JSON da API.
            gravado = self.paperclip.resolver_como_humano(evento)
            validar_registro(gravado, ctx, self.vinculo.autorizador(), interaction_id)
            registro = self._ler(ctx, interaction_id)  # obrigatória após persistência
            exigir(gravado == registro, 'receipt_incerto')
        exigir(registro['status'] == evento.decisao, 'decisao_divergente')
        return self._encaminhar(ctx, interaction_id, registro)

    def _encaminhar(self, ctx, interaction_id, registro):
        # Mesmo nos reenvios, não confia em receipt/cache local.
        exigir(ctx.criado_em <= self.relogio.agora() < ctx.expira_em, 'autorizacao_expirada')
        if registro['status'] != 'accepted':
            exigir(registro['status'] != 'pending', 'decisao_nao_persistida')
            return 'bloqueado:' + registro['status']
        exigir(timestamp(registro['resolvedAt']) <= self.relogio.agora(), 'decisao_futura')
        receipt = projetar_receipt(registro, ctx, self.vinculo.autorizador(), interaction_id)
        return self.supervisor.retomar(receipt)
