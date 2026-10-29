"""EpisodioWorkflow + PublicacaoWorkflow (dry-run) — fila `episodio-pqbr` (t427, t130u).
Ordem vigente: NotebookLM intelectual (roteiro, compliance, SEO; sem vídeo) → storyboard_criar.
Para com a ficha gravada, imagens_revisadas false e pode_gerar_video false.
Pós, quadros, Drive e publicação dry-run continuam registrados e não rodam neste fluxo.
Nada torna público. Os vídeos já prontos do saldo não entram aqui."""
from __future__ import annotations
import asyncio, json, os, re, subprocess
from datetime import timedelta, datetime
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from temporalio import activity, workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from .notebooklm import NotebookLMWorkflow, PedidoNotebookLM, FILA_NOTEBOOKLM, nlm_perguntar
    from .storyboard import PROMPT_STORYBOARD, storyboard_criar
    from ..contratos.storyboard import elenco_alternado, protagonista_ref
    from .pacote import ATIVIDADES_REGISTRO, pacote_garantir, registro_buscar_caderno
    from ..contratos import CATEGORIA_YOUTUBE

FILA_EPISODIO = "episodio-pqbr"
RAIZ = Path("/home/pc/Workspace/PQBR")
TRAB = Path(os.environ.get("PQBR_TRABALHO", "/home/pc/.pqbr/episodios"))
DRYRUN = Path(os.environ.get("PQBR_DRYRUN_DIR", "/home/pc/.pqbr/publicacao-dryrun"))
CODIGO = re.compile(r"^PQBR-EP[0-9]{4,}$")


class PedidoEpisodioE2E(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,60}$")
    codigo: str = Field(pattern=CODIGO.pattern)
    roteiro_texto: str = Field(min_length=50)          # roteiro completo com o bloco visual (vira a fonte do caderno)
    n_cenas: int = Field(ge=2, le=60)
    titulo: str | None = Field(default=None, min_length=5, max_length=100)        # t464: None → SEO do NotebookLM
    descricao: str | None = Field(default=None, min_length=10, max_length=5000)
    roteirizar: bool = False          # t464: roteiro_texto = briefing do tema; NotebookLM escreve roteiro/SEO/capa
    tema: str | None = Field(default=None, max_length=300)
    tema_id: int | None = None        # pqbr.temas_pendentes.id (vira temas_publicados na publicação; reposição automática)
    tags: list[str] = Field(default_factory=list, max_length=15)
    dry_run: bool = True                               # t426: teste nº 1 para antes do upload
    steering: str | None = Field(default=None, max_length=4000)   # t462: bloco visual 2D do roteiro (reforços entram no nlm)
    espera_veredito_h: float = Field(default=24, ge=0.01, le=72)


class VereditoAuditor(BaseModel):
    """Sinal final do Auditor (sem terceira_rodada: o agente desempata antes de sinalizar)."""
    model_config = ConfigDict(extra="forbid", frozen=True)
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
    if not drive.ARQ_CRED.is_file(): return {"pulado": "sem credencial do Drive"}   # E2E 12/10: era drive.TOKEN (inexistente)
    capa = Path(arquivos[-1]).parent / "capa_nlm.png"
    if capa.is_file() and str(capa) not in arquivos: arquivos = [*arquivos, str(capa)]   # t464: capa do NotebookLM junto
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
                         "categoryId": CATEGORIA_YOUTUBE, "defaultLanguage": "pt-BR"},
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
        self._criativo: dict = {}
        self._veredito: VereditoAuditor | None = None

    @workflow.signal
    def veredito_auditor(self, v: VereditoAuditor) -> None:
        self._veredito = v

    @workflow.query
    def criativo(self) -> dict:
        return {k: v for k, v in self._criativo.items() if k != "markdown"}

    @workflow.query
    def estado(self) -> str:
        return self._veredito.veredito if self._veredito else "aguardando_auditor"

    @workflow.run
    async def run(self, p: PedidoEpisodioE2E) -> ResultadoEpisodioE2E:
        curto = dict(start_to_close_timeout=timedelta(minutes=20), retry_policy=RetryPolicy(maximum_attempts=2))
        base = str(TRAB / p.slug)
        pac = await workflow.execute_activity(pacote_garantir, **curto)               # t459: versão do pacote (hash)
        reg = await workflow.execute_activity(registro_buscar_caderno, p.codigo, **curto)
        nlm = await workflow.execute_child_workflow(
            NotebookLMWorkflow.run, PedidoNotebookLM(tipo="short", slug=p.slug, fonte=p.roteiro_texto, solicitante="episodio",
                                                     episodio=p.codigo, caderno_registrado=reg,
                                                     pacote_fonte=pac["fonte"], pacote_hash=pac["hash"], steering=p.steering,
                                                     roteirizar=p.roteirizar, tema=p.tema),
            id=f"nlm-short-{p.slug}-{workflow.info().workflow_id[-6:]}", task_queue=FILA_NOTEBOOKLM)
        if not nlm.ok or not nlm.caderno:
            return ResultadoEpisodioE2E(etapa="roteiro", ok=False, detalhes=nlm.model_dump())
        self._criativo = nlm.criativo
        elenco = elenco_alternado(p.codigo)
        roteiro = (nlm.criativo.get("markdown") or p.roteiro_texto)[:6000]
        base_prompt = PROMPT_STORYBOARD.format(codigo=p.codigo, elenco=elenco, protagonista=protagonista_ref(elenco), roteiro=roteiro)
        uma = dict(start_to_close_timeout=timedelta(minutes=12), retry_policy=RetryPolicy(maximum_attempts=1))
        erro, sb = "", None
        for _ in range(2):
            txt = await workflow.execute_activity(
                nlm_perguntar, args=[nlm.caderno, base_prompt + (f" A resposta anterior foi inválida: {erro}. Corrija." if erro else "")],
                task_queue=FILA_NOTEBOOKLM, **uma)
            try:
                sb = await workflow.execute_activity(
                    storyboard_criar, args=[txt, p.codigo, f"{base}/storyboard.json"],
                    start_to_close_timeout=timedelta(minutes=2), retry_policy=RetryPolicy(maximum_attempts=1))
                break
            except Exception as e:  # noqa: BLE001
                erro = str(getattr(e, "cause", e))[:300]
                sb = None
        if not sb:
            return ResultadoEpisodioE2E(etapa="storyboard", ok=False, detalhes={"motivo": f"storyboard inválido: {erro}", "caderno": nlm.caderno})
        return ResultadoEpisodioE2E(
            etapa="storyboard", ok=True,
            detalhes={"storyboard": sb, "caderno": nlm.caderno,
                      "criativo": {k: v for k, v in nlm.criativo.items() if k != "markdown"},
                      "pode_gerar_video": False})


from .criativo import validar_roteiro, validar_seo, seo_9router, compliance_roteiro, ordenar_fontes, capa_conferir
ATIVIDADES_EPISODIO = [storyboard_criar, capa_conferir, validar_roteiro, validar_seo, seo_9router, compliance_roteiro, ordenar_fontes, pos_produzir, extrair_quadros, capa_a9, drive_enviar, publicacao_dryrun, *ATIVIDADES_REGISTRO]
