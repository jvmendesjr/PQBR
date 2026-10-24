"""F3-05: validação em memória; não substitui TS-11 no runtime Temporal.

O executor e a aleatoriedade do workflow são substituídos neste módulo.
Nenhum servidor, worker, backend Jev/Paperclip ou escritor real é acionado.
"""
import asyncio
import socket
import subprocess
from datetime import timedelta
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from temporalio.exceptions import ApplicationError

from pqbr.workflows import correcao as C


@pytest.fixture(autouse=True)
def sem_efeitos_externos(monkeypatch):
    def proibido(*args, **kwargs):
        raise AssertionError("Teste local tentou rede ou subprocesso")

    monkeypatch.setattr(socket.socket, "connect", proibido)
    monkeypatch.setattr(socket.socket, "connect_ex", proibido)
    monkeypatch.setattr(subprocess, "Popen", proibido)


def pedido(**overrides):
    fields = {
        "ferramenta": "camofox",
        "passo": "localizar botao de teste",
        "erro": "seletor sintetico indisponivel",
        "simulacao": C.Simulacao(),
    }
    fields.update(overrides)
    return C.PedidoCorrecao(**fields)


@pytest.fixture
def runtime_local(monkeypatch):
    calls = []
    records = []
    samples = []
    sleeps = []
    patched_values = {"f3-05-camofox-intervalo-v1": True}
    # timeout da atividade e espera antes das tentativas seguintes, intercalados
    values = None

    class RandomLocal:
        def randint(self, lower, upper):
            nonlocal values
            if values is None:
                values = iter((300, 450, 600, 750, 900)
                              if patched_values["f3-05-camofox-intervalo-v1"] else (300, 600, 900))
            value = next(values)
            assert (lower, upper) == (300, 900)
            assert lower <= value <= upper
            samples.append(value)
            return value

    async def executar(fn, arg, **options):
        calls.append((fn, arg, options))
        if fn is C.registrar_correcao:
            records.append(arg)
            return None
        return await fn(arg)

    async def sleep(duration):
        sleeps.append(duration)

    def patched(key):
        return patched_values.get(key, False)

    monkeypatch.setattr(C.workflow, "execute_activity", executar)
    monkeypatch.setattr(C.workflow, "random", lambda: RandomLocal())
    monkeypatch.setattr(C.workflow, "sleep", sleep)
    monkeypatch.setattr(C.workflow, "patched", patched)
    return SimpleNamespace(
        calls=calls,
        records=records,
        samples=samples,
        sleeps=sleeps,
        patched_values=patched_values,
        of=lambda fn: [call for call in calls if call[0] is fn],
    )


def executar(p):
    return asyncio.run(C.CorrecaoAutonomaWorkflow().run(p))


@pytest.mark.parametrize("field", ["intervencoes", "verificacoes"])
def test_simulacao_vazia_rejeitada_antes_de_indexar(field):
    with pytest.raises(ValidationError):
        C.Simulacao(**{field: []})


@pytest.mark.parametrize("n", [-1, 0, 4])
def test_tentativa_fora_das_tres_posicoes_rejeitada(n):
    with pytest.raises(ValidationError):
        C.Tentativa(pedido=pedido(), n=n)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_tentativa_dentro_do_limite_aceita(n):
    assert C.Tentativa(pedido=pedido(), n=n).n == n


@pytest.mark.parametrize("fn", [C.triagem_jev, C.intervir_agente, C.verificar_jev])
def test_backend_ausente_falha_fechado_e_nao_repetivel(fn):
    p = pedido(simulacao=None)
    arg = p if fn is C.triagem_jev else C.Tentativa(pedido=p, n=1)
    with pytest.raises(ApplicationError) as exc:
        asyncio.run(fn(arg))
    assert exc.value.type == "EmConstrucao"
    assert exc.value.non_retryable is True


