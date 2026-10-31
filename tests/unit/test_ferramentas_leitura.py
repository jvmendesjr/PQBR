import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pqbr.agents.ferramentas import (LEITURA, ContadorChamadas, LimiteChamadas,
    anexar_ferramentas_leitura, exigir_leitura, ferramentas_para_papel,
    ler_arquivo_visivel, ler_estado)
from pqbr.contratos import PropostaTemas
from pqbr.contratos.politica import AcessoNegado, carregar

P = carregar()


def test_so_leitura_filtrada_pela_politica():
    assert ferramentas_para_papel("dev", P) == ("memoria_buscar", "codigo_consultar", "estado_ler")
    assert ferramentas_para_papel("indexador", P) == ()
    assert ferramentas_para_papel("auditor", P) == ("memoria_buscar",)
    assert all(n in LEITURA for n in ferramentas_para_papel("mantenedor", P))
    assert "memoria_registrar" not in ferramentas_para_papel("dev", P)  # escrita, fora


def test_papel_desconhecido_fail_closed():
    with pytest.raises(AcessoNegado):
        ferramentas_para_papel("intruso", P)
    with pytest.raises(AcessoNegado):
        exigir_leitura("auditor", "codigo_consultar", P)  # auditor não tem a ferramenta
    with pytest.raises(AcessoNegado):
        exigir_leitura("dev", "memoria_registrar", P)


def test_contador_limite():
    c = ContadorChamadas(limite=2)
    c.contar("estado_ler"); c.contar("estado_ler")
    assert c.total == 2
    with pytest.raises(LimiteChamadas):
        c.contar("estado_ler")


def test_leitura_local_sem_escrita(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "ESTADO-ATUAL.md").write_text("# ESTADO ATUAL\nok", encoding="utf-8")
    assert ler_estado(tmp_path).startswith("# ESTADO ATUAL")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "x.py").write_text("print(1)", encoding="utf-8")
    assert ler_arquivo_visivel("dev", "src/x.py", P, tmp_path) == "print(1)"
    with pytest.raises(AcessoNegado):
        ler_arquivo_visivel("auditor", "src/x.py", P, tmp_path)  # sem codigo_consultar
    with pytest.raises(AcessoNegado):
        ler_arquivo_visivel("dev", "../fora.py", P, tmp_path)


def test_ferramenta_nativa_anexada_e_com_limite():
    ag = Agent(TestModel(), output_type=PropostaTemas, name="dev")
    ag, contador = anexar_ferramentas_leitura(ag, "dev", P, limite=1)
    ferramentas = ag._function_toolset.tools
    assert "ler_estado" in ferramentas and "consultar_codigo" in ferramentas
    assert "memoria_buscar" not in ferramentas  # sem MCP interno, sem ferramenta nativa de memória
    fn = ferramentas["ler_estado"].function
    assert "ESTADO" in fn()
    with pytest.raises(LimiteChamadas):
        fn()  # segunda chamada estoura o limite de 1
    assert contador.total == 1
    ag2 = Agent(TestModel(), output_type=PropostaTemas, name="indexador")
    anexar_ferramentas_leitura(ag2, "indexador", P)
    assert ag2._function_toolset.tools == {}


def test_sem_import_mcp():
    import inspect, pqbr.agents.ferramentas as f
    src = inspect.getsource(f)
    imports = [l for l in src.splitlines() if l.startswith(("import ", "from "))]
    assert not any("mcp" in l.lower() for l in imports)
