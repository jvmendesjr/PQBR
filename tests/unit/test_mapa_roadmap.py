"""t120u: parser da aba Roadmap."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts/mapa"))
import roadmap  # noqa: E402

RM = """# ROADMAP
## Fase A
- [x] **A-01** feito `x`
  - [ ] subitem ignorado
- [ ] **A-02** falta <script>
## Anexo: fases
- [ ] ignorado
"""
EST = """# ESTADO
## Próximo passo
José assiste o **EP1003**.

## Pendências abertas
| # | Pendência | Ref. | Dono | Bloqueio |
|---|---|---|---|---|
| P1 | EP1003: José assiste | x | José | aguardando |
| P2 | **Feito (t1).** algo pronto | y | agente | concluído |
## Como atualizar
"""


def test_parse_roadmap_niveis_e_anexo():
    r = roadmap.parse_roadmap(RM)
    assert r["feito"] == [("Fase A", "A-01 feito x")]
    assert r["falta"] == [("Fase A", "A-02 falta <script>")]


def test_parse_estado_ordem_e_feito():
    e = roadmap.parse_estado(EST)
    assert e["proximo"] == "José assiste o EP1003."
    assert [p["id"] for p in e["pendencias"]] == ["P1", "P2"]
    assert [p["feito"] for p in e["pendencias"]] == [False, True]


def test_dados_tres_blocos_e_html_escapado():
    d = roadmap.dados(RM, EST)
    assert len(d["feito"]) == 2 and len(d["falta"]) == 1
    assert d["proximos"][0][0] == "Próximo passo" and d["proximos"][1][0] == "P1"
    h = roadmap.secao(d)
    assert 'id="roadmap"' in h and "&lt;script&gt;" in h and "<script>" not in h
    assert "<form" not in h and "POST" not in h and "contenteditable" not in h


def test_repo_real_gera():
    d = roadmap.dados()
    assert d["feito"] and d["proximos"]


def test_checkboxes_marcadas_feito_vazias_falta_e_nada_editavel():
    d = roadmap.dados(RM, EST)
    h = roadmap.secao(d)
    assert h.count("☑") == len(d["feito"])
    assert h.count("☐") == len(d["falta"]) + len(d["proximos"])
    for x in ("<input", "<form", "onclick", "contenteditable", "POST", "<button"):
        assert x not in h
