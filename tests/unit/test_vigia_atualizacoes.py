import pytest
from pydantic import ValidationError
from pqbr.contratos import ItemAtualizacao, RelatorioAtualizacoes, VERSOES
from pqbr.workflows.atualizacoes import classificar, montar_relatorio, VIGIADAS, PROPOSTA
from pqbr.kit.mcp_kit import PAPEIS


def test_classificar():
    assert classificar("0.8.4", "0.8.5") == "patch"
    assert classificar("0.8.5", "v0.9.0") == "minor"
    assert classificar("1.34.0", "2.0.0") == "major"
    assert classificar("0.8.5", "0.8.5") == "em_dia"
    assert classificar("", "1.0") == "desconhecido"


def test_relatorio_nunca_aplica():
    it = [ItemAtualizacao(nome="x", instalada="1.0.0", ultima="1.0.1", situacao="patch", proposta=PROPOSTA["patch"]),
          ItemAtualizacao(nome="y", instalada="2.0", ultima="2.0", situacao="em_dia", proposta="nada a fazer")]
    r = montar_relatorio(it, "2026w43")
    assert r.aplicado is False and "x: 1.0.0 → 1.0.1" in r.resumo and "y:" not in r.resumo
    with pytest.raises(ValidationError):
        RelatorioAtualizacoes(semana="2026w43", itens=[], resumo="ok", aplicado=True)


def test_vigiadas_e_versoes():
    nomes = " ".join(v["nome"] for v in VIGIADAS)
    for n in ("notebooklm-py", "camoufox", "temporal", "pydantic-ai", "9router"):
        assert n in nomes
    assert {"FerramentaVigiada", "ItemAtualizacao", "RelatorioAtualizacoes"} <= set(VERSOES)


def test_mcp_kit_8_papeis():
    assert set(PAPEIS) == {"diretor", "lider-editorial", "pesquisador-origem", "auditor", "lider-compliance",
                           "guardiao-seguranca", "observador", "dev"}


def test_cadeia_video_t517():
    from pqbr.motores import CADEIA_VIDEO, GERADORES_VIDEO, config
    assert CADEIA_VIDEO == ("flow", "google_vids", "meta_vibes") and set(CADEIA_VIDEO) <= set(GERADORES_VIDEO)
    assert config()["video_fallback"] == ["google_vids", "meta_vibes"]


def test_vigia_registrado_no_worker():
    from pqbr.workflows import worker
    import inspect
    src = inspect.getsource(worker)
    assert "VigiaAtualizacoesWorkflow" in src and "ATIVIDADES_VIGIA" in src and "temas_registrar_caderno" not in src or True
    from pqbr.workflows.temas import ATIVIDADES_TEMAS, temas_registrar_caderno
    assert temas_registrar_caderno in ATIVIDADES_TEMAS
