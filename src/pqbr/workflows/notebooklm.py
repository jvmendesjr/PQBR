"""Fila `notebooklm-pqbr` (concorrência 1): NotebookLM isolado da PQBR (venv 0.8.4, NOTEBOOKLM_HOME próprio, perfil pqbr).
Regras (ARQUITETURA §NotebookLM, AGENTES Roteirista): caderno **efêmero por episódio** ("Short - <slug>"), nunca o mestre;
fonte antes de gerar; nunca `ask --new`; em timeout de vídeo, listar artefatos e não regerar; contador diário
(500 chats, 20 vídeos; Pro) + `usage --json` (>80% numa janela = recusa e espaça). Só comandos fechados abaixo."""
from __future__ import annotations
import asyncio, fcntl, json, os, re, subprocess, time
from datetime import date, timedelta
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from temporalio import activity, workflow
from temporalio.common import RetryPolicy

FILA_NOTEBOOKLM = "notebooklm-pqbr"
HOME = Path(os.environ.get("PQBR_NOTEBOOKLM_HOME", "/home/pc/.pqbr/notebooklm"))
TRAB_NLM = os.environ.get("PQBR_TRABALHO", "/home/pc/.pqbr/episodios")   # t464: capa do NotebookLM no mesmo diretório do episódio
from .criativo import PROMPT_ROTEIRO, PROMPT_SEO, PROMPT_CAPA
CLI = str(HOME / "venv/bin/notebooklm")
PERFIL = "pqbr"
PERSONA = Path(os.environ.get("PQBR_NLM_PERSONA", "/home/pc/Workspace/PQBR/templates/notebooklm/persona-pqbr.txt"))
LIMITES = {"chat": int(os.environ.get("PQBR_NLM_CHATS_DIA", "500")), "video": int(os.environ.get("PQBR_NLM_VIDEOS_DIA", "20"))}
TETO_JANELA = 80.0
MESTRES_PROIBIDOS = {"88246689", "c35d7b24-5d4f-4eee-afc4-7a0eadc860bf"}
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,60}$")
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
CODIGO = re.compile(r"^PQBR-EP[0-9]{4,}$")
FILA_REGISTRO = "episodio-pqbr"   # atividades de banco/Drive do ciclo do caderno (workflows/pacote.py)


def titulo_caderno(codigo: str, slug: str) -> str:
    """Rótulo do caderno do episódio. A identidade é o id registrado em pqbr.cadernos_episodio (t459)."""
    if not CODIGO.match(codigo): raise ValueError("código de episódio inválido")
    return f"Short - {codigo} - {slug}"


