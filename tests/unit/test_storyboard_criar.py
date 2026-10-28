import asyncio, json
from pathlib import Path
import pytest
from pydantic import ValidationError
from pqbr.contratos.gasto import GASTO_FLOW_IMAGEM, GASTO_FLOW_VIDEO, GASTO_IMAGEM_NLM, GASTO_STORYBOARD, GASTO_VIDEO_NLM
from pqbr.workflows import storyboard as sb


def _cena():
    return {
        "fala": "Café fraco vira chá de bico.",
        "norte": "mostrar o café ralo na xícara",
        "inicio": "Xícara branca com café claro sobre a mesa, plano médio.",
        "fim": "Personagem olha a xícara, cabeça e óculos inteiros no quadro.",
        "movimento": "ergue a xícara; push-in lento",
        "enquadramento": "plano_medio",
        "prompt_imagem": "Flat 2D cartoon, bold black outlines, medium shot, character holds a cup, full head visible.",
        "prompt_animacao": "Locked camera, slow push-in.",
        "papel_personagem": "observa",
        "figurino": "atual_variavel",
        "expressao": "sobrancelhas lá em cima, careta de nojo do café ralo",
        "cenario_encaixe": "sentado à mesa da cozinha, no centro",
    }


def _texto(**kw):
    corpo = {
        "norte_geral": "explicar a origem da expressão com humor leve",
        "bloco_estilo": "Flat 2D cartoon, bold outlines, flat warm colors",
        "ficha_personagem": "mulher morena, cabelo liso, mais baixa que o masculino",
        "elenco": "masculino",
        "imagens_revisadas": True,
        "cenas": [_cena(), _cena(), _cena()],
    }
    corpo.update(kw)
    return "texto antes\n```json\n" + json.dumps(corpo) + "\n```"


def test_forca_elenco_lips_e_nao_libera_video():
    s = sb.storyboard_de_texto(_texto(), "PQBR-EP1003")
    assert s.elenco == "feminino" and s.elenco_excecao is None and s.imagens_revisadas is False
    assert s.pode_gerar_video() is False
    assert s.cenas[0].rotulo == "PQBR-EP1003_c01"
    assert "lips closed" in s.cenas[0].prompt_animacao
    assert s.cenas[0].refs == ["ASSET_personagem_feminino-v1"]


def test_fala_no_prompt_reprova():
    cena = _cena()
    cena["prompt_imagem"] = 'Flat 2D cartoon. He says "olá pessoal" with a cup.'
    with pytest.raises(ValidationError):
        sb.storyboard_de_texto(_texto(cenas=[cena, _cena(), _cena()]), "PQBR-EP1003")


def test_gasto_desta_etapa():
    assert GASTO_STORYBOARD.pode_gastar and GASTO_STORYBOARD.modelo == "notebooklm-chat"
    assert GASTO_STORYBOARD.meio == "chat_caderno"
    assert GASTO_VIDEO_NLM.pode_gastar is False and GASTO_IMAGEM_NLM.pode_gastar is False
    assert GASTO_FLOW_IMAGEM.pode_gastar and GASTO_FLOW_IMAGEM.meio == "imagem"
    assert "Nano Banana 2 Lite" in GASTO_FLOW_IMAGEM.deterministico
    assert GASTO_FLOW_VIDEO.pode_gastar and "Vids" in GASTO_FLOW_VIDEO.deterministico


def test_activity_grava_so_dentro_do_trabalho(monkeypatch, tmp_path):
    monkeypatch.setattr(sb, "TRAB", tmp_path)
    dest = tmp_path / "cafe-fraco" / "storyboard.json"
    r = asyncio.run(sb.storyboard_criar(_texto(), "PQBR-EP1003", str(dest)))
    assert r["pode_gerar_video"] is False and r["cenas"] == 3
    assert json.loads(Path(r["arquivo"]).read_text())["imagens_revisadas"] is False
    with pytest.raises(ValueError, match="fora do diretório"):
        asyncio.run(sb.storyboard_criar(_texto(), "PQBR-EP1003", "/tmp/storyboard-fora.json"))
