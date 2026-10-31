"""F05-06/F05-08 (rascunho t536): outbox de saída, dedupe de entrada, fail-closed, escada de 3."""
import asyncio
from datetime import datetime, timedelta, timezone
import pytest
from pydantic import ValidationError
from pqbr.contratos.ponte_telegram import EventoCallbackTelegram, MensagemSaida, PedidoAprovacao
from pqbr.workflows.ponte_telegram import (EntregaIncerta, RepositorioMemoria, enviar_idempotente,
                                           novo_token, processar_callback)
from pqbr.workflows.pedidos_telegram import chave_aviso

JOSE = "123456"
AGORA = datetime(2026, 10, 25, 12, tzinfo=timezone.utc)
run = asyncio.run


class Rem:
    def __init__(self, falhas=0, incerto=False):
        self.falhas, self.incerto, self.envios = falhas, incerto, []
    async def enviar(self, m, reenvio):
        self.envios.append((m.chave, reenvio))
        if self.incerto: raise EntregaIncerta("timeout")
        if self.falhas: self.falhas -= 1; raise ConnectionError("https://api.telegram.org/botSEGREDO/x")
        return 42


def _msg(chave="aviso:1:2026102512"):
    return MensagemSaida(chave=chave, classe="aviso_operacional", texto="oi")


def test_envio_confirmado_uma_vez():
    repo, rem = RepositorioMemoria(), Rem()
    assert repo.enfileirar(_msg()) and not repo.enfileirar(_msg())
    r1 = run(enviar_idempotente(repo, rem, _msg().chave)); r2 = run(enviar_idempotente(repo, rem, _msg().chave))
    assert r1.estado == r2.estado == "enviado" and r1.mensagem_id == 42 and len(rem.envios) == 1


def test_falha_clara_retenta_e_tres_viram_ticket_sem_vazar_texto():
    repo, rem = RepositorioMemoria(), Rem(falhas=5); repo.enfileirar(_msg())
    estados = [run(enviar_idempotente(repo, rem, _msg().chave)).estado for _ in range(4)]
    assert estados == ["falhou", "falhou", "ticket", "ticket"] and len(rem.envios) == 3
    assert [x[1] for x in rem.envios] == [False, True, True]
    assert "SEGREDO" not in repo.recibo(_msg().chave).motivo and len(repo.tickets) == 1


def test_ambiguo_nao_reenvia_as_cegas():
    repo, rem = RepositorioMemoria(), Rem(incerto=True); repo.enfileirar(_msg())
    assert run(enviar_idempotente(repo, rem, _msg().chave)).estado == "incerto"
    assert run(enviar_idempotente(repo, rem, _msg().chave)).estado == "incerto" and len(rem.envios) == 1
    repo.reenviar_incerto(_msg().chave); rem.incerto = False
    assert run(enviar_idempotente(repo, rem, _msg().chave)).estado == "enviado" and rem.envios[-1][1] is True


def _cenario(etapa="aguardando_aprovacao", expira=AGORA + timedelta(hours=1)):
    repo, tok = RepositorioMemoria(), novo_token()
    repo.registrar_pedido(PedidoAprovacao(token=tok, workflow_id="ep-1", etapa="aguardando_aprovacao", tarefa="publicar EP1", expira_em=expira))
    sinais = []
    async def sinalizar(wf, t, d, esperada=None): sinais.append((wf, t, d)); return etapa
    return repo, tok, sinais, sinalizar


def _ev(tok, uid=1, de=JOSE, dec="aprovar"):
    return EventoCallbackTelegram(update_id=uid, remetente_id=de, ref_pedido=tok, decisao=dec)


@pytest.mark.parametrize("cfg,de,status", [("", JOSE, "config_ausente"), (JOSE, "999", "remetente_recusado")])
def test_fail_closed_identidade(cfg, de, status):
    repo, tok, sinais, s = _cenario()
    assert run(processar_callback(repo, cfg, _ev(tok, de=de), s, AGORA)).status == status and not sinais


def test_token_desconhecido_expirado_e_etapa_errada():
    repo, tok, sinais, s = _cenario()
    assert run(processar_callback(repo, JOSE, _ev(novo_token()), s, AGORA)).status == "pedido_desconhecido"
    repo, tok, sinais, s = _cenario(expira=AGORA)
    assert run(processar_callback(repo, JOSE, _ev(tok), s, AGORA)).status == "expirado" and not sinais
    repo, tok, sinais, s = _cenario(etapa="publicado")
    assert run(processar_callback(repo, JOSE, _ev(tok), s, AGORA)).status == "estado_invalido"


def test_um_sinal_por_pedido_mesmo_com_update_repetido_ou_segunda_decisao():
    repo, tok, sinais, s = _cenario()
    assert run(processar_callback(repo, JOSE, _ev(tok), s, AGORA)).status == "sinalizado"
    assert run(processar_callback(repo, JOSE, _ev(tok), s, AGORA)).motivo == "update_repetido"
    assert run(processar_callback(repo, JOSE, _ev(tok, uid=2, dec="negar"), s, AGORA)).motivo == "token_decidido"
    assert sinais == [("ep-1", tok, "aprovar")]


def test_tres_falhas_do_temporal_viram_um_ticket():
    repo, tok, _, _ = _cenario(); n = []
    async def cai(wf, t, d, esperada=None): n.append(1); raise RuntimeError("temporal fora")
    r = run(processar_callback(repo, JOSE, _ev(tok), cai, AGORA))
    assert r.status == "ticket" and len(n) == 3 and list(repo.tickets) == [f"ticket:sinal:{tok}"]


def test_contrato_rejeita_remetente_em_texto_e_extra():
    with pytest.raises(ValidationError): EventoCallbackTelegram(update_id=1, remetente_id="jose", ref_pedido="x" * 20, decisao="aprovar")
    with pytest.raises(ValidationError): MensagemSaida(chave="aviso:1:x", classe="aviso_operacional", texto="a", extra=1)


def test_chave_aviso_estavel_na_janela_de_6h():
    t = datetime(2026, 10, 25, 7, 59, tzinfo=timezone.utc)
    assert chave_aviso(7, t) == chave_aviso(7, t.replace(hour=6, minute=0)) != chave_aviso(7, t.replace(hour=12))
