#!/usr/bin/env python3
"""MCP read-only dos documentos canônicos da PQBR (t412). Só lê docs/*.md e docs/<sub>/*.md fora de arquivo/ e pesquisas/."""
import json, re, sys
from pathlib import Path
RAIZ = Path("/home/pc/Workspace/PQBR/docs").resolve()
BLOQ = {"arquivo", "pesquisas"}
MAX = 60000

def _permitido(p: Path) -> bool:
    try:
        r = p.resolve(strict=True)
        rel = r.relative_to(RAIZ)
    except (OSError, ValueError):
        return False
    return r.is_file() and r.suffix == ".md" and not (set(rel.parts[:-1]) & BLOQ) and not any(x.startswith(".") for x in rel.parts)

def _todos():
    return sorted(str(p.relative_to(RAIZ)) for p in RAIZ.rglob("*.md") if _permitido(p))

def listar(a):
    return "\n".join(_todos())

def ler(a):
    nome = str(a.get("arquivo", ""))
    p = RAIZ / nome
    if not _permitido(p):
        raise ValueError("arquivo não permitido (só docs canônicos; arquivo/ e pesquisas/ bloqueados)")
    t = p.read_text(encoding="utf-8", errors="replace")
    ini = max(int(a.get("inicio", 0) or 0), 0)
    return t[ini:ini + MAX] + ("\n[...cortado; use inicio=%d]" % (ini + MAX) if len(t) > ini + MAX else "")

def buscar(a):
    termo = str(a.get("termo", ""))
    if not termo:
        raise ValueError("termo vazio")
    rx = re.compile(re.escape(termo), re.I); out = []
    for n in _todos():
        for i, l in enumerate((RAIZ / n).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if rx.search(l):
                out.append(f"{n}:{i}: {l[:300]}")
                if len(out) >= 80:
                    return "\n".join(out) + "\n[limite de 80 resultados]"
    return "\n".join(out) or "nada encontrado"

S = {"type": "string"}
TOOLS = {
    "docs_listar": ({"type": "object", "properties": {}}, listar, "Lista os documentos canônicos da PQBR (somente leitura)."),
    "docs_ler": ({"type": "object", "properties": {"arquivo": S, "inicio": {"type": "integer"}}, "required": ["arquivo"]}, ler,
                 "Lê um documento canônico (ex.: REGRAS.md). Somente leitura; arquivo/ e pesquisas/ bloqueados."),
    "docs_buscar": ({"type": "object", "properties": {"termo": S}, "required": ["termo"]}, buscar,
                    "Busca um termo nos documentos canônicos e devolve arquivo:linha."),
}

def responder(id_, result=None, error=None):
    m = {"jsonrpc": "2.0", "id": id_}; m["error" if error else "result"] = error or result
    sys.stdout.write(json.dumps(m, ensure_ascii=False) + "\n"); sys.stdout.flush()

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
                        "capabilities": {"tools": {}}, "serverInfo": {"name": "docs-pqbr", "version": "1.0"}})
    elif met == "tools/list":
        responder(id_, {"tools": [{"name": n, "description": d, "inputSchema": s} for n, (s, _, d) in TOOLS.items()]})
    elif met == "tools/call":
        p = m.get("params", {}); n = p.get("name")
        if n not in TOOLS:
            responder(id_, {"content": [{"type": "text", "text": "ferramenta não permitida"}], "isError": True}); continue
        try:
            responder(id_, {"content": [{"type": "text", "text": TOOLS[n][1](p.get("arguments") or {})}]})
        except Exception as e:  # noqa: BLE001
            responder(id_, {"content": [{"type": "text", "text": f"erro: {e}"[:500]}], "isError": True})
    elif met == "ping":
        responder(id_, {})
    else:
        responder(id_, error={"code": -32601, "message": "método não suportado"})
