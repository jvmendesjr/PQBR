"""t161u: gate fail-closed do projeto Flow por episódio."""
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


def test_ep1003_fichas_ok_storyboard_hold():
    r = fp.conferir_episodio("EP1003", exigir_fichas=True, exigir_storyboard=False)
    assert r.ok is True
    assert r.fichas_ok is True
    assert r.storyboard_ok is False
    assert r.pode_pedir_storyboard is True
    assert r.pode_gerar_cenas is False
    assert r.project_id == "025dcfef-7eef-4551-b60c-5106812508db"


def test_cenas_bloqueadas_sem_storyboard():
    r = fp.conferir_episodio("EP1003", exigir_fichas=True, exigir_storyboard=True)
    assert r.ok is False
    assert "storyboard_ausente" in r.motivos
    with pytest.raises(RuntimeError, match="fail-closed"):
        fp.exigir_antes_cenas("EP1003")


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
