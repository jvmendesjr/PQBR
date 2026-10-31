"""t150u: contrato da ficha do catálogo visual aberto (personagem, figura, animal, objeto, ambiente, situação)."""
from datetime import date

import pytest
from pydantic import ValidationError

from pqbr.contratos.catalogo_visual import (ID_ELENCO, PASTA, PREFIXO, PROIBIDO_PADRAO, PROTAGONISTAS, TAMANHO_MAX_IMAGEM, FichaCatalogo,
                                            VideoCatalogo, afirmativo)

TRAVA_PERS = ("Stickman 2D flat colorido do canal Porquê BR: menina de cabelo preto curto e blusa lilás chapada. Cabeça redonda branca grande "
              "com contorno preto, dois olhos pretos sempre visíveis, boca de reação, fundo claro em tom creme, sem texto e sem marca na imagem.")
BASE = dict(id="OBJ-teste", tipo="objeto", titulo="Objeto de teste", estado="sugestao", origem="agente", criado_em=date(2026, 10, 28),
            trava="Cadeira de madeira simples em cartoon 2D flat colorido, contorno preto e cores chapadas suaves.")


def ficha(**kw) -> FichaCatalogo:
    return FichaCatalogo.model_validate({**BASE, **kw})


def recusa(trecho: str, **kw) -> None:
    with pytest.raises(ValidationError, match=trecho):
        ficha(**kw)


def test_um_item_valido_de_cada_tipo():
    assert ficha().estado == "sugestao"
    assert ficha(id="PERS-teste", tipo="personagem", trava=TRAVA_PERS, acento="blusa lilás").tipo == "personagem"
    assert ficha(id="SIT-teste", tipo="situacao", acao="Acena com a mão aberta para cumprimentar").acao
    assert ficha(id="FIG-teste", tipo="figura").tipo == "figura"
    assert ficha(id="ANIM-teste", tipo="animal").tipo == "animal"
    assert ficha(id="AMB-teste", tipo="ambiente", com_elenco=False).com_elenco is False


def test_id_segue_o_prefixo_do_tipo_e_a_unica_excecao_e_a_grade_do_elenco():
    recusa("não é de objeto", id="PERS-teste")
    recusa("String should match", id="obj-teste")
    recusa("String should match", id="OBJ-Teste")
    assert set(PREFIXO) == set(PASTA) == {"personagem", "figura", "animal", "objeto", "ambiente", "situacao"}
    grade = ficha(id=ID_ELENCO, tipo="personagem", papel="colecao", imagem="personagens/ELENCO-catalogo.png", estado="permanente", origem="jose")
    assert grade.papel == "colecao"
    recusa("grade", id=ID_ELENCO, tipo="personagem", papel="item", acento="x", trava=TRAVA_PERS)
    recusa("grade", id=ID_ELENCO, tipo="objeto", papel="colecao")


def test_situacao_exige_acao_e_so_ela_tem_acao():
    recusa("situação exige `acao`", id="SIT-teste", tipo="situacao")
    recusa("só de situação", acao="Segura uma caneca fumegante")


def test_so_personagem_tem_acento_elenco_e_folha():
    recusa("só de personagem", acento="azul")
    recusa("só de personagem", elenco_num=3)
    recusa("só de personagem", folha_individual=True)
    recusa("com_elenco é só de ambiente", com_elenco=True)


def test_personagem_item_exige_acento_e_stickman():
    recusa("exige `acento`", id="PERS-teste", tipo="personagem", trava=TRAVA_PERS)
    recusa("descreve o stickman", id="PERS-teste", tipo="personagem", acento="lilás", trava="Menina de cabelo preto curto e blusa lilás chapada, fundo creme.")


def test_estado_e_midia():
    recusa("sem mídia só existe como `sugestao`", estado="aguardando_ok_jose")
    assert ficha(estado="aguardando_ok_jose", imagem_drive_id="1AbCdEfGhIjKlMnOp").estado == "aguardando_ok_jose"
    assert ficha(estado="aguardando_ok_jose", videos=[{"drive_id": "1AbCdEfGhIjKlMnOp", "duracao_s": 4.5}]).videos[0].duracao_s == 4.5
    recusa("aguardando OK não tem aprovação", estado="aguardando_ok_jose", imagem_drive_id="1AbCdEfGhIjKlMnOp", aprovado_por="Jose")
    recusa("precisa de aprovado_por e aprovado_em", estado="permanente", imagem_drive_id="1AbCdEfGhIjKlMnOp")
    assert ficha(estado="permanente", imagem_drive_id="1AbCdEfGhIjKlMnOp", aprovado_por="Jose", aprovado_em=date(2026, 10, 28)).estado == "permanente"
    assert ficha(estado="permanente", origem="jose", imagem_drive_id="1AbCdEfGhIjKlMnOp").origem == "jose"


def test_imagem_fica_na_pasta_do_tipo_e_so_com_extensao_conhecida():
    assert ficha(imagem="objetos/OBJ-teste.png", estado="aguardando_ok_jose").imagem == "objetos/OBJ-teste.png"
    recusa("fica em objetos/", imagem="ambientes/OBJ-teste.png", estado="aguardando_ok_jose")
    recusa("sem '..'", imagem="objetos/../x.png", estado="aguardando_ok_jose")
    recusa("sem '..'", imagem="/tmp/x.png", estado="aguardando_ok_jose")
    recusa("extensão", imagem="objetos/OBJ-teste.gif", estado="aguardando_ok_jose")
    assert TAMANHO_MAX_IMAGEM == 2_000_000