@pytest.mark.parametrize("passo", ["solicitar pagamento", "excluir item", "publicar_fora das regras"])
def test_risco_nao_controverso_para_antes_do_backend(runtime_local, passo):
    result = executar(pedido(passo=passo, simulacao=None))
    assert (result.resultado, result.tentativas, result.chamar_jose) == ("sensivel", 0, True)
    assert runtime_local.of(C.intervir_agente) == []
    assert runtime_local.of(C.verificar_jev) == []
    assert runtime_local.samples == []
    assert runtime_local.sleeps == []
    assert runtime_local.records == [result]


@pytest.mark.parametrize("classe", ["sensivel", "fora_de_escopo"])
def test_triagem_nao_corrigivel_nao_intervem(runtime_local, classe):
    result = executar(pedido(simulacao=C.Simulacao(triagem=classe)))
    assert (result.resultado, result.tentativas) == ("sensivel", 0)
    assert result.chamar_jose is True
    assert runtime_local.of(C.intervir_agente) == []
    assert runtime_local.of(C.verificar_jev) == []
    assert runtime_local.sleeps == []
    assert runtime_local.records == [result]


def test_sucesso_exige_verificacao_e_registro(runtime_local):
    result = executar(pedido())
    assert (result.resultado, result.tentativas, result.chamar_jose) == ("corrigido", 1, False)
    assert result.proposta_script
    assert [call[0] for call in runtime_local.calls] == [
        C.triagem_jev, C.intervir_agente, C.verificar_jev, C.registrar_correcao
    ]
    agent_options = runtime_local.of(C.intervir_agente)[0][2]
    assert agent_options["retry_policy"].maximum_attempts == 1
    assert agent_options["start_to_close_timeout"] == timedelta(minutes=5)
    assert runtime_local.samples == [300]
    assert runtime_local.sleeps == []
    assert runtime_local.records == [result]


def test_sucesso_na_terceira_preserva_teto_timeouts_e_esperas(runtime_local):
    result = executar(pedido(simulacao=C.Simulacao(intervencoes=[False, False, True])))
    calls = runtime_local.of(C.intervir_agente)
    assert (result.resultado, result.tentativas) == ("corrigido", 3)
    assert [call[1].n for call in calls] == [1, 2, 3]
    assert [call[2]["start_to_close_timeout"] for call in calls] == [
        timedelta(seconds=300), timedelta(seconds=600), timedelta(seconds=900)
    ]
    assert runtime_local.samples == [300, 450, 600, 750, 900]
    assert runtime_local.sleeps == [timedelta(seconds=450), timedelta(seconds=750)]
    assert all(call[2]["retry_policy"].maximum_attempts == 1 for call in calls)
    assert len(runtime_local.of(C.verificar_jev)) == 1
    assert runtime_local.records == [result]


def test_tres_falhas_esgotam_sem_quarta_intervencao(runtime_local):
    result = executar(pedido(simulacao=C.Simulacao(intervencoes=[False])))
    assert (result.resultado, result.tentativas, result.chamar_jose) == ("esgotado", 3, True)
    assert len(runtime_local.of(C.intervir_agente)) == 3
    assert runtime_local.sleeps == [timedelta(seconds=450), timedelta(seconds=750)]
    assert runtime_local.of(C.verificar_jev) == []
    assert runtime_local.records == [result]


def test_intervencao_sem_verificacao_positiva_nao_vira_sucesso(runtime_local):
    result = executar(pedido(simulacao=C.Simulacao(verificacoes=[False])))
    assert (result.resultado, result.tentativas) == ("esgotado", 3)
    assert len(runtime_local.of(C.intervir_agente)) == 3
    assert len(runtime_local.of(C.verificar_jev)) == 3
    assert runtime_local.sleeps == [timedelta(seconds=450), timedelta(seconds=750)]
    assert result.chamar_jose is True
    assert runtime_local.records == [result]


def test_conta_divergente_para_sem_verificar_ou_repetir(runtime_local):
    result = executar(pedido(simulacao=C.Simulacao(conta_confere=False)))
    assert (result.resultado, result.tentativas, result.chamar_jose) == ("sensivel", 1, True)
    assert len(runtime_local.of(C.intervir_agente)) == 1
    assert runtime_local.sleeps == []
    assert runtime_local.of(C.verificar_jev) == []
    assert runtime_local.records == [result]


