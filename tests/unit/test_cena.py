import pytest
from pydantic import ValidationError
from pqbr.contratos.cena import CenaIndividual, rotulo_cena, label_curto_flow, validar_stem_rotulo

ANIM = "Locked camera, slow push-in, lips closed, only blinking and breathing."
def ficha(n=1, **kw):
    base = dict(numero=n, rotulo=f"PQBR-EP1003-S{n:02d}", fala="Café fraco vira chá de bico.", norte="mostrar o café ralo na xícara",
                inicio="Xícara branca com café claro sobre a mesa, plano médio.", fim="Personagem olha a xícara, cabeça e óculos inteiros no quadro.",
                movimento="ergue a xícara; push-in lento", enquadramento="plano_medio",
                prompt_imagem="Flat 2D cartoon, bold black outlines, medium shot, character holds a cup, full head visible.",
                prompt_animacao=ANIM, refs=["ASSET_personagem_pqbr-v1"], papel_personagem="observa", figurino="atual_variavel", expressao="sobrancelhas lá em cima, careta de nojo do café ralo", cenario_encaixe="sentado à mesa da cozinha, no centro")
    base.update(kw); return base

def test_ficha_ok(): assert CenaIndividual(**ficha()).numero == 1
@pytest.mark.parametrize("kw", [dict(prompt_animacao="slow push-in, no movement"), dict(prompt_imagem="Flat 2D cartoon, from the chest up portrait of him"),
    dict(prompt_animacao=ANIM + ' He says "olá pessoal"'), dict(refs=["foto.png"]), dict(rotulo="PQBR-EP1003_c02"),
    dict(rotulo="PQBR-EP1003-S02"),  # numero=1 vs S02
    dict(papel_personagem="participa"), dict(papel_personagem="participa", figurino="epoca_local"),
    dict(expressao="boca mexendo, mouthing words"), dict(expressao="diz que o café está fraco"), dict(figurino="epoca_local", caracterizacao="gibão de couro")])
def test_ficha_reprova(kw):
    with pytest.raises(ValidationError): CenaIndividual(**ficha(**kw))
def test_passado_observador(): assert CenaIndividual(**ficha(epoca="passado", cenario_encaixe="escondido atrás de um barril, espiando a feira"))
def test_participa_caracterizado():
    assert CenaIndividual(**ficha(epoca="passado", papel_personagem="participa", figurino="epoca_local", caracterizacao="chapéu de palha e camisa de algodão cru, Brasil 1900"))
def test_alternancia():
    from pqbr.contratos.cena import elenco_alternado
    assert elenco_alternado("PQBR-EP1004") == "masculino" and elenco_alternado("PQBR-EP1003") == "feminino"
def test_cenas_sao_individuais_sem_board():
    import pqbr.contratos.cena as cena_mod
    assert not hasattr(cena_mod, "Storyboard")
    assert CenaIndividual(**ficha(1)).numero == 1
    assert CenaIndividual(**ficha(2)).rotulo == "PQBR-EP1003-S02"


def test_coadjuvante_com_justificativa():
    assert CenaIndividual(**ficha(coadjuvante="masculino", coadjuvante_justificativa="roteiro pede a reação de outra pessoa ao café"))
    with pytest.raises(ValidationError): CenaIndividual(**ficha(coadjuvante="masculino"))

def test_refs_do_catalogo_sao_ate_seis_e_o_legado_continua_valido():
    assert CenaIndividual(**ficha(refs=["PERS-menina-rosa", "AMB-metro", "OBJ-caneca", "ANIM-gato", "FIG-robo", "SIT-pensando"]))
    assert CenaIndividual(**ficha(refs=["ASSET_personagem_pqbr-v1", "AMB-metro"]))
    with pytest.raises(ValidationError): CenaIndividual(**ficha(refs=["PERS-menina-rosa"] * 7))
    for ruim in ("ELENCO-catalogo", "pers-menina-rosa", "PERS-", "PERS_menina-rosa", "XYZ-abc", "PERS-menina rosa"):
        with pytest.raises(ValidationError): CenaIndividual(**ficha(refs=[ruim]))


def test_versao_cena_2_0_0():
    assert CenaIndividual(**ficha()).versao == "2.0.0"
    with pytest.raises(ValidationError): CenaIndividual(**ficha(versao="1.0.0"))


def test_rotulo_helpers_e_stem():
    assert rotulo_cena("PQBR-EP1003", 4) == "PQBR-EP1003-S04"
    assert label_curto_flow("PQBR-EP1003-S04") == "S04"
    validar_stem_rotulo("PQBR-EP1003-S04", "/tmp/PQBR-EP1003-S04.png")
    with pytest.raises(ValueError):
        validar_stem_rotulo("PQBR-EP1003-S04", "/tmp/PQBR-EP1003_c04.png")
    with pytest.raises(ValueError):
        rotulo_cena("EP1003", 1)


def test_coadjuvante_pode_ser_qualquer_personagem_do_catalogo():
    just = "o roteiro pede a reação de outra pessoa ao café"
    assert CenaIndividual(**ficha(coadjuvante="PERS-punk-azul", coadjuvante_justificativa=just)).coadjuvante == "PERS-punk-azul"
    for ruim in ("AMB-metro", "PERS-", "outro", "Masculino"):
        with pytest.raises(ValidationError): CenaIndividual(**ficha(coadjuvante=ruim, coadjuvante_justificativa=just))


def test_protagonista_do_jose_por_genero():
    from pqbr.contratos.cena import protagonista_ref
    assert protagonista_ref("masculino") == "PERS-menino-azul" and protagonista_ref("feminino") == "PERS-menina-rosa"
    just = "dupla no balcão, roteiro cena 3"
    assert CenaIndividual(**ficha(3, coadjuvante="PERS-menino-azul", coadjuvante_justificativa=just)).coadjuvante == "PERS-menino-azul"


def test_protagonista_unico_vira_regra_de_prompt():
    from pqbr.contratos.cena import elenco_alternado
    assert elenco_alternado("PQBR-EP1003") == "feminino" and elenco_alternado("PQBR-EP1004") == "masculino"
    assert CenaIndividual(**ficha(1)).numero == 1
