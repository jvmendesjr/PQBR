from pqbr.workflows.acesso import deslogado, PedidoJose, ACAO_JOSE
import pytest

def test_deslogado():
    assert deslogado('- link "Sign in to your account" [e2]')
    assert deslogado('- button "Fazer login" [e3]')
    assert not deslogado('- textbox "Insira um comando para o Gemini" [e13]')

def test_pedido_contrato():
    p = PedidoJose(servico="paperclip_cli", motivo="401", acao_jose=ACAO_JOSE["paperclip_cli"])
    assert p.servico == "paperclip_cli"
    with pytest.raises(Exception): PedidoJose(servico="x", motivo="", acao_jose="")


def test_pedidos_telegram_formatar():
    from pqbr.workflows.pedidos_telegram import formatar
    assert formatar([]) == ""
    t = formatar([(1, "acesso:google_camofox", "Login Google", {"motivo": "Sign in"})])
    assert "#1 acesso google_camofox: Login Google" in t and "Sign in" in t
