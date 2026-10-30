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
    assert s.cenas[0].refs == ["PERS-menina-rosa"]            # sem refs na resposta: o protagonista do catálogo (t150u)
    assert s.versao == "1.3.0" and {c.versao for c in s.cenas} == {"1.3.0"}


IDS = {"PERS-menina-rosa", "PERS-menino-azul", "PERS-punk-azul", "AMB-metro", "OBJ-caneca", "SIT-pensando", "ANIM-gato", "FIG-robo", "OBJ-lupa"}


def test_refs_do_catalogo_ficam_e_o_que_nao_existe_sai_da_ficha(monkeypatch):
    monkeypatch.setattr(sb, "_ids_do_catalogo", lambda: IDS)
    cena = {**_cena(), "refs": ["PERS-menina-rosa", "AMB-metro", "AMB-inventado", "ASSET_personagem_pqbr-v1", "OBJ-caneca", "OBJ-caneca", "foto.png", 3]}
    s, fora = sb._montar(_texto(cenas=[cena, _cena(), _cena()]), "PQBR-EP1003")
    assert s.cenas[0].refs == ["PERS-menina-rosa", "AMB-metro", "OBJ-caneca"]
    assert fora == ["c01:AMB-inventado", "c01:ASSET_personagem_pqbr-v1", "c01:foto.png"]
    assert s.cenas[1].refs == ["PERS-menina-rosa"]


def test_ref_do_legado_vira_o_protagonista_do_catalogo(monkeypatch):
    monkeypatch.setattr(sb, "_ids_do_catalogo", lambda: IDS)
    cena = {**_cena(), "refs": ["ASSET_personagem_masculino-v1", "SIT-pensando"]}
    s, fora = sb._montar(_texto(cenas=[cena, _cena(), _cena()]), "PQBR-EP1004")
    assert s.elenco == "masculino" and s.cenas[0].refs == ["PERS-menino-azul", "SIT-pensando"] and fora == []


def test_no_maximo_seis_refs_por_cena(monkeypatch):
    monkeypatch.setattr(sb, "_ids_do_catalogo", lambda: IDS)
    cena = {**_cena(), "refs": ["PERS-menina-rosa", "PERS-punk-azul", "AMB-metro", "OBJ-caneca", "SIT-pensando", "ANIM-gato", "FIG-robo", "OBJ-lupa"]}
    s, fora = sb._montar(_texto(cenas=[cena, _cena(), _cena()]), "PQBR-EP1003")
    assert s.cenas[0].refs == ["PERS-menina-rosa", "PERS-punk-azul", "AMB-metro", "OBJ-caneca", "SIT-pensando", "ANIM-gato"]
    assert fora == ["c01:FIG-robo", "c01:OBJ-lupa"]


def test_coadjuvante_do_catalogo_precisa_existir_e_nao_pode_ser_o_protagonista(monkeypatch):
    monkeypatch.setattr(sb, "_ids_do_catalogo", lambda: IDS)
    just = "o roteiro pede a reação de outra pessoa"
    ok = {**_cena(), "coadjuvante": "PERS-punk-azul", "coadjuvante_justificativa": just}
    assert sb.storyboard_de_texto(_texto(cenas=[_cena(), ok, _cena()]), "PQBR-EP1003").cenas[1].coadjuvante == "PERS-punk-azul"
    fantasma = {**_cena(), "coadjuvante": "PERS-fantasma", "coadjuvante_justificativa": just}
    with pytest.raises(ValueError, match="fora do catálogo"):
        sb.storyboard_de_texto(_texto(cenas=[fantasma, _cena(), _cena()]), "PQBR-EP1003")
    protagonista = {**_cena(), "coadjuvante": "PERS-menina-rosa", "coadjuvante_justificativa": just}
    with pytest.raises(ValidationError, match="coadjuvante"):
        sb.storyboard_de_texto(_texto(cenas=[protagonista, _cena(), _cena()]), "PQBR-EP1003")


def test_sem_indice_do_catalogo_vale_so_a_forma_do_id(monkeypatch):
    monkeypatch.setattr(sb, "_ids_do_catalogo", lambda: None)
    cena = {**_cena(), "refs": ["AMB-qualquer", "foto.png"]}
    s, fora = sb._montar(_texto(cenas=[cena, _cena(), _cena()]), "PQBR-EP1003")
    assert s.cenas[0].refs == ["AMB-qualquer"] and fora == ["c01:foto.png"]


def test_ids_do_catalogo_real_tem_os_protagonistas_e_nao_as_grades():
    ids = sb._ids_do_catalogo()
    assert {"PERS-menino-azul", "PERS-menina-rosa", "PERS-bob-oculos"} <= ids
    assert "ELENCO-catalogo" not in ids and "OBJ-catalogo" not in ids and "ANIM-catalogo" not in ids


def test_prompt_cita_o_protagonista_do_catalogo_e_nao_o_asset_antigo():
    p = sb.PROMPT_STORYBOARD.format(codigo="PQBR-EP1003", elenco="feminino", protagonista="PERS-menina-rosa", roteiro="Roteiro de teste")
    assert p.count("PERS-menina-rosa") == 3 and "catalogo_visual" in p and "ASSET_" not in p and "Cartoon 2D flat colorido" in p
    assert "tubos" not in p and "sem pessoa de cartum" not in p and "varie entre episódios" in p


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
    assert r["pode_gerar_video"] is False and r["cenas"] == 3 and r["refs_descartadas"] == []
    assert json.loads(Path(r["arquivo"]).read_text())["imagens_revisadas"] is False
    with pytest.raises(ValueError, match="fora do diretório"):
        asyncio.run(sb.storyboard_criar(_texto(), "PQBR-EP1003", "/tmp/storyboard-fora.json"))
