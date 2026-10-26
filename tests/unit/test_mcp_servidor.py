import hashlib, json, os
import pytest
from pqbr.mcp import servidor as S
from pqbr.contratos.politica import AcessoNegado

IMPL = {"onboarding": lambda: "pacote", "buscar_memoria": lambda q, papel: [{"text": "m", "tags": ["licao"]}],
        "codigo": lambda papel, c, a: {"ok": c}, "estado": lambda: "estado"}


def test_token_para_papel_e_desconhecido(tmp_path):
    arq = tmp_path / "c.json"
    arq.write_text(json.dumps({"clientes": [{"nome": "x", "papel": "mantenedor", "sha256": hashlib.sha256(b"tok").hexdigest()}]}))
    os.chmod(arq, 0o644)
    assert S._carregar_clientes(arq) == {}          # permissão aberta ⇒ nada aceito
    os.chmod(arq, 0o600)
    cl = S._carregar_clientes(arq)
    assert S.papel_do_token("tok", cl) == "mantenedor"
    assert S.papel_do_token("outro", cl) is None and S.papel_do_token(None, cl) is None


def test_papel_desconhecido_negado():
    with pytest.raises(AcessoNegado):
        S.ferramentas_do_papel("intruso")


def test_ferramentas_por_papel():
    assert set(S.ferramentas_do_papel("mantenedor")) == {"onboarding", "buscar_memoria", "codigo", "estado", "registrar_memoria", "registrar_alteracao"}
    assert S.ferramentas_do_papel("indexador") == ["onboarding"]
    assert "codigo" not in S.ferramentas_do_papel("auditor")


def test_unica_escrita_e_memoria():
    escrita = {n for n in S.FERR if any(k in n for k in ("registrar", "criar", "enfileirar", "comentar", "status"))}
    assert escrita == {"registrar_memoria", "registrar_alteracao"}


def test_jsonrpc_list_e_call():
    r = S.tratar({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, "auditor", IMPL)
    assert {t["name"] for t in r["result"]["tools"]} == {"onboarding", "buscar_memoria", "registrar_memoria", "registrar_alteracao"}
    r = S.tratar({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "codigo", "arguments": {}}}, "auditor", IMPL)
    assert r["result"]["isError"] and "negado" in r["result"]["content"][0]["text"]
    r = S.tratar({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "buscar_memoria", "arguments": {"consulta": "q"}}}, "auditor", IMPL)
    assert not r["result"]["isError"]
    assert S.tratar({"jsonrpc": "2.0", "method": "notifications/initialized"}, "auditor") is None


def test_bind_so_loopback():
    assert S.HOST == "127.0.0.1"


def test_onboarding_real_tem_fontes():
    from pqbr.mcp.onboarding import pacote
    t = pacote()
    assert "BRIEFING" in t and "Decisões recentes" in t and "docs/mapa" in t


# t114u: MCP externo exclusivo do mantenedor
def test_token_de_papel_interno_recusado(tmp_path):
    import os
    arq = tmp_path / "c.json"
    arq.write_text(json.dumps({"clientes": [{"nome": "a", "papel": "auditor", "sha256": hashlib.sha256(b"aud").hexdigest()},
                                            {"nome": "m", "papel": "mantenedor", "sha256": hashlib.sha256(b"man").hexdigest()}]}))
    os.chmod(arq, 0o600)
    assert S.cliente_do_token("aud", arq) is None
    assert S.cliente_do_token("man", arq) == ("m", "mantenedor")


def test_papel_declarado_diferente_recusado():
    assert S.papel_externo_aceito("mantenedor", None) == "mantenedor"
    assert S.papel_externo_aceito("mantenedor", "mantenedor") == "mantenedor"
    for p in ("auditor", "dev", "diretor", "indexador", "intruso"):
        assert S.papel_externo_aceito("mantenedor", p) is None
        assert S.papel_externo_aceito(p, p) is None
    assert S.papel_externo_aceito(None, None) is None
