#!/usr/bin/env python3
"""MCP (stdio, só stdlib) do Hermes `pqbr` para o Paperclip (t372).
Única porta do perfil para o Paperclip: ferramentas fixas, empresa fixa (contexto do perfil),
chave lida do .env do perfil e nunca devolvida. Escritas (comentar, criar, atualizar) abrem antes
um heartbeat do próprio agente `pqbr-assistente` e mandam o run id, como o Paperclip exige."""
import json, os, subprocess, sys, urllib.request

PERFIL = os.environ.get("HERMES_PQBR_HOME", "/home/pc/.hermes/profiles/pqbr")
CTX = os.path.join(PERFIL, "paperclip", "context.json")
NODE = "/home/pc/.hermes/node/bin/node"
CLI = "/home/pc/.paperclip/cli/current/node_modules/paperclipai/dist/index.js"


def _chave():
    for linha in open(os.path.join(PERFIL, ".env"), encoding="utf-8"):
        if linha.startswith("PAPERCLIP_PQBR_API_KEY="):
            return linha.split("=", 1)[1].strip()
    raise RuntimeError("sem credencial do Paperclip no perfil")


def _ctx():
    d = json.load(open(CTX, encoding="utf-8"))
    return d["profiles"][d["currentProfile"]]


def _cli(*args, run_id=None):
    env = dict(os.environ)
    env["PAPERCLIP_PQBR_API_KEY"] = _chave()
    cmd = [NODE, CLI, *args, "--context", CTX, "--json"]
    if run_id:
        cmd += ["--run-id", run_id]
    p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=60)
    out = (p.stdout or p.stderr).strip()
    if p.returncode != 0:
        raise RuntimeError(out[:1500])
    return out


def _run_para(issue):
    """Heartbeat do próprio agente ligado à issue; devolve o run id."""
    c = _ctx()
    iid = json.loads(_cli("issue", "get", issue))["id"]
    req = urllib.request.Request(
        f"{c['apiBase']}/api/agents/{c['agentId']}/heartbeat/invoke",
        data=json.dumps({"payload": {"issueId": iid}}).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + _chave()}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["id"]


def _resumo_issues(out):
    return json.dumps([{k: i.get(k) for k in ("identifier", "title", "status", "priority", "assigneeAgentId", "updatedAt")}
                       for i in json.loads(out)], ensure_ascii=False)


S = {"type": "string"}
TOOLS = {
    "listar_issues": ({"type": "object", "properties": {"status": S, "busca": S}},
                      lambda a: _resumo_issues(_cli("issue", "list", *(["--status", a["status"]] if a.get("status") else []),
                                                    *(["--match", a["busca"]] if a.get("busca") else [])))),
    "ver_issue": ({"type": "object", "properties": {"issue": S}, "required": ["issue"]},
                  lambda a: _cli("issue", "get", a["issue"])),
    "ver_comentarios": ({"type": "object", "properties": {"issue": S}, "required": ["issue"]},
                        lambda a: _cli("issue", "comments", a["issue"])),
    "comentar_issue": ({"type": "object", "properties": {"issue": S, "texto": S, "acordar_responsavel": {"type": "boolean"}},
                        "required": ["issue", "texto"]},
                       lambda a: _cli("issue", "comment", a["issue"], "--body", a["texto"],
                                      *(["--resume"] if a.get("acordar_responsavel") else []), run_id=_run_para(a["issue"]))),
    "criar_issue": ({"type": "object", "properties": {"titulo": S, "descricao": S, "agente_responsavel_id": S},
                     "required": ["titulo", "descricao"]},
                    lambda a: _cli("issue", "create", "--title", a["titulo"], "--description", a["descricao"],
                                   *(["--assignee-agent-id", a["agente_responsavel_id"]] if a.get("agente_responsavel_id") else []))),
    "listar_agentes": ({"type": "object", "properties": {}},
                       lambda a: json.dumps([{k: x.get(k) for k in ("id", "name", "title", "status")}
                                             for x in json.loads(_cli("agent", "list"))], ensure_ascii=False)),
    "acordar_agente": ({"type": "object", "properties": {"agente_id": S}, "required": ["agente_id"]},
                       lambda a: _cli("agent", "heartbeat:invoke", a["agente_id"])),
}
DESC = {
    "listar_issues": "Lista as issues da empresa PQBR (filtros opcionais: status csv, busca de texto).",
    "ver_issue": "Mostra uma issue (ex.: PQB-4) e o estado dela.",
    "ver_comentarios": "Lista os comentários/resultados de uma issue.",
    "comentar_issue": "Comenta numa issue; acordar_responsavel=true chama o agente responsável.",
    "criar_issue": "Abre uma issue/ticket pré-estruturado (localização, falha observada, correções sugeridas).",
    "listar_agentes": "Lista os agentes do Paperclip da empresa.",
    "acordar_agente": "Acorda (heartbeat) um agente do Paperclip.",
}


def responder(id_, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id_}
    msg["error" if error else "result"] = error or result
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n"); sys.stdout.flush()


for linha in sys.stdin:
    try:
        m = json.loads(linha)
    except ValueError:
        continue
    met, id_ = m.get("method"), m.get("id")
    if id_ is None:
        continue
    if met == "initialize":
        responder(id_, {"protocolVersion": m.get("params", {}).get("protocolVersion", "2024-11-05"),
                        "capabilities": {"tools": {}}, "serverInfo": {"name": "paperclip-pqbr", "version": "1.0"}})
    elif met == "tools/list":
        responder(id_, {"tools": [{"name": n, "description": DESC[n], "inputSchema": s} for n, (s, _) in TOOLS.items()]})
    elif met == "tools/call":
        p = m.get("params", {}); n = p.get("name")
        if n not in TOOLS:
            responder(id_, {"content": [{"type": "text", "text": "ferramenta não permitida"}], "isError": True}); continue
        try:
            responder(id_, {"content": [{"type": "text", "text": TOOLS[n][1](p.get("arguments") or {})}]})
        except Exception as e:  # noqa: BLE001
            responder(id_, {"content": [{"type": "text", "text": f"erro: {e}"[:1500]}], "isError": True})
    elif met == "ping":
        responder(id_, {})
    else:
        responder(id_, error={"code": -32601, "message": "método não suportado"})