class UsoDia(BaseModel):
    """Saída de nlm_checar_saldo: contador local do dia + % das janelas do `notebooklm usage` (t437)."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    dia: dict[Literal["chat", "video"], int] = Field(default_factory=dict)
    janelas: dict[str, float] = Field(default_factory=dict)


class PedidoNotebookLM(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    tipo: Literal["pesquisa", "roteiro", "seo", "contexto", "short"]
    slug: str = Field(pattern=SLUG.pattern)
    fonte: str = Field(min_length=20, max_length=200_000)   # roteiro/briefing; vira a fonte do caderno
    pergunta: str | None = Field(default=None, max_length=4000)  # pesquisa
    perguntas: list[str] | None = Field(default=None, max_length=3)   # t430: até 3 chats no mesmo caderno
    pesquisa_web: list[str] | None = Field(default=None, max_length=3)  # t430: add-research --mode fast antes dos chats
    solicitante: str = "kit"
    episodio: str | None = Field(default=None, pattern=CODIGO.pattern)   # t459: caderno casado pelo código do episódio
    caderno_registrado: str | None = Field(default=None, pattern=UUID.pattern)
    pacote_fonte: str | None = None                                      # arquivo do pacote canônico (workflows/pacote.py)
    pacote_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    steering: str | None = Field(default=None, max_length=4000)          # t462: direcionamento do Short (bloco 2D + reforços)
    roteirizar: bool = False          # t464: o NotebookLM escreve roteiro/SEO/capa no caderno; `fonte` = briefing do tema
    tema: str | None = Field(default=None, max_length=300)


class ResultadoNotebookLM(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    ok: bool
    tipo: str
    caderno: str | None = None
    resposta: str | None = None
    artefato: str | None = None
    estado_artefato: str | None = None
    motivo: str | None = None
    uso_dia: UsoDia = Field(default_factory=UsoDia)
    criativo: dict = Field(default_factory=dict)   # t464: roteiro, compliance, seo, capa (com a origem de cada um)


class SemSaldo(Exception):
    pass


_AUTH_ERR = ("authentication expired", "re-authenticate", "notebooklm login",
             "csrf token not found")   # 12/10: rebrand Gemini Notebook (notebook.google.com) → sessão velha cai aqui; sync do Camofox resolve


SYNC_SESSAO = os.environ.get("NOTEBOOKLM_REFRESH_CMD", "/home/pc/.pqbr/camofox/nlm-sync.sh")


def _sincronizar_sessao() -> bool:
    """Copia a sessão viva do Camofox (única fonte e único renovador, José 12/10) para o perfil pqbr.
    Sem `auth refresh`, sem re-login headless, sem perfil Chromium próprio. Playbook nlm-auth."""
    try:
        return subprocess.run([SYNC_SESSAO], capture_output=True, timeout=60).returncode == 0
    except Exception:  # noqa: BLE001
        return False


def _cli(*args: str, timeout: int = 300) -> str:
    env = {**os.environ, "NOTEBOOKLM_HOME": str(HOME)}
    r = subprocess.run([CLI, "-p", PERFIL, "--quiet", *args], capture_output=True, text=True, timeout=timeout, env=env)
    if r.returncode != 0 and any(t in (r.stderr or r.stdout or "").lower() for t in _AUTH_ERR) and _sincronizar_sessao():
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
async def nlm_caderno(slug: str, codigo: str | None = None, existente: str | None = None) -> str:
    """Episódio (t459): casa pelo id registrado para o código (pqbr.cadernos_episodio); se não houver, cria
    "Short - <código> - <slug>" (o workflow registra o id). Nunca casa episódio por título.
    Sem código (pesquisa/kit): caderno efêmero "Short - <slug>" como antes."""
    lst = list(_ids(_json(await asyncio.to_thread(_cli, "list", "--json", timeout=120))))
    if codigo:
        if existente:
            if not UUID.match(existente) or existente in MESTRES_PROIBIDOS: raise RuntimeError("caderno registrado inválido")
            if any(n["id"] == existente for n in lst): return existente
            raise RuntimeError(f"caderno registrado {existente} sumiu do NotebookLM (revisar antes de recriar)")
        titulo = titulo_caderno(codigo, slug)
    else:
        titulo = f"Short - {slug}"
        for n in lst:
            if n.get("title") == titulo and n["id"] not in MESTRES_PROIBIDOS:
                return n["id"]
    novo = next(_ids(_json(await asyncio.to_thread(_cli, "create", titulo, "--json", timeout=120))))["id"]
    if novo in MESTRES_PROIBIDOS: raise RuntimeError("caderno mestre proibido")
    return novo


@activity.defn
async def nlm_persona(caderno: str) -> str:
    """Regra canônica (t427): todo caderno recebe o preset de persona ANTES de qualquer atividade."""
    if caderno in MESTRES_PROIBIDOS: raise RuntimeError("caderno mestre proibido")
    texto = PERSONA.read_text(encoding="utf-8").strip()[:10000]
    await asyncio.to_thread(_cli, "configure", "-n", caderno, "--persona", texto, timeout=120)
    return "persona ok"


@activity.defn
async def nlm_baixar_video(caderno: str, artefato: str, destino: str) -> dict:
    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(_cli, "download", "video", destino, "-n", caderno, "-a", artefato, timeout=900)
    f = Path(destino)
    if not f.is_file() or f.stat().st_size < 10_000: raise RuntimeError("download vazio")
    return {"arquivo": str(f), "bytes": f.stat().st_size}


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
async def nlm_pesquisa_web(caderno: str, consulta: str) -> str:
    if caderno in MESTRES_PROIBIDOS: raise RuntimeError("caderno mestre proibido")
    out = await asyncio.to_thread(_cli, "source", "add-research", "-n", caderno, "--mode", "fast", "--import-all",
                                  "--timeout", "600", consulta[:1500], timeout=1300)
    return out[-500:]


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


REFORCO_SHORT = (   # José 16:08: mais movimento; personagem consistente QUANDO aparece (não precisa estar em todas)
    "Movimento cinematográfico do início ao fim: câmera sempre em movimento (zoom in e zoom out lentos, pan lateral, travelling), "
    "cortes dinâmicos a cada 2 a 3 segundos e variação de planos (close, plano médio, plano geral). "
    "O personagem principal não precisa aparecer em todas as cenas; sempre que aparecer, mantenha-o consistente: mesmo rosto, cabelo, "
    "roupa e cores. Sem nenhum texto escrito dentro da imagem (sem letreiros, placas, rótulos ou balões).")


def steering_short(bloco: str = "") -> str:
    """t462 (José 13:30): steering do Short = bloco visual 2D do roteiro + reforços fixos (sem texto na imagem; mesmo personagem)."""
    b = " ".join((bloco or "").split())[:3000]
    return (b + " " if b else "Cartum 2D plano, cores chapadas, 1 personagem, fundo minimalista. ") + REFORCO_SHORT


@activity.defn
async def nlm_gerar_short(caderno: str, steering: str = "") -> str:
    _contador("video")
    extra = [steering_short(steering)]
    out = await asyncio.to_thread(_cli, "generate", "video", "-n", caderno, "--format", "short", "--language", "pt_BR",
                                  "--no-wait", "--json", *extra, timeout=300)
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
        tipo = "video" if p.tipo == "short" else "chat"
        try:
            uso = await workflow.execute_activity(nlm_checar_saldo, tipo, **curto)
        except Exception as e:
            return ResultadoNotebookLM(ok=False, tipo=p.tipo, motivo=f"sem saldo: {e}")
        nb = await workflow.execute_activity(nlm_caderno, args=[p.slug, p.episodio, p.caderno_registrado], **curto)
        if p.episodio and not p.caderno_registrado:   # t459: registra o id do caderno para o código do episódio
            await workflow.execute_activity("registro_caderno", args=[nb, p.episodio, p.slug, p.pacote_hash],
                                            task_queue=FILA_REGISTRO, **curto)
        await workflow.execute_activity(nlm_persona, nb, **curto)   # persona antes de tudo (t427)
        if p.pacote_fonte and p.pacote_hash:   # t459: pacote canônico injetado (sem caderno mestre)
            pid = await workflow.execute_activity("nlm_injetar_pacote", args=[nb, p.pacote_fonte, p.pacote_hash], **curto)
            if p.episodio:
                await workflow.execute_activity("registro_fonte", args=[nb, pid, "pacote", f"PQBR pacote {p.pacote_hash[:12]}"],
                                                task_queue=FILA_REGISTRO, **curto)
        fid = await workflow.execute_activity(nlm_fonte, args=[nb, p.slug, p.fonte], **curto)
        if p.episodio:   # t459c: toda fonte do episódio registrada por id
            await workflow.execute_activity("registro_fonte", args=[nb, fid, "roteiro", f"{p.slug}.md"], task_queue=FILA_REGISTRO, **curto)
        if p.tipo != "short" and (p.pesquisa_web or p.perguntas):
            for q in (p.pesquisa_web or []):
                await workflow.execute_activity(nlm_pesquisa_web, args=[nb, q], start_to_close_timeout=timedelta(minutes=25),
                                                retry_policy=RetryPolicy(maximum_attempts=1))
            rs = []
            for q in (p.perguntas or [p.pergunta or "Resuma."])[:3]:
                rs.append(await workflow.execute_activity(nlm_perguntar, args=[nb, q], start_to_close_timeout=timedelta(minutes=12),
                                                          retry_policy=RetryPolicy(maximum_attempts=1)))
            return ResultadoNotebookLM(ok=True, tipo=p.tipo, caderno=nb, resposta="\n\n=====\n\n".join(rs), uso_dia=uso)
        if p.tipo != "short":
            r = await workflow.execute_activity(nlm_perguntar, args=[nb, p.pergunta or "Resuma a origem e o significado."],
                                                start_to_close_timeout=timedelta(minutes=12),
                                                retry_policy=RetryPolicy(maximum_attempts=1))
            return ResultadoNotebookLM(ok=True, tipo=p.tipo, caderno=nb, resposta=r, uso_dia=uso)
        cri: dict = {}
        if p.roteirizar:   # t464: NotebookLM escreve o roteiro no caderno; modelos só validam
            r = await self._roteirizar(p, nb, curto)
            if isinstance(r, ResultadoNotebookLM): return r
            cri = r
        if p.episodio:   # t459c: sem contaminação cruzada — só pacote + fontes registradas do próprio episódio
            ok_ids = await workflow.execute_activity("registro_fontes_listar", nb, task_queue=FILA_REGISTRO, **curto)
            try:
                await workflow.execute_activity("nlm_conferir_fontes", args=[nb, ok_ids], start_to_close_timeout=timedelta(minutes=5),
                                                retry_policy=RetryPolicy(maximum_attempts=2, non_retryable_error_types=["ContaminacaoCaderno"]))
            except Exception as e:
                return ResultadoNotebookLM(ok=False, tipo=p.tipo, caderno=nb, motivo=f"bloqueado: {e}")
        vids = await workflow.execute_activity(nlm_artefatos_video, nb, **curto)
        art = vids[0]["id"] if vids else await workflow.execute_activity(
            nlm_gerar_short, args=[nb, cri.get("steering") or p.steering or ""], start_to_close_timeout=timedelta(minutes=6), retry_policy=RetryPolicy(maximum_attempts=1))
        estado = ""
        for _ in range(60):   # até ~60 min
            vids = await workflow.execute_activity(nlm_artefatos_video, nb, **curto)
            if all(v["id"] != art for v in vids) and len(vids) == 1:
                art = vids[0]["id"]   # E2E 12/10: `generate --json` devolve o id da tarefa, não o do artefato
            estado = next((v["status"] for v in vids if v["id"] == art), estado)
            if re.search(r"complet|fail|error", estado, re.I): break
            await workflow.sleep(60)
        ok = bool(re.search("complet", estado, re.I))
        if ok and p.roteirizar:
            cri["seo"] = await self._seo(nb, cri, curto)
            try:
                cri["capa"] = await workflow.execute_activity(nlm_gerar_capa, args=[nb, f"{TRAB_NLM}/{p.slug}/capa_nlm.png", PROMPT_CAPA],
                                                              start_to_close_timeout=timedelta(minutes=20), retry_policy=RetryPolicy(maximum_attempts=1))
            except Exception as e:  # noqa: BLE001
                cri["capa"] = {"falhou": str(e)[:300]}
        return ResultadoNotebookLM(ok=ok, tipo=p.tipo, caderno=nb, artefato=art, estado_artefato=estado, uso_dia=uso, criativo=cri)

    async def _registrar_novas(self, nb: str, tipo: str, curto: dict) -> None:
        ja = set(await workflow.execute_activity("registro_fontes_listar", nb, task_queue=FILA_REGISTRO, **curto))
        for fid in await workflow.execute_activity(nlm_fontes_ids, nb, **curto):
            if fid not in ja:
                await workflow.execute_activity("registro_fonte", args=[nb, fid, tipo, None], task_queue=FILA_REGISTRO, **curto)

    async def _roteirizar(self, p: "PedidoNotebookLM", nb: str, curto: dict):
        uma = dict(start_to_close_timeout=timedelta(minutes=25), retry_policy=RetryPolicy(maximum_attempts=1))
        try:   # pesquisa web do tema dentro do caderno; as fontes importadas viram fontes registradas do episódio
            await workflow.execute_activity(nlm_pesquisa_web, args=[nb, f"origem e explicação: {p.tema}"], **uma)
        except Exception as e:  # noqa: BLE001  (E2E 12/10: add-research pode falhar "outcome unknown" e ainda importar)
            workflow.logger.warning(f"pesquisa web falhou: {e}")
        if p.episodio: await self._registrar_novas(nb, "pesquisa", curto)   # importadas pela pesquisa do próprio episódio
        erro, val = "", None
        for _ in range(2):
            txt = await workflow.execute_activity(nlm_perguntar, args=[nb, PROMPT_ROTEIRO.format(tema=p.tema, slug=p.slug) +
                                                  (f" A resposta anterior foi inválida: {erro}. Corrija." if erro else "")], **uma)
            try:
                val = await workflow.execute_activity("validar_roteiro", args=[txt, p.slug], task_queue=FILA_REGISTRO, **uma); break
            except Exception as e:  # noqa: BLE001
                erro = str(getattr(e, "cause", e))[:300]
        if not val:
            return ResultadoNotebookLM(ok=False, tipo=p.tipo, caderno=nb, motivo=f"roteiro do NotebookLM inválido: {erro}")
        comp = await workflow.execute_activity("compliance_roteiro", val["markdown"], task_queue=FILA_REGISTRO, **curto)
        if comp.get("aprovado") is not True:
            return ResultadoNotebookLM(ok=False, tipo=p.tipo, caderno=nb, motivo="compliance não aprovou",
                                       criativo={"roteiro": val, "compliance": comp})
        fid = await workflow.execute_activity(nlm_fonte, args=[nb, f"{p.slug}-roteiro", val["markdown"]], **curto)
        if p.episodio:
            await workflow.execute_activity("registro_fonte", args=[nb, fid, "roteiro", f"{p.slug}-roteiro.md"], task_queue=FILA_REGISTRO, **curto)
        return {"roteiro": val["roteiro"], "fontes": val["fontes"], "markdown": val["markdown"], "steering": val["steering"],
                "compliance": comp, "origem_roteiro": "notebooklm"}

    async def _seo(self, nb: str, cri: dict, curto: dict) -> dict:
        uma = dict(start_to_close_timeout=timedelta(minutes=12), retry_policy=RetryPolicy(maximum_attempts=1))
        erro = ""
        reg = await workflow.execute_activity("registro_fontes_listar", nb, task_queue=FILA_REGISTRO, **curto)
        fontes = await workflow.execute_activity(nlm_fontes_urls, args=[nb, reg], **curto)
        fontes = await workflow.execute_activity("ordenar_fontes", args=[cri.get("fontes") or [], fontes], task_queue=FILA_REGISTRO, **curto)
        for _ in range(2):
            try:
                txt = await workflow.execute_activity(nlm_perguntar, args=[nb, PROMPT_SEO + (f" Corrija: {erro}" if erro else "")], **uma)
                return (await workflow.execute_activity("validar_seo", args=[txt, fontes], task_queue=FILA_REGISTRO, **uma)) | {"_origem": "notebooklm"}
            except Exception as e:  # noqa: BLE001
                erro = str(getattr(e, "cause", e))[:300]
        return await workflow.execute_activity("seo_9router", args=[cri["markdown"], fontes], task_queue=FILA_REGISTRO, **uma)


@activity.defn
async def nlm_fontes_ids(caderno: str) -> list[str]:
    lst = _json(await asyncio.to_thread(_cli, "source", "list", "-n", caderno, "--json", timeout=120))
    return [f["id"] for f in _ids(lst.get("sources", lst) if isinstance(lst, dict) else lst)]


@activity.defn
async def nlm_fontes_urls(caderno: str, registradas: list[str]) -> list[dict]:
    """t466: título + URL real das fontes REGISTRADAS do episódio (web/pdf); base da lista de fontes da descrição."""
    lst = _json(await asyncio.to_thread(_cli, "source", "list", "-n", caderno, "--json", timeout=120))
    ok = set(registradas)
    return [{"id": f["id"], "titulo": f.get("title") or "", "url": f["url"]} for f in _ids(lst.get("sources", lst) if isinstance(lst, dict) else lst)
            if f["id"] in ok and str(f.get("url") or "").startswith("http")]


@activity.defn
async def nlm_gerar_capa(caderno: str, destino: str, prompt: str) -> dict:
    """t464: capa = infográfico retrato do próprio caderno (teste t460); falha → o episódio usa A9 num quadro."""
    if caderno in MESTRES_PROIBIDOS: raise RuntimeError("caderno mestre proibido")
    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(_cli, "generate", "infographic", "-n", caderno, "--orientation", "portrait", "--detail", "concise",
                            "--language", "pt_BR", "--wait", "--timeout", "900", "--json", prompt, timeout=960)
    await asyncio.to_thread(_cli, "download", "infographic", "-n", caderno, destino, "--force", "--json", timeout=300)
    f = Path(destino)
    if not f.is_file() or f.stat().st_size < 10_000: raise RuntimeError("capa vazia")
    return {"arquivo": str(f), "bytes": f.stat().st_size}


ATIVIDADES = [nlm_fontes_urls, nlm_fontes_ids, nlm_gerar_capa, nlm_checar_saldo, nlm_pesquisa_web, nlm_caderno, nlm_persona, nlm_baixar_video, nlm_fonte, nlm_perguntar, nlm_artefatos_video, nlm_gerar_short]
