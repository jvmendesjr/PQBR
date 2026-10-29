"""t148u/t150u: o banco de fichas real (`banco-fichas/`) é consistente: índice 3.1.0, arquivos, recortes, referências e protagonistas."""
import json
import struct
from pathlib import Path

from pqbr.contratos.catalogo_visual import ID_ELENCO, PASTA, PROTAGONISTAS, TAMANHO_MAX_IMAGEM, FichaCatalogo
from pqbr.pipeline import banco_fichas as bf

RAIZ = Path(__file__).resolve().parents[2]
FICHAS = RAIZ / "banco-fichas"
FOLHAS = ("PERS-menina-rosa", "PERS-cacheada", "PERS-bone-verde", "PERS-gravata-azul", "PERS-roxo-ansioso", "PERS-bob-oculos")
AMBIENTES = ("AMB-praca", "AMB-calcadao-mar", "AMB-pista-skate", "AMB-jardim", "AMB-sala-estar", "AMB-escritorio", "AMB-estudio-foto",
             "AMB-cafe", "AMB-metro", "AMB-skate-urbano", "AMB-calcada-compras")
# O que o José entregou ou escolheu (t148u, t150u). O agente acrescenta fichas, mas a semente não some nem perde a aprovação.
SEMENTE = {ID_ELENCO, "OBJ-catalogo", "ANIM-catalogo", "PERS-menino-azul", *FOLHAS, *AMBIENTES}


def _indice() -> dict:
    return json.loads((FICHAS / "indice.json").read_text(encoding="utf-8"))


def _png(caminho: Path) -> tuple[int, int]:
    dados = caminho.read_bytes()
    assert dados[:8] == b"\x89PNG\r\n\x1a\n", caminho
    return struct.unpack(">II", dados[16:24])


def test_indice_3_1_0_traz_o_estilo_e_a_regra_do_catalogo_aberto():
    idx = _indice()
    assert idx["versao"] == "3.1.0" and idx["decisao"] == "t131u"
    assert "cartoon 2D" in idx["estilo"] and "flat" in idx["estilo"] and "stickman" in idx["estilo"]
    assert "Catálogo aberto" in idx["regra_catalogo_aberto"] and "2 MB" in idx["regra_catalogo_aberto"]
    assert isinstance(idx["descartadas"], list)
    assert set(idx["categorias"]) == set(PASTA)
    for tipo, cat in idx["categorias"].items():
        assert cat["pasta"] == PASTA[tipo]


def test_toda_ficha_e_valida_e_aponta_arquivos_existentes():
    idx = _indice()
    ids = [d["id"] for d in idx["fichas"]]
    assert len(ids) == len(set(ids)), "id repetido"
    imagens_da_semente = {d["imagem"] for d in idx["fichas"] if d["id"] in SEMENTE and d.get("imagem")}
    for d in idx["fichas"]:
        f = FichaCatalogo.model_validate(d)
        assert bf.caminho_md(f, FICHAS).is_file(), f"{f.id}: falta o .md"
        if f.imagem:
            imagem = FICHAS / f.imagem
            assert imagem.is_file(), f"{f.id}: imagem {f.imagem} não existe"
            if imagem.suffix == ".png": _png(imagem)
            assert imagem.stat().st_size <= TAMANHO_MAX_IMAGEM or f.imagem in imagens_da_semente, f"{f.id}: imagem nova acima de 2 MB (use o Drive)"
        for ref in (*f.personagens, *f.objetos, *([f.ambiente] if f.ambiente else [])):
            assert ref in ids, f"{f.id} cita {ref}, que não está no catálogo"
        assert len(f.recortes) <= 24


def test_nao_sobra_arquivo_sem_ficha():
    idx = _indice()
    ids = {d["id"] for d in idx["fichas"]}
    imagens = {d["imagem"] for d in idx["fichas"] if d.get("imagem")}
    for pasta in PASTA.values():
        for arquivo in sorted((FICHAS / pasta).glob("*")) if (FICHAS / pasta).is_dir() else []:
            if arquivo.suffix == ".md": assert arquivo.stem in ids, f"{arquivo}: .md sem ficha no índice"
            else: assert f"{pasta}/{arquivo.name}" in imagens, f"{arquivo}: arquivo que nenhuma ficha usa"


