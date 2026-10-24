"""Servidor MCP `pqbr-kit` (stdio, JSON-RPC, só stdlib + kit). Expõe só as ferramentas do papel em PQBR_KIT_PAPEL.
Efeito externo nunca é direto: Camofox e NotebookLM só entram como workflow nas filas do Temporal (concorrência 1)."""
from __future__ import annotations
import asyncio, json, os, subprocess, sys
from pathlib import Path

RAIZ = Path("/home/pc/Workspace/PQBR")
DOCS = RAIZ / "docs"
PROIBIDO = ("arquivo", "pesquisas")
UNIDADES = ["pqbr-camofox", "pqbr-camofox-worker", "pqbr-notebooklm-worker", "pqbr-temporal-worker", "paperclipai", "9router"]

# Lista fechada por papel (AGENTES §2, §6). Leitura de docs e API do Paperclip para todos os papéis com ferramenta.
COMUM = ["docs_ler", "paperclip_comentar", "paperclip_status", "paperclip_criar_issue"]
PAPEIS = {  # 8 papéis (t512/t516); legado Paperclip em retirada
    "diretor": COMUM + ["temporal_listar", "saude_servicos", "segunda_opiniao", "memoria_buscar"],
    "lider-editorial": COMUM + ["notebooklm_enfileirar"],
    "pesquisador-origem": COMUM + ["notebooklm_enfileirar"],
    "auditor": COMUM + ["segunda_opiniao"],
    "lider-compliance": COMUM + ["segunda_opiniao"],
    "guardiao-seguranca": COMUM + ["temporal_listar", "saude_servicos", "seguranca_varrer", "seguranca_varrer_logs", "segunda_opiniao"],
    "observador": COMUM + ["temporal_listar", "saude_servicos", "camofox_saude", "memoria_buscar", "memoria_registrar"],
    "dev": COMUM + ["temporal_listar", "memoria_buscar"],   # só diagnostica e propõe
}

