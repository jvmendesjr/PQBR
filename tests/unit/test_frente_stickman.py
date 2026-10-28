"""t139u/t144u/t146u: fichas permanentes geradas no Google Flow (Nano Banana Pro) ancoradas nas referências reais do canal."""
import json
import struct
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FICHAS = RAIZ / "banco-fichas"
PESSOAS = FICHAS / "personagens"
AMBIENTES = FICHAS / "ambientes"
OBJETOS = FICHAS / "objetos"


def _png(caminho: Path) -> tuple[int, int]:
    dados = caminho.read_bytes()
    assert dados[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", dados[16:24])


def test_frentes_verticais_folhas_e_comparacao_deitada():
    assert _png(PESSOAS / "PERS-M.png") == (768, 1376)
    assert _png(PESSOAS / "PERS-F.png") == (768, 1376)
    assert _png(PESSOAS / "PERS-M-classico.png") == (768, 1376)
    assert _png(PESSOAS / "PERS-M-folha.png") == (1376, 768)
    assert _png(PESSOAS / "PERS-F-folha.png") == (1376, 768)
    assert _png(PESSOAS / "PERS-M-classico-folha.png") == (1376, 768)


def test_acento_e_roupa_chapada_no_svg_sem_letra():
    m = (PESSOAS / "PERS-M.svg").read_text(encoding="utf-8")
    f = (PESSOAS / "PERS-F.svg").read_text(encoding="utf-8")
    assert 'stroke="#e23b2f"' in m and "e6b325" not in m
    assert 'stroke="#e6b325"' in f and "e23b2f" not in f
    for texto in (m, f):
        assert "<text" not in texto


def test_ambientes_e_objetos_gerados_sem_letra():
    for amb in ("AMB-cozinha", "AMB-sala"):
        assert _png(AMBIENTES / f"{amb}.png") == (768, 1376)
    for obj in ("OBJ-chaleira", "OBJ-xicara", "OBJ-filtro-pano", "OBJ-controle-remoto"):
        assert _png(OBJETOS / f"{obj}.png") == (1024, 1024)


def test_indice_banco_fichas_aponta_arquivos_existentes():
    idx = json.loads((FICHAS / "indice.json").read_text(encoding="utf-8"))
    assert idx["modelo_geracao"] == "Nano Banana Pro"
    assert len(idx["referencias_canal"]) == 6
    for ref in idx["referencias_canal"]:
        assert (FICHAS / ref).is_file()
    assert len(idx["fichas"]) == 9
    for item in idx["fichas"]:
        assert item["permanente"] is True
        assert item["modelo_ficha"] == "Nano Banana Pro"
        assert (FICHAS / item["arquivo"]).is_file()
        assert (FICHAS / item["imagem"]).is_file()
        if "folha" in item:
            assert (FICHAS / item["folha"]).is_file()
