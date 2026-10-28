"""JEV-EF (t143u): porta decide(), adaptadores, limiar, fallback e consumo.

Sem rede: provedores falsos, transporte injetado e um guarda que impede urlopen e build_opener.
"""
from __future__ import annotations

import http.client
import json
import urllib.error
import urllib.request

import pytest

from pqbr.contratos import ClassificacaoPopupCamofox, RegistroConsumo
from pqbr.motores import decisao as d
from pqbr.storage.consumo import sql_insercao

ENDPOINT = "https://api.exemplo.invalido/v1/systemone"
CHAVE = "chave-de-teste-nao-real-0001"
LIMIARES = {"ClassificacaoPopupCamofox": 0.9}
CATEGORIAS = {"cookie_consent": "aviso de cookies", "login_required": "pede login",
              "promo": "propaganda", "other": "outra coisa"}
ACOES = {"aceitar": "clicar em aceitar", "fechar": "fechar a tela", "chamar_jose": "levar ao José", "ignorar": "não mexer"}
PERGUNTAS = [
    d.Pergunta("categoria", "choice", "Que tipo de tela apareceu?", CATEGORIAS),
    d.Pergunta("acao", "choice", "O que fazer com ela?", ACOES),
]


def montar_popup(respostas):
    return {"categoria": respostas["categoria"].escolha, "acao": respostas["acao"].escolha}


def resposta_jev(categoria="cookie_consent", acao="aceitar", confianca=0.95):
    sobra = round(1 - confianca, 4)
    return {
        "answers": {
            "categoria": {"type": "choice", "choice": categoria,
                          "probabilities": {categoria: confianca, "other": sobra}, "confidence": confianca},
            "acao": {"type": "choice", "choice": acao,
                     "probabilities": {acao: confianca, "ignorar": sobra}, "confidence": confianca},
        },
        "usage": {"input_tokens": 120, "output_tokens": 8},
    }


class Falso:
    """Provedor de teste. Cada chamada consome o próximo item da fila: exceção é levantada, dict é devolvido."""

    def __init__(self, nome, fila):
        self.nome = nome
        self.modelo = f"{nome}-teste"
        self.fila = list(fila)
        self.corpos = []

    def consultar(self, corpo, timeout):
        self.corpos.append(corpo)
        item = self.fila.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def decisor(provedores, registros, *, limiares=LIMIARES, tentativas=2):
    return d.DecisorJev(provedores, limiares=limiares, registrar=registros.append, pausa_s=0, tentativas=tentativas)


def decidir(provedores, registros, montar=montar_popup, contrato=ClassificacaoPopupCamofox, **kw):
    return decisor(provedores, registros, **kw).decidir(contrato, "Tela com aviso de cookies.", PERGUNTAS,
                                                        montar, tipo_acao="jev_classificacao")


@pytest.fixture(autouse=True)
def sem_rede(monkeypatch):
    def proibido(*_args, **_kwargs):
        raise AssertionError("teste não pode abrir conexão de rede")
    monkeypatch.setattr(urllib.request, "urlopen", proibido)
    monkeypatch.setattr(urllib.request, "build_opener", proibido)


