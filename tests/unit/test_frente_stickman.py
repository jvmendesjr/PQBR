"""t139u/t144u: fichas do elenco (com roupa chapada e acento), ambientes e objetos sem letra."""
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
    assert _png(PESSOAS / "PERS-M.png") == (1080, 1920)
    assert _png(PESSOAS / "PERS-F.png") == (1080, 1920)
    assert _png(PESSOAS / "PERS-M-folha.png") == (1920, 1080)
    assert _png(PESSOAS / "PERS-F-folha.png") == (1920, 1080)
    assert _png(PESSOAS / "ELENCO-frente.png") == (1920, 1080)


def test_acento_e_roupa_chapada_no_svg_sem_letra():
    m = (PESSOAS / "PERS-M.svg").read_text(encoding="utf-8")
    f = (PESSOAS / "PERS-F.svg").read_text(encoding="utf-8")
    # Acento individual preservado
    assert 'stroke="#e23b2f"' in m and "e6b325" not in m
    assert 'stroke="#e6b325"' in f and "e23b2f" not in f
    # Roupa chapada fixa presente em cada personagem
    assert 'fill="#2b6cb0"' in m and 'fill="#334155"' in m
    assert 'fill="#d96b43"' in f and 'fill="#1e3a5f"' in f
    for texto in (m, f):
        assert "<text" not in texto
        assert "1080" in texto and "1920" in texto


def test_ambientes_e_objetos_gerados_sem_letra():
    for amb in ("AMB-cozinha", "AMB-sala"):
        assert _png(AMBIENTES / f"{amb}.png") == (1080, 1920)
        svg = (AMBIENTES / f"{amb}.svg").read_text(encoding="utf-8")
        assert "<text" not in svg
    for obj in ("OBJ-chaleira", "OBJ-xicara", "OBJ-filtro-pano", "OBJ-controle-remoto"):
        assert _png(OBJETOS / f"{obj}.png") == (1080, 1080)
        svg = (OBJETOS / f"{obj}.svg").read_text(encoding="utf-8")
        assert "<text" not in svg


def test_indice_banco_fichas_aponta_arquivos_existentes():
    idx = json.loads((FICHAS / "indice.json").read_text(encoding="utf-8"))
    assert len(idx["fichas"]) == 8
    for item in idx["fichas"]:
        assert (FICHAS / item["arquivo"]).is_file()
        assert (FICHAS / item["imagem"]).is_file()
        assert (FICHAS / item["svg"]).is_file()
