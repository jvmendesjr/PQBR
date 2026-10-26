"""t108u: juiz Gemini por etapa + 3 critérios de bloqueio visual (P7)."""
import json
import pytest
from pqbr.contratos.juiz_gemini import JuizGeminiConfig
from pqbr.pipeline import auditor_visual as av
from pqbr.workflows import auditor_gemini as ag


@pytest.fixture(autouse=True)
def _sem_env(monkeypatch):
    monkeypatch.delenv(ag.ENV_MODELO, raising=False); monkeypatch.delenv(ag.ENV_RACIOCINIO, raising=False)


def test_config_por_etapa():
    assert ag.modelo_configurado("pre_producao") == "3.8 Flash" and ag.raciocinio_configurado("pre_producao") is None
    assert ag.modelo_configurado("producao") == "4 Argon" and ag.raciocinio_configurado("producao") == "Baixo"
    assert ag.modelo_configurado() == "3.8 Flash"   # legado sem etapa


def test_override_vence_etapa(monkeypatch):
    monkeypatch.setenv(ag.ENV_MODELO, "3.8 Flash")
    assert ag.modelo_configurado("producao") == "3.8 Flash" and ag.raciocinio_configurado("producao") is None
    monkeypatch.setenv(ag.ENV_RACIOCINIO, "Médio")
    assert ag.raciocinio_configurado("producao") == "Médio"


def test_contrato_fail_closed():
    with pytest.raises(Exception):
        JuizGeminiConfig.model_validate({"pre_producao": {"modelo": "x"}, "producao": {"modelo": "y", "raciocinio": "Minimo"}})
    with pytest.raises(Exception):
        ag.modelo_configurado("pos")


def _cena(i, **k):
    base = {"id": i, "tem_personagem": "sim", "tem_texto_na_tela": "nao", **{m: "sim" for m in av.METRICAS},
            "legenda_com_erro": "nao", **{s: "nao" for s in av.SEGURANCA + av.BLOQUEIO_VISUAL},
            "foco_unico_zona_segura": "na", "corresponde_ao_titulo": "na", "legenda_cobre_foco": "na"}
    base.update(k); return base


@pytest.mark.parametrize("k", av.BLOQUEIO_VISUAL)
def test_bloqueio_visual_reprova(k):
    r = json.dumps({"rodada": 1, "cenas": [_cena("S01", **{k: "sim"})]})
    res = av.decidir([r, r], ["S01"])
    assert res["veredito"] == "reprova" and ("S01", k) in res["falhas"]


def test_bloqueio_divergente_vai_a_terceira():
    a = json.dumps({"rodada": 1, "cenas": [_cena("S01", grotesco="sim")]}); b = json.dumps({"rodada": 2, "cenas": [_cena("S01")]})
    assert av.decidir([a, b], ["S01"])["veredito"] == "terceira_rodada"


def test_sem_personagem_na_permitido():
    r = json.dumps({"rodada": 1, "cenas": [_cena("S01", tem_personagem="nao", boca_articula_fala="na", corte_oculos_cabeca="na",
                                                  mesmo_personagem_do_bloco="na")]})
    assert av.decidir([r, r], ["S01"])["veredito"] == "aprova"


def test_template_tem_os_criterios():
    t = av.TEMPLATE.read_text()
    assert all(f"- {k}:" in t for k in av.BLOQUEIO_VISUAL)
