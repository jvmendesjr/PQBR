import json, pytest
from pqbr.workflows.criativo import roteiro_de_texto, steering_de_roteiro, roteiro_markdown
from pqbr.contratos import CTA, ESTILO_PADRAO_2D
from pqbr.kit.router9 import combo

def _rot(n=8, fontes=2, tipo_cta="fallback", cta=CTA):
    falas = ["Por que a gente diz que algo custou os olhos da cara quando é muito caro hoje em dia no Brasil?"] * (n - 1) + [cta]
    cenas = [{"fala": f, "acao": "aponta para a vitrine", "enquadramento": "plano médio", "ambiente": "rua de comércio"} for f in falas]
    return {"titulo": "Custou os olhos da cara", "falas": falas, "tipo_cta": tipo_cta, "entidades_cena": ["vitrine"],
            "bloco_visual": {"personagem": "Homem de 40 anos, bigode grosso, camisa amarela e calça marrom", "cenas": cenas},
            "fontes": ["https://a.example", "https://b.example"][:fontes]}

def test_roteiro_nlm_valido_com_texto_em_volta():
    r, f = roteiro_de_texto("Aqui está:\n```json\n" + json.dumps(_rot()) + "\n```", "olhos-da-cara")
    assert r["episodio_id"] == "olhos-da-cara" and r["bloco_visual"]["estilo"] == ESTILO_PADRAO_2D and len(f) == 2
    assert r["tipo_cta"] == "fallback"
    assert "[PERSONAGEM]" in steering_de_roteiro(r) and "## Fontes" in roteiro_markdown(r, f)

def test_roteiro_nlm_contextual_preserva_tipo_e_artefato():
    cta = "Segue o canal: a curiosidade também sobe como o elevador."
    r, fontes = roteiro_de_texto(json.dumps(_rot(tipo_cta="trocadilho_tema", cta=cta)), "elevador-duplo")
    assert r["tipo_cta"] == "trocadilho_tema"
    assert r["falas"][-1] == cta
    assert "**Tipo de CTA:** `trocadilho_tema`" in roteiro_markdown(r, fontes)


def test_roteiro_nlm_sem_fontes_reprova():
    with pytest.raises(ValueError): roteiro_de_texto(json.dumps(_rot(fontes=1)), "olhos-da-cara")

def test_roteiro_nlm_sem_json_reprova():
    with pytest.raises(ValueError): roteiro_de_texto("não sei", "x-y")

def test_combo_por_papel():
    assert combo("roteirista") == "core-alto" and combo("lider-editorial") == "core-medio"
    assert combo("especialista-seo") == "core-baixo" and combo("revisao") == "core-revisao"
    with pytest.raises(KeyError): combo("inexistente")
