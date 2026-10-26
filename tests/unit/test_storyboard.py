import pytest
from pydantic import ValidationError
from pqbr.contratos.storyboard import FichaCena, Storyboard

ANIM = "Locked camera, slow push-in, lips closed, only blinking and breathing."
def ficha(n=1, **kw):
    base = dict(numero=n, rotulo=f"PQBR-EP1003_c{n:02d}", fala="Café fraco vira chá de bico.", norte="mostrar o café ralo na xícara",
                inicio="Xícara branca com café claro sobre a mesa, plano médio.", fim="Personagem olha a xícara, cabeça e óculos inteiros no quadro.",
                movimento="ergue a xícara; push-in lento", enquadramento="plano_medio",
                prompt_imagem="Flat 2D cartoon, bold black outlines, medium shot, character holds a cup, full head visible.",
                prompt_animacao=ANIM, refs=["ASSET_personagem_pqbr-v1"], papel_personagem="protagonista")
    base.update(kw); return base

def test_ficha_ok(): assert FichaCena(**ficha()).numero == 1
@pytest.mark.parametrize("kw", [dict(prompt_animacao="slow push-in, no movement"), dict(prompt_imagem="Flat 2D cartoon, from the chest up portrait of him"),
    dict(prompt_animacao=ANIM + ' He says "olá pessoal"'), dict(refs=["foto.png"]), dict(rotulo="PQBR-EP1003_c02"),
    dict(epoca="passado"), dict(epoca="passado", papel_personagem="caracterizado_epoca")])
def test_ficha_reprova(kw):
    with pytest.raises(ValidationError): FichaCena(**ficha(**kw))
def test_passado_observador(): assert FichaCena(**ficha(epoca="passado", papel_personagem="observador_escondido"))
def test_storyboard_ordem_e_revisao():
    sb = Storyboard(codigo="PQBR-EP1003", norte_geral="explicar a origem da expressão com humor leve",
                    bloco_estilo="Flat 2D cartoon, bold outlines, flat warm colors", ficha_personagem="homem de 30 anos, óculos redondos vermelhos",
                    cenas=[FichaCena(**ficha(i)) for i in (1, 2, 3)])
    assert not sb.pode_gerar_video()
    with pytest.raises(ValidationError):
        Storyboard(codigo="PQBR-EP1003", norte_geral="x" * 25, bloco_estilo="y" * 25, ficha_personagem="z" * 25,
                   cenas=[FichaCena(**ficha(i)) for i in (1, 3, 2)])
