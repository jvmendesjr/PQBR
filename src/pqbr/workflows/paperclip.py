"""Activities da ponte Temporal → Paperclip (TZ-04, t334). Usa o CLI oficial `paperclipai` com o
contexto de board já configurado no servidor; nenhum segredo no código. O agente nunca recebe
acesso ao Postgres do Temporal."""
from __future__ import annotations
import asyncio, json, os, re
from temporalio import activity
from temporalio.exceptions import ApplicationError
from pydantic import BaseModel, ConfigDict
from ..seguranca.barreira import exigir_limpo
from ..seguranca.segredos import SegredoDetectado

NODE = os.environ.get("PAPERCLIP_NODE", os.path.expanduser("~/.hermes/node/bin/node"))
CLI = os.environ.get("PAPERCLIP_CLI", os.path.expanduser("~/.paperclip/cli/current/node_modules/paperclipai/dist/index.js"))
BLOCO = re.compile(r"```json\s*(\{.*?\})\s*```", re.S)


class PedidoIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    company_id: str
    project_id: str
    marcador: str  # idempotência: vai no título
    titulo: str
    descricao: str
    agente_id: str | None = None


class Comentario(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    issue_id: str
    corpo: str
    acordar_responsavel: bool = False  # --resume: acorda o agente com o contexto desta issue


class LeituraPropostas(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    issue_id: str
    agente_id: str
    ja_vistos: list[str] = []


class PropostaBruta(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    comentario_id: str
    dados: dict | None  # None = comentário do agente sem JSON legível


async def _cli(*args: str) -> object:
    _barreira(args)
    env = {k: v for k, v in os.environ.items() if k != "PAPERCLIP_API_KEY"}  # a ponte age como board
    p = await asyncio.create_subprocess_exec(NODE, CLI, *args, "--json", env=env,
                                            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, err = await p.communicate()
    if p.returncode != 0:
        raise ApplicationError(f"paperclip cli falhou (exit={p.returncode})")
    return json.loads(out or b"null")


def _lista(d) -> list:
    if isinstance(d, list):
        return d
    for k in ("items", "issues", "comments", "data"):
        if isinstance(d, dict) and isinstance(d.get(k), list):
            return d[k]
    return []


def _barreira(obj) -> None:
    try:
        exigir_limpo(obj, "ticket")
    except SegredoDetectado as e:
        raise ApplicationError(str(e), type="SegredoDetectado", non_retryable=True) from None


@activity.defn
async def abrir_issue_paperclip(p: PedidoIssue) -> str:
    _barreira(p)
    for it in _lista(await _cli("issue", "list", "-C", p.company_id)):
        if p.marcador in (it.get("title") or ""):
            return it["id"]  # já existe: idempotente
    args = ["issue", "create", "-C", p.company_id, "--project-id", p.project_id,
            "--title", f"{p.titulo} {p.marcador}", "--description", p.descricao, "--status", "todo"]
    if p.agente_id:
        args += ["--assignee-agent-id", p.agente_id]
    return (await _cli(*args))["id"]


@activity.defn
async def comentar_paperclip(c: Comentario) -> str:
    _barreira(c)
    args = ["issue", "comment", c.issue_id, "--body", c.corpo] + (["--resume"] if c.acordar_responsavel else [])
    return (await _cli(*args)).get("id", "")


@activity.defn
async def ler_propostas_paperclip(r: LeituraPropostas) -> list[PropostaBruta]:
    novas = []
    for cm in sorted(_lista(await _cli("issue", "comments", r.issue_id)), key=lambda c: c.get("createdAt") or ""):
        autor = cm.get("authorAgentId") or (cm.get("author") or {}).get("agentId")
        if autor != r.agente_id or cm["id"] in r.ja_vistos:
            continue
        m = BLOCO.search(cm.get("body") or "")
        try:
            dados = json.loads(m.group(1)) if m else None
        except json.JSONDecodeError:
            dados = None
        novas.append(PropostaBruta(comentario_id=cm["id"], dados=dados))
    return novas


@activity.defn
async def concluir_issue_paperclip(issue_id: str) -> None:
    await _cli("issue", "update", issue_id, "--status", "done")