FERR = {
    "docs_ler": ("Lê um arquivo de docs/ (canônicos; arquivo/ e pesquisas/ bloqueados).", {"caminho": "string"}),
    "paperclip_comentar": ("Comenta numa issue (como o próprio agente).", {"issue": "string", "texto": "string"}),
    "paperclip_status": ("Muda o status de uma issue.", {"issue": "string", "status": "string"}),
    "paperclip_criar_issue": ("Abre issue na PQBR (ticket pré-estruturado).", {"titulo": "string", "descricao": "string"}),
    "temporal_listar": ("Lista execuções recentes de workflows da PQBR (só leitura).", {"consulta": "string"}),
    "saude_servicos": ("Estado dos serviços da PQBR (systemd, só leitura).", {}),
    "camofox_saude": ("Enfileira CamofoxSaudeWorkflow na fila camofox-pqbr e devolve o resultado.", {}),
    "notebooklm_enfileirar": ("Pedido ao NotebookLM pela fila notebooklm-pqbr (um por vez, caderno efêmero 'Short - <slug>', "
                              "contador diário). tipo=pesquisa (espera e devolve a resposta; use pergunta) ou short (devolve o id do "
                              "workflow; vídeo vertical --format short). fonte = roteiro/briefing (vira a fonte do caderno).",
                              {"tipo": "string", "slug": "string", "fonte": "string", "pergunta": "string"}),
    "memoria_buscar": ("Busca na memória da PQBR (Hindsight, bank pqbr): decisões, incidentes, commits, lições. Use ANTES de corrigir/decidir.", {"consulta": "string"}),
    "memoria_registrar": ("Registra uma lição no Hindsight (passa pela barreira de segredos/PII). Formato: falha → causa → correção → como evitar.", {"licao": "string"}),
    "segunda_opiniao": ("Segunda opinião independente no combo core-revisao (t421). OBRIGATÓRIA antes de pausar agente/bloquear publicação (Guardião) e antes de aplicar correção de playbook (Diretor). Devolve CONCORDO/DISCORDO + motivo.", {"contexto": "string", "decisao": "string"}),
    "seguranca_varrer_logs": ("Varre os run-logs da PQBR das últimas N horas (padrão 24) com o detector de segredos; devolve só contagens por arquivo, nunca o valor.", {"horas": "number"}),
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


def _notebooklm(a: dict) -> str:
    sys.path.insert(0, str(RAIZ / "src"))
    from pqbr.workflows.notebooklm import NotebookLMWorkflow, PedidoNotebookLM, FILA_NOTEBOOKLM
    import uuid
    p = PedidoNotebookLM(tipo=a.get("tipo", "pesquisa"), slug=a["slug"], fonte=a["fonte"], pergunta=a.get("pergunta") or None,
                         solicitante=os.environ.get("PQBR_KIT_PAPEL", "kit"))
    wid = f"nlm-{p.tipo}-{p.slug}-{uuid.uuid4().hex[:6]}"
    async def f(c):
        if p.tipo == "short":
            await c.start_workflow(NotebookLMWorkflow.run, p, id=wid, task_queue=FILA_NOTEBOOKLM)
            return f"enfileirado: {wid} (acompanhe com temporal_listar)"
        r = await c.execute_workflow(NotebookLMWorkflow.run, p, id=wid, task_queue=FILA_NOTEBOOKLM)
        return r.model_dump_json()
    return _temporal(f)


def _saude() -> str:
    linhas = []
    for u in UNIDADES:
        r = subprocess.run(["systemctl", "--user", "is-active", u], capture_output=True, text=True)
        linhas.append(f"{u}: {r.stdout.strip() or r.stderr.strip()}")
    return "\n".join(linhas)


def _varrer_logs(horas: float = 24) -> str:
    import time, re
    sys.path.insert(0, str(RAIZ / "src"))
    from pqbr.seguranca import segredos
    co = os.environ.get("PQBR_COMPANY_ID", "be3980d6-51ae-4cee-b85f-923b4568188c")
    base = Path.home() / ".paperclip/instances/default/data/run-logs" / co
    if not base.is_dir():
        base = Path("/home/pc/.paperclip/instances/default/data/run-logs") / co
    lim = time.time() - float(horas) * 3600
    achados, n = [], 0
    extra = [("paperclip_key_env", re.compile("PAPERCLIP_API_" + "KEY" + r"=(?!\*\*\*REDACTED)(?!via-relay)[^\s\\\"]{12,}")),
             ("ninerouter_key_env", re.compile("NINEROUTER_API_" + "KEY" + r"=(?!\*\*\*REDACTED)(?!via-relay)[^\s\\\"]{12,}")),
             ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"))]
    for f in base.glob("*/*.ndjson"):
        if f.stat().st_mtime < lim: continue
        n += 1; t = f.read_text(errors="ignore")
        c = {nome: len(rx.findall(t)) for nome, rx in list(segredos.REGRAS) + extra if rx.findall(t)} if hasattr(segredos, "REGRAS") else \
            {nome: len(rx.findall(t)) for nome, rx in extra if rx.findall(t)}
        if c: achados.append(f"{f.parent.name}/{f.name}: {c}")
    return f"{n} logs varridos ({horas} h); " + ("ACHADOS:\n" + "\n".join(achados) if achados else "nada encontrado")


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
    if nome == "notebooklm_enfileirar": return _notebooklm(a)
    if nome == "seguranca_varrer": return _varrer(a["texto"])
    if nome == "memoria_buscar":
        import urllib.request
        u = os.environ.get("HINDSIGHT_URL", "http://127.0.0.1:8890")
        corpo = {"query": a["consulta"][:500], "max_tokens": 1500}
        r = urllib.request.Request(f"{u}/v1/default/banks/pqbr/memories/recall", method="POST", headers={"Content-Type": "application/json"},
                                   data=json.dumps(corpo).encode())
        with urllib.request.urlopen(r, timeout=60) as resp:
            res = json.load(resp).get("results", [])
        return "\n".join(f"- {x.get('text', '')[:400]}" for x in res[:8]) or "nada na memória"
    if nome == "memoria_registrar":
        from pqbr.storage.hindsight import reter
        reter(a["licao"][:3000], f"PQBR lição registrada por {os.environ.get('PQBR_KIT_PAPEL', '?')}"); return "registrado"
    if nome == "segunda_opiniao":
        from pqbr.kit.agente_texto import segunda_leitura; from pqbr.kit import router9
        from pqbr.seguranca.barreira import exigir_limpo
        r = segunda_leitura(os.environ.get("PQBR_MODELO_REVISAO") or router9.combo("revisao"), a["contexto"], a["decisao"])
        exigir_limpo(r, "log"); return r
    if nome == "seguranca_varrer_logs": return _varrer_logs(a.get("horas", 24) or 24)
    raise KeyError(nome)


def _imprimir_jsonrpc(obj: dict) -> None:
    """Valida a resposta inteira e não ecoa ID/dados se a barreira bloquear."""
    from pqbr.seguranca.barreira import exigir_limpo
    try:
        exigir_limpo(obj, "log")
        linha = json.dumps(obj, ensure_ascii=False)
    except Exception:
        identificador = obj.get("id")
        try:
            exigir_limpo(identificador, "log")
        except Exception:
            identificador = None
        seguro = {"jsonrpc": "2.0", "id": identificador,
                  "error": {"code": -32000, "message": "resposta bloqueada"}}
        try:
            exigir_limpo(seguro, "log")
            linha = json.dumps(seguro, ensure_ascii=False)
        except Exception:
            return
    print(linha, flush=True)

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
            _imprimir_jsonrpc({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "método"}})
            continue
        _imprimir_jsonrpc({"jsonrpc": "2.0", "id": mid, "result": res})


if __name__ == "__main__":
    main()
