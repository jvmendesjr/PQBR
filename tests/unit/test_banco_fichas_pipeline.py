"""t150u: pipeline do catálogo aberto (registrar, anexar mídia, recortes, aprovar, descartar, buscar, resumo) num banco temporário."""
import json
import struct
import zlib
from pathlib import Path

import pytest

from pqbr.pipeline import banco_fichas as bf

TRAVA_PERS = ("Stickman 2D flat colorido do canal Porquê BR: moça de cabelo ruivo preso em coque e jaqueta verde chapada. Cabeça redonda branca grande "
              "com contorno preto, dois olhos pretos sempre visíveis, boca de reação, fundo claro em tom creme, sem texto e sem marca na imagem.")
TRAVA_OBJ = "Lupa de cabo marrom e aro dourado em cartoon 2D flat colorido, contorno preto e cores chapadas suaves, sem texto e sem marca."
DRIVE = "1AbCdEfGhIjKlMnOpQrSt"


def png(lado: int = 2, extra: int = 0) -> bytes:
    def pedaco(tipo: bytes, dados: bytes) -> bytes:
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)
    cru = b"".join(b"\x00" + b"\xff\xff\xff" * lado for _ in range(lado))
    return (b"\x89PNG\r\n\x1a\n" + pedaco(b"IHDR", struct.pack(">IIBBBBB", lado, lado, 8, 2, 0, 0, 0))
            + pedaco(b"IDAT", zlib.compress(cru)) + pedaco(b"IEND", b"") + b"\x00" * extra)


@pytest.fixture()
def banco(tmp_path) -> Path:
    raiz = tmp_path / "banco-fichas"
    (raiz / "personagens").mkdir(parents=True)
    (raiz / "personagens" / "PERS-menino-azul-folha.png").write_bytes(png())
    (raiz / "personagens" / "PERS-menina-rosa-folha.png").write_bytes(png())
    (raiz / "personagens" / "PERS-menina-rosa.md").write_text("# PERS-menina-rosa\n\nEstado: `permanente` — escrita à mão.\n", encoding="utf-8")
    base = [
        dict(id="PERS-menino-azul", tipo="personagem", titulo="Menino de camiseta azul", trava=TRAVA_PERS.replace("moça", "menino"), estado="permanente", origem="jose",
             criado_em="2026-10-28", imagem="personagens/PERS-menino-azul-folha.png", acento="camiseta azul", tags=["masculino"]),
        dict(id="PERS-menina-rosa", tipo="personagem", titulo="Menina de vestido rosa", trava=TRAVA_PERS, estado="permanente", origem="jose",
             criado_em="2026-10-28", imagem="personagens/PERS-menina-rosa-folha.png", acento="vestido rosa", tags=["feminino"]),
    ]
    (raiz / "indice.json").write_text(json.dumps({"versao": "3.0.0", "fichas": base, "protagonistas": {"masculino": "PERS-menino-azul", "feminino": "PERS-menina-rosa"}},
                                                 ensure_ascii=False), encoding="utf-8")
    return raiz


def lupa(banco, **kw):
    args = dict(tipo="objeto", slug="lupa", titulo="Lupa de investigação", trava=TRAVA_OBJ, tags=["lupa", "investigacao"], raiz=banco)
    args.update(kw)
    return bf.registrar(**args)


def test_registrar_sem_midia_vira_sugestao_com_md_gerado(banco):
    r = bf.registrar(tipo="situacao", slug="acenando", titulo="Acenando para cumprimentar", acao="Levanta uma mão aberta e balança para cumprimentar",
                     trava="Corpo inteiro de frente, uma mão aberta no alto, sorriso de reação.", tags=["gesto"], raiz=banco)
    assert r["id"] == "SIT-acenando" and r["estado"] == "sugestao" and r["imagem"] is None and r["arquivo"] == "situacoes/SIT-acenando.md"
    md = (banco / r["arquivo"]).read_text(encoding="utf-8")
    assert md.startswith(bf.MARCA_MD) and "Estado: `sugestao`" in md and "Mídia:** pendente" in md and "Levanta uma mão" in md
    assert bf.obter("SIT-acenando", banco).origem == "agente"
    assert json.loads((banco / "indice.json").read_text(encoding="utf-8"))["atualizado"]


