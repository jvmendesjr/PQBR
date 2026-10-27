"""PublicacaoAgendadaWorkflow (F8-01 v2, t540/t541) — publicação AUTOMÁTICA, sem aprovação humana.
Decisão do José (25/10/2026): o gate (com o LOOP do Gemini) é a ÚNICA barreira; passou → entra na agenda
(11:40 e 18:35 America/Fortaleza, 1 vídeo por janela). O Telegram só AVISA (publicado/reprovado/erro/pausa),
nunca espera resposta. Fluxo: gate → reserva de horário (idempotente) → upload PRIVADO → espera a janela →
público → registro (temas_publicados + Drive) → aviso. Sinal `reverter` volta para privado (nunca apaga).
Botão de emergência (t541): flag global de pausa checada ANTES de cada ação externa (fail-closed: erro de leitura =
pausado); `ControlePublicacaoWorkflow` recebe /pausar, /retomar e /privar do Telegram (só from.id do José).
Simulação é o padrão (integrations.youtube.modo_real).
t124u: se o refresh de 7 dias voltar invalid_grant, o envio inteiro daquele vídeo passa ao Studio
pelo Camofox. O roteiro de cliques ainda é hipótese: grava o plano, avisa e não envia."""
from __future__ import annotations
import json, os
from datetime import datetime, timedelta, time
from pathlib import Path
from zoneinfo import ZoneInfo
from pydantic import BaseModel, ConfigDict, Field
from temporalio import activity, workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError, ApplicationError

with workflow.unsafe.imports_passed_through():
    from ..contratos.emergencia import ComandoEmergencia, EstadoControle

FILA_PUBLICACAO = "episodio-pqbr"
TZ = ZoneInfo("America/Fortaleza")
JANELAS = (time(11, 40), time(18, 35))
ANTECEDENCIA = timedelta(minutes=30)
ID_CONTROLE = "pqbr-controle-publicacao"
ESTADO_DIR = Path(os.environ.get("PQBR_PUBLICACAO_DIR", "/home/pc/.pqbr/publicacao"))
UMA = RetryPolicy(maximum_attempts=1)
TRES = RetryPolicy(initial_interval=timedelta(seconds=5), maximum_attempts=3)


