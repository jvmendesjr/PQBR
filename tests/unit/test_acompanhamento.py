from pqbr.contratos import VERSOES
from pqbr.workflows.acompanhamento import (SINAL_APROVACAO, acompanhar, canario_interface,
    deriva_contratos, dev_diagnosticar, resumir_fallbacks)


def test_fallbacks_contam_por_papel():
    metas = [{"papel": "dev", "combo": "core-alto", "modelo": "x", "fallback": True},
             {"papel": "dev", "combo": "core-alto", "modelo": "y", "fallback": False},
             {"papel": "auditor", "combo": "core-alto", "modelo": "z", "fallback": True}]
    r = resumir_fallbacks(metas)
    assert r["total"] == 3 and r["com_fallback"] == 2 and r["por_papel"] == {"dev": 1, "auditor": 1}


def test_deriva_detecta_versao_e_ausencia():
    fixture = dict(VERSOES); fixture["CenaIndividual"] = "9.9.9"; del fixture["BriefingEfemerico"]
    d = deriva_contratos(fixture)
    tipos = {(x["contrato"], x["tipo"]) for x in d}
    assert ("CenaIndividual", "versao_diferente") in tipos
    assert ("BriefingEfemerico", "ausente_na_fixture") in tipos
    assert deriva_contratos(dict(VERSOES)) == []


def test_canario_sem_notebooklm():
    ok = canario_interface(lambda: {"login_google": True, "surpresas_flow": [], "notebooklm": "ignorar"})
    assert ok == {"status": "ok", "login_google": True, "surpresas_flow": [], "notebooklm_verificado": False}
    falha = canario_interface(lambda: {"login_google": True, "surpresas_flow": ["popup novo no Flow"]})
    assert falha["status"] == "falha" and falha["surpresas_flow"] == ["popup novo no Flow"]


def test_dev_diagnosticar_nao_aplica_nem_envia():
    parcial = {"fallbacks": {"com_fallback": 1}, "deriva": [], "canario": {"status": "ok"}}
    d = dev_diagnosticar(parcial, "flowchart TD\n  A-->B")
    assert d["aplicado"] is False
    assert d["sinal"]["tipo"] == SINAL_APROVACAO and d["sinal"]["tarefa"] == "acompanhamento_mudancas"
    assert "rascunho" in d["rascunho_diff_mapa"] and "aguardar OK do José" in d["aviso"]


def test_acompanhar_ordem_e_escopo_correcao():
    r = acompanhar([{"papel": "dev", "fallback": True}], dict(VERSOES),
                   lambda: {"login_google": True, "surpresas_flow": []}, "flowchart TD")
    assert r["ordem"] == ["fallbacks", "deriva", "canario", "dev_diagnosticar"]
    assert r["correcao_autonoma_escopo"] == "sessao_e_fila"
    assert r["registrado_no_worker"] is False
    assert r["deriva"] == [] and r["diagnostico"]["aplicado"] is False


def test_snapshot_bate_com_versoes_atuais():
    import json
    from pathlib import Path as _P
    snap = json.loads((_P(__file__).resolve().parents[2] / "config" / "contratos_versoes_snapshot.json").read_text())
    assert snap == dict(VERSOES)


def test_workflow_registrado_no_worker():
    import inspect
    from pqbr.workflows import worker
    src = inspect.getsource(worker)
    assert "AcompanhamentoMudancasWorkflow" in src and "ATIVIDADES_ACOMPANHAMENTO" in src
    from pqbr.workflows.acompanhamento import AcompanhamentoMudancasWorkflow, ATIVIDADES_ACOMPANHAMENTO
    assert AcompanhamentoMudancasWorkflow is not None and len(ATIVIDADES_ACOMPANHAMENTO) == 1
