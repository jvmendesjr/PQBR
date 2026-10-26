"""t540/t541: LOOP Gemini (contrato), gate, adaptador YouTube (simulação), agenda, emergência e workflow (time-skipping)."""
import asyncio, json, uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pytest
from pqbr.workflows import auditor_loop as al
from pqbr.pipeline import gate_publicacao as gp
from pqbr.integrations import youtube as yt
from pqbr.contratos.emergencia import interpretar, ComandoEmergencia
from pqbr.workflows import publicacao as pub

TZ = ZoneInfo("America/Fortaleza")
OK = '{"ultima_continua_na_primeira":"sim","fala_final_cortada_no_meio":"nao"}'
RUIM = '{"ultima_continua_na_primeira":"nao","fala_final_cortada_no_meio":"nao"}'
VIS = {"veredito": "aprova", "motivos": [], "conversas": [], "bruto": {"metricas": {"imagem_corresponde_a_fala": 1.0, "corresponde_ao_titulo": 1.0}}}


def test_loop_aprova_e_contrato_fechado():
    r = al.combinar("PQBR-EP1002", VIS, [OK, OK], [])
    assert r.veredito == "aprova" and r.publicavel and r.versao == "1.0.0"
    with pytest.raises(Exception): al.ResultadoLoopGemini(codigo="X", imagem_fala="aprova", capa_titulo="aprova", loop_texto="aprova", veredito="aprova")


def test_loop_divergente_e_texto_nao_avaliado_fail_closed():
    assert al.combinar("PQBR-EP1002", VIS, [OK, RUIM], []).veredito == "terceira_rodada"
    sem = {**VIS, "bruto": {"metricas": {"imagem_corresponde_a_fala": None, "corresponde_ao_titulo": 1.0}}}
    assert al.combinar("PQBR-EP1002", sem, [OK, OK], []).imagem_fala == "terceira_rodada"
    assert al.combinar("PQBR-EP1002", VIS, [RUIM, RUIM], []).veredito == "reprova"


def test_loop_ressalva_de_metrica_nao_reprova():
    v = {**VIS, "veredito": "aprova_com_ressalva", "motivos": ["S02:imagem_corresponde_a_fala", "CAPA:corresponde_ao_titulo"]}
    r = al.combinar("PQBR-EP1002", v, [OK, OK], [])
    assert (r.imagem_fala, r.capa_titulo, r.veredito) == ("aprova_com_ressalva",) * 3
    assert al.combinar("PQBR-EP1002", {**VIS, "veredito": "reprova"}, [OK, OK], []).veredito == "reprova"


def _gate(**k):
    g = {"codigo": "PQBR-EP1003", "tema": "cafe", "pronto": "a.mp4", "sha256": "a" * 64,
         "gate": {"A1_A3_tecnico": "PASS", "B1_B10_editorial": "PASS (x)"}, "publicado": False}
    g.update(k); return g


def test_gate():
    loop = {"veredito": "aprova_com_ressalva", "imagem_fala": "aprova_com_ressalva", "capa_titulo": "aprova", "loop_texto": "aprova"}
    d = gp.avaliar(_gate(), loop, "a" * 64); assert d.publicavel and d.ressalvas == ["imagem_fala"]
    assert gp.avaliar(_gate(), None, "a" * 64).motivos == ["loop_gemini_ausente"]
    assert "hash_diverge" in gp.avaliar(_gate(), loop, "b" * 64).motivos
    assert "tema_adiado" in gp.avaliar(_gate(tema="brigadeiro"), loop, "a" * 64, {"brigadeiro"}).motivos
    assert not gp.avaliar(_gate(), {**loop, "veredito": "terceira_rodada"}, "a" * 64).publicavel


def test_youtube_corpo_e_simulacao(tmp_path, monkeypatch):
    monkeypatch.setattr(yt, "SIM_DIR", tmp_path); monkeypatch.delenv("PQBR_PUBLICACAO_REAL", raising=False)
    c = yt.montar_corpo("PQBR-EP1003", "Título bom", "desc", ["#shorts"])
    assert c["status"]["privacyStatus"] == "private" and c["status"]["containsSyntheticMedia"] is True
    assert "PQBR-EP1003" in c["snippet"]["description"] and "PQBR-EP1003" in c["snippet"]["tags"]
    f = tmp_path / "v.mp4"; f.write_bytes(b"x")
    yt.conferir_hash(str(f), yt.sha256(str(f)))
    with pytest.raises(ValueError): yt.conferir_hash(str(f), "0" * 64)
    r = yt.enviar_privado(str(f), c, "PQBR-EP1003"); assert r["simulado"] and r["video_id"] is None
    monkeypatch.setenv("YOUTUBE_DRY_RUN", "false"); assert not yt.modo_real()   # precisa das DUAS chaves
    assert yt.definir_privacidade(None, "private")["simulado"]