def test_a_semente_do_jose_segue_permanente():
    por_id = {d["id"]: d for d in _indice()["fichas"]}
    assert SEMENTE <= set(por_id)
    for id_ in SEMENTE:
        assert por_id[id_]["estado"] == "permanente" and por_id[id_]["origem"] == "jose", id_


def test_protagonistas_do_jose_e_bob_oculos_no_catalogo():
    idx = _indice()
    assert idx["protagonistas"] == PROTAGONISTAS == {"masculino": "PERS-menino-azul", "feminino": "PERS-menina-rosa"}
    assert bf.protagonista("masculino", FICHAS).elenco_num == 1
    assert bf.protagonista("feminino", FICHAS).elenco_num == 2
    assert bf.obter("PERS-bob-oculos", FICHAS).elenco_num == 13
    nums = [f.elenco_num for f in bf.listar("personagem", raiz=FICHAS) if f.elenco_num is not None]
    assert len(nums) == len(set(nums)) and set(range(1, 14)) <= set(nums)


def test_config_de_estilo_bate_com_o_indice():
    cfg = json.loads((RAIZ / "config" / "estilo_visual.json").read_text(encoding="utf-8"))
    idx = _indice()
    estilo = cfg["estilos"][cfg["ativo"]].lower()
    assert "cartoon 2d flat colorido" in estilo and "stickman" in estilo
    protagonistas = {k: v for k, v in cfg["elenco"]["protagonistas"].items() if not k.startswith("_")}
    assert protagonistas == idx["protagonistas"] == PROTAGONISTAS
    com_folha = {d["id"]: d["elenco_num"] for d in idx["fichas"] if d.get("folha_individual")}
    assert {k: v["elenco_num"] for k, v in cfg["elenco"]["folhas"].items()} == com_folha
    for id_, item in cfg["elenco"]["folhas"].items():
        assert (RAIZ / item["ficha"]).is_file() and (RAIZ / item["imagem"]).is_file(), id_
    assert "EM CONSTRUÇÃO" not in json.dumps(cfg, ensure_ascii=False)


def test_o_catalogo_dos_12_tem_um_recorte_por_numero_e_o_cachecol_do_3_e_cinza():
    grade = bf.obter(ID_ELENCO, FICHAS)
    assert grade.papel == "colecao" and sorted(grade.recortes) == [f"num-{n:02d}" for n in range(1, 13)]
    senhor = bf.obter("PERS-senhor-cachecol", FICHAS)
    assert senhor.elenco_num == 3 and senhor.recortes["num-03"] == grade.recortes["num-03"] and "cachecol cinza" in senhor.trava
    assert "sapatos brancos" in bf.obter("PERS-menina-rosa", FICHAS).trava


def test_folhas_de_personagem_sao_paisagem_com_giros_expressoes_e_poses():
    folhas = sorted((FICHAS / "personagens").glob("PERS-*-folha.png"))
    assert [f.name for f in folhas] == sorted(f"{i}-folha.png" for i in FOLHAS)
    for folha in folhas:
        largura, altura = _png(folha)
        assert largura > altura, folha
        recortes = bf.obter(folha.name.removesuffix("-folha.png"), FICHAS).recortes
        assert len(recortes) == 24 and {"giro-frente", "giro-perfil", "exp-feliz", "pose-base", "pose-explicando"} <= set(recortes), folha


def test_situacoes_sao_acoes_e_a_pasta_do_tipo_existe():
    situacoes = bf.listar("situacao", raiz=FICHAS)
    assert situacoes and all(s.acao and s.id.startswith("SIT-") for s in situacoes)
    assert (FICHAS / "situacoes").is_dir() and (FICHAS / "modelos" / "situacao.md").is_file() and (FICHAS / "modelos" / "figura.md").is_file()


def test_resumo_do_catalogo_real_cabe_no_prompt_sem_cortar():
    texto = bf.resumo_para_prompt(FICHAS)
    assert "[protagonista masculino]" in texto and "[protagonista feminino]" in texto and "PERS-bob-oculos" in texto
    assert "Situações" in texto and not texto.endswith("- …"), "o resumo passou do limite: suba o limite de resumo_para_prompt"


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


def test_referencias_do_canal_foram_removidas_em_t149u():
    idx = _indice()
    assert idx["referencias_canal"]["estado"].startswith("descartado") and "arquivos" not in idx["referencias_canal"]
    assert not (FICHAS / "referencias-canal").exists()
