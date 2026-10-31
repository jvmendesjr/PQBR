"""Passo 1 pós-roteiro: DirecaoCenas 2.0.0 + adaptador falso (sem rede)."""
from __future__ import annotations
import asyncio
import pytest
from pydantic import ValidationError
from pqbr.contratos.cena import CenaIndividual
from pqbr.contratos.direcao_cenas import VERSAO, DirecaoCenas
from pqbr.motores.direcao_cenas import AdaptadorFalsoDirecao, parse_cenas, diretor_cenas
from pqbr.pipeline.validar_direcao_cenas import validar_lista
from pqbr.workflows.episodio import direcao_cenas_nlm, flow_projeto_exigir_antes_cenas


ANIM = "Locked camera, slow push-in, lips closed, only blinking and breathing."


def _cena(n=1, **kw):
    base = dict(
        numero=n, rotulo=f"PQBR-EP1003-S{n:02d}",
        fala="Café fraco vira chá de bico no Brasil contemporâneo.",
        norte="mostrar o café ralo na xícara",
        inicio="Mulher jovem adulta stickman em pé no café, xícara na mão.",
        fim="Mesma câmera, ela olha a xícara com surpresa, cabeça inteira no quadro.",
        movimento="ergue a xícara; push-in lento",
        enquadramento="plano_medio",
        prompt_imagem=(
            "Cartoon 2D flat colorido stickman, mulher jovem adulta, cabeça redonda branca, "
            "@PERS-menina-rosa holds a clear cup, full body on the floor, cafe kitchen, 9:16."
        ),
        prompt_animacao=ANIM,
        refs=["PERS-menina-rosa", "AMB-cafe", "OBJ-caneca"],
        papel_personagem="observa", figurino="atual_variavel",
        expressao="sobrancelhas levantadas, boca de reação fechada",
        cenario_encaixe="em pé no chão ao lado do balcão do café",
    )
    base.update(kw)
    return base


def test_contrato_direcao_2_0_0():
    cenas = [CenaIndividual(**_cena(1)), CenaIndividual(**_cena(2))]
    d = DirecaoCenas(
        codigo="PQBR-EP1003", slug="cafe-fraco", caderno="nb-abc12345",
        estilo_aplicado="Cartoon 2D flat colorido com personagens stickman do canal",
        cenas=cenas,
    )
    assert d.versao == VERSAO == "2.0.0"
    assert d.proximo == "flow_cenas_individuais_pendente"


def test_adaptador_falso_sem_rede():
    d = AdaptadorFalsoDirecao().direcionar(
        codigo="PQBR-EP1003", slug="cafe-fraco", caderno="nb-fake-12345678", n_cenas=3,
    )
    assert d.versao == "2.0.0" and len(d.cenas) == 3
    assert all("stickman" in c.prompt_imagem.lower() for c in d.cenas)
    assert "PERS-menina-rosa" in d.cenas[0].refs
    assert d.cenas[0].rotulo == "PQBR-EP1003-S01"


def test_fail_closed_ref_inexistente():
    with pytest.raises(ValueError, match="inexistente"):
        validar_lista([CenaIndividual(**_cena(refs=["PERS-nao-existe"]))])


def test_fail_closed_girl_em_adulta():
    with pytest.raises(ValueError, match="girl"):
        validar_lista([CenaIndividual(**_cena(prompt_imagem=_cena()["prompt_imagem"] + " girl pouring"))])


def test_fail_closed_sem_persona_adulta():
    img = "Cartoon 2D flat stickman @PERS-menina-rosa holds a cup, 9:16."  # sem adulta
    with pytest.raises(ValueError, match="adulta"):
        validar_lista([CenaIndividual(**_cena(prompt_imagem=img))])


def test_fail_closed_sem_stickman_no_prompt():
    img = "Cartoon 2D flat colorido, mulher jovem adulta holds a cup, 9:16."
    with pytest.raises(ValueError, match="stickman"):
        validar_lista([CenaIndividual(**_cena(prompt_imagem=img))])


def test_parse_cenas_completa_lips_e_rotulo():
    import json
    corpo = {"cenas": [_cena(1), _cena(2)]}
    corpo["cenas"][0]["prompt_animacao"] = "slow push-in"
    txt = "prefixo\n" + json.dumps(corpo) + "\nsufixo"
    cenas = parse_cenas(txt, "PQBR-EP1003", 2)
    assert cenas[0].rotulo == "PQBR-EP1003-S01"
    assert "lips closed" in cenas[0].prompt_animacao.lower()


def test_activity_com_adaptador_falso():
    out = asyncio.run(direcao_cenas_nlm({
        "codigo": "PQBR-EP1003", "slug": "cafe-fraco",
        "caderno": "nb-fake-12345678", "n_cenas": 2, "adaptador": "falso",
    }))
    assert out["versao"] == "2.0.0"
    assert len(out["cenas"]) == 2
    assert out["proximo"] == "flow_cenas_individuais_pendente"


def test_gate_flow_antes_cenas_ep1003():
    r = asyncio.run(flow_projeto_exigir_antes_cenas("EP1003"))
    assert r["ok"] is True and r["pode_gerar_cenas"] is True


def test_diretor_selecao():
    assert diretor_cenas("falso").nome == "falso"
    with pytest.raises(KeyError):
        diretor_cenas("xyz")
