import pytest
from pqbr.contratos.politica import carregar, AcessoNegado, PoliticaPapeis
from pqbr.storage import hindsight
from pqbr.integrations import codebase_memory

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
        codebase_memory.consultar("intruso", "context", "X", executor=lambda a: {})


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


def test_codigo_filtra_caminhos_e_ferramenta():
    resp = {"symbol": {"filePath": "src/pqbr/workflows/publicacao.py"},
            "incoming": {"imports": [{"filePath": "src/pqbr/workflows/worker_episodio.py"}, {"filePath": "docs/x.md"}]}}
    with pytest.raises(AcessoNegado):
        codebase_memory.consultar("auditor", "context", "X", executor=lambda a: resp)   # sem a ferramenta
    r = codebase_memory.consultar("dev", "context", "X", executor=lambda a: resp)
    assert len(r["incoming"]["imports"]) == 2
    with pytest.raises(ValueError):
        codebase_memory.consultar("dev", "cypher", "MATCH (n) DETACH DELETE n", executor=lambda a: resp)
    with pytest.raises(ValueError):
        codebase_memory.consultar("dev", "query_graph", "MATCH (n) RETURN n", executor=lambda a: resp)
    # ambiguidade filtrada pelo papel: dev ve src/, nao infra/; sem candidato visivel, vira negado, nao vazamento
    amb = {"status": "ambiguous", "suggestions": [{"qualified_name": "PQBR.infra.mcp.x.f", "file_path": "infra/mcp/x.py"}]}
    assert codebase_memory.consultar("dev", "context", "f", executor=lambda a: amb) == {"status": "negado", "motivo": "nenhum candidato visível para o papel"}


def test_caminho_absoluto_ou_curinga_invalido():
    with pytest.raises(ValueError):
        PoliticaPapeis.model_validate({"versao": "1", "bank": "pqbr", "papeis": {"x": {"codigo": ["/etc"]}}})
    with pytest.raises(ValueError):
        PoliticaPapeis.model_validate({"versao": "1", "bank": "pqbr", "papeis": {"x": {"leitura": ["*"]}}})
    with pytest.raises(ValueError):
        PoliticaPapeis.model_validate({"versao": "1", "bank": "outro", "papeis": {}})


# t112u/t113u: mantenedor externo lê tudo; internos continuam restritos
def test_mantenedor_le_todas_as_tags_de_conteudo():
    todas = set(P.papeis["indexador"].escrita)
    assert set(P.papeis["mantenedor"].leitura) == todas
    for papel, pol in P.papeis.items():
        assert set(pol.leitura) <= set(P.papeis["mantenedor"].leitura), papel


def test_mantenedor_recebe_memoria_de_qualquer_papel():
    res = [{"text": t, "tags": [t]} for t in sorted(P.papeis["indexador"].escrita)]
    r = hindsight.recuperar("q", papel="mantenedor", transporte=lambda u, c: {"results": res})
    assert len(r) == len(res)


def test_mantenedor_ve_repo_todo_e_escreve_manutencao():
    for c in ("src/pqbr/seguranca/x.py", "docs/mapa/13.mmd", "company/agents/auditor/AGENTS.md", "infra/mcp/x"):
        assert P.ve_caminho("mantenedor", c)
    P.exigir_escrita("mantenedor", ["decisao", "incidente", "licao", "playbook", "doc", "estado"])
    for proibida in (["obsoleto_candidato"], ["commit"], ["publicacao"], ["seguranca"]):
        with pytest.raises(AcessoNegado):
            P.exigir_escrita("mantenedor", proibida)


@pytest.mark.parametrize("papel", ["diretor", "lider-editorial", "pesquisador-origem", "auditor",
                                   "lider-compliance", "guardiao-seguranca", "observador", "dev", "motion"])
def test_papeis_internos_continuam_restritos(papel):
    assert set(P.papeis[papel].leitura) < set(P.papeis["mantenedor"].leitura)
    fora = sorted(set(P.papeis["indexador"].escrita) - set(P.papeis[papel].leitura))[0]
    r = hindsight.recuperar("q", papel=papel, transporte=lambda u, c: {"results": [{"text": "x", "tags": [fora]}]})
    assert r == []
    assert "" not in P.papeis[papel].codigo


def test_sem_papel_sem_escrita():
    for p in (None, "", "intruso"):
        with pytest.raises(AcessoNegado):
            P.exigir_escrita(p, ["licao"])
        with pytest.raises(AcessoNegado):
            hindsight.reter("x", papel=p, tags=["licao"], transporte=lambda u, c: {})
