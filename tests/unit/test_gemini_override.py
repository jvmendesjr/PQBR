"""t105u: override do modelo/raciocínio do juiz Gemini só por execução; padrão (config) intacto."""
import json
import pytest
from pqbr.workflows import auditor_gemini as ag
from pqbr.motores import CONFIG

MENU = ('- menuitem "3.8 Flash Ajuda para tudo" [e66]\n- menuitem "Selecionado 4 Argon Tarefas complexas" [e68]\n'
        '- menuitem "Nível de raciocínio" [e69] [expanded]\n- menuitem "Selecionado Baixo Rápido e eficiente" [e70]\n'
        '- menuitem "Médio Aprofundamento equilibrado" [e71]')


def test_padrao_e_config(monkeypatch):
    monkeypatch.delenv(ag.ENV_MODELO, raising=False); monkeypatch.delenv(ag.ENV_RACIOCINIO, raising=False)
    assert ag.modelo_configurado() == json.loads(open(CONFIG).read())["gemini_modelo"] == "3.8 Flash"
    assert ag.raciocinio_configurado() is None


def test_override_por_execucao(monkeypatch):
    monkeypatch.setenv(ag.ENV_MODELO, "4 Argon"); monkeypatch.setenv(ag.ENV_RACIOCINIO, "Baixo")
    assert ag.modelo_configurado() == "4 Argon" and ag.raciocinio_configurado() == "Baixo"
    assert json.loads(open(CONFIG).read())["gemini_modelo"] == "3.8 Flash"


def test_raciocinio_invalido(monkeypatch):
    monkeypatch.setenv(ag.ENV_RACIOCINIO, "minimo")
    with pytest.raises(ValueError):
        ag.raciocinio_configurado()


def test_leitura_do_menu():
    assert ag.modelo_selecionado(MENU).startswith("4 Argon") and ag.nivel_selecionado(MENU) == "Baixo"
    assert ag.nivel_selecionado("- menuitem \"Baixo Rápido\" [e70]") is None