def test_recortes_normalizados_e_no_maximo_24():
    ok = {"item": [0.1, 0.1, 0.4, 0.5]}
    assert ficha(imagem="objetos/OBJ-teste.png", estado="aguardando_ok_jose", recortes=ok).recortes == ok
    recusa("recortes exigem `imagem`", recortes=ok)
    for ruim in ([0.5, 0.1, 0.4, 0.5], [0.1, 0.5, 0.4, 0.5], [0.1, 0.1, 1.2, 0.5], [0.1, 0.1, 0.4]):
        recusa("recorte", imagem="objetos/OBJ-teste.png", estado="aguardando_ok_jose", recortes={"item": ruim})
    recusa("recorte 'Item'", imagem="objetos/OBJ-teste.png", estado="aguardando_ok_jose", recortes={"Item": [0.1, 0.1, 0.4, 0.5]})
    muitos = {f"r-{i}": [0.1, 0.1, 0.4, 0.5] for i in range(25)}
    recusa("at most 24", imagem="objetos/OBJ-teste.png", estado="aguardando_ok_jose", recortes=muitos)
    assert len(ficha(imagem="objetos/OBJ-teste.png", estado="aguardando_ok_jose", recortes={k: v for k, v in list(muitos.items())[:24]}).recortes) == 24


def test_referencias_sao_ids_do_tipo_certo_e_nao_apontam_para_si():
    assert ficha(id="AMB-teste", tipo="ambiente", personagens=["PERS-a", "PERS-b"], com_elenco=True).personagens == ["PERS-a", "PERS-b"]
    assert ficha(id="SIT-teste", tipo="situacao", acao="Digita no laptop sentado", ambiente="AMB-escritorio", objetos=["OBJ-laptop"]).objetos == ["OBJ-laptop"]
    recusa("ids PERS-", id="AMB-teste", tipo="ambiente", personagens=["OBJ-a"])
    recusa("id AMB-", id="SIT-teste", tipo="situacao", acao="Digita no laptop sentado", ambiente="OBJ-x")
    recusa("ids OBJ-", id="SIT-teste", tipo="situacao", acao="Digita no laptop sentado", objetos=["PERS-x"])
    recusa("não referencia a si mesma", objetos=["OBJ-teste"])
    recusa("at most 4", id="AMB-teste", tipo="ambiente", personagens=[f"PERS-{c}" for c in "abcde"])


def test_tags_em_minusculas_sem_repetir():
    assert ficha(tags=["cafe", "pausa-curta"]).tags == ["cafe", "pausa-curta"]
    recusa("tags:", tags=["Café"])
    recusa("tag repetida", tags=["cafe", "cafe"])
    recusa("tags:", tags=["x" * 31])


def test_trava_recusa_3d_realismo_texto_pessoa_real_e_nome():
    recusa("3D ou realismo", trava="Cadeira de madeira em 3D com luz realista e sombra volumétrica.")
    recusa("3D ou realismo", trava="Cadeira de madeira fotorrealista com textura detalhada de madeira.")
    recusa("texto na imagem", trava="Cadeira de madeira com o texto 'Porquê' escrito no encosto em cartoon 2D flat.")
    recusa("pessoa real", trava="Cadeira de madeira usada por uma celebridade conhecida em cartoon 2D flat.")
    recusa("sem nome falado ou escrito", trava="Cadeira de madeira simples que se chama Zé, em cartoon 2D flat colorido.")
    recusa("sem nome falado ou escrito", titulo="Cadeira, de nome Zé")


def test_negacao_nao_conta_como_pedido():
    # "sem volume 3D" e "proibido: texto escrito" são o oposto do pedido e passam
    assert ficha(trava="Cadeira de madeira simples em cartoon 2D flat colorido; sem volume 3D, sem fotorrealismo, sem texto escrito.").trava
    assert ficha(trava="Cadeira de madeira simples em cartoon 2D flat colorido. Proibido: 3D, texto escrito, pessoa realista.").trava
    assert "3D" not in afirmativo("flat; sem volume 3D, nada de realismo. Proibido: 3D e fotorrealismo.")
    assert "flat" in afirmativo("flat; sem volume 3D")


def test_campos_extras_e_ficha_imutavel():
    with pytest.raises(ValidationError):
        ficha(inventado="x")
    f = ficha()
    with pytest.raises(ValidationError):
        f.titulo = "outro"


def test_video_so_por_drive_com_duracao_limitada():
    assert VideoCatalogo(drive_id="1AbCdEfGhIjKlMnOp", duracao_s=8).loop is False
    for ruim in ({"drive_id": "curto", "duracao_s": 5}, {"drive_id": "1AbCdEfGhIjKlMnOp", "duracao_s": 0}, {"drive_id": "1AbCdEfGhIjKlMnOp", "duracao_s": 31},
                 {"drive_id": "a/b/c/d/e/f/g/h", "duracao_s": 5}):
        with pytest.raises(ValidationError):
            VideoCatalogo(**ruim)
    recusa("at most 6", estado="aguardando_ok_jose", videos=[{"drive_id": "1AbCdEfGhIjKlMnOp", "duracao_s": 3}] * 7)


def test_protagonistas_e_proibido_padrao():
    assert PROTAGONISTAS == {"masculino": "PERS-menino-azul", "feminino": "PERS-menina-rosa"}
    for texto in ("texto escrito", "3D", "ciclope", "pessoa realista", "nome de personagem"):
        assert texto in PROIBIDO_PADRAO
