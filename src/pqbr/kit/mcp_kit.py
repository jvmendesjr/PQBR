"""Servidor MCP `pqbr-kit` (stdio, JSON-RPC, só stdlib + kit). Expõe só as ferramentas do papel em PQBR_KIT_PAPEL.
Efeito externo nunca é direto: Camofox e NotebookLM só entram como workflow nas filas do Temporal (concorrência 1)."""
from __future__ import annotations
import asyncio, json, os, subprocess, sys
from pathlib import Path

RAIZ = Path("/home/pc/Workspace/PQBR")
DOCS = RAIZ / "docs"
PROIBIDO = ("arquivo", "pesquisas")
UNIDADES = ["pqbr-camofox", "pqbr-camofox-worker", "pqbr-temporal-worker", "paperclipai", "9router"]

# Lista fechada por papel (AGENTES §2, §6). Leitura de docs e API do Paperclip para todos os papéis com ferramenta.
COMUM = ["docs_ler", "paperclip_comentar", "paperclip_status", "paperclip_criar_issue"]
PAPEIS = {
    "diretor": COMUM + ["temporal_listar", "saude_servicos"],
    "pesquisador-origem": COMUM + ["notebooklm_enfileirar"],
    "diretor-arte-2d": COMUM + ["notebooklm_enfileirar"],
    "observador": COMUM + ["temporal_listar", "saude_servicos", "camofox_saude"],
    "guardiao-seguranca": COMUM + ["temporal_listar", "saude_servicos", "seguranca_varrer"],
    "dev-corretor": COMUM + ["temporal_listar"],
    "dev-revisor": COMUM + ["temporal_listar"],
}

FERR = {
    "docs_ler": ("Lê um arquivo de docs/ (canônicos; arquivo/ e pesquisas/ bloqueados).", {"caminho": "string"}),
    "paperclip_comentar": ("Comenta numa issue (como o próprio agente).", {"issue": "string", "texto": "string"}),
    "paperclip_status": ("Muda o status de uma issue.", {"issue": "string", "status": "string"}),
    "paperclip_criar_issue": ("Abre issue na PQBR (ticket pré-estruturado).", {"titulo": "string", "descricao": "string"}),
    "temporal_listar": ("Lista execuções recentes de workflows da PQBR (só leitura).", {"consulta": "string"}),
    "saude_servicos": ("Estado dos serviços da PQBR (systemd, só leitura).", {}),
    "camofox_saude": ("Enfileira CamofoxSaudeWorkflow na fila camofox-pqbr e devolve o resultado.", {}),
    "notebooklm_enfileirar": ("Pede uma geração ao NotebookLM pela fila do Temporal (EM CONSTRUÇÃO: só registra).", {"pedido": "string"}),
    "seguranca_varrer": ("Roda a barreira de segredos/PII sobre um texto.", {"texto": "string"}),
}


def _docs_ler(caminho: str) -> str:
    p = (DOCS / caminho).resolve()
    if DOCS.resolve() not in p.parents or any(x in p.relative_to(DOCS.resolve()).parts for x in PROIBIDO):
        return "negado: fora de docs/ canônicos"
    return p.read_text(encoding="utf-8")[:20000]


def _temporal(fn):
    async def run():
        sys.path.insert(0, str(RAIZ / "src"))
        from pqbr.workflows.worker import client
        return await fn(await client())
    return asyncio.run(run())


def _temporal_listar(consulta: str = "") -> str:
    async def f(c):
        out = []
        async for w in c.list_workflows(consulta or None, limit=20):
            out.append(f"{w.id} {w.workflow_type} {w.status.name if w.status else ''} {w.start_time:%Y-%m-%d %H:%M}")
            if len(out) >= 20: break
        return "\n".join(out) or "nenhuma"
    return _temporal(f)


def _camofox_saude() -> str:
    async def f(c):
        from pqbr.workflows.camofox import CamofoxSaudeWorkflow, FILA_CAMOFOX
        import uuid
        r = await c.execute_workflow(CamofoxSaudeWorkflow.run, 0.0, id=f"kit-saude-{uuid.uuid4().hex[:8]}", task_queue=FILA_CAMOFOX)
        return r.model_dump_json()
    return _temporal(f)


def _saude() -> str:
    linhas = []
    for u in UNIDADES:
        r = subprocess.run(["systemctl", "--user", "is-active", u], capture_output=True, text=True)
        linhas.append(f"{u}: {r.stdout.strip() or r.stderr.strip()}")
    return "\n".join(linhas)


def _varrer(texto: str) -> str:
    sys.path.insert(0, str(RAIZ / "src"))
    from pqbr.seguranca.barreira import exigir_limpo
    try:
        exigir_limpo(texto, "log"); return "limpo"
    except Exception as e:
        return f"bloqueado: {type(e).__name__}"


def chamar(nome: str, a: dict) -> str:
    sys.path.insert(0, str(RAIZ / "src"))
    from pqbr.kit import paperclip_api as pc
    if nome == "docs_ler": return _docs_ler(a["caminho"])
    if nome == "paperclip_comentar": pc.comentar(a["issue"], a["texto"]); return "ok"
    if nome == "paperclip_status": pc.atualizar(a["issue"], status=a["status"]); return "ok"
    if nome == "paperclip_criar_issue":
        me = pc.eu(); r = pc.criar_issue(me["companyId"], title=a["titulo"], description=a["descricao"], status="todo")
        return r.get("identifier", "ok")
    if nome == "temporal_listar": return _temporal_listar(a.get("consulta", ""))
    if nome == "saude_servicos": return _saude()
    if nome == "camofox_saude": return _camofox_saude()
    if nome == "notebooklm_enfileirar": return "EM CONSTRUÇÃO: fila NotebookLM ainda sem workflow de pedido; registrado no comentário."
    if nome == "seguranca_varrer": return _varrer(a["texto"])
    raise KeyError(nome)


def main() -> None:
    papel = os.environ.get("PQBR_KIT_PAPEL", "")
    permitidas = PAPEIS.get(papel, [])
    for linha in sys.stdin:
        try:
            msg = json.loads(linha)
        except json.JSONDecodeError:
            continue
        mid, met = msg.get("id"), msg.get("method")
        if mid is None:
            continue
        if met == "initialize":
            res = {"protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
                   "capabilities": {"tools": {}}, "serverInfo": {"name": "pqbr-kit", "version": "0.1"}}
        elif met == "tools/list":
            res = {"tools": [{"name": n, "description": FERR[n][0], "inputSchema": {"type": "object",
                    "properties": {k: {"type": v} for k, v in FERR[n][1].items()}, "required": list(FERR[n][1])}}
                   for n in permitidas]}
        elif met == "tools/call":
            n = msg["params"]["name"]
            if n not in permitidas:
                res = {"content": [{"type": "text", "text": f"negado para o papel {papel or '?'}"}], "isError": True}
            else:
                try:
                    res = {"content": [{"type": "text", "text": chamar(n, msg["params"].get("arguments") or {})}]}
                except Exception as e:
                    res = {"content": [{"type": "text", "text": f"erro: {type(e).__name__}: {str(e)[:300]}"}], "isError": True}
        else:
            print(json.dumps({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "método"}}), flush=True)
            continue
        print(json.dumps({"jsonrpc": "2.0", "id": mid, "result": res}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
