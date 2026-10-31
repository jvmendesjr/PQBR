"""Aba Portões (:8088, só leitura) — 31/10/2026, proposta em branch.

A aba não executa nada: os testes garantem que a saída não traz
formulário, botão nem chamada de rede, e que os dados vêm das fontes
(ESTADO-ATUAL, flow_projetos, índices de fichas), não de texto digitado
à mão no gerador.
"""
import importlib.util
from pathlib import Path

R = Path(__file__).resolve().parents[2]


def _mod():
    spec = importlib.util.spec_from_file_location("portoes", R / "scripts/mapa/portoes.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ESTADO = """## Pendências abertas
| # | Pendência | Ref. | Dono | Bloqueio |
| P1 | Lote parado | MG-11 | José | sem apagar |
| P11 | Merge da branch X | — | José | merge exige OK |
| P5 | **Substituída (t148u).** Fichas antigas | Fase 3 | José | descartadas |
| P2 | Publicação | F8-01 | agente | sem envio |
| P18 | Combo core-ultra criado | MG-12 | José | OK troca+reinício |
"""


def _fixture():
    m = _mod()
    flow = {
        "projetos": {
            "EP1003": {
                "codigo": "PQBR-EP1003",
                "slug": "cafe-fraco",
                "titulo": "PQBR-EP1003-cafe-fraco-v3",
                "id": "9c4ad934",
                "imagens_revisadas": True,
                "imagens_inicio": ["S01", "S02"],
                "fichas_entregues": ["PERS-menina-rosa"],
                "videos": [],
            }
        }
    }
    fichas = {
        "versao": "3.1.0",
        "fichas": [
            {"id": "PERS-menina-rosa", "estado": "permanente"},
            {"id": "SIT-acenando", "estado": "sugestao"},
        ],
    }
    refs = {"versao": "0.4.0", "referencias": [{"id": "REF-MG-00", "estado": "aprovada"}]}
    return m, m.dados(flow=flow, fichas=fichas, ref_motion=refs, estado_md=ESTADO)


def test_parse_classifica_fechada_e_aberta():
    m = _mod()
    pend = {p["id"]: p for p in m.parse_pendencias(ESTADO)}
    assert pend["P1"]["aberta"] is True
    assert pend["P18"]["aberta"] is True
    assert pend["P5"]["aberta"] is False


def test_dados_so_portoes_abertos_do_jose_em_ordem():
    m, d = _fixture()
    assert [p["id"] for p in d["portoes"]] == ["P1", "P11", "P18"]
    assert d["pendencias_fechadas_jose"] == ["P5"]


def test_dados_fichas_e_referencias():
    m, d = _fixture()
    assert d["fichas_aguardando"] == []
    assert d["fichas_sugestao"] == ["SIT-acenando"]
    assert d["fichas_permanente"] == 1
    assert d["refs_aguardando"] == []
    assert d["refs_aprovadas"] == 1


def test_secao_e_so_leitura_sem_formulario_botao_ou_rede():
    m, d = _fixture()
    html = m.secao(d)
    assert 'id="portoes"' in html
    assert "P18" in html
    assert "core-alto" in html
    assert "SIT-acenando" in html
    assert "imagens aprovadas" in html
    for proibido in ("<form", "<button", "fetch(", "POST /api", "onclick"):
        assert proibido not in html


def test_secao_escapa_html_das_fontes():
    m, d = _fixture()
    d["portoes"] = [
        {
            "id": "P99",
            "texto": "<script>alert(1)</script>",
            "dono": "José",
            "bloqueio": "nada",
            "aberta": True,
        }
    ]
    html = m.secao(d)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
