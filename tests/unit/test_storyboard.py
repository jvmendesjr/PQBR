import pytest
from pydantic import ValidationError
from pqbr.contratos.storyboard import FichaCena, Storyboard

ANIM = "Locked camera, slow push-in, lips closed, only blinking and breathing."
def ficha(n=1, **kw):
    base = dict(numero=n, rotulo=f"PQBR-EP1003_c{n:02d}", fala="Café fraco vira chá de bico.", norte="mostrar o café ralo na xícara",
                inicio="Xícara branca com café claro sobre a mesa, plano médio.", fim="Personagem olha a xícara, cabeça e óculos inteiros no quadro.",
                movimento="ergue a xícara; push-in lento", enquadramento="plano_medio",
                prompt_imagem="Flat 2D cartoon, bold black outlines, medium shot, character holds a cup, full head visible.",
                prompt_animacao=ANIM, refs=["ASSET_personagem_pqbr-v1"], papel_personagem="observa", figurino="atual_variavel", expressao="sobrancelhas lá em cima, careta de nojo do café ralo", cenario_encaixe="sentado à mesa da cozinha, no centro")
    base.update(kw); return base

def test_ficha_ok(): assert FichaCena(**ficha()).numero == 1
@pytest.mark.parametrize("kw", [dict(prompt_animacao="slow push-in, no movement"), dict(prompt_imagem="Flat 2D cartoon, from the chest up portrait of him"),
    dict(prompt_animacao=ANIM + ' He says "olá pessoal"'), dict(refs=["foto.png"]), dict(rotulo="PQBR-EP1003_c02"),
    dict(papel_personagem="participa"), dict(papel_personagem="participa", figurino="epoca_local"),
    dict(expressao="boca mexendo, mouthing words"), dict(expressao="diz que o café está fraco"), dict(figurino="epoca_local", caracterizacao="gibão de couro")])
def test_ficha_reprova(kw):
    with pytest.raises(ValidationError): FichaCena(**ficha(**kw))
def test_passado_observador(): assert FichaCena(**ficha(epoca="passado", cenario_encaixe="escondido atrás de um barril, espiando a feira"))
def test_participa_caracterizado():
    assert FichaCena(**ficha(epoca="passado", papel_personagem="participa", figurino="epoca_local", caracterizacao="chapéu de palha e camisa de algodão cru, Brasil 1900"))
def test_alternancia():
    from pqbr.contratos.storyboard import elenco_alternado
    assert elenco_alternado("PQBR-EP1004") == "masculino" and elenco_alternado("PQBR-EP1003") == "feminino"
def test_storyboard_ordem_e_revisao():
    sb = Storyboard(codigo="PQBR-EP1003", norte_geral="explicar a origem da expressão com humor leve",
                    bloco_estilo="Flat 2D cartoon, bold outlines, flat warm colors", ficha_personagem="homem de 30 anos, óculos redondos vermelhos",
                    cenas=[FichaCena(**ficha(i)) for i in (1, 2, 3)], elenco="feminino")
    with pytest.raises(ValidationError): Storyboard(**{**sb.model_dump(exclude={"cenas"}), "cenas": sb.cenas, "elenco": "masculino"})
    assert not sb.pode_gerar_video()
    with pytest.raises(ValidationError):
        Storyboard(codigo="PQBR-EP1003", norte_geral="x" * 25, bloco_estilo="y" * 25, ficha_personagem="z" * 25,
                   cenas=[FichaCena(**ficha(i)) for i in (1, 3, 2)], elenco="feminino")


def test_coadjuvante_com_justificativa():
    assert FichaCena(**ficha(coadjuvante="masculino", coadjuvante_justificativa="roteiro pede a reação de outra pessoa ao café"))
    with pytest.raises(ValidationError): FichaCena(**ficha(coadjuvante="masculino"))

def test_refs_do_catalogo_sao_ate_seis_e_o_legado_continua_valido():
    assert FichaCena(**ficha(refs=["PERS-menina-rosa", "AMB-metro", "OBJ-caneca", "ANIM-gato", "FIG-robo", "SIT-pensando"]))
    assert FichaCena(**ficha(refs=["ASSET_personagem_pqbr-v1", "AMB-metro"]))
    with pytest.raises(ValidationError): FichaCena(**ficha(refs=["PERS-menina-rosa"] * 7))
    for ruim in ("ELENCO-catalogo", "pers-menina-rosa", "PERS-", "PERS_menina-rosa", "XYZ-abc", "PERS-menina rosa"):
        with pytest.raises(ValidationError): FichaCena(**ficha(refs=[ruim]))


def test_versao_1_3_0_e_as_antigas_seguem_aceitas():
    from pqbr.contratos.storyboard import VERSAO
    assert VERSAO == "1.3.0" and FichaCena(**ficha()).versao == "1.3.0"
    for v in ("1.0.0", "1.1.0", "1.2.0", "1.3.0"):
        assert FichaCena(**ficha(versao=v)).versao == v
    with pytest.raises(ValidationError): FichaCena(**ficha(versao="1.4.0"))


def test_coadjuvante_pode_ser_qualquer_personagem_do_catalogo():
    just = "o roteiro pede a reação de outra pessoa ao café"
    assert FichaCena(**ficha(coadjuvante="PERS-punk-azul", coadjuvante_justificativa=just)).coadjuvante == "PERS-punk-azul"
    for ruim in ("AMB-metro", "PERS-", "outro", "Masculino"):
        with pytest.raises(ValidationError): FichaCena(**ficha(coadjuvante=ruim, coadjuvante_justificativa=just))


def test_protagonista_do_jose_por_genero_e_nao_vira_coadjuvante_pelo_id():
    from pqbr.contratos.storyboard import protagonista_ref
    assert protagonista_ref("masculino") == "PERS-menino-azul" and protagonista_ref("feminino") == "PERS-menina-rosa"
    just = "dupla no balcão, roteiro cena 3"
    cenas = [FichaCena(**ficha(i)) for i in (1, 2)] + [FichaCena(**ficha(3, coadjuvante="PERS-menina-rosa", coadjuvante_justificativa=just))]
    with pytest.raises(ValidationError, match="coadjuvante"):
        Storyboard(codigo="PQBR-EP1003", norte_geral="x" * 25, bloco_estilo="y" * 25, ficha_personagem="z" * 25, cenas=cenas, elenco="feminino")
    cenas[2] = FichaCena(**ficha(3, coadjuvante="PERS-menino-azul", coadjuvante_justificativa=just))
    assert Storyboard(codigo="PQBR-EP1003", norte_geral="x" * 25, bloco_estilo="y" * 25, ficha_personagem="z" * 25, cenas=cenas, elenco="feminino")


def test_protagonista_unico():
    cenas = [FichaCena(**ficha(i)) for i in (1, 2)] + [FichaCena(**ficha(3, coadjuvante="feminino", coadjuvante_justificativa="dupla no balcão, roteiro cena 3"))]
    with pytest.raises(ValidationError):
        Storyboard(codigo="PQBR-EP1003", norte_geral="x" * 25, bloco_estilo="y" * 25, ficha_personagem="z" * 25, cenas=cenas, elenco="feminino")
    cenas[2] = FichaCena(**ficha(3, coadjuvante="masculino", coadjuvante_justificativa="dupla no balcão, roteiro cena 3"))
    assert Storyboard(codigo="PQBR-EP1003", norte_geral="x" * 25, bloco_estilo="y" * 25, ficha_personagem="z" * 25, cenas=cenas, elenco="feminino")
