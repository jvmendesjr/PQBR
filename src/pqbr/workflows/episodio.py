"""EpisodioWorkflow + PublicacaoWorkflow (dry-run) — fila `episodio-pqbr` (t427).
Ordem (docs/sdd/teste-e2e-short-1.md): NotebookLM short (fila notebooklm-pqbr, filho) → download → pós (trim+logo)
→ quadros por cena + capa A9 (código) → espera o veredito do Auditor (sinal) → Drive → Publicação **dry-run**
(payload privado, sem agendar, nada enviado ao YouTube). Nada torna público; sem veredito ou reprovado, para."""
from __future__ import annotations
import asyncio, json, os, re, subprocess
from datetime import timedelta, datetime
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field
from temporalio import activity, workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from .notebooklm import NotebookLMWorkflow, PedidoNotebookLM, FILA_NOTEBOOKLM, nlm_baixar_video

FILA_EPISODIO = "episodio-pqbr"
RAIZ = Path("/home/pc/Workspace/PQBR")
TRAB = Path(os.environ.get("PQBR_TRABALHO", "/home/pc/.pqbr/episodios"))
DRYRUN = Path(os.environ.get("PQBR_DRYRUN_DIR", "/home/pc/.pqbr/publicacao-dryrun"))
CODIGO = re.compile(r"^PQBR-EP[0-9]{4,}$")


class PedidoEpisodioE2E(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,60}$")
    codigo: str = Field(pattern=CODIGO.pattern)
    roteiro_texto: str = Field(min_length=50)          # roteiro completo com o bloco visual (vira a fonte do caderno)
    n_cenas: int = Field(ge=2, le=60)
    titulo: str = Field(min_length=5, max_length=100)
    descricao: str = Field(min_length=10, max_length=5000)
    tags: list[str] = Field(default_factory=list, max_length=15)
    dry_run: bool = True                               # t426: teste nº 1 para antes do upload
    espera_veredito_h: float = Field(default=24, ge=0.01, le=72)


class VereditoAuditor(BaseModel):
    veredito: Literal["aprova", "aprova_com_ressalva", "reprova"]
    motivo: str = ""


class ResultadoEpisodioE2E(BaseModel):
    etapa: str
    ok: bool
    detalhes: dict = {}


def _sh(cmd: list[str], timeout: int = 900) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0: raise RuntimeError(f"{Path(cmd[0]).name} rc={r.returncode}: {(r.stderr or r.stdout)[-300:]}")
    return r.stdout


@activity.defn
async def pos_produzir(entrada: str, saida: str) -> dict:
    out = await asyncio.to_thread(_sh, [str(RAIZ / "scripts/pos/post-short.sh"), entrada, saida, "2.5"])
    linha = [l for l in out.splitlines() if l.startswith("ok ")][-1]
    return dict(kv.split("=", 1) for kv in linha[3:].split())