def test_registrar_com_imagem_copia_o_arquivo_e_fica_aguardando_o_jose(banco, tmp_path):
    origem = tmp_path / "lupa.png"
    origem.write_bytes(png())
    r = lupa(banco, imagem_origem=origem)
    assert r["estado"] == "aguardando_ok_jose" and r["imagem"] == "objetos/OBJ-lupa.png"
    assert (banco / "objetos" / "OBJ-lupa.png").read_bytes() == origem.read_bytes()
    assert (banco / "objetos" / "OBJ-lupa.md").is_file()


def test_registrar_nao_sobrescreve_nem_repete_titulo(banco):
    lupa(banco)
    with pytest.raises(ValueError, match="já existe"):
        lupa(banco)
    with pytest.raises(ValueError, match="mesmo título: OBJ-lupa"):
        lupa(banco, slug="lupa-2", titulo="LUPA de investigação")
    assert [f.id for f in bf.listar("objeto", raiz=banco)] == ["OBJ-lupa"]


def test_registrar_devolve_similares_antes_de_criar(banco):
    lupa(banco)
    r = lupa(banco, slug="lupa-grande", titulo="Lupa gigante de detetive", tags=["lupa"])
    assert "OBJ-lupa" in r["similares"]


def test_registrar_valida_tudo_antes_de_gravar(banco, tmp_path):
    antes = (banco / "indice.json").read_text(encoding="utf-8")
    origem = tmp_path / "lupa.png"
    origem.write_bytes(png())
    ruins = [
        dict(trava="Lupa de cabo marrom em 3D realista com sombra volumétrica detalhada."),
        dict(trava="Lupa de cabo marrom que se chama Zé, em cartoon 2D flat colorido simples."),
        dict(trava="Lupa de cabo marrom com o texto 'detetive' escrito no cabo, em cartoon 2D flat."),
        dict(slug="Lupa"),
        dict(tipo="invalido"),
        dict(personagens=["PERS-inexistente"]),
        dict(origem="jose"),
    ]
    for ruim in ruins:
        with pytest.raises(ValueError):
            lupa(banco, imagem_origem=origem, **ruim)
    assert (banco / "indice.json").read_text(encoding="utf-8") == antes
    assert not (banco / "objetos").exists()


def test_imagem_acima_do_limite_vai_para_o_drive(banco, tmp_path):
    grande = tmp_path / "grande.png"
    grande.write_bytes(png(extra=2_000_000))
    with pytest.raises(ValueError, match="Drive"):
        lupa(banco, imagem_origem=grande)
    assert not (banco / "objetos").exists()
    r = lupa(banco, imagem_drive_id=DRIVE)
    assert r["estado"] == "aguardando_ok_jose" and bf.obter("OBJ-lupa", banco).imagem_drive_id == DRIVE


def test_imagem_com_extensao_ou_conteudo_falsos_e_recusada(banco, tmp_path):
    falsa = tmp_path / "falsa.png"
    falsa.write_bytes(b"\xff\xd8\xff\xe0" + b"0" * 40)
    with pytest.raises(ValueError, match="não é png"):
        lupa(banco, imagem_origem=falsa)
    gif = tmp_path / "anim.gif"
    gif.write_bytes(b"GIF89a" + b"0" * 40)
    with pytest.raises(ValueError, match="extensão"):
        lupa(banco, imagem_origem=gif)
    with pytest.raises(FileNotFoundError):
        lupa(banco, imagem_origem=tmp_path / "nao-existe.png")
    jpg = tmp_path / "foto.jpg"
    jpg.write_bytes(b"\xff\xd8\xff\xe0" + b"0" * 40)
    assert lupa(banco, imagem_origem=jpg)["imagem"] == "objetos/OBJ-lupa.jpg"


def test_origem_jose_so_por_ordem_dele(banco):
    with pytest.raises(ValueError, match="só por ordem dele"):
        lupa(banco, origem="jose")
    r = lupa(banco, origem="jose", por_jose=True, imagem_drive_id=DRIVE)
    ficha = bf.obter(r["id"], banco)
    assert r["estado"] == "permanente" and ficha.aprovado_por == "Jose" and ficha.aprovado_em is not None


def test_imagem_existente_reaproveita_a_folha_com_recorte(banco):
    r = bf.registrar(tipo="personagem", slug="ruiva-coque", titulo="Moça ruiva de jaqueta verde", acento="jaqueta verde", trava=TRAVA_PERS, folha_individual=False,
                     imagem_existente="personagens/PERS-menino-azul-folha.png", recortes={"num-01": [0.1, 0.1, 0.5, 0.9]}, raiz=banco)
    assert r["estado"] == "aguardando_ok_jose" and r["imagem"] == "personagens/PERS-menino-azul-folha.png"
    assert bf.obter("PERS-ruiva-coque", banco).recortes["num-01"] == [0.1, 0.1, 0.5, 0.9]
    with pytest.raises(FileNotFoundError):
        lupa(banco, imagem_existente="objetos/nao-existe.png")
    with pytest.raises(ValueError, match="não os dois"):
        lupa(banco, imagem_existente="personagens/PERS-menino-azul-folha.png", imagem_origem="x.png")