class PedidoPublicacao(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    pasta_gate: str                                   # docs/pesquisas/<lote>/<slug>
    titulo: str = Field(min_length=5, max_length=100)
    descricao: str = Field(min_length=10, max_length=5000)
    tags: list[str] = Field(default_factory=list, max_length=15)
    tema_id: int | None = None
    janela_reversao_h: float = Field(default=168, ge=0, le=720)


# ---------- horário (função pura: testável e determinística) ----------
def proximo_horario(agora: datetime, ocupados: set[str]) -> datetime:
    a = agora.astimezone(TZ) + ANTECEDENCIA
    d = a.date()
    for _ in range(400):
        for j in JANELAS:
            h = datetime.combine(d, j, TZ)
            if h >= a and h.isoformat() not in ocupados: return h
        d += timedelta(days=1)
    raise ValueError("sem horário livre")


# ---------- registro (simulação: JSON local; real: Postgres 0020) ----------
def _arq(nome: str) -> Path:
    ESTADO_DIR.mkdir(parents=True, exist_ok=True); return ESTADO_DIR / nome


def _ler(nome: str, padrao):
    f = _arq(nome); return json.loads(f.read_text()) if f.exists() else padrao


def _gravar(nome: str, dados) -> None:
    f = _arq(nome); t = f.with_suffix(".tmp"); t.write_text(json.dumps(dados, ensure_ascii=False, indent=1, default=str)); t.replace(f)


def _real() -> bool:
    from ..integrations.youtube import modo_real
    return modo_real()


def ler_controle() -> EstadoControle:
    if _real():
        from ..storage.banco import conectar
        with conectar() as c:
            r = c.execute("select pausado, desde, autor_id, motivo from pqbr.controle_publicacao where id=1").fetchone()
        return EstadoControle(pausado=r[0], desde=r[1], autor_id=r[2], motivo=r[3])
    return EstadoControle(**_ler("controle.json", {"pausado": False, "motivo": "simulação"}))


def auditar(acao: str, alvo: str, motivo: str, autor: str, origem: str, video_id: str | None = None,
            update_id: int | None = None) -> bool:
    """Insere na auditoria; dedupe por update_id. Devolve False se já registrado."""
    agora = datetime.now(TZ)
    if _real():
        from ..storage.banco import conectar
        with conectar() as c:
            r = c.execute("insert into pqbr.auditoria_publicacao (acao, alvo, video_id, motivo, autor_id, origem, simulado, update_id)"
                          " values (%s,%s,%s,%s,%s,%s,false,%s) on conflict (update_id) do nothing returning id",
                          (acao, alvo, video_id, motivo, autor, origem, update_id)).fetchone(); c.commit()
        return r is not None
    log = _ler("auditoria.json", [])
    if update_id is not None and any(x.get("update_id") == update_id for x in log): return False
    log.append({"acao": acao, "alvo": alvo, "video_id": video_id, "motivo": motivo, "autor_id": autor, "origem": origem,
                "simulado": True, "update_id": update_id, "em": agora.isoformat()})
    _gravar("auditoria.json", log); return True


def _agenda() -> dict:
    return _ler("agenda.json", {})


def _salvar_item(codigo: str, item: dict) -> None:
    if _real():
        from ..storage.banco import conectar
        with conectar() as c:
            c.execute("insert into pqbr.agenda_publicacao (codigo, sha256, horario, estado, video_id, workflow_id, simulado)"
                      " values (%(codigo)s,%(sha256)s,%(horario)s,%(estado)s,%(video_id)s,%(workflow_id)s,false)"
                      " on conflict (codigo) do update set estado=excluded.estado, video_id=coalesce(excluded.video_id, pqbr.agenda_publicacao.video_id),"
                      " atualizado_em=now()", {**item, "codigo": codigo}); c.commit()
        return
    a = _agenda(); a[codigo] = {**a.get(codigo, {}), **item}; _gravar("agenda.json", a)


def _item(codigo: str) -> dict | None:
    if _real():
        from ..storage.banco import conectar
        with conectar() as c:
            r = c.execute("select sha256, horario, estado, video_id, workflow_id from pqbr.agenda_publicacao where codigo=%s", (codigo,)).fetchone()
        return dict(zip(("sha256", "horario", "estado", "video_id", "workflow_id"), (*r[:1], r[1].isoformat(), *r[2:]))) if r else None
    return _agenda().get(codigo)


# ---------- activities ----------
@activity.defn
async def pub_checar_pausa() -> bool:
    """Fail-closed: qualquer erro ao ler a flag = pausado."""
    try: return ler_controle().pausado
    except Exception: return True  # noqa: BLE001


@activity.defn
async def pub_gate(pasta: str) -> dict:
    from ..pipeline.gate_publicacao import avaliar_pasta
    return avaliar_pasta(pasta, adiados={"brigadeiro"}).model_dump()


@activity.defn
async def pub_reservar(codigo: str, sha: str, workflow_id: str) -> str:
    it = _item(codigo)
    if it:
        if it["sha256"] != sha: raise ApplicationError("mesmo código com outro arquivo", non_retryable=True)
        return it["horario"]
    ocup = {v["horario"] for v in _agenda().values()} if not _real() else set()
    if _real():
        from ..storage.banco import conectar
        with conectar() as c:
            ocup = {r[0].astimezone(TZ).isoformat() for r in c.execute("select horario from pqbr.agenda_publicacao").fetchall()}
    h = proximo_horario(datetime.now(TZ), ocup).isoformat()
    _salvar_item(codigo, {"sha256": sha, "horario": h, "estado": "reservado", "video_id": None, "workflow_id": workflow_id})
    return h


@activity.defn
async def pub_upload_privado(p: dict, codigo: str, video: str, sha: str) -> dict:
    from ..integrations import youtube as yt
    it = _item(codigo) or {}
    if it.get("estado") in ("enviado_privado", "publicado", "privado", "revertido"):
        return {"video_id": it.get("video_id"), "privacidade": "private", "idempotente": True, "simulado": not _real()}
    yt.conferir_hash(video, sha)
    from ..storage.banco import conectar
    if _real() and not yt.real_para(codigo):   # t69s317: escopo mínimo
        raise ApplicationError(f"{codigo} fora de PQBR_PUBLICACAO_REAL_CODIGOS", non_retryable=True)
    if _real() and not yt.credenciais_presentes():
        raise ApplicationError("credenciais OAuth do YouTube ausentes no worker (LACUNA)", non_retryable=True)
    if _real():
        with conectar() as c:
            if c.execute("select 1 from pqbr.temas_publicados where codigo=%s", (codigo,)).fetchone():
                raise ApplicationError("código já publicado (duplicata)", non_retryable=True)
    corpo = yt.montar_corpo(codigo, p["titulo"], p["descricao"], p.get("tags", []),
                            publish_at=datetime.fromisoformat(it["horario"]).astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ") if it.get("horario") else None)
    try:
        dup = yt.buscar_no_canal(codigo)
        if dup: raise ApplicationError(f"duplicata no canal: {dup}", non_retryable=True)
        r = yt.enviar_privado(video, corpo, codigo)
    except yt.RenovacaoOAuthFalhou:
        from ..integrations.studio_publicacao import planejar
        planejar(video, corpo, codigo)
        raise ApplicationError("refresh de 7 dias recusado; envio inteiro pelo Camofox; roteiro do Studio ainda não verificado",
                               type="renovacao_oauth", non_retryable=True)
    _salvar_item(codigo, {**it, "estado": "enviado_privado", "video_id": r.get("video_id")})
    return r


@activity.defn
async def pub_privacidade(codigo: str, privacidade: str, motivo: str, autor: str, origem: str) -> dict:
    from ..integrations import youtube as yt
    it = _item(codigo) or {}
    if _real() and not yt.real_para(codigo):
        raise ApplicationError(f"{codigo} fora de PQBR_PUBLICACAO_REAL_CODIGOS", non_retryable=True)
    try:
        r = yt.definir_privacidade(it.get("video_id"), privacidade)
    except yt.RenovacaoOAuthFalhou:
        from ..integrations.studio_publicacao import planejar_privacidade
        planejar_privacidade(codigo, it.get("video_id"), privacidade)
        raise ApplicationError("refresh de 7 dias recusado; privacidade pelo Camofox; roteiro do Studio ainda não verificado",
                               type="renovacao_oauth", non_retryable=True)
    estado = "publicado" if privacidade == "public" else ("revertido" if origem == "sinal" else "privado")
    _salvar_item(codigo, {**it, "estado": estado})
    auditar("publicar" if privacidade == "public" else ("reverter" if origem == "sinal" else "privar"),
            codigo, motivo, autor, origem, it.get("video_id"))
    return r


@activity.defn
async def pub_registrar(codigo: str, p: dict, video_id: str | None, gate: dict) -> dict:
    """Publicado: temas_publicados + publicacao.json na pasta do Drive. Simulação: só arquivo local."""
    reg = {"codigo": codigo, "video_id": video_id, "titulo": p["titulo"], "gate": gate, "em": datetime.now(TZ).isoformat()}
    if not _real():
        _gravar(f"registro-{codigo}.json", reg); return {"simulado": True}
    from ..storage.banco import conectar
    with conectar() as c:
        c.execute("select pqbr.publicar_tema(%s, %s, %s, %s)", (p.get("tema_id"), codigo, video_id, "public")); c.commit()
    g = json.loads((Path(p["pasta_gate"]) / "gate-pronto.json").read_text())
    if g.get("drive"):
        from ..integrations import drive
        f = _arq(f"registro-{codigo}.json"); f.write_text(json.dumps(reg, ensure_ascii=False, indent=1)); drive.enviar(str(f), g["drive"])
    return {"simulado": False}


@activity.defn
async def pub_avisar(chave: str, texto: str) -> str:
    """Só AVISO (classe aviso_operacional) pela ponte; nunca espera resposta. Melhor esforço."""
    if not _real():
        log = _ler("avisos.json", []); log.append({"chave": chave, "texto": texto}); _gravar("avisos.json", log); return "simulado"
    from .ponte_atividades import enfileirar_telegram
    from .telegram_bot import enviar_telegram
    from ..contratos.ponte_telegram import MensagemSaida
    if await enfileirar_telegram(MensagemSaida(chave=chave, classe="aviso_operacional", texto=texto[:3500])) == "desligado":
        return "desligado"
    return (await enviar_telegram(chave)).estado


@activity.defn
async def ctl_aplicar(cmd: dict) -> dict:
    """Comando de emergência: grava flag/auditoria e, em `privar`, volta os vídeos para privado. Nunca apaga."""
    from ..integrations import youtube as yt
    c = ComandoEmergencia(**cmd)
    if not auditar(c.acao, c.alvo or "*", c.motivo, c.autor_id, "telegram", update_id=c.update_id):
        return {"status": "duplicado"}
    if c.acao in ("pausar", "retomar"):
        estado = {"pausado": c.acao == "pausar", "desde": datetime.now(TZ).isoformat(), "autor_id": c.autor_id, "motivo": c.motivo}
        if _real():
            from ..storage.banco import conectar
            with conectar() as db:
                db.execute("update pqbr.controle_publicacao set pausado=%s, desde=now(), autor_id=%s, motivo=%s where id=1",
                           (estado["pausado"], c.autor_id, c.motivo)); db.commit()
        else:
            _gravar("controle.json", estado)
        return {"status": c.acao, "pausado": estado["pausado"]}
    alvos = [k for k, v in _agenda().items() if v.get("estado") in ("publicado", "enviado_privado")] if c.alvo == "todos" else [c.alvo]
    feitos = []
    for cod in alvos:
        it = _item(cod) or {}
        try:
            yt.definir_privacidade(it.get("video_id"), "private")
        except yt.RenovacaoOAuthFalhou:
            from ..integrations.studio_publicacao import planejar_privacidade
            planejar_privacidade(cod, it.get("video_id"), "private")
            return {"status": "renovacao_oauth", "alvos": feitos, "pendente": cod}
        _salvar_item(cod, {**it, "estado": "privado"}); feitos.append(cod)
    return {"status": "privado", "alvos": feitos}


ATIVIDADES_PUBLICACAO = [pub_checar_pausa, pub_gate, pub_reservar, pub_upload_privado, pub_privacidade,
                         pub_registrar, pub_avisar, ctl_aplicar]


@workflow.defn
class PublicacaoAgendadaWorkflow:
    def __init__(self) -> None:
        self._reverter: str | None = None
        self.etapa = "inicio"

    @workflow.signal
    def reverter(self, motivo: str) -> None:
        self._reverter = motivo or "sem motivo"

    @workflow.query
    def estado(self) -> dict:
        return {"etapa": self.etapa, "reverter": self._reverter}

    async def _aviso(self, cod: str, tipo: str, texto: str) -> None:
        try:
            await workflow.execute_activity(pub_avisar, args=[f"pub:{cod.lower()}:{tipo}:{workflow.info().run_id[:8]}", texto],
                                            start_to_close_timeout=timedelta(seconds=90), retry_policy=TRES)
        except ActivityError:
            workflow.logger.warning("aviso telegram falhou (melhor esforço)")

    async def _esperar_liberado(self) -> None:
        """Pausa geral: congela aqui até /retomar (checa a cada 5 min). Erro de leitura = pausado."""
        avisado = False
        while await workflow.execute_activity(pub_checar_pausa, start_to_close_timeout=timedelta(seconds=30), retry_policy=TRES):
            self.etapa = "pausado"
            if not avisado: avisado = True
            await workflow.sleep(timedelta(minutes=5))

    @workflow.run
    async def run(self, p: PedidoPublicacao) -> dict:
        o = dict(start_to_close_timeout=timedelta(minutes=5))
        self.etapa = "gate"
        g = await workflow.execute_activity(pub_gate, p.pasta_gate, retry_policy=TRES, **o)
        cod = g.get("codigo") or "sem-codigo"
        if not g["publicavel"]:
            await self._aviso(cod, "reprovado", f"PQBR {cod}: reprovado no gate ({', '.join(g['motivos'])}). Não publicado.")
            return {"etapa": "reprovado", "gate": g}
        try:
            h = await workflow.execute_activity(pub_reservar, args=[cod, g["sha256"], workflow.info().workflow_id], retry_policy=TRES, **o)
            await self._esperar_liberado(); self.etapa = "upload_privado"
            up = await workflow.execute_activity(pub_upload_privado, args=[p.model_dump(), cod, g["video"], g["sha256"]],
                                                 start_to_close_timeout=timedelta(minutes=30), retry_policy=UMA)
            self.etapa = "agendado"
            espera = datetime.fromisoformat(h) - workflow.now()
            if espera > timedelta(0):
                try: await workflow.wait_condition(lambda: self._reverter is not None, timeout=espera)
                except TimeoutError: pass                     # chegou a janela
            if self._reverter is not None:
                await workflow.execute_activity(pub_privacidade, args=[cod, "private", self._reverter, "sinal", "sinal"], retry_policy=TRES, **o)
                await self._aviso(cod, "revertido", f"PQBR {cod}: revertido antes de publicar ({self._reverter}). Segue privado.")
                return {"etapa": "revertido_antes", "video": up}
            await self._esperar_liberado(); self.etapa = "publicando"
            await self._aviso(cod, "logo",
                              f"PQBR {cod}: antes de tornar público, confira a silhueta do mapa do Brasil no logo "
                              "(branding/overlay/logo-corner-br.png, logo-sting.png e logo-bug.png). "
                              "A correção do desenho pode ficar para depois (t131u).")
            await workflow.execute_activity(pub_privacidade, args=[cod, "public", "janela " + h, "sistema", "sistema"], retry_policy=TRES, **o)
            await workflow.execute_activity(pub_registrar, args=[cod, p.model_dump(), up.get("video_id"), g], retry_policy=TRES, **o)
            await self._aviso(cod, "publicado", f"PQBR {cod} publicado ({h}): {p.titulo}" + (" [SIMULAÇÃO]" if up.get("simulado") else ""))
        except ActivityError as e:
            tipo = getattr(e.cause, "type", "") or ""
            if tipo == "renovacao_oauth":
                texto = (f"PQBR {cod}: refresh de 7 dias recusado. O envio inteiro passa ao Studio pelo Camofox. "
                         "O roteiro de cliques ainda não foi verificado, e nada foi enviado.")
            else:
                texto = f"PQBR {cod}: erro na publicação na etapa {self.etapa} ({type(e.cause).__name__}). Nada apagado."
            await self._aviso(cod, "erro", texto)
            raise
        self.etapa = "publicado"
        if p.janela_reversao_h:
            try:
                await workflow.wait_condition(lambda: self._reverter is not None, timeout=timedelta(hours=p.janela_reversao_h))
            except TimeoutError:
                return {"etapa": "publicado", "horario": h, "video": up}
            await workflow.execute_activity(pub_privacidade, args=[cod, "private", self._reverter, "sinal", "sinal"], retry_policy=TRES, **o)
            await self._aviso(cod, "revertido", f"PQBR {cod}: voltou para privado ({self._reverter}). Nada apagado.")
            return {"etapa": "revertido", "horario": h, "video": up}
        return {"etapa": "publicado", "horario": h, "video": up}


@workflow.defn
class ControlePublicacaoWorkflow:
    """Singleton (id pqbr-controle-publicacao). Recebe comandos de emergência já validados pela entrada do Telegram."""
    def __init__(self) -> None:
        self._fila: list[dict] = []
        self.ultimos: list[dict] = []

    @workflow.signal
    def comando(self, cmd: dict) -> None:
        self._fila.append(cmd)

    @workflow.query
    def historico(self) -> list[dict]:
        return self.ultimos[-20:]

    @workflow.run
    async def run(self) -> None:
        n = 0
        while True:
            await workflow.wait_condition(lambda: bool(self._fila))
            cmd = self._fila.pop(0)
            r = await workflow.execute_activity(ctl_aplicar, cmd, start_to_close_timeout=timedelta(minutes=10), retry_policy=TRES)
            self.ultimos.append({"acao": cmd["acao"], "alvo": cmd.get("alvo"), **r}); n += 1
            try:
                await workflow.execute_activity(pub_avisar, args=[f"ctl:{cmd['update_id']}", f"PQBR emergência: {cmd['acao']} {cmd.get('alvo') or ''} → {r.get('status')}"],
                                                start_to_close_timeout=timedelta(seconds=90), retry_policy=TRES)
            except ActivityError:
                pass
            if n >= 500 and not self._fila:
                workflow.continue_as_new()
