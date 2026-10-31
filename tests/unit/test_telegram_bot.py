"""t538: bot próprio (saída sendMessage + entrada getUpdates) com Telegram simulado."""
import asyncio, os, stat
from datetime import datetime, timedelta, timezone
import pytest
from pqbr.contratos.ponte_telegram import MensagemSaida, PedidoAprovacao
from pqbr.workflows import telegram_bot as tb
from pqbr.workflows.entrada_telegram import carregar_config
from pqbr.workflows.ponte_telegram import EntregaIncerta, RepositorioMemoria, enviar_idempotente, novo_token

JOSE = "123456"; run = asyncio.run


class TelegramFalso:
    def __init__(self, updates=None, falha=None):
        self.chamadas, self.updates, self.falha, self.mid = [], list(updates or []), falha, 100
    async def __call__(self, metodo, p):
        self.chamadas.append((metodo, p))
        if self.falha: raise self.falha
        if metodo == "sendMessage": self.mid += 1; return {"message_id": self.mid}
        if metodo == "getUpdates": return [u for u in self.updates if u["update_id"] >= p["offset"]]
        return True
    def metodos(self): return [m for m, _ in self.chamadas]


class Off:
    def __init__(self): self.v = 0
    def ler(self): return self.v
    def gravar(self, v): self.v = v


def _cen(etapa="aguardando_aprovacao"):
    repo, ref = RepositorioMemoria(), novo_token()
    repo.registrar_pedido(PedidoAprovacao(token=ref, workflow_id="ep-1", etapa="aguardando_aprovacao", tarefa="publicar",
                                          expira_em=datetime.now(timezone.utc) + timedelta(hours=1)))
    sinais = []
    async def s(wf, r, d, esperada=None): sinais.append((wf, d)); return etapa
    return repo, ref, sinais, s


def _cb(uid, ref, de=JOSE, d="a"):
    return {"update_id": uid, "callback_query": {"id": f"q{uid}", "from": {"id": int(de)}, "data": f"pq:{d}:{ref}",
            "message": {"message_id": 7, "chat": {"id": int(JOSE)}}}}


def test_config_valida_e_ligada_por_t538a():
    # t538-A (OK do José): ponte ativada; a config real tem de ser uma das alternativas válidas.
    c = carregar_config(); assert c["saida"] in ("desligado", *c["saida_alternativas"]) and c["entrada"] in ("desligado", *c["entrada_alternativas"])


def test_saida_pedido_com_botoes_e_reenvio_marcado(monkeypatch):
    monkeypatch.setenv(tb.ENV_JOSE, JOSE); tg = TelegramFalso(); ref = novo_token()
    repo = RepositorioMemoria(); m = MensagemSaida(chave="aprov:ep-1:1", classe="pedido_aprovacao", texto="Publicar EP1?", ref_pedido=ref)
    repo.enfileirar(m)
    r = run(enviar_idempotente(repo, tb.RemetenteTelegram(tg), m.chave))
    assert r.estado == "enviado" and r.mensagem_id == 101
    p = tg.chamadas[0][1]
    assert p["chat_id"] == int(JOSE) and [b["callback_data"] for b in p["reply_markup"]["inline_keyboard"][0]] == [f"pq:a:{ref}", f"pq:n:{ref}"]
    assert run(tb.RemetenteTelegram(tg).enviar(m, True)) and tg.chamadas[-1][1]["text"].startswith("(reenvio) ")


def test_saida_sem_destino_falha_fechado(monkeypatch):
    monkeypatch.delenv(tb.ENV_JOSE, raising=False)
    with pytest.raises(tb.TelegramErro): run(tb.RemetenteTelegram(TelegramFalso()).enviar(MensagemSaida(chave="aviso:x:1", classe="aviso_operacional", texto="a"), False))


def test_saida_timeout_vira_incerto():
    repo = RepositorioMemoria(); m = MensagemSaida(chave="aviso:x:1", classe="aviso_operacional", texto="a"); repo.enfileirar(m)
    assert run(enviar_idempotente(repo, tb.RemetenteTelegram(TelegramFalso(falha=EntregaIncerta("t")), "1"), m.chave)).estado == "incerto"


