"""Cliente mínimo da API do Paperclip com a chave do próprio agente (injetada pelo harness no run).
Nunca devolve nem registra a chave."""
from __future__ import annotations
import json, os, urllib.request, urllib.error

def _base() -> str:
    """URL da API: PQBR_PAPERCLIP_API, senão o apiBase do contexto do CLI (o PAPERCLIP_API_URL do run não escuta)."""
    if os.environ.get("PQBR_PAPERCLIP_API"):
        return os.environ["PQBR_PAPERCLIP_API"]
    ctx = json.load(open(os.path.expanduser("~/.paperclip/context.json"), encoding="utf-8"))
    perfil = ctx.get("profiles", {}).get(ctx.get("currentProfile", "default"), {})
    return perfil.get("apiBase") or os.environ["PAPERCLIP_API_URL"]


BASE = _base().rstrip("/")


def _req(metodo: str, caminho: str, corpo: dict | None = None) -> dict | list:
    h = {"Authorization": "Bearer " + os.environ["PAPERCLIP_API_KEY"], "Content-Type": "application/json"}
    if os.environ.get("PAPERCLIP_RUN_ID"):
        h["X-Paperclip-Run-Id"] = os.environ["PAPERCLIP_RUN_ID"]
    dados = json.dumps(corpo).encode() if corpo is not None else None
    r = urllib.request.Request(BASE + caminho, data=dados, method=metodo, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            t = resp.read()
            return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Paperclip {metodo} {caminho}: HTTP {e.code} {e.read()[:200]!r}") from None


def eu() -> dict: return _req("GET", "/api/agents/me")
def inbox() -> list:
    d = _req("GET", "/api/agents/me/inbox-lite")
    return d if isinstance(d, list) else d.get("items", d.get("issues", []))
def issue(i: str) -> dict: return _req("GET", f"/api/issues/{i}")
def checkout(i: str, agente: str) -> dict:
    return _req("POST", f"/api/issues/{i}/checkout", {"agentId": agente, "expectedStatuses": ["todo", "backlog", "blocked", "in_progress"]})
def comentar(i: str, corpo: str) -> dict: return _req("POST", f"/api/issues/{i}/comments", {"body": corpo})
def atualizar(i: str, **campos) -> dict: return _req("PATCH", f"/api/issues/{i}", campos)
def criar_issue(empresa: str, **campos) -> dict: return _req("POST", f"/api/companies/{empresa}/issues", campos)
