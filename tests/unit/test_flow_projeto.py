"""t161u: gate fail-closed do projeto Flow por episódio (storyboard removido 29/10/2026)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pqbr.pipeline import flow_projeto as fp


def test_titulo_canonico():
    assert fp.titulo_canonico("EP1003", "cafe-fraco") == "PQBR-EP1003-cafe-fraco"
    assert fp.titulo_canonico("1003", "cafe_fraco") == "PQBR-EP1003-cafe-fraco"
    assert fp.validar_titulo("PQBR-EP1003-cafe-fraco")
    assert not fp.validar_titulo("out. 27 - 17:09")


def test_ep1003_fichas_ok_sem_storyboard():
    # Sem gate de storyboard: fichas_ok libera cenas individuais.
    r = fp.conferir_episodio("EP1003", exigir_fichas=True)
    assert r.ok is True
    assert r.fichas_ok is True
    assert r.pode_gerar_cenas is True
    assert r.project_id == "3a9ca558-4c85-4502-8c19-7a8f42fa41dd"


def test_exigir_antes_cenas_libera_com_fichas():
    r = fp.conferir_episodio("EP1003", exigir_fichas=True)
    assert r.pode_gerar_cenas is True
    assert fp.exigir_antes_cenas("EP1003").pode_gerar_cenas is True


def test_episodio_ausente(tmp_path: Path):
    cfg = {
        "projeto_testes": {"id": "e2dacb70-b9d0-4dc7-8b93-e6ac1688a454"},
        "projetos": {},
    }
    p = tmp_path / "flow_projetos.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")
    r = fp.conferir_episodio("EP1003", cfg_path=p)
    assert r.ok is False
    assert "projeto_nao_registrado" in r.motivos


def test_projeto_testes_proibido(tmp_path: Path):
    cfg = {
        "projeto_testes": {"id": "e2dacb70-b9d0-4dc7-8b93-e6ac1688a454"},
        "projetos": {
            "EP1003": {
                "titulo": "PQBR-EP1003-cafe-fraco",
                "id": "e2dacb70-b9d0-4dc7-8b93-e6ac1688a454",
                "fichas_ok": True,
                "storyboard_ok": True,
            }
        },
    }
    p = tmp_path / "flow_projetos.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")
    r = fp.conferir_episodio("EP1003", cfg_path=p)
    assert r.ok is False
    assert "projeto_testes_proibido_para_episodio" in r.motivos
