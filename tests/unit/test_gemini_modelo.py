import json
import pytest
from pqbr.workflows import auditor_gemini as ag

MENU = """    - 'button "Abrir seletor de modo. No momento: Pro" [expanded]': Pro
      - menuitem "3.5 Flash Lite Respostas mais rápidas" [e52]
      - menuitem "3.8 Flash Ajuda para tudo" [e53]
      - menuitem "Selecionado 3.1 Pro Raciocínio avançado" [e54]: 3.1 Pro Raciocínio avançado
      - menuitem "4 Argon Tarefas complexas Novo" [e55]"""


def test_parse_menu():
    assert ag.modelo_selecionado(MENU).startswith("3.1 Pro ")
    assert ag.ref_do_modelo(MENU, "3.8 Flash") == "e53"
    assert ag.ref_do_modelo(MENU, "3.5 Flash") is None or ag.ref_do_modelo(MENU, "3.5 Flash") == "e52"
    assert ag.ref_do_modelo(MENU, "9 Nada") is None


def test_config(tmp_path, monkeypatch):
    import pqbr.motores as m
    f = tmp_path / "m.json"; f.write_text(json.dumps({"gemini_modelo": "4 Argon"}))
    monkeypatch.setattr(m, "CONFIG", f); assert ag.modelo_configurado() == "4 Argon"
    f.write_text("{}"); assert ag.modelo_configurado() == "3.8 Flash"


def _fake(monkeypatch, snaps):
    it = iter(snaps)
    monkeypatch.setattr(ag, "_snap", lambda tab: next(it))
    monkeypatch.setattr(ag, "_api", lambda *a, **k: {})
    import pqbr.workflows.camofox_humano as h
    monkeypatch.setattr(h, "clicar", lambda *a, **k: {}); monkeypatch.setattr(h, "pausa_humana", lambda *a, **k: None)


def test_seleciona_e_confirma(monkeypatch):
    depois = MENU.replace('"Selecionado 3.1 Pro', '"3.1 Pro').replace('"3.8 Flash Ajuda', '"Selecionado 3.8 Flash Ajuda')
    _fake(monkeypatch, [MENU, depois]); assert ag.selecionar_modelo("t", "3.8 Flash") == "3.8 Flash"


def test_falha_fechada_sem_confirmar(monkeypatch):
    _fake(monkeypatch, [MENU, MENU])
    with pytest.raises(ag.ModeloIndisponivel): ag.selecionar_modelo("t", "3.8 Flash")


def test_falha_fechada_modelo_ausente(monkeypatch):
    _fake(monkeypatch, [MENU])
    with pytest.raises(ag.ModeloIndisponivel): ag.selecionar_modelo("t", "9 Nada")