def test_referencias_precisam_existir_no_catalogo(banco):
    lupa(banco)
    r = bf.registrar(tipo="situacao", slug="investigando", titulo="Investigando com a lupa", acao="Segura a lupa diante do olho e examina o chão",
                     trava="Corpo inteiro de lado, lupa diante do olho, tronco inclinado para o chão.", objetos=["OBJ-lupa"], personagens=["PERS-menina-rosa"], raiz=banco)
    ficha = bf.obter(r["id"], banco)
    assert ficha.objetos == ["OBJ-lupa"] and ficha.personagens == ["PERS-menina-rosa"]
    with pytest.raises(ValueError, match="fora do catálogo"):
        bf.registrar(tipo="situacao", slug="fantasma", titulo="Situação com objeto fantasma", acao="Segura um objeto que ninguém cadastrou",
                     trava="Corpo inteiro de frente, segurando algo com as duas mãos.", objetos=["OBJ-fantasma"], raiz=banco)


def test_anexar_midia_promove_a_sugestao_e_nao_troca_imagem(banco, tmp_path):
    bf.registrar(tipo="situacao", slug="tomando-cafe", titulo="Tomando café", acao="Segura a caneca com as duas mãos junto ao rosto",
                 trava="Corpo inteiro de frente, caneca nas duas mãos junto ao rosto.", raiz=banco)
    f = bf.anexar_midia("SIT-tomando-cafe", video={"drive_id": DRIVE, "duracao_s": 5, "legenda": "loop curto", "loop": True}, raiz=banco)
    assert f.estado == "aguardando_ok_jose" and f.videos[0].loop is True
    md = (banco / "situacoes" / "SIT-tomando-cafe.md").read_text(encoding="utf-8")
    assert "Estado: `aguardando_ok_jose`" in md and DRIVE in md and "loop curto" in md
    origem = tmp_path / "cena.png"
    origem.write_bytes(png())
    f = bf.anexar_midia("SIT-tomando-cafe", imagem_origem=origem, raiz=banco)
    assert f.imagem == "situacoes/SIT-tomando-cafe.png" and (banco / f.imagem).is_file() and len(f.videos) == 1
    with pytest.raises(ValueError, match="já tem imagem"):
        bf.anexar_midia("SIT-tomando-cafe", imagem_drive_id=DRIVE, raiz=banco)
    with pytest.raises(ValueError, match="nada para anexar"):
        bf.anexar_midia("SIT-tomando-cafe", raiz=banco)
    with pytest.raises(KeyError):
        bf.anexar_midia("SIT-nao-existe", imagem_drive_id=DRIVE, raiz=banco)


def test_ficha_permanente_so_muda_por_ordem_do_jose(banco):
    with pytest.raises(ValueError, match="por ordem do José"):
        bf.anexar_midia("PERS-menina-rosa", video={"drive_id": DRIVE, "duracao_s": 3}, raiz=banco)
    f = bf.anexar_midia("PERS-menina-rosa", video={"drive_id": DRIVE, "duracao_s": 3}, por_jose=True, raiz=banco)
    assert f.estado == "permanente" and len(f.videos) == 1


def test_adicionar_recorte_vale_em_qualquer_estado_e_valida_o_retangulo(banco):
    f = bf.adicionar_recorte("PERS-menina-rosa", "pose-base", [0.1, 0.2, 0.3, 0.9], raiz=banco)
    assert f.recortes["pose-base"] == [0.1, 0.2, 0.3, 0.9] and f.estado == "permanente"
    for ruim in ([0.3, 0.2, 0.1, 0.9], [0, 0, 2, 1]):
        with pytest.raises(ValueError, match="recorte"):
            bf.adicionar_recorte("PERS-menina-rosa", "pose-base", ruim, raiz=banco)
    with pytest.raises(ValueError):
        bf.adicionar_recorte("PERS-menina-rosa", "Pose Base", [0.1, 0.2, 0.3, 0.9], raiz=banco)


