"""F3-05: contratos no SDK Temporal, sem servidor, Worker ou conexão.

Usa as APIs públicas ActivityEnvironment e pydantic_data_converter instaladas.
Não executa o workflow nem comprova replay, retries, timers ou persistência.
Os payloads e resultados são sintéticos; nenhum backend/escritor é acionado.
"""
import asyncio
import os
import socket
import subprocess

import pytest
from pydantic import ValidationError
from temporalio.api.failure.v1 import Failure
from temporalio.contrib.pydantic import pydantic_data_converter as CONVERTER
from temporalio.exceptions import ApplicationError
from temporalio.testing import ActivityEnvironment

from pqbr.contratos import (
    PassoCorrecao,
    ResultadoCorrecao,
    ResultadoIntervencao,
    TriagemCorrecao,
    VerificacaoCorrecao,
)
from pqbr.workflows import correcao as C


@pytest.fixture(autouse=True)
def sem_rede_ou_processos(monkeypatch):
    def proibido(*args, **kwargs):
        raise AssertionError("Teste SDK offline tentou rede ou processo externo")

    # socketpair do event loop continua permitido; não abre um endpoint de rede.
    for name in ("connect", "connect_ex", "bind", "listen", "sendto"):
        monkeypatch.setattr(socket.socket, name, proibido)
    monkeypatch.setattr(socket, "create_connection", proibido)
    monkeypatch.setattr(socket, "getaddrinfo", proibido)
    monkeypatch.setattr(subprocess, "Popen", proibido)
    monkeypatch.setattr(os, "system", proibido)
    for name in ("posix_spawn", "posix_spawnp", "fork", "forkpty"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, proibido)


def pedido(**overrides):
    fields = dict(
        ferramenta="camofox",
        passo="localizar botao sintetico",
        erro="seletor sintetico indisponivel",
        episodio="PQBR-EP9999",
        simulacao=C.Simulacao(),
    )
    fields.update(overrides)
    return C.PedidoCorrecao(**fields)


async def ida_e_volta(value, model):
    payloads = await CONVERTER.encode([value])
    assert len(payloads) == 1
    assert payloads[0].metadata["encoding"] == b"json/plain"
    # Inclui a serialização protobuf em bytes, sem transporte ou fila.
    restored_payload = type(payloads[0]).FromString(payloads[0].SerializeToString())
    restored = (await CONVERTER.decode([restored_payload], [model]))[0]
    assert type(restored) is model
    return restored


@pytest.mark.parametrize("value", [
    C.Simulacao(intervencoes=[False, True], verificacoes=[False, True]),
    pedido(),
    pedido(simulacao=None),
    C.Tentativa(pedido=pedido(), n=1),
    C.Tentativa(pedido=pedido(), n=3),
    TriagemCorrecao(classe="corrigivel", motivo="dado sintetico"),
    TriagemCorrecao(classe="sensivel", motivo="dado sintetico"),
    TriagemCorrecao(classe="fora_de_escopo", motivo="dado sintetico"),
    ResultadoIntervencao(
        resolvido=True,
        passos=[PassoCorrecao(acao="ler", alvo="elemento sintetico")],
        aprendizado="dado sintetico",
        proposta_script="proposta sintetica",
    ),
    ResultadoIntervencao(resolvido=False, conta_confere=False),
    VerificacaoCorrecao(ok=True),
    VerificacaoCorrecao(ok=False, motivo="dado sintetico"),
    ResultadoCorrecao(resultado="corrigido", tentativas=1, chamar_jose=False,
                      proposta_script="proposta sintetica"),
    ResultadoCorrecao(resultado="esgotado", tentativas=3, chamar_jose=True),
    ResultadoCorrecao(resultado="sensivel", tentativas=0, chamar_jose=True),
], ids=[
    "simulacao", "pedido-simulado", "pedido-sem-backend", "tentativa-1",
    "tentativa-3", "triagem-corrigivel", "triagem-sensivel", "triagem-fora",
    "intervencao-com-passos", "conta-divergente", "verificacao-ok",
    "verificacao-reprovada", "corrigido", "esgotado", "sensivel",
])
def test_contrato_sobrevive_ao_conversor_temporal(value):
    restored = asyncio.run(ida_e_volta(value, type(value)))
    assert restored == value
    assert restored is not value
    if isinstance(restored, C.PedidoCorrecao) and restored.simulacao is not None:
        assert type(restored.simulacao) is C.Simulacao
    if isinstance(restored, C.Tentativa):
        assert type(restored.pedido) is C.PedidoCorrecao
        assert type(restored.pedido.simulacao) is C.Simulacao
    if isinstance(restored, ResultadoIntervencao) and restored.passos:
        assert type(restored.passos[0]) is PassoCorrecao


