"""Fila `notebooklm-pqbr` (concorrência 1): NotebookLM isolado da PQBR (venv 0.8.4, NOTEBOOKLM_HOME próprio, perfil pqbr).
Regras (ARQUITETURA §NotebookLM, AGENTES Roteirista): caderno **efêmero por episódio** ("Short - <slug>"), nunca o mestre;
fonte antes de gerar; nunca `ask --new`; em timeout de vídeo, listar artefatos e não regerar; contador diário
(500 chats, 20 vídeos; Pro) + `usage --json` (>80% numa janela = recusa e espaça). Só comandos fechados abaixo."""
from __future__ import annotations
import asyncio, fcntl, json, os, re, subprocess, time
from datetime import date, timedelta
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field
from temporalio import activity, workflow
from temporalio.common import RetryPolicy

FILA_NOTEBOOKLM = "notebooklm-pqbr"
HOME = Path(os.environ.get("PQBR_NOTEBOOKLM_HOME", "/home/pc/.pqbr/notebooklm"))
CLI = str(HOME / "venv/bin/notebooklm")
PERFIL = "pqbr"
LIMITES = {"chat": int(os.environ.get("PQBR_NLM_CHATS_DIA", "500")), "video": int(os.environ.get("PQBR_NLM_VIDEOS_DIA", "20"))}
TETO_JANELA = 80.0
MESTRES_PROIBIDOS = {"88246689", "c35d7b24-5d4f-4eee-afc4-7a0eadc860bf"}
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,60}$")


class PedidoNotebookLM(BaseModel):
    tipo: Literal["pesquisa", "short"]
    slug: str = Field(pattern=SLUG.pattern)
    fonte: str = Field(min_length=20, max_length=200_000)   # roteiro/briefing; vira a fonte do caderno
    pergunta: str | None = Field(default=None, max_length=4000)  # pesquisa
    solicitante: str = "kit"


class ResultadoNotebookLM(BaseModel):
    ok: bool
    tipo: str
    caderno: str | None = None
    resposta: str | None = None
    artefato: str | None = None
    estado_artefato: str | None = None
    motivo: str | None = None
    uso_dia: dict = {}


class SemSaldo(Exception):
    pass


def _cli(*args: str, timeout: int = 300) -> str:
    env = {**os.environ, "NOTEBOOKLM_HOME": str(HOME)}
    r = subprocess.run([CLI, "-p", PERFIL, "--quiet", *args], capture_output=True, text=True, timeout=timeout, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"notebooklm {args[0]} rc={r.returncode}: {(r.stderr or r.stdout)[-400:]}")
    return r.stdout


def _json(s: str):
    s = s.strip()
    return json.loads(s[s.find("{") if s.find("{") >= 0 and (s.find("[") < 0 or s.find("{") < s.find("[")) else s.find("["):])


def _ids(o, chave="id"):
    if isinstance(o, dict):
        if isinstance(o.get(chave), str): yield o
        for v in o.values(): yield from _ids(v, chave)
    elif isinstance(o, list):
        for v in o: yield from _ids(v, chave)


# ---- contador diário (arquivo com lock; uma linha por dia) ----
def _contador(tipo: str | None = None) -> dict:
    d = HOME / "uso"; d.mkdir(parents=True, exist_ok=True)
    f = d / f"{date.today().isoformat()}.json"
    with open(f, "a+") as h:
        fcntl.flock(h, fcntl.LOCK_EX); h.seek(0)
        c = json.loads(h.read() or "{}")
        if tipo:
            if c.get(tipo, 0) >= LIMITES[tipo]:
                raise SemSaldo(f"limite diário de {tipo} atingido ({LIMITES[tipo]})")
            c[tipo] = c.get(tipo, 0) + 1
            h.seek(0); h.truncate(); h.write(json.dumps(c))
        return c


@activity.defn
async def nlm_checar_saldo(tipo: str) -> dict:
    c = _contador()
    if c.get(tipo, 0) >= LIMITES[tipo]:
        raise SemSaldo(f"limite diário de {tipo} atingido ({LIMITES[tipo]})")
    u = _json(await asyncio.to_thread(_cli, "usage", "--json", timeout=60))
    if u.get("is_exhausted"): raise SemSaldo("conta sem saldo (usage)")
    for w in u.get("windows", []):
        if float(w.get("used_percent", 0)) > TETO_JANELA:
            raise SemSaldo(f"janela {w.get('kind')} acima de {TETO_JANELA}% (reset {w.get('resets_at')})")
    return {"dia": c, "janelas": {w["kind"]: round(w["used_percent"], 1) for w in u.get("windows", [])}}