def test_aprovar_so_ficha_aguardando_e_md_a_mao_so_troca_a_linha_de_estado(banco):
    lupa(banco, imagem_drive_id=DRIVE)
    antes = (banco / "objetos" / "OBJ-lupa.md").read_text(encoding="utf-8")
    f = bf.aprovar("OBJ-lupa", "Jose", banco)
    assert f.estado == "permanente" and f.aprovado_por == "Jose" and f.aprovado_em is not None
    depois = (banco / "objetos" / "OBJ-lupa.md").read_text(encoding="utf-8")
    assert "Estado: `permanente`" in depois and "Aprovada por Jose" in depois and antes != depois
    with pytest.raises(ValueError, match="aguardando OK"):
        bf.aprovar("OBJ-lupa", "Jose", banco)
    bf.registrar(tipo="situacao", slug="acenando", titulo="Acenando", acao="Levanta uma mão aberta e balança", trava="Corpo inteiro de frente com uma mão no alto.", raiz=banco)
    with pytest.raises(ValueError, match="aguardando OK"):
        bf.aprovar("SIT-acenando", "Jose", banco)
    # ficha escrita à mão (sem a marca): só a linha Estado muda; o resto do texto fica como está
    md = banco / "personagens" / "PERS-menina-rosa.md"
    bf._atualizar("PERS-menina-rosa", lambda f: {"estado": "aguardando_ok_jose", "aprovado_por": None, "aprovado_em": None}, banco, nota="voltou para revisão")
    texto = md.read_text(encoding="utf-8")
    assert texto.startswith("# PERS-menina-rosa") and "Estado: `aguardando_ok_jose`" in texto and texto.rstrip().endswith("- voltou para revisão")
    assert not texto.startswith(bf.MARCA_MD)


def test_descartar_protege_permanente_referenciada_e_imagem_compartilhada(banco):
    lupa(banco, imagem_drive_id=DRIVE)
    bf.registrar(tipo="situacao", slug="investigando", titulo="Investigando com a lupa", acao="Segura a lupa diante do olho", objetos=["OBJ-lupa"],
                 trava="Corpo inteiro de lado, lupa diante do olho, tronco inclinado.", raiz=banco)
    with pytest.raises(ValueError, match="referenciada"):
        bf.descartar("OBJ-lupa", "não serve mais", raiz=banco)
    with pytest.raises(ValueError, match="motivo"):
        bf.descartar("SIT-investigando", "  ", raiz=banco)
    r = bf.descartar("SIT-investigando", "ideia repetida", por="droid", raiz=banco)
    assert r["apagados"] == ["situacoes/SIT-investigando.md"] and not bf.existe("SIT-investigando", banco)
    dados = bf.carregar(banco)
    assert dados["descartadas"][0]["id"] == "SIT-investigando" and dados["descartadas"][0]["motivo"] == "ideia repetida"
    with pytest.raises(ValueError, match="por ordem do José"):
        bf.descartar("PERS-menina-rosa", "teste de proteção", raiz=banco)
    # imagem compartilhada com outra ficha não é apagada
    bf.registrar(tipo="personagem", slug="ruiva", titulo="Moça ruiva de jaqueta verde", acento="jaqueta verde", trava=TRAVA_PERS, folha_individual=False,
                 imagem_existente="personagens/PERS-menino-azul-folha.png", recortes={"num-01": [0.1, 0.1, 0.5, 0.9]}, raiz=banco)
    r = bf.descartar("PERS-ruiva", "trocada por outra", raiz=banco)
    assert r["apagados"] == ["personagens/PERS-ruiva.md"] and (banco / "personagens" / "PERS-menino-azul-folha.png").is_file()
    r = bf.descartar("PERS-menina-rosa", "ordem do José", por="Jose", por_jose=True, raiz=banco)
    assert "personagens/PERS-menina-rosa-folha.png" in r["apagados"] and not (banco / "personagens" / "PERS-menina-rosa-folha.png").exists()


