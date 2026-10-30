"""EpisodioWorkflow + PublicacaoWorkflow (dry-run) — fila `episodio-pqbr` (t427, t130u; storyboard removido 29/10/2026, ordem do José).
Ordem vigente: NotebookLM intelectual (roteiro, compliance, SEO; sem vídeo) → cenas individuais no Google Flow.
Após o roteiro: activity de direção (NotebookLM → lista CenaIndividual, fail-closed), gates
flow_projeto.exigir_antes_cenas + processo_criacao; passo 2 (adaptador Flow) permanece pendente.
Não há mais etapa de storyboard neste workflow.
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
    from .pacote import ATIVIDADES_REGISTRO, pacote_garantir, registro_buscar_caderno
    from ..contratos import CATEGORIA_YOUTUBE
    from ..contratos.pedidos_producao import PedidoEpisodioE2E

FILA_EPISODIO = "episodio-pqbr"
RAIZ = Path("/home/pc/Workspace/PQBR")
TRAB = Path(os.environ.get("PQBR_TRABALHO", "/home/pc/.pqbr/episodios"))
DRYRUN = Path(os.environ.get("PQBR_DRYRUN_DIR", "/home/pc/.pqbr/publicacao-dryrun"))
CODIGO = re.compile(r"^PQBR-EP[0-9]{4,}$")


# PedidoEpisodioE2E: contrato 1.0.0 em pqbr.contratos.pedidos_producao (pt162u)


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




@activity.defn
async def flow_projeto_exigir_antes_cenas(codigo_ep: str) -> dict:
    """Fail-closed: projeto Flow do episódio com fichas_ok antes das cenas."""
    from ..pipeline import flow_projeto as fp
    return fp.exigir_antes_cenas(codigo_ep).model_dump()


@activity.defn
async def direcao_cenas_nlm(pedido: dict) -> dict:
    """Passo 1 pós-roteiro: NotebookLM devolve direção/prompts; valida CenaIndividual fail-closed.
    pedido.adaptador=falso só para testes (sem rede). Default = notebooklm."""
    from ..motores.direcao_cenas import AdaptadorFalsoDirecao, AdaptadorNotebookLMDirecao, GASTO_DIRECAO_CENAS
    from ..contratos import ESTILO_PADRAO_STICKMAN
    if not GASTO_DIRECAO_CENAS.pode_gastar:
        raise RuntimeError("gasto direção cenas bloqueado")
    adaptador = (pedido.get("adaptador") or "notebooklm").lower()
    if adaptador == "falso":
        motor = AdaptadorFalsoDirecao(pedido.get("cenas_falsas"))
    elif adaptador == "notebooklm":
        motor = AdaptadorNotebookLMDirecao()
    else:
        raise RuntimeError(f"adaptador direção desconhecido: {adaptador}")
    r = motor.direcionar(
        codigo=pedido["codigo"],
        slug=pedido["slug"],
        caderno=pedido["caderno"],
        n_cenas=int(pedido["n_cenas"]),
        estilo=pedido.get("estilo") or ESTILO_PADRAO_STICKMAN,
    )
    return r.model_dump(mode="json")

@activity.defn
async def processo_criacao_conferir(plataforma: str = "flow") -> dict:
    """Fail-closed: confere docs/processos canônico (versão pinada + hash + playbook).
    Só vale em runtime após reinício do pqbr-episodio-worker (OK do José)."""
    from ..pipeline import processo_criacao as pc
    if plataforma not in pc.PLATAFORMAS:
        raise RuntimeError(f"plataforma desconhecida: {plataforma}")
    operavel = plataforma == "flow"
    r = pc.exigir(plataforma, exigir_playbook_operavel=operavel)
    return r.model_dump()


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
        await workflow.execute_activity(processo_criacao_conferir, args=["flow"], start_to_close_timeout=timedelta(minutes=1), retry_policy=RetryPolicy(maximum_attempts=1))
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
        # Passo 1: direção NLM → CenaIndividual (fail-closed). Adaptador Flow = passo 2, ainda pendente.
        uma = dict(start_to_close_timeout=timedelta(minutes=25), retry_policy=RetryPolicy(maximum_attempts=1))
        direcao = await workflow.execute_activity(
            direcao_cenas_nlm,
            {"codigo": p.codigo, "slug": p.slug, "caderno": nlm.caderno, "n_cenas": p.n_cenas, "adaptador": "notebooklm"},
            **uma)
        await workflow.execute_activity(
            flow_projeto_exigir_antes_cenas, args=[p.codigo],
            start_to_close_timeout=timedelta(minutes=1), retry_policy=RetryPolicy(maximum_attempts=1))
        await workflow.execute_activity(
            processo_criacao_conferir, args=["flow"],
            start_to_close_timeout=timedelta(minutes=1), retry_policy=RetryPolicy(maximum_attempts=1))
        # Passo 2 (adaptador Flow / cenas individuais) NÃO implementado — permanece pendente.
        return ResultadoEpisodioE2E(
            etapa="direcao_cenas", ok=True,
            detalhes={"caderno": nlm.caderno,
                      "criativo": {k: v for k, v in nlm.criativo.items() if k != "markdown"},
                      "direcao": {k: v for k, v in direcao.items() if k != "cenas"} | {"n_cenas": len(direcao.get("cenas") or [])},
                      "cenas": direcao.get("cenas"),
                      "proximo": "flow_cenas_individuais_pendente"})


from .criativo import validar_roteiro, validar_seo, seo_9router, compliance_roteiro, ordenar_fontes, capa_conferir
ATIVIDADES_EPISODIO = [processo_criacao_conferir, flow_projeto_exigir_antes_cenas, direcao_cenas_nlm, capa_conferir, validar_roteiro, validar_seo, seo_9router, compliance_roteiro, ordenar_fontes, pos_produzir, extrair_quadros, capa_a9, drive_enviar, publicacao_dryrun, *ATIVIDADES_REGISTRO]
