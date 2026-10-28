"""t139u: a frente do elenco é desenho, com um acento cada, e não leva letra."""
import struct
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PESSOAS = RAIZ / "banco-fichas" / "personagens"


def _png(nome: str) -> tuple[int, int]:
    dados = (PESSOAS / nome).read_bytes()
    assert dados[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", dados[16:24])


def test_frentes_verticais_e_comparacao_deitada():
    assert _png("PERS-M.png") == (1080, 1920)
    assert _png("PERS-F.png") == (1080, 1920)
    assert _png("ELENCO-frente.png") == (1920, 1080)


def test_acento_esta_no_svg_e_nao_ha_letra():
    m = (PESSOAS / "PERS-M.svg").read_text(encoding="utf-8")
    f = (PESSOAS / "PERS-F.svg").read_text(encoding="utf-8")
    assert 'stroke="#e23b2f"' in m and "e6b325" not in m
    assert 'stroke="#e6b325"' in f and "e23b2f" not in f
    for texto in (m, f):
        assert "<text" not in texto
        assert "1080" in texto and "1920" in texto