@pytest.mark.parametrize("model,fields", [
    (C.Simulacao, {"intervencoes": []}),
    (C.Simulacao, {"verificacoes": []}),
    (C.Tentativa, {"pedido": pedido().model_dump(), "n": 0}),
    (C.Tentativa, {"pedido": pedido().model_dump(), "n": 4}),
    (C.PedidoCorrecao, {**pedido().model_dump(), "desconhecido": True}),
], ids=["intervencoes-vazias", "verificacoes-vazias", "tentativa-zero",
        "quarta-tentativa", "campo-extra"])
def test_payload_invalido_rejeitado_na_decodificacao_tipificada(model, fields):
    async def executar():
        payloads = await CONVERTER.encode([fields])
        with pytest.raises(ValidationError):
            await CONVERTER.decode(payloads, [model])

    asyncio.run(executar())


@pytest.mark.parametrize("n,resolve,verifica", [
    (1, False, False), (2, False, True), (3, True, True),
])
def test_activities_simuladas_em_contexto_sdk_com_payloads_tipados(n, resolve, verifica):
    async def executar():
        p = pedido(simulacao=C.Simulacao(
            intervencoes=[False, False, True], verificacoes=[False, True, True],
        ))
        env = ActivityEnvironment()
        env.payload_converter = CONVERTER.payload_converter
        decoded_p = await ida_e_volta(p, C.PedidoCorrecao)
        triagem = await env.run(C.triagem_jev, decoded_p)
        triagem = await ida_e_volta(triagem, TriagemCorrecao)
        assert triagem.classe == "corrigivel"
        tentativa = await ida_e_volta(C.Tentativa(pedido=p, n=n), C.Tentativa)
        intervencao = await env.run(C.intervir_agente, tentativa)
        intervencao = await ida_e_volta(intervencao, ResultadoIntervencao)
        assert intervencao.resolvido is resolve
        assert intervencao.conta_confere is True
        assert bool(intervencao.proposta_script) is resolve
        verificacao = await env.run(C.verificar_jev, tentativa)
        verificacao = await ida_e_volta(verificacao, VerificacaoCorrecao)
        assert verificacao.ok is verifica

    # As três invocações acima são explícitas, não escalonadas pelo Temporal.
    asyncio.run(executar())


@pytest.mark.parametrize("fn", [C.triagem_jev, C.intervir_agente, C.verificar_jev])
def test_backend_ausente_preserva_falha_nao_repetivel_no_sdk(fn):
    async def executar():
        env = ActivityEnvironment()
        env.payload_converter = CONVERTER.payload_converter
        p = pedido(simulacao=None)
        arg = p if fn is C.triagem_jev else C.Tentativa(pedido=p, n=1)
        arg = await ida_e_volta(arg, type(arg))
        with pytest.raises(ApplicationError) as caught:
            await env.run(fn, arg)
        failure = Failure()
        await CONVERTER.encode_failure(caught.value, failure)
        failure = Failure.FromString(failure.SerializeToString())
        assert failure.application_failure_info.type == "EmConstrucao"
        assert failure.application_failure_info.non_retryable is True
        restored = await CONVERTER.decode_failure(failure)
        assert isinstance(restored, ApplicationError)
        assert restored.type == "EmConstrucao"
        assert restored.non_retryable is True
        assert restored.message == caught.value.message

    # Valida o sinal da falha, não a aplicação de retries por um servidor.
    asyncio.run(executar())


@pytest.mark.parametrize("passo", [
    "solicitar pagamento", "excluir item sintetico", "publicar_fora das regras",
])
def test_triagem_sensivel_sem_backend_no_contexto_sdk(passo):
    async def executar():
        p = await ida_e_volta(pedido(passo=passo, simulacao=None), C.PedidoCorrecao)
        result = await ActivityEnvironment().run(C.triagem_jev, p)
        result = await ida_e_volta(result, TriagemCorrecao)
        assert result.classe == "sensivel"
        assert result.motivo == f"passo sensível: {passo}"

    asyncio.run(executar())