@activity.defn
async def nlm_caderno(slug: str) -> str:
    titulo = f"Short - {slug}"
    lst = _json(await asyncio.to_thread(_cli, "list", "--json", timeout=120))
    for n in _ids(lst):
        if n.get("title") == titulo and n["id"] not in MESTRES_PROIBIDOS:
            return n["id"]
    novo = _json(await asyncio.to_thread(_cli, "create", titulo, "--json", timeout=120))
    return next(_ids(novo))["id"]


@activity.defn
async def nlm_fonte(caderno: str, slug: str, texto: str) -> str:
    if caderno in MESTRES_PROIBIDOS: raise RuntimeError("caderno mestre proibido")
    tmp = HOME / "tmp"; tmp.mkdir(exist_ok=True)
    f = tmp / f"{slug}.md"; f.write_text(texto, encoding="utf-8")
    try:
        src = next(_ids(_json(await asyncio.to_thread(_cli, "source", "add", "-n", caderno, "--type", "file",
                                                     "--title", f"{slug}.md", str(f), "--json", timeout=300))))["id"]
        await asyncio.to_thread(_cli, "source", "wait", "-n", caderno, src, "--timeout", "300", timeout=330)
        return src
    finally:
        f.unlink(missing_ok=True)


@activity.defn
async def nlm_perguntar(caderno: str, pergunta: str) -> str:
    _contador("chat")   # conta antes: chamada iniciada consome
    out = await asyncio.to_thread(_cli, "ask", "-n", caderno, pergunta, "--json", timeout=600)  # nunca --new
    try:
        j = _json(out); return str(j.get("answer") or j.get("text") or j)[:20000]
    except Exception:
        return out[:20000]


@activity.defn
async def nlm_artefatos_video(caderno: str) -> list[dict]:
    j = _json(await asyncio.to_thread(_cli, "artifact", "list", "-n", caderno, "--type", "video", "--json", timeout=120))
    return [{"id": a["id"], "status": str(a.get("status", ""))} for a in _ids(j)]


@activity.defn
async def nlm_gerar_short(caderno: str) -> str:
    _contador("video")
    out = await asyncio.to_thread(_cli, "generate", "video", "-n", caderno, "--format", "short", "--language", "pt_BR",
                                  "--no-wait", "--json", timeout=300)
    a = next(_ids(_json(out)), None)
    return a["id"] if a else ""


@workflow.defn
class NotebookLMWorkflow:
    """Um pedido por vez (fila concorrência 1). Pesquisa: caderno efêmero + fonte + ask. Short: caderno + fonte +
    generate --format short (não-bloqueante) + acompanha por artifact list; nunca regera se já há vídeo."""
    @workflow.run
    async def run(self, p: PedidoNotebookLM) -> ResultadoNotebookLM:
        curto = dict(start_to_close_timeout=timedelta(minutes=12),
                     retry_policy=RetryPolicy(maximum_attempts=3, non_retryable_error_types=["SemSaldo"]))
        tipo = "chat" if p.tipo == "pesquisa" else "video"
        try:
            uso = await workflow.execute_activity(nlm_checar_saldo, tipo, **curto)
        except Exception as e:
            return ResultadoNotebookLM(ok=False, tipo=p.tipo, motivo=f"sem saldo: {e}")
        nb = await workflow.execute_activity(nlm_caderno, p.slug, **curto)
        await workflow.execute_activity(nlm_fonte, args=[nb, p.slug, p.fonte], **curto)
        if p.tipo == "pesquisa":
            r = await workflow.execute_activity(nlm_perguntar, args=[nb, p.pergunta or "Resuma a origem e o significado."],
                                                start_to_close_timeout=timedelta(minutes=12),
                                                retry_policy=RetryPolicy(maximum_attempts=1))
            return ResultadoNotebookLM(ok=True, tipo=p.tipo, caderno=nb, resposta=r, uso_dia=uso)
        vids = await workflow.execute_activity(nlm_artefatos_video, nb, **curto)
        art = vids[0]["id"] if vids else await workflow.execute_activity(
            nlm_gerar_short, nb, start_to_close_timeout=timedelta(minutes=6), retry_policy=RetryPolicy(maximum_attempts=1))
        estado = ""
        for _ in range(60):   # até ~60 min
            vids = await workflow.execute_activity(nlm_artefatos_video, nb, **curto)
            estado = next((v["status"] for v in vids if v["id"] == art), estado)
            if re.search(r"complet|fail|error", estado, re.I): break
            await workflow.sleep(60)
        return ResultadoNotebookLM(ok=bool(re.search("complet", estado, re.I)), tipo=p.tipo, caderno=nb, artefato=art,
                                   estado_artefato=estado, uso_dia=uso)


ATIVIDADES = [nlm_checar_saldo, nlm_caderno, nlm_fonte, nlm_perguntar, nlm_artefatos_video, nlm_gerar_short]
