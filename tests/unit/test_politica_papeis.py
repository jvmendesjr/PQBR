import pytest
from pqbr.contratos.politica import carregar, AcessoNegado, PoliticaPapeis
from pqbr.storage import hindsight
from pqbr.integrations import gitnexus

P = carregar()


def test_bank_unico_e_papeis_dos_agentes():
    from pqbr.agents import REGISTRO
    assert P.bank == "pqbr"
    assert set(REGISTRO) | {"mantenedor", "indexador"} == set(P.papeis)


def test_papel_desconhecido_fail_closed():
    with pytest.raises(AcessoNegado):
        P.de("intruso")
    with pytest.raises(AcessoNegado):
        hindsight.reter("x", papel="intruso", tags=["licao"], transporte=lambda u, c: {})
    with pytest.raises(AcessoNegado):
        hindsight.recuperar("x", papel=None, transporte=lambda u, c: {})
    with pytest.raises(AcessoNegado):
        gitnexus.consultar("intruso", "context", "X", executor=lambda a: {})


def test_escrita_fora_das_tags_negada():
    with pytest.raises(AcessoNegado):
        hindsight.reter("x", papel="pesquisador-origem", tags=["decisao"], transporte=lambda u, c: {})
    with pytest.raises(AcessoNegado):
        hindsight.reter("x", papel="auditor", tags=[], transporte=lambda u, c: {})


def test_escrita_permitida_leva_tag_do_papel():
    vis = {}
    hindsight.reter("lição ok", "ctx", papel="auditor", tags=["licao"], transporte=lambda u, c: vis.update(c) or {})
    assert vis["items"][0]["tags"] == ["licao", "papel:auditor"]


def test_leitura_filtra_tags():
    def t(u, c):
        assert set(c["tags"]) == set(P.papeis["pesquisador-origem"].leitura)
        return {"results": [{"text": "a", "tags": ["pesquisa"]}, {"text": "b", "tags": ["seguranca"]}, {"text": "c"}]}
    assert [m["text"] for m in hindsight.recuperar("q", papel="pesquisador-origem", transporte=t)] == ["a"]


def test_indexador_nao_le():
    with pytest.raises(AcessoNegado):
        hindsight.recuperar("q", papel="indexador", transporte=lambda u, c: {})


def test_gitnexus_filtra_caminhos_e_ferramenta():
    resp = {"symbol": {"filePath": "src/pqbr/workflows/publicacao.py"},
            "incoming": {"imports": [{"filePath": "src/pqbr/workflows/worker_episodio.py"}, {"filePath": "docs/x.md"}]}}
    with pytest.raises(AcessoNegado):
        gitnexus.consultar("auditor", "context", "X", executor=lambda a: resp)   # sem a ferramenta
    r = gitnexus.consultar("dev", "context", "X", executor=lambda a: resp)
    assert len(r["incoming"]["imports"]) == 2
    with pytest.raises(ValueError):
        gitnexus.consultar("dev", "cypher", "MATCH (n) DETACH DELETE n", executor=lambda a: resp)


def test_caminho_absoluto_ou_curinga_invalido():
    with pytest.raises(ValueError):
        PoliticaPapeis.model_validate({"versao": "1", "bank": "pqbr", "papeis": {"x": {"codigo": ["/etc"]}}})
    with pytest.raises(ValueError):
        PoliticaPapeis.model_validate({"versao": "1", "bank": "pqbr", "papeis": {"x": {"leitura": ["*"]}}})
    with pytest.raises(ValueError):
        PoliticaPapeis.model_validate({"versao": "1", "bank": "outro", "papeis": {}})