def test_ferramenta_sem_camofox_nao_usa_sorteio_ou_espera(runtime_local):
    result = executar(pedido(ferramenta="drive"))
    assert result.resultado == "corrigido"
    assert result.tentativas == 1
    assert runtime_local.samples == []
    assert runtime_local.sleeps == []
    assert runtime_local.of(C.intervir_agente)[0][2]["start_to_close_timeout"] == timedelta(minutes=10)


def test_segunda_tentativa_tem_uma_espera_sem_espera_final(runtime_local):
    result = executar(pedido(simulacao=C.Simulacao(intervencoes=[False, True])))
    assert (result.resultado, result.tentativas) == ("corrigido", 2)
    assert runtime_local.sleeps == [timedelta(seconds=450)]
    assert runtime_local.samples == [300, 450, 600]


def test_outra_ferramenta_nao_espera_entre_tres_tentativas(runtime_local):
    result = executar(pedido(ferramenta="drive", simulacao=C.Simulacao(intervencoes=[False])))
    assert (result.resultado, result.tentativas) == ("esgotado", 3)
    assert len(runtime_local.of(C.intervir_agente)) == 3
    assert runtime_local.samples == []
    assert runtime_local.sleeps == []


def test_intervalo_camofox_usa_limite_sorteado(runtime_local, monkeypatch):
    for limite in (300, 900):
        runtime_local.samples.clear()
        runtime_local.sleeps.clear()
        values = iter((300, limite, 300))

        class RandomLimite:
            def randint(self, lower, upper):
                assert (lower, upper) == (300, 900)
                value = next(values)
                runtime_local.samples.append(value)
                return value

        monkeypatch.setattr(C.workflow, "random", lambda: RandomLimite())
        # Execute cada limite em um workflow com sucesso na segunda intervenção.
        executar(pedido(simulacao=C.Simulacao(intervencoes=[False, True])))
        assert runtime_local.sleeps == [timedelta(seconds=limite)]
        assert runtime_local.samples == [300, limite, 300]
        # Isola cada execução removendo apenas o estado registrado, mantendo fixture.
        runtime_local.calls.clear()
        runtime_local.records.clear()


def test_patch_false_preserva_sorteios_originais_sem_espera(runtime_local):
    runtime_local.patched_values["f3-05-camofox-intervalo-v1"] = False
    result = executar(pedido(simulacao=C.Simulacao(intervencoes=[False, False, True])))
    assert result.tentativas == 3
    assert runtime_local.samples == [300, 600, 900]
    assert runtime_local.sleeps == []


def test_excecao_tecnica_propaga_sem_esperas_extras_ou_registro(runtime_local, monkeypatch):
    erro = RuntimeError("falha técnica")

    async def falhar(fn, arg, **options):
        if fn is C.intervir_agente:
            raise erro
        if fn is C.registrar_correcao:
            runtime_local.records.append(arg)
            return None
        return await fn(arg)

    monkeypatch.setattr(C.workflow, "execute_activity", falhar)
    with pytest.raises(RuntimeError) as exc:
        executar(pedido())
    assert exc.value is erro
    assert runtime_local.sleeps == []
    assert runtime_local.records == []


def test_workflow_sem_backend_nao_intervem_nem_registra(runtime_local):
    with pytest.raises(ApplicationError) as exc:
        executar(pedido(simulacao=None))
    assert exc.value.type == "EmConstrucao"
    assert runtime_local.of(C.intervir_agente) == []
    assert runtime_local.of(C.verificar_jev) == []
    assert runtime_local.sleeps == []
    assert runtime_local.records == []


@pytest.mark.parametrize("model,fields", [
    (C.Simulacao, {}),
    (C.PedidoCorrecao, {"ferramenta": "drive", "passo": "teste", "erro": "teste"}),
    (C.Tentativa, {"pedido": pedido(), "n": 1}),
])
def test_entrada_extra_nao_e_aceita(model, fields):
    with pytest.raises(ValidationError):
        model(**fields, desconhecido=True)