def test_agenda_1140_1835():
    a = datetime(2026, 10, 26, 9, 0, tzinfo=TZ)
    h1 = pub.proximo_horario(a, set()); assert (h1.hour, h1.minute) == (11, 40)
    h2 = pub.proximo_horario(a, {h1.isoformat()}); assert (h2.hour, h2.minute) == (18, 35)
    h3 = pub.proximo_horario(a, {h1.isoformat(), h2.isoformat()}); assert h3.day == 27 and h3.hour == 11
    assert pub.proximo_horario(datetime(2026, 10, 26, 11, 20, tzinfo=TZ), set()).hour == 18   # < 30 min de antecedência


def test_comandos_emergencia():
    c = interpretar("/privar pqbr-ep1003 gestor pediu", 7, "123"); assert (c.acao, c.alvo, c.motivo) == ("privar", "PQBR-EP1003", "gestor pediu")
    assert interpretar("/privar todos crise", 8, "123").alvo == "todos"
    assert interpretar("/pausar@ottopulsar_bot revisão", 9, "123").acao == "pausar"
    for t in ("/privar", "/privar xyz motivo", "oi", "/apagar tudo"):
        with pytest.raises(ValueError): interpretar(t, 1, "123")
    with pytest.raises(ValueError): ComandoEmergencia(update_id=1, autor_id="1", acao="pausar", alvo="todos", motivo="abc")


def test_entrada_aceita_so_jose():
    from pqbr.workflows import telegram_bot as tb
    sinais = []
    async def comandar(c): sinais.append(c)
    async def chamar(m, p): return True
    msg = {"from": {"id": 999}, "text": "/pausar teste", "chat": {"id": 1}}
    assert asyncio.run(tb.tratar_comando(chamar, 1, msg, "123", comandar)) == "remetente_recusado" and not sinais
    msg["from"]["id"] = 123
    assert asyncio.run(tb.tratar_comando(chamar, 2, msg, "123", comandar)) == "sinalizado" and sinais[0]["acao"] == "pausar"


def test_pausa_fail_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(pub, "ESTADO_DIR", tmp_path)
    assert asyncio.run(pub.pub_checar_pausa()) is False
    (tmp_path / "controle.json").write_text("{quebrado")
    assert asyncio.run(pub.pub_checar_pausa()) is True


def test_privar_audita_e_dedup(tmp_path, monkeypatch):
    monkeypatch.setattr(pub, "ESTADO_DIR", tmp_path)
    pub._salvar_item("PQBR-EP1003", {"sha256": "a" * 64, "horario": "x", "estado": "publicado", "video_id": None, "workflow_id": "w"})
    cmd = interpretar("/privar todos teste", 50, "123").model_dump(mode="json")
    assert asyncio.run(pub.ctl_aplicar(cmd))["alvos"] == ["PQBR-EP1003"]
    assert asyncio.run(pub.ctl_aplicar(cmd))["status"] == "duplicado"
    aud = json.loads((tmp_path / "auditoria.json").read_text()); assert aud[0]["autor_id"] == "123" and aud[0]["motivo"] == "teste"
    assert pub._item("PQBR-EP1003")["estado"] == "privado"


@pytest.mark.parametrize("reverter", [False, True])
def test_workflow_ponta_a_ponta_simulado(tmp_path, monkeypatch, reverter):
    from temporalio.testing import WorkflowEnvironment
    from temporalio.worker import Worker
    from temporalio import activity
    monkeypatch.setattr(pub, "ESTADO_DIR", tmp_path)
    @activity.defn(name="pub_gate")
    async def gate_falso(p: str) -> dict:
        return {"codigo": "PQBR-EP1003", "publicavel": True, "motivos": [], "ressalvas": [], "video": "v.mp4", "sha256": "a" * 64}
    @activity.defn(name="pub_upload_privado")
    async def up_falso(p: dict, c: str, v: str, s: str) -> dict:
        return {"video_id": None, "simulado": True, "privacidade": "private"}
    async def go():
        async with await WorkflowEnvironment.start_time_skipping() as env:
            acts = [a for a in pub.ATIVIDADES_PUBLICACAO if a not in (pub.pub_gate, pub.pub_upload_privado)] + [gate_falso, up_falso]
            async with Worker(env.client, task_queue="t", workflows=[pub.PublicacaoAgendadaWorkflow], activities=acts):
                h = await env.client.start_workflow(pub.PublicacaoAgendadaWorkflow.run, pub.PedidoPublicacao(
                    pasta_gate="x", titulo="Título bom", descricao="descrição longa", janela_reversao_h=1), id=str(uuid.uuid4()), task_queue="t")
                if reverter:
                    await env.sleep(timedelta(minutes=1)); await h.signal(pub.PublicacaoAgendadaWorkflow.reverter, "teste")
                return await h.result()
    r = asyncio.run(go())
    assert r["etapa"] == ("revertido_antes" if reverter else "publicado")
    assert pub._item("PQBR-EP1003")["estado"] == ("revertido" if reverter else "publicado")