def test_buscar_acha_por_tag_titulo_e_acao_e_respeita_o_tipo(banco):
    lupa(banco, imagem_drive_id=DRIVE)
    bf.registrar(tipo="situacao", slug="investigando", titulo="Investigando com a lupa", acao="Segura a lupa diante do olho e examina o chão",
                 trava="Corpo inteiro de lado, lupa diante do olho, tronco inclinado.", tags=["detetive"], raiz=banco)
    bf.registrar(tipo="situacao", slug="tomando-cafe", titulo="Tomando café", acao="Segura a caneca junto ao rosto", trava="Corpo inteiro de frente, caneca junto ao rosto.", raiz=banco)
    assert [f.id for f in bf.buscar("lupa", raiz=banco)][:2] == ["OBJ-lupa", "SIT-investigando"]
    assert [f.id for f in bf.buscar("lupa", tipo="situacao", raiz=banco)] == ["SIT-investigando"]
    assert [f.id for f in bf.buscar("detetive", raiz=banco)] == ["SIT-investigando"]
    assert [f.id for f in bf.buscar("investigação", raiz=banco)][0] == "OBJ-lupa"       # sem acento nem caixa; título e tag pesam mais que a ação
    assert [f.id for f in bf.buscar("café caneca", raiz=banco)] == ["SIT-tomando-cafe"]
    assert bf.buscar("assunto que nao existe", raiz=banco) == [] and bf.buscar("de da do", raiz=banco) == []
    assert len(bf.buscar("lupa", limite=1, raiz=banco)) == 1


def test_protagonista_vem_do_indice(banco):
    assert bf.protagonista("masculino", banco).id == "PERS-menino-azul" and bf.protagonista("feminino", banco).id == "PERS-menina-rosa"
    with pytest.raises(KeyError):
        bf.protagonista("neutro", banco)


def test_resumo_para_prompt_lista_ids_marca_protagonistas_e_respeita_o_limite(banco):
    lupa(banco, imagem_drive_id=DRIVE)
    bf.registrar(tipo="situacao", slug="acenando", titulo="Acenando para cumprimentar", acao="Levanta uma mão aberta e balança", trava="Corpo inteiro de frente com uma mão no alto.", raiz=banco)
    texto = bf.resumo_para_prompt(banco)
    assert "- PERS-menino-azul [protagonista masculino]: Menino de camiseta azul" in texto
    assert "- PERS-menina-rosa [protagonista feminino]" in texto
    assert "Objetos:" in texto and "- OBJ-lupa: Lupa de investigação" in texto
    assert "- SIT-acenando: Acenando para cumprimentar [sem mídia]" in texto and "Situações" in texto
    assert "- OBJ-lupa: Lupa de investigação\n" in texto  # tem mídia (Drive): sem a marca [sem mídia]
    bf.registrar(tipo="personagem", slug="ruiva-coque", titulo="Moça ruiva de jaqueta verde", acento="jaqueta verde", trava=TRAVA_PERS, folha_individual=False,
                 imagem_existente="personagens/PERS-menino-azul-folha.png", recortes={"num-01": [0.1, 0.1, 0.5, 0.9]}, raiz=banco)
    texto = bf.resumo_para_prompt(banco)
    assert texto.index("PERS-menino-azul") < texto.index("PERS-menina-rosa") < texto.index("PERS-ruiva-coque")  # protagonistas antes dos coadjuvantes
    curto = bf.resumo_para_prompt(banco, limite=120)
    assert len(curto) <= 125 and curto.endswith("- …")


def test_cli_lista_registra_e_resume(banco, tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("PQBR_BANCO_FICHAS", str(banco))
    assert bf._cli(["listar", "--tipo", "personagem"]) == 0
    saida = json.loads(capsys.readouterr().out)
    assert {x["id"] for x in saida} == {"PERS-menino-azul", "PERS-menina-rosa"}
    pedido = tmp_path / "pedido.json"
    pedido.write_text(json.dumps(dict(tipo="objeto", slug="lupa", titulo="Lupa de investigação", trava=TRAVA_OBJ, tags=["lupa"])), encoding="utf-8")
    assert bf._cli(["registrar", str(pedido)]) == 0
    assert json.loads(capsys.readouterr().out)["id"] == "OBJ-lupa"
    assert bf._cli(["registrar", str(pedido)]) == 1 and "já existe" in capsys.readouterr().err
    assert bf._cli(["buscar", "lupa"]) == 0 and "OBJ-lupa" in capsys.readouterr().out
    assert bf._cli(["obter", "PERS-fantasma"]) == 1 and "inexistente" in capsys.readouterr().err
    assert bf._cli(["resumo"]) == 0 and "Personagens:" in capsys.readouterr().out
    assert bf._cli(["aprovar", "OBJ-lupa"]) == 1 and "aguardando OK" in capsys.readouterr().err
    assert bf._cli(["descartar", "OBJ-lupa", "--motivo", "teste de limpeza"]) == 0 and not bf.existe("OBJ-lupa", banco)
