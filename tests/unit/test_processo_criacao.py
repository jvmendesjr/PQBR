"""t160u: pré-condição fail-closed do processo canônico de criação."""
from __future__ import annotations

import pytest
from pqbr.pipeline import processo_criacao as pc


def test_nucleo_flow_ok():
    r = pc.conferir("flow", exigir_playbook_operavel=True)
    assert r.ok is True
    assert r.versao == pc.VERSAO_ESPERADA
    assert r.sha256 and len(r.sha256) == 64
    assert r.playbook_status == "aprovado"
    assert r.motivos == []


def test_vids_stub_bloqueia_quando_operavel():
    r = pc.conferir("google_vids", exigir_playbook_operavel=True)
    assert r.ok is False
    assert "playbook_a_descobrir" in r.motivos


def test_vibes_stub_bloqueia_quando_operavel():
    r = pc.conferir("meta_vibes", exigir_playbook_operavel=True)
    assert r.ok is False
    assert "playbook_a_descobrir" in r.motivos


def test_exigir_ok_flow():
    r = pc.exigir("flow", exigir_playbook_operavel=True)
    assert r.ok and r.versao == "1.1.0"


def test_exigir_falha_vids():
    with pytest.raises(RuntimeError, match="fail-closed"):
        pc.exigir("google_vids", exigir_playbook_operavel=True)


def test_versao_diverge(monkeypatch, tmp_path):
    fake = tmp_path / "CRIACAO-README.md"
    fake.write_text("# x\n\n- **versão:** 9.9.9\n", encoding="utf-8")
    monkeypatch.setattr(pc, "DOC_NUCLEO", fake)
    r = pc.conferir("flow")
    assert r.ok is False
    assert any(m.startswith("versao_diverge:") for m in r.motivos)


def test_nucleo_ausente(monkeypatch, tmp_path):
    monkeypatch.setattr(pc, "DOC_NUCLEO", tmp_path / "missing.md")
    r = pc.conferir("flow")
    assert r.ok is False
    assert "nucleo_ausente" in r.motivos


def test_extrair_versao():
    assert pc.extrair_versao("- **versão:** 1.2.3\n") == "1.2.3"
    assert pc.extrair_versao("versão: 0.1.0\n") == "0.1.0"