@activity.defn
async def extrair_quadros(video: str, n_cenas: int, pasta: str) -> list[str]:
    """1 quadro no meio de cada cena (cenas de duração igual — aproximação até termos os tempos reais)."""
    d = float(json.loads(_sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", video]))["format"]["duration"])
    Path(pasta).mkdir(parents=True, exist_ok=True); qs = []
    for i in range(n_cenas):
        t = d * (i + 0.5) / n_cenas; f = str(Path(pasta) / f"cena_{i + 1:02d}.png")
        await asyncio.to_thread(_sh, ["ffmpeg", "-nostdin", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", f])
        qs.append(f)
    return qs


@activity.defn
async def capa_a9(quadros: list[str]) -> dict:
    from ..pipeline.capa import escolher
    c, todos = await asyncio.to_thread(escolher, quadros)
    return {"escolhido": c.arquivo if c else None, "candidatos": [x.model_dump() for x in todos]}


@activity.defn
async def drive_enviar(codigo: str, slug: str, arquivos: list[str]) -> dict:
    from ..integrations import drive
    if not drive.TOKEN.is_file(): return {"pulado": "sem credencial do Drive"}
    pasta = drive.garantir_pasta(f"PQBR/02_Episodios/{datetime.now():%Y-%m}/{codigo}_{slug}")
    return {"pasta": pasta, "arquivos": {Path(a).name: drive.enviar(a, pasta) for a in arquivos}}


@activity.defn
async def publicacao_dryrun(p: dict) -> dict:
    """Monta o payload de videos.insert (privado, sem agendamento) e grava em arquivo. Nunca chama o YouTube."""
    if os.environ.get("YOUTUBE_DRY_RUN", "true").lower() != "true" or not p.get("dry_run", True):
        raise RuntimeError("só dry-run implementado (F8-01): upload real bloqueado")
    if not CODIGO.match(p["codigo"]): raise RuntimeError("código inválido")
    dup = None
    try:
        import psycopg
        with psycopg.connect(os.environ["PQBR_DB_DSN"], connect_timeout=10) as c:
            dup = c.execute("select 1 from pqbr.temas_publicados where codigo = %s", (p["codigo"],)).fetchone()
    except KeyError:
        dup = None
    if dup: raise RuntimeError(f"código {p['codigo']} já publicado (sem duplicata)")
    corpo = {"snippet": {"title": p["titulo"], "description": p["descricao"], "tags": p.get("tags", []) + [p["codigo"]],
                         "categoryId": "24", "defaultLanguage": "pt-BR"},
             "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": False},
             "_arquivo": p["video"], "_capa": p.get("capa"), "_dry_run": True}
    DRYRUN.mkdir(parents=True, exist_ok=True)
    f = DRYRUN / f"{p['codigo']}.json"; f.write_text(json.dumps(corpo, ensure_ascii=False, indent=1))
    return {"payload": str(f), "privacidade": "private", "agendado": False, "enviado": False}


@workflow.defn
class PublicacaoWorkflow:
    @workflow.run
    async def run(self, p: dict) -> dict:
        return await workflow.execute_activity(publicacao_dryrun, p, start_to_close_timeout=timedelta(minutes=2),
                                               retry_policy=RetryPolicy(maximum_attempts=1))


@workflow.defn
class EpisodioWorkflow:
    def __init__(self) -> None:
        self._veredito: VereditoAuditor | None = None

    @workflow.signal
    def veredito_auditor(self, v: VereditoAuditor) -> None:
        self._veredito = v

    @workflow.query
    def estado(self) -> str:
        return self._veredito.veredito if self._veredito else "aguardando_auditor"

    @workflow.run
    async def run(self, p: PedidoEpisodioE2E) -> ResultadoEpisodioE2E:
        curto = dict(start_to_close_timeout=timedelta(minutes=20), retry_policy=RetryPolicy(maximum_attempts=2))
        base = str(TRAB / p.slug)
        nlm = await workflow.execute_child_workflow(
            NotebookLMWorkflow.run, PedidoNotebookLM(tipo="short", slug=p.slug, fonte=p.roteiro_texto, solicitante="episodio"),
            id=f"nlm-short-{p.slug}-{workflow.info().workflow_id[-6:]}", task_queue=FILA_NOTEBOOKLM)
        if not nlm.ok or not nlm.artefato:
            return ResultadoEpisodioE2E(etapa="geracao", ok=False, detalhes=nlm.model_dump())
        raw = await workflow.execute_activity(nlm_baixar_video, args=[nlm.caderno, nlm.artefato, f"{base}/raw.mp4"],
                                              task_queue=FILA_NOTEBOOKLM, **curto)
        pos = await workflow.execute_activity(pos_produzir, args=[raw["arquivo"], f"{base}/final.mp4"], **curto)
        quadros = await workflow.execute_activity(extrair_quadros, args=[f"{base}/final.mp4", p.n_cenas, f"{base}/pranchas"], **curto)
        capa = await workflow.execute_activity(capa_a9, quadros, **curto)
        try:
            await workflow.wait_condition(lambda: self._veredito is not None, timeout=timedelta(hours=p.espera_veredito_h))
        except asyncio.TimeoutError:
            return ResultadoEpisodioE2E(etapa="auditor", ok=False, detalhes={"motivo": "sem veredito no prazo", "pranchas": quadros, "capa": capa})
        if self._veredito.veredito == "reprova":
            return ResultadoEpisodioE2E(etapa="auditor", ok=False, detalhes=self._veredito.model_dump())
        drv = await workflow.execute_activity(drive_enviar, args=[p.codigo, p.slug, [raw["arquivo"], f"{base}/final.mp4"]], **curto)
        pub = await workflow.execute_child_workflow(PublicacaoWorkflow.run, {
            "codigo": p.codigo, "titulo": p.titulo, "descricao": p.descricao, "tags": p.tags, "dry_run": p.dry_run,
            "video": f"{base}/final.mp4", "capa": capa.get("escolhido")}, id=f"pub-{p.codigo}-{workflow.info().workflow_id[-6:]}")
        return ResultadoEpisodioE2E(etapa="publicacao_dryrun", ok=True,
                                    detalhes={"pos": pos, "capa": capa.get("escolhido"), "drive": drv, "publicacao": pub,
                                              "auditor": self._veredito.model_dump()})


ATIVIDADES_EPISODIO = [pos_produzir, extrair_quadros, capa_a9, drive_enviar, publicacao_dryrun]
