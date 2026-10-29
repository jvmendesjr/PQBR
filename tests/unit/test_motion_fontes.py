"""Banco de fontes do motion: leitor sfnt, validação de registro e índice real."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import pytest

from pqbr.pos.motion import fontes

RAIZ_REAL = fontes.RAIZ_FONTES
BALOO = RAIZ_REAL / "baloo-2" / "baloo-2.ttf"
SHORT = RAIZ_REAL / "short-stack" / "short-stack.ttf"
OFL_TXT = RAIZ_REAL / "short-stack" / "LICENSE.txt"


def _sfnt(codepoints: list[int], tag: bytes = b"\x00\x01\x00\x00") -> bytes:
    """Fonte mínima: head, name (familia 'Teste') e cmap formato 4 com os pontos dados."""
    pts = sorted(set(codepoints))
    segs = [(c, c) for c in pts] + [(0xFFFF, 0xFFFF)]
    n = len(segs)
    fins = b"".join(struct.pack(">H", b) for _a, b in segs)
    inis = b"".join(struct.pack(">H", a) for a, _b in segs)
    deltas = b"".join(struct.pack(">h", 1 - a if a != 0xFFFF else 1) for a, _b in segs)
    rangos = b"\x00\x00" * n
    sub = struct.pack(">HHHHHHH", 4, 16 + 8 * n, 0, n * 2, 0, 0, 0) + fins + b"\x00\x00" + inis + deltas + rangos
    cmap = struct.pack(">HH", 0, 1) + struct.pack(">HHI", 3, 1, 12) + sub
    nome = "Teste".encode("utf-16-be")
    name = struct.pack(">HHH", 0, 1, 18) + struct.pack(">HHHHHH", 3, 1, 0x409, 1, len(nome), 0) + nome
    head = b"\x00" * 54
    tabs = {b"cmap": cmap, b"head": head, b"name": name}
    off = 12 + 16 * len(tabs)
    diretorio = b""
    corpo = b""
    for t, d in tabs.items():
        diretorio += struct.pack(">4sIII", t, 0, off + len(corpo), len(d))
        corpo += d + b"\x00" * (-len(d) % 4)
    return tag + struct.pack(">HHHH", len(tabs), 0, 0, 0) + diretorio + corpo


def _licenca(tmp_path: Path) -> Path:
    p = tmp_path / "OFL.txt"
    p.write_text("SIL OPEN FONT LICENSE Version 1.1", encoding="utf-8")
    return p


def test_ler_fonte_variavel_do_banco():
    info = fontes.ler_fonte(BALOO)
    assert info.familia == "Baloo 2"
    assert info.formato == "ttf"
    assert info.variavel is True
    assert info.eixos["wght"][0] == 400 and info.eixos["wght"][2] == 800
    assert "SIL Open Font License" in info.licenca_texto
    assert fontes.faltantes_ptbr(info) == []


def test_ler_fonte_estatica_do_banco():
    info = fontes.ler_fonte(SHORT)
    assert info.familia == "Short Stack"
    assert info.variavel is False
    assert info.eixos == {}
    assert info.peso_classe == 400
    assert fontes.faltantes_ptbr(info) == []


def test_faltantes_ptbr_com_fonte_sintetica(tmp_path):
    p = tmp_path / "s.ttf"
    p.write_bytes(_sfnt(list(range(ord("A"), ord("Z") + 1))))
    info = fontes.ler_fonte(p)
    assert info.familia == "Teste"
    assert set(range(ord("A"), ord("Z") + 1)) <= info.cmap
    falt = fontes.faltantes_ptbr(info)
    assert "a" in falt and "ç" in falt and "–" in falt and "A" not in falt
    assert falt == sorted(falt)


def test_leitor_recusas(tmp_path):
    casos = {
        "lixo.ttf": b"nao sou fonte, apenas texto simples",
        "col.ttf": b"ttcf" + b"\x00" * 20,
        "w2.ttf": b"wOF2" + b"\x00" * 40,
        "w1.ttf": b"wOFF" + b"\x00" * 40,
        "curto.ttf": b"\x00\x01",
        "trunc.ttf": _sfnt([65])[:40],
    }
    for nome, dados in casos.items():
        p = tmp_path / nome
        p.write_bytes(dados)
        with pytest.raises(ValueError):
            fontes.ler_fonte(p)
    p = tmp_path / "w2.ttf"
    with pytest.raises(ValueError, match="TTF/OTF"):
        fontes.ler_fonte(p)


def test_registrar_recusas(tmp_path):
    raiz = tmp_path / "banco"
    lic = _licenca(tmp_path)
    base = dict(origem_url="https://exemplo.org/f", licenca="OFL-1.1", arquivo_licenca=lic, raiz=raiz)

    def tenta(arquivo=SHORT, **kw):
        args = {**base, "id": "boa-fonte", **kw}
        with pytest.raises(ValueError):
            fontes.registrar(arquivo, **args)

    tenta(id="Ruim_ID")
    tenta(id="ab")
    tenta(licenca="GPL-3.0")
    tenta(arquivo_licenca=tmp_path / "nao-existe.txt")
    vazio = tmp_path / "vazio.txt"
    vazio.write_text("")
    tenta(arquivo_licenca=vazio)
    outra = tmp_path / "outra.txt"
    outra.write_text("texto qualquer")
    tenta(arquivo_licenca=outra)
    tenta(origem_url="http://exemplo.org/f")

    incompleta = tmp_path / "inc.ttf"
    incompleta.write_bytes(_sfnt(list(range(65, 91))))
    tenta(arquivo=incompleta)

    nao_fonte = tmp_path / "x.ttf"
    nao_fonte.write_bytes(b"isto nao e uma fonte de verdade")
    tenta(arquivo=nao_fonte)
    woff2 = tmp_path / "f.woff2"
    woff2.write_bytes(b"wOF2" + b"\x00" * 40)
    tenta(arquivo=woff2)
    falso = tmp_path / "f2.ttf"
    falso.write_bytes(b"wOF2" + b"\x00" * 40)
    tenta(arquivo=falso)

    assert fontes.listar(raiz=raiz) == []
    assert not (raiz / "boa-fonte").exists()


def test_fluxo_registrar_listar_aprovar(tmp_path):
    raiz = tmp_path / "banco"
    ent = fontes.registrar(
        SHORT, id="minha-fonte", origem_url="https://exemplo.org/f", licenca="OFL-1.1",
        arquivo_licenca=OFL_TXT, uso="teste", raiz=raiz,
    )
    assert ent["estado"] == "aguardando_ok_jose" and ent["aprovada_em"] is None
    assert ent["pesos"] == [400, 400] and ent["variavel"] is False and "eixos" not in ent
    assert (raiz / ent["arquivo"]).is_file() and (raiz / ent["arquivo_licenca"]).is_file()
    assert ent["sha256"] == hashlib.sha256(SHORT.read_bytes()).hexdigest()
    assert [f["id"] for f in fontes.listar("aguardando_ok_jose", raiz)] == ["minha-fonte"]
    assert fontes.listar("aprovada", raiz) == []
    with pytest.raises(ValueError, match="já existe"):
        fontes.registrar(SHORT, id="minha-fonte", origem_url="https://x.org", licenca="OFL-1.1", arquivo_licenca=OFL_TXT, raiz=raiz)
    ap = fontes.aprovar("minha-fonte", raiz=raiz)
    assert ap["estado"] == "aprovada" and ap["aprovada_por"] == "Jose" and ap["aprovada_em"]
    with pytest.raises(ValueError):
        fontes.aprovar("minha-fonte", raiz=raiz)
    with pytest.raises(KeyError):
        fontes.obter("nao-existe", raiz)
    assert json.loads((raiz / "indice.json").read_text(encoding="utf-8"))["fontes"][0]["estado"] == "aprovada"


def test_registrar_variavel_grava_eixos(tmp_path):
    ent = fontes.registrar(
        BALOO, id="baloo-copia", origem_url="https://exemplo.org/f", licenca="OFL-1.1",
        arquivo_licenca=OFL_TXT, raiz=tmp_path / "b",
    )
    assert ent["variavel"] is True and ent["pesos"] == [400, 800] and ent["eixos"]["wght"] == [400, 800]


def test_fonte_css(tmp_path):
    raiz = tmp_path / "banco"
    fontes.registrar(BALOO, id="baloo-copia", origem_url="https://exemplo.org/f", licenca="OFL-1.1", arquivo_licenca=OFL_TXT, raiz=raiz)
    css = fontes.fonte_css("baloo-copia", raiz)
    assert "\n" not in css
    assert 'font-family:"PQBR-baloo-copia"' in css
    assert "file:///" in css and 'format("truetype")' in css
    assert "font-weight:400 800" in css
    assert fontes.familia_css("x-y") == "PQBR-x-y"


def test_indice_real_do_repo():
    indice = json.loads((RAIZ_REAL / "indice.json").read_text(encoding="utf-8"))
    assert indice["versao"] == "1.0.0" and indice["fontes"]
    ids = [f["id"] for f in indice["fontes"]]
    assert len(ids) == len(set(ids))
    for f in indice["fontes"]:
        arq = RAIZ_REAL / f["arquivo"]
        assert arq.is_file() and (RAIZ_REAL / f["arquivo_licenca"]).stat().st_size > 0
        assert hashlib.sha256(arq.read_bytes()).hexdigest() == f["sha256"]
        assert arq.stat().st_size == f["tamanho"]
        assert f["estado"] in fontes.ESTADOS
        if f["estado"] == "aprovada":
            assert f["aprovada_por"] == "Jose" and f["aprovada_em"]
        else:
            assert f["aprovada_por"] is None and f["aprovada_em"] is None, "quem aprova é o José"
        assert f["cobertura_ptbr"] is True
        assert f["licenca"] in fontes.LICENCAS_LIVRES
        assert f["origem_url"].startswith("https://")
        assert fontes.faltantes_ptbr(fontes.ler_fonte(arq)) == []


def test_remover_candidata_e_aprovada(tmp_path):
    raiz = tmp_path / "banco"
    base = dict(origem_url="https://exemplo.org/f", licenca="OFL-1.1", arquivo_licenca=OFL_TXT, raiz=raiz)
    fontes.registrar(SHORT, id="fonte-a", **base)
    fontes.registrar(SHORT, id="fonte-b", **base)
    fontes.aprovar("fonte-b", raiz=raiz)
    saiu = fontes.remover("fonte-a", raiz=raiz)
    assert saiu["id"] == "fonte-a" and not (raiz / "fonte-a").exists()
    assert [f["id"] for f in fontes.listar(raiz=raiz)] == ["fonte-b"]
    with pytest.raises(ValueError, match="ordem do José"):
        fontes.remover("fonte-b", raiz=raiz)
    assert (raiz / "fonte-b").is_dir()
    fontes.remover("fonte-b", por_jose=True, raiz=raiz)
    assert fontes.listar(raiz=raiz) == [] and not (raiz / "fonte-b").exists()
    with pytest.raises(KeyError):
        fontes.remover("fonte-b", raiz=raiz)


def test_nomes_canonicos_ascii_no_banco_e_no_registro(tmp_path):
    import re

    ent = fontes.registrar(
        BALOO, id="baloo-copia", origem_url="https://exemplo.org/f", licenca="OFL-1.1",
        arquivo_licenca=OFL_TXT, raiz=tmp_path / "b",
    )
    assert ent["arquivo"] == "baloo-copia/baloo-copia.ttf" and ent["arquivo_licenca"] == "baloo-copia/LICENSE.txt"
    assert ent["arquivo_original"] == BALOO.name
    for f in fontes.listar():
        if f["id"] in {"baloo-2", "fredoka", "short-stack", "shantell-sans"}:
            assert re.fullmatch(r"[a-z0-9-]+/[a-z0-9-]+\.(ttf|otf)", f["arquivo"]), f["arquivo"]


def test_fonte_css_com_eixo_de_largura():
    css = fontes.fonte_css("fredoka")
    assert "font-weight:300 700" in css and "font-stretch:75% 125%" in css

