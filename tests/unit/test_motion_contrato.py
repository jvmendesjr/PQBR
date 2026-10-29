"""PlanoMotion (REGRAS §26, t145u, t150u): texto só do bloco travado, bloco nunca na última cena, transição padrão, catálogo,
elenco por gênero e personagem presente no layout (ficha PERS-* e pose)."""
import json
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
    base = dict(episodio="PQBR-EP1003", duracao_video_s=43.48, elenco="masculino", bloco_numeros=BlocoNumeros(itens=ITENS), bloco=b, pecas=pecas)
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
    assert {"#4b83ba", "#ee7e91", "#0f766e"} <= PALETA and not {"#2b6cb0", "#d96b43"} & PALETA   # paleta do padrão flat (t150u); a de t144u saiu


def test_imagem_exige_recurso_declarado():
    b = FaixaBloco(inicio=14.9, fim=33.5)
    with pytest.raises(ValidationError, match="sem recurso"):
        plano(pecas=transicao_padrao(b) + [PecaMotion(modelo="recorte-aponta", inicio=15, fim=20, parametros={"imagem": "pm", "texto": ITENS[4]})])
    p = plano(recursos={"pm": "banco-fichas/personagens/PERS-menina-rosa-folha.png"},
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
    assert {"transicao-cortina", "titulo-expressao", "linha-tempo", "origem-pino", "versus", "recorte-aponta", "barra-progresso", "imagem-cena",
            "personagem-moldura"} <= set(cat)
    assert cat["barra-progresso"].camada == "sobre" and cat["transicao-cortina"].camada == "ambas"
    for m in cat.values():
        assert m.arquivo_js.is_file(), m.slug


def test_fonte_padrao_do_canal_e_so_fonte_aprovada(tmp_path, monkeypatch):
    assert plano().fonte == "fredoka" and plano().versao == "1.2.0"
    assert plano(fonte="baloo-2").fonte == "baloo-2"
    with pytest.raises(ValidationError, match="fora do banco de fontes"):
        plano(fonte="nao-existe")
    from pqbr.pos.motion import fontes
    raiz = tmp_path / "banco"
    base = fontes.RAIZ_FONTES
    fontes.registrar(base / "fredoka" / "fredoka.ttf", id="candidata", origem_url="https://exemplo.org/f", licenca="OFL-1.1",
                     arquivo_licenca=base / "fredoka" / "LICENSE.txt", raiz=raiz)
    monkeypatch.setenv("PQBR_FONTES_DIR", str(raiz))
    with pytest.raises(ValidationError, match="ainda não foi aprovada"):
        plano(fonte="candidata")


def test_elenco_e_o_genero_do_protagonista_e_planos_antigos_ainda_carregam():
    assert plano(elenco="feminino").elenco == "feminino"
    assert plano(elenco="PERS-F").elenco == "feminino" and plano(elenco="PERS-M").elenco == "masculino"   # planos de t145u–t149u
    assert plano(versao="1.0.0").versao == "1.0.0" and plano(versao="1.1.0").versao == "1.1.0"
    for ruim in ("PERS-menina-rosa", "PERS-X", "outro", ""):
        with pytest.raises(ValidationError, match="elenco"):
            plano(elenco=ruim)


def moldura(**parametros):
    return PecaMotion(modelo="personagem-moldura", inicio=15.3, fim=20, parametros={"personagem": "PERS-menina-rosa", **parametros})


def test_personagem_presente_cita_ficha_do_catalogo_e_pose_da_ficha():
    b = FaixaBloco(inicio=14.9, fim=33.5)
    p = plano(pecas=transicao_padrao(b) + [moldura(pose="exp-feliz", canto="sup-dir", tamanho=300, espelhar="sim")])
    assert p.personagens_usados() == ["PERS-menina-rosa"]
    sem_pose = plano(pecas=transicao_padrao(b) + [moldura(), PecaMotion(modelo="personagem-moldura", inicio=21, fim=25, parametros={"personagem": "PERS-menino-azul"})])
    assert sem_pose.personagens_usados() == ["PERS-menina-rosa", "PERS-menino-azul"]     # protagonista (nº 1) e a da folha própria; ordem de aparição
    assert plano().personagens_usados() == []


def test_personagem_ruim_reprova_com_motivo():
    b = FaixaBloco(inicio=14.9, fim=33.5)
    casos = [
        ({"personagem": "PERS-nao-existe"}, "fora do catálogo"),
        ({"personagem": "ELENCO-catalogo"}, "não é um personagem individual"),
        ({"personagem": "OBJ-skate"}, "não é um personagem individual"),
        ({"personagem": "PERS-menina-rosa", "pose": "exp-inventada"}, "não tem a pose"),
        ({"personagem": "PERS-menina-rosa", "canto": "centro"}, "opção inválida"),
        ({"personagem": "PERS-menina-rosa", "tamanho": 90}, "fora de 220 a 460"),
        ({"personagem": "PERS-menina-rosa", "tamanho": 900}, "fora de 220 a 460"),
        ({"personagem": 7}, "esperava o id"),
    ]
    for parametros, trecho in casos:
        with pytest.raises(ValidationError, match=trecho):
            plano(pecas=transicao_padrao(b) + [PecaMotion(modelo="personagem-moldura", inicio=15.3, fim=20, parametros=parametros)])
    with pytest.raises(ValidationError, match="falta parâmetro personagem"):
        plano(pecas=transicao_padrao(b) + [PecaMotion(modelo="personagem-moldura", inicio=15.3, fim=20, parametros={"pose": "exp-feliz"})])


def test_personagem_vive_so_dentro_do_bloco_de_tela_cheia():
    b = FaixaBloco(inicio=14.9, fim=33.5)
    with pytest.raises(ValidationError, match="fora do bloco"):
        plano(pecas=transicao_padrao(b) + [PecaMotion(modelo="personagem-moldura", inicio=5, fim=9, parametros={"personagem": "PERS-menina-rosa"})])
    with pytest.raises(ValidationError, match="sem bloco"):
        plano(bloco=None, pecas=[PecaMotion(modelo="personagem-moldura", inicio=5, fim=9, parametros={"personagem": "PERS-menina-rosa"})])


def test_personagem_precisa_de_imagem_local_e_recorte(tmp_path, monkeypatch):
    # catálogo aberto: ficha nova pode vir só com imagem no Drive ou sem recorte; o motion não renderiza o que não tem no repositório
    raiz = tmp_path / "banco-fichas"
    (raiz / "personagens").mkdir(parents=True)
    (raiz / "personagens" / "PERS-completa.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 40)
    trava = "Stickman do canal em cartoon 2D flat colorido, camiseta verde chapada, cabeça redonda branca e dois olhos pretos."
    comum = dict(tipo="personagem", titulo="Personagem de teste", trava=trava, acento="camiseta verde", criado_em="2026-10-28", origem="agente")
    fichas = [dict(comum, id="PERS-completa", estado="aguardando_ok_jose", imagem="personagens/PERS-completa.png", recortes={"giro-frente": [0.1, 0.1, 0.3, 0.5]}),
              dict(comum, id="PERS-sem-recorte", estado="aguardando_ok_jose", imagem="personagens/PERS-completa.png"),
              dict(comum, id="PERS-so-drive", estado="aguardando_ok_jose", imagem_drive_id="1abcdefghijklmnop"),
              dict(comum, id="PERS-arquivo-sumiu", estado="aguardando_ok_jose", imagem="personagens/PERS-sumiu.png", recortes={"giro-frente": [0.1, 0.1, 0.3, 0.5]})]
    (raiz / "indice.json").write_text(json.dumps({"versao": "3.0.0", "fichas": fichas}, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setenv("PQBR_BANCO_FICHAS", str(raiz))
    b = FaixaBloco(inicio=14.9, fim=33.5)
    usar = lambda pid: plano(pecas=transicao_padrao(b) + [PecaMotion(modelo="personagem-moldura", inicio=15.3, fim=20, parametros={"personagem": pid})])
    assert usar("PERS-completa").personagens_usados() == ["PERS-completa"]      # aguardando OK do José já é usável (t150u)
    for pid in ("PERS-sem-recorte", "PERS-so-drive", "PERS-arquivo-sumiu"):
        with pytest.raises(ValidationError, match="imagem local com recortes"):
            usar(pid)
