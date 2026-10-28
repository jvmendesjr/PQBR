"""t148u: o banco de fichas definitivo é o conjunto entregue pelo José no Drive (Fontes/Imagens)."""
import json
import struct
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FICHAS = RAIZ / "banco-fichas"


def _png(caminho: Path) -> tuple[int, int]:
    dados = caminho.read_bytes()
    assert dados[:8] == b"\x89PNG\r\n\x1a\n", caminho
    return struct.unpack(">II", dados[16:24])


def test_indice_aponta_arquivos_existentes():
    idx = json.loads((FICHAS / "indice.json").read_text(encoding="utf-8"))
    assert idx["versao"] == "2.0.0" and idx["decisao"] == "t148u"
    assert len(idx["fichas"]) == 20
    for item in idx["fichas"]:
        assert item["permanente"] is True
        assert item["estado"] == "permanente"
        assert (FICHAS / item["arquivo"]).is_file(), item["id"]
        imagem = FICHAS / item["imagem"]
        assert imagem.is_file(), item["id"]
        assert _png(imagem), item["id"]


def test_contagens_por_tipo_e_referencias_historicas():
    idx = json.loads((FICHAS / "indice.json").read_text(encoding="utf-8"))
    tipos: dict[str, int] = {}
    for item in idx["fichas"]:
        tipos[item["tipo"]] = tipos.get(item["tipo"], 0) + 1
    assert tipos == {"personagem": 7, "ambiente": 11, "objeto": 1, "animal": 1}
    assert idx["referencias_canal"]["estado"].startswith("historico")
    for ref in idx["referencias_canal"]["arquivos"]:
        assert (FICHAS / ref).is_file()


def test_fichas_nanquim_de_t146u_foram_descartadas():
    for antiga in ("PERS-M", "PERS-F", "PERS-M-classico", "ELENCO-frente"):
        assert not (FICHAS / "personagens" / f"{antiga}.png").exists()
    for antiga in ("AMB-cozinha", "AMB-sala"):
        assert not (FICHAS / "ambientes" / f"{antiga}.png").exists()
    for antiga in ("OBJ-chaleira", "OBJ-xicara", "OBJ-filtro-pano", "OBJ-controle-remoto"):
        assert not (FICHAS / "objetos" / f"{antiga}.png").exists()
    # o gerador programático de t144u foi aposentado junto
    assert (RAIZ / "scripts" / "aposentado" / "frente_stickman.py").is_file()
    assert not (RAIZ / "scripts" / "visual" / "frente_stickman.py").exists()


def test_folhas_de_personagem_sao_paisagem():
    folhas = sorted((FICHAS / "personagens").glob("PERS-*-folha.png"))
    assert len(folhas) == 6
    for folha in folhas:
        largura, altura = _png(folha)
        assert largura > altura, folha
