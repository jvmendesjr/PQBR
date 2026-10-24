"""Composição exclusiva H3: sem cliente HTTP, credenciais, bot ou banco real."""
from copy import deepcopy
from dataclasses import asdict
import json
from temporalio import activity
from temporalio.exceptions import ApplicationError
from modelos import Escopo, Contexto, Receipt, exigir, timestamp
from adaptador_confirmacao import projetar_receipt


def wire(receipt):
    return json.loads(json.dumps(dict(**asdict(receipt), consumo_key=receipt.consumo_key)))


class PortaSupervisorTemporal:
    """Porta síncrona H2 só enfileira; confirmar() async entrega ao workflow.
    'enfileirado_sem_ack' NÃO confirma consumo nem execução.
    """
    def __init__(self, ctx, trilha):
        self.ctx, self.trilha = ctx, trilha
        self.atual = ctx.escopo
        self.saida = []

    def consultar(self):
        return self.atual

    def retomar(self, receipt):
        self.saida.append(wire(receipt))
        self.trilha.append(['receipt_enfileirado_sem_ack', receipt.consumo_key])
        return 'enfileirado_sem_ack'


class ValidadorCanonico:
    def __init__(self):
        self.ctx = self.paperclip = self.vinculo = self.relogio = self.trilha = None
        self.tentativas_validacao = []
        self.falhar_validacao = False
        self.depois_validar = None

    @activity.defn(name='reler_confirmacao_canonica_falsa')
    async def reler_confirmacao(self, recebido: dict) -> dict:
        self.tentativas_validacao.append(activity.info().attempt)
        try:
            exigir(not self.falhar_validacao, 'persistencia_receptor_fake_falhou')
            exigir(self.ctx is not None, 'fixture_ausente')
            usuario = self.vinculo.autorizador()
            registros = self.paperclip.listar_interacoes(recebido['issue_id'])
            exigir(type(registros) is list, 'leitura_incerta_receptor')
            candidatos = [r for r in registros if isinstance(r, dict) and (
                r.get('id') == recebido['interaction_id'] or
                r.get('idempotencyKey') == recebido['confirmacao_key'])]
            exigir(len(candidatos) == 1, 'receipt_ambiguo_receptor')
            canonico = projetar_receipt(candidatos[0], self.ctx, usuario, recebido['interaction_id'])
            exigir(wire(canonico) == recebido and canonico.decisao == 'accepted', 'receipt_divergente_receptor')
            exigir(self.ctx.criado_em <= timestamp(canonico.timestamp) <= self.relogio.agora()
                   < self.ctx.expira_em, 'receipt_expirado_receptor')
            self.trilha.append(['receipt_relido_validado_no_receptor', canonico.consumo_key])
            if self.depois_validar:
                await self.depois_validar()
            return dict(receipt=wire(canonico), expira_em=self.ctx.expira_em)
        except Exception as exc:
            raise ApplicationError('validação canônica FAKE recusada: ' + type(exc).__name__,
                                   type='ConfirmacaoFakeRecusada', non_retryable=True) from None
