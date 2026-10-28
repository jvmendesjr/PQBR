"""PlanoMotion (REGRAS §26, t145u): texto só do bloco travado, bloco nunca na última cena, transição padrão, catálogo."""
import pytest
from pydantic import ValidationError
from pqbr.contratos.motion import PlanoMotion, PecaMotion, BlocoNumeros, FaixaBloco, transicao_padrao
from pqbr.pos.motion.catalogo import carregar_catalogo, PALETA

ITENS = ["A versão mais aceita", "Reaproveitar o mesmo pó no filtro até sair só líquido claro", "Tem quem diga",
         "Água quente no bico da chaleira pra aproveitar a borra", "Chá de bico de chaleira"]
CORTES = [9.8, 6.85, 8.58, 5.76, 7.01, 5.87, 3.02, 1.7]


def plano(**kw):
    b = kw.pop("bloco", FaixaBloco(inicio=14.9, fim=33.5))
    pecas = kw.pop("pecas", None)
    if pecas is None:
        pecas = transicao_padrao(b) + [PecaMotion(modelo="titulo-expressao", inicio=15.3, fim=20, parametros={"texto": "Chá de bico de chaleira"})]
    base = dict(episodio="PQBR-EP1003", duracao_video_s=43.48, elenco="PERS-M", bloco_numeros=BlocoNumeros(itens=ITENS), bloco=b, pecas=pecas)
    base.update(kw)
    return PlanoMotion(**base)


def test_plano_valido_e_clipes_substituidos():
    p = plano()
    assert len(p.pecas) == 5
    assert p.clipes_substituidos(CORTES) == [3, 4]      # c3 e c4 caem inteiros no bloco


def test_texto_fora_do_bloco_de_numeros_reprova():
    with pytest.raises(ValidationError, match="bloco de números travados"):
        plano(pecas=transicao_padrao(FaixaBloco(inicio=14.9, fim=33.5)) +
              [PecaMotion(modelo="titulo-expressao", inicio=15.3, fim=20, parametros={"texto": "Inventado em 1850"})])
    with pytest.raises(ValidationError, match="bloco de números travados"):
        plano(pecas=transicao_padrao(FaixaBloco(inicio=14.9, fim=33.5)) +
              [PecaMotion(modelo="linha-tempo", inicio=15.3, fim=20, parametros={"marcos": [ITENS[0], "1900"]})])


def test_bloco_nunca_e_a_ultima_cena_nem_cobre_o_gancho():
    with pytest.raises(ValidationError, match="última cena"):
        plano(bloco=FaixaBloco(inicio=20, fim=42), pecas=transicao_padrao(FaixaBloco(inicio=20, fim=42)))
    with pytest.raises(ValidationError, match="gancho"):
        plano(bloco=FaixaBloco(inicio=1, fim=12), pecas=transicao_padrao(FaixaBloco(inicio=1, fim=12)))


def test_bloco_exige_transicao_padrao_dos_dois_lados():
    b = FaixaBloco(inicio=14.9, fim=33.5)
    with pytest.raises(ValidationError, match="transição padrão"):
        plano(pecas=transicao_padrao(b)[:2] + [PecaMotion(modelo="titulo-expressao", inicio=15.3, fim=20, parametros={"texto": ITENS[4]})])
    with pytest.raises(ValidationError, match="0,2 a 0,8"):
        plano(pecas=transicao_padrao(b, dur=1.5))


def test_peca_de_tela_cheia_fora_do_bloco_reprova():
    with pytest.raises(ValidationError, match="fora do bloco"):
        plano(pecas=transicao_padrao(FaixaBloco(inicio=14.9, fim=33.5)) +
              [PecaMotion(modelo="titulo-expressao", inicio=5, fim=9, parametros={"texto": ITENS[4]})])
    with pytest.raises(ValidationError, match="sem bloco"):
        plano(bloco=None, pecas=[PecaMotion(modelo="titulo-expressao", inicio=5, fim=9, parametros={"texto": ITENS[4]})])


def test_modelo_fora_do_catalogo_parametro_desconhecido_e_cor_fora_da_paleta():
    b = FaixaBloco(inicio=14.9, fim=33.5)
    with pytest.raises(ValidationError, match="fora do catálogo"):
        plano(pecas=transicao_padrao(b) + [PecaMotion(modelo="particulas-brilho", inicio=15, fim=20)])
    with pytest.raises(ValidationError, match="desconhecido"):
        plano(pecas=transicao_padrao(b) + [PecaMotion(modelo="titulo-expressao", inicio=15, fim=20, parametros={"texto": ITENS[4], "gradiente": True})])
    with pytest.raises(ValidationError, match="cor fora"):
        plano(pecas=transicao_padrao(b) + [PecaMotion(modelo="barra-progresso", inicio=0, fim=43.48, parametros={"cor": "#ff00ff"})])
    assert "#2b6cb0" in PALETA and "#d96b43" in PALETA


def test_imagem_exige_recurso_declarado():
    b = FaixaBloco(inicio=14.9, fim=33.5)
    with pytest.raises(ValidationError, match="sem recurso"):
        plano(pecas=transicao_padrao(b) + [PecaMotion(modelo="recorte-aponta", inicio=15, fim=20, parametros={"imagem": "pm", "texto": ITENS[4]})])
    p = plano(recursos={"pm": "banco-fichas/personagens/PERS-M.png"},
              pecas=transicao_padrao(b) + [PecaMotion(modelo="recorte-aponta", inicio=15, fim=20, parametros={"imagem": "pm", "texto": ITENS[4]})])
    assert p.recursos["pm"].endswith(".png")


def test_bloco_de_numeros_nao_pede_acao():
    with pytest.raises(ValidationError, match="pede ação"):
        BlocoNumeros(itens=["Comenta aí qual é a sua versão"])
    with pytest.raises(ValidationError, match="pede ação"):
        BlocoNumeros(itens=["Clique para seguir"])
    with pytest.raises(ValidationError, match="repetido"):
        BlocoNumeros(itens=["1850", "1850"])


def test_barra_de_progresso_pode_cobrir_o_video_inteiro_sem_bloco():
    p = plano(bloco=None, pecas=[PecaMotion(modelo="barra-progresso", inicio=0, fim=43.48)])
    assert p.clipes_substituidos(CORTES) == []


def test_catalogo_tem_os_modelos_iniciais_com_camada():
    cat = carregar_catalogo()
    assert {"transicao-cortina", "titulo-expressao", "linha-tempo", "origem-pino", "versus", "recorte-aponta", "barra-progresso", "imagem-cena"} <= set(cat)
    assert cat["barra-progresso"].camada == "sobre" and cat["transicao-cortina"].camada == "ambas"
    for m in cat.values():
        assert m.arquivo_js.is_file(), m.slug
