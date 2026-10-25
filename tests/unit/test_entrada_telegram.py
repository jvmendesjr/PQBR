"""t537/t538: parser de callback do bot próprio → entrada_telegram → sinal."""
import asyncio, json, os, tempfile
from datetime import datetime, timedelta, timezone
import pytest
from pqbr.contratos.ponte_telegram import PedidoAprovacao
from pqbr.workflows.entrada_telegram import (CONFIG, EnvelopeInvalido, callback_data, carregar_config,
                                             para_evento, tratar_envelope)
from pqbr.workflows.ponte_telegram import RepositorioMemoria, novo_token

JOSE = "123456"; run = asyncio.run


def _cen():
    repo, ref = RepositorioMemoria(), novo_token()
    repo.registrar_pedido(PedidoAprovacao(token=ref, workflow_id="ep-1", etapa="aguardando_aprovacao",
                                          tarefa="publicar EP1", expira_em=datetime.now(timezone.utc) + timedelta(hours=1)))
    sinais = []
    async def s(wf, t, d, esperada=None): sinais.append((wf, d)); return "aguardando_aprovacao"
    return repo, ref, sinais, s


def _linha(ref, uid=1, de=JOSE, d="a"):
    return json.dumps({"update_id": uid, "from_id": int(de), "chat_id": -100, "data": f"pq:{d}:{ref}"}).encode()


def test_config_padrao_desligada_e_valida():
    assert carregar_config(CONFIG)["entrada"] == "desligado"


def test_callback_data_cabe_em_64_bytes():
    assert callback_data("aprovar", novo_token()).startswith("pq:a:")
    with pytest.raises(ValueError): callback_data("negar", "x" * 64)


@pytest.mark.parametrize("env", [
    {"update_id": 1, "from_id": 1, "data": "ea:x:y"},                 # prefixo do core
    {"update_id": 1, "from_id": 1, "data": "pq:z:" + "x" * 20},        # decisão inválida
    {"update_id": 1, "from_id": True, "data": "pq:a:" + "x" * 20},     # from_id bool
    {"update_id": 1, "from_id": "jose", "data": "pq:a:" + "x" * 20},   # from_id não numérico
    {"update_id": 1, "from_id": 1, "data": "pq:a:" + "x" * 20, "texto": "aprova"},  # campo extra
])
def test_envelope_invalido(env):
    with pytest.raises(EnvelopeInvalido): para_evento(env)


def test_fluxo_aprova_uma_vez_e_recusa_estranho():
    repo, ref, sinais, s = _cen()
    assert run(tratar_envelope(_linha(ref, de="999"), repo, JOSE, s))["status"] == "remetente_recusado"
    assert run(tratar_envelope(_linha(ref), repo, JOSE, s))["status"] == "sinalizado"
    assert run(tratar_envelope(_linha(ref, uid=2, d="n"), repo, JOSE, s))["status"] == "duplicado"
    assert run(tratar_envelope(b"lixo", repo, JOSE, s))["status"] == "envelope_invalido"
    assert sinais == [("ep-1", "aprovar")]
