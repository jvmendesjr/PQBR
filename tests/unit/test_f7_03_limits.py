import asyncio

import pytest
from pydantic import ValidationError

from pqbr.contratos import CTA, RoteiroShort
from pqbr.workflows import notebooklm


def roteiro_valido():
    falas = [
        "Por que a gente desliga a TV e acorda na hora?",
        *["O corpo sabe que o barulho sumiu e estranha o silêncio da sala."] * 8,
        CTA,
    ]
    return {
        "episodio_id": "ep-0001",
        "titulo": "Por que acordamos sem a TV?",
        "falas": falas,
        "tipo_cta": "fallback",
        "entidades_cena": ["sofá", "TV"],
        "bloco_visual": {
            "estilo": "stickman de tubos grossos, traço chapado, cabeça redonda, sem pessoa de cartum",
            "personagem": "homem de ~40 anos, magro, cabelo grisalho curto, camiseta verde, bigode, expressão curiosa",
            "cenas": [
                {
                    "fala": "Por que a gente fala isso?",
                    "acao": "ele olha a TV desligada",
                    "enquadramento": "plano médio",
                    "ambiente": "sala brasileira, sofá, TV de tubo, noite",
                },
                {
                    "fala": "Comenta aí",
                    "acao": "ele volta ao sofá",
                    "enquadramento": "plano aberto",
                    "ambiente": "mesma sala, noite",
                },
            ],
        },
    }


def setup_limits(monkeypatch, tmp_path):
    # Limites de teste intencionalmente pequenos; não representam quotas reais.
    monkeypatch.setattr(notebooklm, "HOME", tmp_path)
    monkeypatch.setattr(notebooklm, "LIMITES", {"chat": 1, "video": 1})


def test_roteiro_sem_bloco_visual_eh_rejeitado():
    payload = roteiro_valido()
    RoteiroShort.model_validate(payload)
    payload.pop("bloco_visual")

    with pytest.raises(ValidationError) as erro:
        RoteiroShort.model_validate(payload)

    assert any(item["loc"] == ("bloco_visual",) for item in erro.value.errors())


def test_contador_de_chat_bloqueia_antes_da_segunda_chamada(monkeypatch, tmp_path):
    setup_limits(monkeypatch, tmp_path)
    chamadas = []

    def cli_mock(*args, **kwargs):
        chamadas.append(args)
        return '{"answer":"resposta local"}'

    monkeypatch.setattr(notebooklm, "_cli", cli_mock)

    assert asyncio.run(notebooklm.nlm_perguntar("caderno-teste", "pergunta")) == "resposta local"
    with pytest.raises(notebooklm.SemSaldo, match="limite local de segurança"):
        asyncio.run(notebooklm.nlm_perguntar("caderno-teste", "segunda pergunta"))

    assert len(chamadas) == 1
    assert notebooklm._contador() == {"chat": 1}


def test_gerar_short_recusa_sem_chamar_cli(monkeypatch, tmp_path):
    setup_limits(monkeypatch, tmp_path)
    chamadas = []
    monkeypatch.setattr(notebooklm, "_cli", lambda *args, **kwargs: chamadas.append(args))

    with pytest.raises(notebooklm.VideoNotebookLMDescartado, match="não gera vídeo"):
        asyncio.run(notebooklm.nlm_gerar_short("caderno-teste"))

    assert chamadas == []
    assert notebooklm._contador() == {}


def test_preflight_de_saldo_bloqueia_no_limite_sem_consultar_provider(monkeypatch, tmp_path):
    setup_limits(monkeypatch, tmp_path)
    notebooklm._contador("chat")
    chamadas = []
    monkeypatch.setattr(notebooklm, "_cli", lambda *args, **kwargs: chamadas.append(args))

    with pytest.raises(notebooklm.SemSaldo, match="limite local de segurança"):
        asyncio.run(notebooklm.nlm_checar_saldo("chat"))

    assert chamadas == []

def test_saldo_separa_contador_local_das_janelas_oficiais(monkeypatch, tmp_path):
    setup_limits(monkeypatch, tmp_path)
    chamadas = []

    def cli_mock(*args, **kwargs):
        chamadas.append(args)
        return '{"is_exhausted":false,"windows":[{"kind":"day","used_percent":12.5}]}'

    monkeypatch.setattr(notebooklm, "_cli", cli_mock)

    resultado = asyncio.run(notebooklm.nlm_checar_saldo("chat"))

    assert resultado == {"dia": {}, "janelas": {"day": 12.5}}
    assert chamadas == [("usage", "--json")]

