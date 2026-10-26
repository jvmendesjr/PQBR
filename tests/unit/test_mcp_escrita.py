"""Escrita de memória pelo MCP (t95u/t96u)."""
import json
from pqbr.contratos.politica import carregar
import pytest
from pqbr.mcp import servidor as S
from pqbr.contratos.politica import AcessoNegado
from pqbr.storage import hindsight

GRAV = []
IMPL = {"reter": lambda texto, ctx, **k: GRAV.append((texto, ctx, k)) or {}, "verificar_commit": lambda h: h == "abc1234"}


def _call(nome, args, papel="mantenedor", cliente="mantenedor-externo"):
    return S.tratar({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": nome, "arguments": args}},
                    papel, IMPL, cliente)["result"]


def setup_function():
    GRAV.clear()


def test_registrar_memoria_ok_autor_e_referencias():
    r = _call("registrar_memoria", {"conteudo": "Ajustei o guia de acesso do MCP.", "tags": ["licao"], "arquivos": ["docs/x.md"]})
    assert not r["isError"], r
    out = json.loads(r["content"][0]["text"])
    assert out["autor"] == "mantenedor-externo" and out["tags"] == ["licao"] and out["versao"] == "1.1.0"
    texto, ctx, k = GRAV[0]
    assert "docs/x.md" in texto and k["autor"] == "mantenedor-externo" and k["papel"] == "mantenedor"


def test_tags_derivadas_dentro_da_escrita():
    _call("registrar_memoria", {"conteudo": "Incidente de queda corrigido no fluxo, lição registrada."})
    assert set(GRAV[0][2]["tags"]) <= set(carregar().papeis["mantenedor"].escrita) and GRAV[0][2]["tags"]


def test_tag_fora_da_escrita_negada():
    r = _call("registrar_memoria", {"conteudo": "Tentando escrever tag editorial.", "tags": ["editorial"]})
    assert r["isError"] and "negado" in r["content"][0]["text"] and not GRAV
    r = _call("registrar_memoria", {"conteudo": "Tentando marcar como obsoleto.", "tags": ["obsoleto_candidato"]})
    assert r["isError"] and not GRAV


def test_alteracao_exige_commit_existente():
    assert _call("registrar_alteracao", {"conteudo": "Mudança sem commit informado."})["isError"]
    assert _call("registrar_alteracao", {"conteudo": "Mudança com commit inexistente.", "commit": "deadbee"})["isError"]
    r = _call("registrar_alteracao", {"conteudo": "Mudança com commit real no repo.", "commit": "abc1234"})
    assert not r["isError"] and json.loads(r["content"][0]["text"])["commit_verificado"]
    assert "commit abc1234" in GRAV[-1][0] and "commit abc1234" in GRAV[-1][1]


def test_papel_sem_escrita_e_sem_cliente_negados():
    assert "registrar_memoria" not in S.ferramentas_do_papel("indexador")
    r = _call("registrar_memoria", {"conteudo": "indexador não usa o MCP para escrever."}, papel="indexador")
    assert r["isError"] and "negado" in r["content"][0]["text"]
    r = _call("registrar_memoria", {"conteudo": "sem cliente identificado não grava."}, cliente="")
    assert r["isError"] and not GRAV


def test_caminho_absoluto_e_segredo_bloqueados():
    assert _call("registrar_memoria", {"conteudo": "caminho fora do repo.", "arquivos": ["/etc/passwd"]})["isError"]
    with pytest.raises(Exception):
        hindsight.reter("token " + "ghp" + "_" + "A1b2C3d4E5" * 4 + " vazado", "", papel="mantenedor", tags=["licao"],
                        autor="x-y", transporte=lambda u, c: {})


def test_reter_adiciona_autor():
    vist = []
    hindsight.reter("conteúdo limpo de teste", "", papel="mantenedor", tags=["licao"], autor="mantenedor-externo",
                    transporte=lambda u, c: vist.append(c) or {})
    assert vist[0]["items"][0]["tags"] == ["licao", "papel:mantenedor", "autor:mantenedor-externo"]


def test_cliente_do_token(tmp_path):
    import hashlib, os
    arq = tmp_path / "c.json"
    arq.write_text(json.dumps({"clientes": [{"nome": "ext", "papel": "mantenedor", "sha256": hashlib.sha256(b"t").hexdigest()}]}))
    os.chmod(arq, 0o600)
    assert S.cliente_do_token("t", arq) == ("ext", "mantenedor") and S.cliente_do_token("x", arq) is None