@pytest.fixture
def chave(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", CHAVE)
    return CHAVE


# perguntas e respostas -----------------------------------------------------------------------

def test_pergunta_exige_opcoes_do_tipo_certo():
    with pytest.raises(ValueError):
        d.Pergunta("x", "choice", "pergunta", {"so_uma": "opção"})
    with pytest.raises(ValueError):
        d.Pergunta("x", "score", "pergunta", ["so_um_nivel"])
    with pytest.raises(ValueError):
        d.Pergunta("x", "score", "pergunta", "baixo-alto")
    with pytest.raises(ValueError):
        d.Pergunta("x", "noul", "pergunta", {"a": "b"})


def test_pergunta_vira_o_formato_do_jev():
    assert PERGUNTAS[0].como_jev() == {"type": "choice", "instructions": "Que tipo de tela apareceu?",
                                       "criteria": CATEGORIAS}
    assert d.Pergunta("n", "noul", "isto é verdade?").como_jev() == {"type": "noul", "instructions": "isto é verdade?"}
    assert d.Pergunta("g", "score", "quão grave?", ["baixo", "médio", "alto"]).como_jev()["criteria"] == \
        ["baixo", "médio", "alto"]


RESPOSTAS_FORA_DO_ESQUEMA = [
    None,
    {"type": "noul", "noul": 0.9},
    {"type": "choice", "choice": "inventada", "probabilities": {}, "confidence": 0.9},
    {"type": "choice", "choice": "promo", "probabilities": {"promo": 0.9, "x": 0.1}, "confidence": 0.9},
    {"type": "choice", "choice": "promo", "probabilities": {"promo": 0.9}, "confidence": 1.5},
    {"type": "choice", "choice": "promo", "probabilities": {"promo": True}, "confidence": 0.9},
    {"type": "choice", "choice": "promo", "probabilities": {"promo": 0.9}},
]


@pytest.mark.parametrize("resposta", RESPOSTAS_FORA_DO_ESQUEMA)
def test_resposta_fora_do_esquema_e_malformada(resposta):
    bruto = {"answers": {"categoria": resposta, "acao": resposta_jev()["answers"]["acao"]}}
    with pytest.raises(d.FalhaDecisao) as erro:
        d._validar_respostas(PERGUNTAS, bruto)
    assert erro.value.codigo == "malformed"


def test_resposta_sem_campo_answers_e_malformada():
    with pytest.raises(d.FalhaDecisao) as erro:
        d._validar_respostas(PERGUNTAS, {"usage": {}})
    assert erro.value.codigo == "malformed"


def test_score_fora_da_escala_ou_sem_confianca_e_malformado():
    grau = d.Pergunta("grau", "score", "quão grave?", ["baixo", "médio", "alto"])
    with pytest.raises(d.FalhaDecisao):
        d._validar_respostas([grau], {"answers": {"grau": {"type": "score", "score": 5, "confidence": 0.9}}})
    with pytest.raises(d.FalhaDecisao):
        d._validar_respostas([grau], {"answers": {"grau": {"type": "score", "score": 1}}})
    ok = d._validar_respostas([grau], {"answers": {"grau": {"type": "score", "score": 1, "confidence": 0.8}}})
    assert ok["grau"] == d.Resposta("score", 0.8, nivel=1.0)


def test_noul_confia_no_lado_que_o_jev_prefere_e_nao_na_probabilidade_de_sim():
    # p=0,03 de sim é um "não" firme: a confiança é a do lado escolhido
    resposta = resposta_jev()
    resposta["answers"]["ok"] = {"type": "noul", "noul": 0.03}
    dec = decisor([Falso("typesafe", [resposta])], []).decidir(
        ClassificacaoPopupCamofox, "Tela com aviso de cookies.",
        PERGUNTAS + [d.Pergunta("ok", "noul", "a tela tem aviso?")], montar_popup)
    assert dec.valor is not None and dec.motivo == "ok"
    assert dec.respostas["ok"].nivel == 0.03
    assert dec.respostas["ok"].confianca == pytest.approx(0.97)


# decisão ---------------------------------------------------------------------------------------

def test_decisao_acima_do_limiar_vira_contrato_validado():
    registros = []
    principal = Falso("typesafe", [resposta_jev()])
    dec = decidir([principal], registros, tentativas=2)
    assert dec.escalar is False and dec.motivo == "ok" and dec.provedor == "typesafe"
    assert dec.valor == ClassificacaoPopupCamofox(categoria="cookie_consent", acao="aceitar", confianca=0.95)
    assert principal.corpos[0]["questions"]["acao"]["type"] == "choice"
    (registro,) = registros
    assert isinstance(registro, RegistroConsumo)
    assert (registro.provedor, registro.modelo, registro.tipo_acao, registro.sucesso) == \
        ("typesafe", "typesafe-teste", "jev_classificacao", True)
    assert (registro.tokens_entrada, registro.tokens_saida, registro.erro_classe, registro.ferramenta) == \
        (120, 8, None, "jev")


def test_confianca_da_decisao_e_a_menor_das_respostas():
    resposta = resposta_jev(confianca=0.95)
    resposta["answers"]["acao"]["confidence"] = 0.92
    dec = decidir([Falso("typesafe", [resposta])], [])
    assert dec.confianca == 0.92 and dec.valor.confianca == 0.92


def test_abaixo_do_limiar_escala_mas_registra_a_chamada():
    registros = []
    dec = decidir([Falso("typesafe", [resposta_jev(confianca=0.6)])], registros)
    assert dec.valor is None and dec.escalar is True and dec.motivo == "confianca_abaixo_do_limiar"
    assert [r.sucesso for r in registros] == [True]


def test_sem_limiar_para_o_contrato_nao_age():
    dec = decidir([Falso("typesafe", [resposta_jev()])], [], limiares={})
    assert dec.valor is None and dec.escalar is True and dec.motivo == "sem_limiar_para_o_contrato"


def test_contrato_recusa_combinacao_proibida():
    # captcha nunca é resolvido por agente: o contrato só aceita chamar_jose
    dec = decidir([Falso("typesafe", [resposta_jev()])], [], montar=lambda r: {"categoria": "captcha", "acao": "aceitar"})
    assert dec.valor is None and dec.escalar is True and dec.motivo == "contrato_recusou_a_resposta"


def test_erro_repetivel_tenta_de_novo_no_mesmo_provedor():
    registros = []
    principal = Falso("typesafe", [d.FalhaDecisao("network"), resposta_jev()])
    dec = decidir([principal], registros, tentativas=2)
    assert dec.valor is not None and len(principal.corpos) == 2
    assert [(r.sucesso, r.erro_classe, r.tentativa) for r in registros] == [(False, "network", 1), (True, None, 2)]


def test_erro_nao_repetivel_passa_ao_fallback_com_o_mesmo_pedido():
    registros = []
    principal = Falso("typesafe", [d.FalhaDecisao("auth_failed")])
    fallback = Falso("openrouter", [resposta_jev()])
    dec = decidir([principal, fallback], registros)
    assert dec.provedor == "openrouter" and dec.valor is not None
    assert len(principal.corpos) == 1 and len(fallback.corpos) == 1
    assert principal.corpos[0] == fallback.corpos[0]
    assert [(r.provedor, r.sucesso, r.erro_classe) for r in registros] == \
        [("typesafe", False, "auth_failed"), ("openrouter", True, None)]


def test_sem_chave_nao_gera_linha_de_consumo_e_passa_ao_fallback():
    registros = []
    principal = Falso("typesafe", [d.FalhaDecisao("no_key")])
    fallback = Falso("openrouter", [resposta_jev()])
    dec = decidir([principal, fallback], registros)
    assert dec.provedor == "openrouter"
    assert [r.provedor for r in registros] == ["openrouter"]


def test_resposta_malformada_ainda_registra_o_consumo_com_tokens():
    # o Jev respondeu e cobrou; a resposta fora do esquema não pode sair do registro sem tokens
    registros = []
    estragada = resposta_jev()
    estragada["answers"]["acao"] = {"type": "choice", "choice": "inventada"}
    dec = decidir([Falso("typesafe", [estragada]), Falso("openrouter", [resposta_jev()])], registros)
    assert dec.provedor == "openrouter"
    assert (registros[0].sucesso, registros[0].erro_classe, registros[0].tokens_entrada) == (False, "malformed", 120)


def test_tudo_fora_escala_e_registra_cada_chamada():
    registros = []
    principal = Falso("typesafe", [d.FalhaDecisao("network"), d.FalhaDecisao("network")])
    fallback = Falso("openrouter", [d.FalhaDecisao("credits_exhausted")])
    dec = decidir([principal, fallback], registros)
    assert dec.valor is None and dec.escalar is True
    assert dec.motivo == "jev_indisponivel: typesafe:network, typesafe:network, openrouter:credits_exhausted"
    assert [(r.provedor, r.tentativa, r.sucesso) for r in registros] == \
        [("typesafe", 1, False), ("typesafe", 2, False), ("openrouter", 3, False)]


def test_estado_grande_demais_nao_chama_o_jev():
    principal = Falso("typesafe", [resposta_jev()])
    dec = decisor([principal], []).decidir(ClassificacaoPopupCamofox, "x" * (d.MAX_ESTADO_CHARS + 1),
                                           PERGUNTAS, montar_popup)
    assert dec.motivo == "estado_grande_demais" and principal.corpos == []


def test_perguntas_vazias_ou_repetidas_sao_erro_de_uso():
    with pytest.raises(ValueError):
        decisor([Falso("typesafe", [])], []).decidir(ClassificacaoPopupCamofox, "x", [], montar_popup)
    with pytest.raises(ValueError):
        decisor([Falso("typesafe", [])], []).decidir(ClassificacaoPopupCamofox, "x",
                                                     [PERGUNTAS[0], PERGUNTAS[0]], montar_popup)


# adaptadores -----------------------------------------------------------------------------------

def test_adaptador_typesafe_monta_o_pedido_do_systemone(chave):
    enviados = {}

    def transporte(url, corpo, cabecalhos, timeout):
        enviados.update(url=url, corpo=json.loads(corpo), cabecalhos=cabecalhos, timeout=timeout)
        return json.dumps(resposta_jev()).encode("utf-8")

    provedor = d.JevTypeSafe(endpoint=ENDPOINT, modelo="jev-latest", chave_env="TYPESAFE_API_KEY", transporte=transporte)
    bruto = provedor.consultar({"state": "estado", "questions": {"categoria": PERGUNTAS[0].como_jev()}}, 7)
    assert enviados["url"] == ENDPOINT and enviados["timeout"] == 7
    assert enviados["corpo"]["model"] == "jev-latest" and enviados["corpo"]["state"] == "estado"
    assert enviados["cabecalhos"]["Authorization"] == f"Bearer {chave}"
    assert "answers" in bruto


def test_adaptador_sem_chave_recusa_antes_de_enviar(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    enviou = []
    provedor = d.JevTypeSafe(endpoint=ENDPOINT, modelo="jev-latest", chave_env="TYPESAFE_API_KEY",
                             transporte=lambda *a: enviou.append(a) or b"{}")
    with pytest.raises(d.FalhaDecisao) as erro:
        provedor.consultar({"state": "x", "questions": {}}, 5)
    assert erro.value.codigo == "no_key" and enviou == []


def test_resposta_que_nao_e_json_e_malformada(chave):
    provedor = d.JevTypeSafe(endpoint=ENDPOINT, modelo="jev-latest", chave_env="TYPESAFE_API_KEY",
                             transporte=lambda *a: b"<html>erro</html>")
    with pytest.raises(d.FalhaDecisao) as erro:
        provedor.consultar({"state": "x", "questions": {}}, 5)
    assert erro.value.codigo == "malformed"


def test_leitura_http_quebrada_vira_network_e_nao_escapa(monkeypatch):
    class Quebrado:
        def open(self, *_args, **_kwargs):
            raise http.client.IncompleteRead(b"")
    monkeypatch.setattr(urllib.request, "build_opener", lambda *_handlers: Quebrado())
    with pytest.raises(d.FalhaDecisao) as erro:
        d._enviar_urllib(ENDPOINT, b"{}", {}, 5)
    assert erro.value.codigo == "network"


def test_redirecionamento_nao_e_seguido_para_o_token_nao_sair_da_origem():
    pedido = urllib.request.Request(ENDPOINT, data=b"{}", method="POST")
    with pytest.raises(urllib.error.HTTPError):
        d._SemRedirecionamento().redirect_request(pedido, None, 302, "Found", {}, "https://outro.invalido/")


@pytest.mark.parametrize("status, codigo", [(401, "auth_failed"), (403, "auth_failed"),
                                            (402, "credits_exhausted"), (429, "rate_limited"),
                                            (529, "overloaded"), (500, "http_500")])
def test_status_http_vira_codigo_de_falha(status, codigo):
    assert d.codigo_http(status) == codigo


# configuração e consumo ------------------------------------------------------------------------

def test_config_aponta_o_jev_direto_com_fallback_desligado():
    dec = d.decisor_padrao(registrar=lambda r: None)
    assert [p.nome for p in dec.cadeia] == ["typesafe"]
    principal = dec.cadeia[0]
    assert (principal.endpoint, principal.modelo, principal.chave_env) == \
        ("https://api.typesafe.ai/v1/systemone", "jev-latest", "TYPESAFE_API_KEY")
    assert {"ClassificacaoPopupCamofox", "ClassificacaoEmailYouTube", "TriagemCorrecao", "VerificacaoCorrecao"} \
        <= set(dec.limiares)
    assert dec.tentativas == 2


def test_decide_usa_o_decisor_da_config(monkeypatch):
    registros = []
    principal = Falso("typesafe", [resposta_jev()])
    monkeypatch.setattr(d, "decisor_padrao", lambda registrar=None: decisor([principal], registros))
    dec = d.decide(ClassificacaoPopupCamofox, "Tela com aviso de cookies.", PERGUNTAS, montar_popup,
                   tipo_acao="jev_classificacao")
    assert dec.valor is not None and len(registros) == 1


def test_consumo_grava_uma_coluna_por_campo():
    registro = RegistroConsumo(provedor="typesafe", modelo="jev-latest", tipo_acao="jev_classificacao",
                               sucesso=True, ferramenta="jev", tokens_entrada=120, tokens_saida=8)
    sql, params = sql_insercao(registro)
    assert sql.startswith("insert into pqbr.consumo_modelos (")
    assert sql.count("%s") == len(params) == len(registro.model_dump())


# usos estruturados e ligação aos fluxos (t144u) ------------------------------------------------

def _decisor_usos(respostas: list[Any], registros: list[RegistroConsumo] | None = None) -> d.DecisorJev:
    reg = registros if registros is not None else []
    return d.DecisorJev(
        [Falso("typesafe", respostas)],
        limiares={
            "ClassificacaoPopupCamofox": 0.9,
            "EscolhaRefCanario": 0.9,
            "TriagemCorrecao": 0.9,
            "DecisaoRepeticao": 0.85,
            "VerificacaoCorrecao": 0.8,
            "ClassificacaoEmailYouTube": 0.8,
        },
        registrar=reg.append,
    )


def _choice_mock(escolha: str, confianca: float = 0.98) -> dict[str, Any]:
    return {"type": "choice", "choice": escolha, "probabilities": {escolha: confianca}, "confidence": confianca}


def test_classificar_popup_camofox_fechar_novidades():
    dec = _decisor_usos([{
        "answers": {
            "categoria": _choice_mock("promo", 0.98),
            "acao": _choice_mock("fechar", 0.98),
        },
        "usage": {"input_tokens": 800, "output_tokens": 140},
    }])
    r = d.classificar_popup_camofox("Modal O que há de novo no Flow com botão Começar", seletor="e5", decisor=dec)
    assert not r.escalar and r.valor is not None
    assert (r.valor.categoria, r.valor.acao, r.valor.seletor) == ("promo", "fechar", "e5")


def test_escolher_ref_canario_escolhe_elemento_ou_abstain():
    dec = _decisor_usos([
        {"answers": {"ref": _choice_mock("e19", 0.99)}},
        {"answers": {"ref": _choice_mock("abstain", 1.0)}},
    ])
    elems = {"e5": "button 'Começar'", "e19": "button 'Criar'"}
    r1 = d.escolher_ref_canario("Clicar em Criar", elems, decisor=dec)
    assert not r1.escalar and r1.valor is not None and r1.valor.ref == "e19" and not r1.valor.absteve
    r2 = d.escolher_ref_canario("Clicar em Publicar", elems, decisor=dec)
    assert not r2.escalar and r2.valor is not None and r2.valor.ref == "abstain" and r2.valor.absteve


def test_triagem_e_verificacao_correcao_ligadas_ao_workflow(monkeypatch):
    import asyncio
    from pqbr.workflows import correcao as wf

    dec = _decisor_usos([
        {"answers": {"classe": _choice_mock("corrigivel", 0.99)}},
        {"answers": {"ok": {"type": "noul", "noul": 0.92}}},
    ])
    monkeypatch.setattr(d, "jev_disponivel", lambda decisor=None: True)
    monkeypatch.setattr(d, "decisor_padrao", lambda registrar=None: dec)
    ped = wf.PedidoCorrecao(ferramenta="camofox", passo="clicar no botão Criar", erro="TimeoutError: e14 ausente")
    tri = asyncio.run(wf.triagem_jev(ped))
    assert tri.classe == "corrigivel" and "jev:corrigivel" in tri.motivo
    ver = asyncio.run(wf.verificar_jev(wf.Tentativa(pedido=ped, n=1)))
    assert ver.ok is True and "jev:ok" in ver.motivo


def test_checar_repeticao_usa_jev_na_faixa_de_duvida_semantica():
    from pqbr.pipeline.grade import checar_repeticao

    dec = _decisor_usos([
        {
            "answers": {
                "mesmo_assunto": {"type": "noul", "noul": 0.95},
                "qual": _choice_mock("u0", 0.96),
            }
        },
        {
            "answers": {
                "mesmo_assunto": {"type": "noul", "noul": 0.05},
                "qual": _choice_mock("nenhum", 0.94),
            }
        },
    ])
    usados = ["Por que batemos na madeira para afastar azar?"]
    # Sem palavras do núcleo em comum, mas variação semântica direta:
    r1 = checar_repeticao("De onde surgiu a superstição de dar três toques no móvel?", usados, decisor=dec)
    assert r1.repetido is True and r1.barreira == "variacao" and r1.tema_parecido == usados[0]
    r2 = checar_repeticao("Por que o chuveiro elétrico faz barulho no modo inverno?", usados, decisor=dec)
    assert r2.repetido is False and r2.barreira == "nenhuma"


def test_classificar_email_youtube_strike_chama_jose():
    dec = _decisor_usos([{
        "answers": {
            "categoria": _choice_mock("strike", 0.99),
            "gravidade": _choice_mock("critico", 0.99),
            "acao": _choice_mock("chamar_jose", 0.99),
        }
    }])
    r = d.classificar_email_youtube("Strike de direitos autorais", "Seu vídeo recebeu um strike.", decisor=dec)
    assert not r.escalar and r.valor is not None
    assert (r.valor.categoria, r.valor.gravidade, r.valor.acao) == ("strike", "critico", "chamar_jose")