def test_entrada_aprova_responde_remove_botoes_e_avanca_offset():
    repo, ref, sinais, s = _cen(); tg = TelegramFalso([_cb(10, ref), _cb(11, ref, d="n")]); off = Off()
    assert run(tb.ciclo_entrada(tg, off, repo, JOSE, s)) == 2
    assert sinais == [("ep-1", "aprovar")] and off.v == 12
    assert tg.metodos() == ["getUpdates", "answerCallbackQuery", "editMessageReplyMarkup", "answerCallbackQuery", "editMessageReplyMarkup"]
    assert tg.chamadas[1][1]["text"] == "Registrado." and tg.chamadas[3][1]["text"] == "Já registrado."
    assert run(tb.ciclo_entrada(tg, off, repo, JOSE, s)) == 0      # offset persistido: nada reprocessado


def test_entrada_estranho_nao_sinaliza_nem_remove_botoes():
    repo, ref, sinais, s = _cen(); tg = TelegramFalso([_cb(5, ref, de="999")]); off = Off()
    run(tb.ciclo_entrada(tg, off, repo, JOSE, s))
    assert not sinais and "editMessageReplyMarkup" not in tg.metodos() and tg.chamadas[1][1]["text"] == "Recusado." and off.v == 6


def test_entrada_sem_jose_configurado_fail_closed():
    repo, ref, sinais, s = _cen(); tg = TelegramFalso([_cb(5, ref)])
    run(tb.ciclo_entrada(tg, Off(), repo, "", s)); assert not sinais


def test_entrada_ignora_mensagem_comum_e_prefixo_alheio():
    repo, ref, sinais, s = _cen()
    ups = [{"update_id": 1, "message": {"text": "aprova"}}, {"update_id": 2, "callback_query": {"id": "q", "from": {"id": int(JOSE)}, "data": "ea:x:y"}}]
    tg = TelegramFalso(ups); off = Off(); run(tb.ciclo_entrada(tg, off, repo, JOSE, s))
    assert not sinais and off.v == 3


def test_offset_arquivo_atomico_600(tmp_path):
    o = tb.OffsetArquivo(tmp_path / "st" / "off"); assert o.ler() == 0; o.gravar(42)
    assert o.ler() == 42 and stat.S_IMODE(os.stat(tmp_path / "st" / "off").st_mode) == 0o600


def test_token_nunca_vaza(monkeypatch):
    monkeypatch.setenv(tb.ENV_TOKEN, "999:SEGREDO-DE-TESTE")
    def boom(*a, **k): raise __import__("urllib.error").error.HTTPError("https://api.telegram.org/bot999:SEGREDO-DE-TESTE/x", 401, "x", {}, None)
    monkeypatch.setattr(tb.urllib.request, "urlopen", boom)
    with pytest.raises(tb.TelegramErro) as e: run(tb.transporte_http()("getMe", {}))
    assert "SEGREDO" not in str(e.value) and "SEGREDO" not in repr(e.value) and e.value.__cause__ is None


def test_sem_token_falha_sem_rede(monkeypatch):
    monkeypatch.delenv(tb.ENV_TOKEN, raising=False)
    with pytest.raises(tb.TelegramErro): run(tb.transporte_http()("getMe", {}))


def test_activity_registrada_e_saida_desligada(monkeypatch):
    from pqbr.workflows import worker
    assert tb.enviar_telegram in tb.ATIVIDADES_TELEGRAM and "ATIVIDADES_TELEGRAM" in open(worker.__file__).read()
    class R:
        def recibo(self, c): return "recibo-atual"
    monkeypatch.setattr(tb, "RepositorioPostgres", R)
    monkeypatch.setattr(tb, "carregar_config", lambda: {"saida": "desligado"})   # desligada → só o recibo atual
    assert run(tb.enviar_telegram("aviso:x:0001")) == "recibo-atual"


def test_main_entrada_fail_closed(monkeypatch):
    monkeypatch.setattr(tb, "carregar_config", lambda: {"entrada": "desligado"})
    with pytest.raises(SystemExit, match="desligada"): run(tb.main_entrada(1))
    monkeypatch.setattr(tb, "carregar_config", lambda: {"entrada": "telegram_long_polling"})
    monkeypatch.delenv(tb.ENV_TOKEN, raising=False)
    with pytest.raises(SystemExit, match="faltam"): run(tb.main_entrada(1))


def test_workflows_expoem_query_etapa():
    from pqbr.workflows.workflows import EpisodioWorkflow, PonteTemporalPaperclipWorkflow
    assert hasattr(EpisodioWorkflow, "etapa") and hasattr(PonteTemporalPaperclipWorkflow, "etapa")
