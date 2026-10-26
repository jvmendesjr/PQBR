"""Servidor MCP da PQBR (t89u). Fica DENTRO da aplicação e só é acessível pela tailnet:
bind 127.0.0.1:PQBR_MCP_PORTA (8791) + `tailscale serve` (tailnet only, nunca Funnel/0.0.0.0).
Transporte: MCP Streamable HTTP (POST /mcp, respostas JSON; sem SSE). Só leitura: nenhuma ferramenta escreve ou age.
Identidade: `Authorization: Bearer <token>`; o token é procurado (sha256) em ~/.pqbr/secrets/mcp_clientes.json (600),
que mapeia cliente → papel da config/politica_papeis.json. Token ou papel desconhecido ⇒ 401/negado."""
from __future__ import annotations
import hashlib, hmac, json, os, stat, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

from ..contratos.politica import carregar, AcessoNegado
from . import onboarding

HOST = "127.0.0.1"
PORTA = int(os.environ.get("PQBR_MCP_PORTA", "8791"))
CLIENTES = Path(os.environ.get("PQBR_MCP_CLIENTES", str(Path.home() / ".pqbr/secrets/mcp_clientes.json")))
VERSAO = "0.1.0"

FERR: dict[str, tuple[str, str | None, dict]] = {  # nome: (descrição, ferramenta exigida na política, parâmetros)
    "onboarding": ("Pacote de entrada no projeto (BRIEFING, REGRAS, DECISOES recentes, estado do ROADMAP, LACUNAS, mapa).", None, {}),
    "buscar_memoria": ("Busca no Hindsight (bank pqbr), só nas tags que o seu papel pode ler.", "memoria_buscar", {"consulta": "string"}),
    "codigo": ("GitNexus query|context|impact, filtrado pelos caminhos do seu papel.", "gitnexus_consultar", {"comando": "string", "alvo": "string"}),
    "estado": ("Estado só leitura: serviços systemd, workflows recentes do Temporal, gates/temas.", "estado_ler", {}),
}


def _carregar_clientes(arq: Path = CLIENTES) -> dict[str, str]:
    """{sha256(token): papel}. Arquivo precisa ser 600; senão nada é aceito (fail-closed)."""
    try:
        if stat.S_IMODE(arq.stat().st_mode) & 0o077:
            return {}
        d = json.loads(arq.read_text())
    except (OSError, ValueError):
        return {}
    return {c["sha256"]: c["papel"] for c in d.get("clientes", []) if c.get("sha256") and c.get("papel")}


def papel_do_token(token: str | None, clientes: dict[str, str]) -> str | None:
    if not token:
        return None
    h = hashlib.sha256(token.encode()).hexdigest()
    for k, p in clientes.items():
        if hmac.compare_digest(k, h):
            return p
    return None


def ferramentas_do_papel(papel: str) -> list[str]:
    pol = carregar().de(papel)  # AcessoNegado se desconhecido
    return [n for n, (_, req, _) in FERR.items() if req is None or req in pol.ferramentas]


def _estado() -> str:
    from ..kit import mcp_kit
    partes = ["## Serviços", mcp_kit._saude()]
    try:
        partes += ["## Temporal (20 mais recentes)", mcp_kit._temporal_listar("")]
    except Exception as e:
        partes += ["## Temporal", f"indisponível: {type(e).__name__}"]
    return "\n".join(partes)


def executar(papel: str, nome: str, a: dict, impl: dict[str, Callable[..., Any]] | None = None) -> str:
    if nome not in ferramentas_do_papel(papel):
        raise AcessoNegado(f"{nome} negado para {papel}")
    impl = impl or {}
    if nome == "onboarding":
        return (impl.get("onboarding") or onboarding.pacote)()
    if nome == "buscar_memoria":
        from ..storage.hindsight import recuperar
        r = (impl.get("buscar_memoria") or recuperar)(str(a.get("consulta", ""))[:500], papel=papel)
        return json.dumps([{"texto": m.get("text"), "tags": m.get("tags"), "data": m.get("mentioned_at") or m.get("date")}
                           for m in r[:20]], ensure_ascii=False)
    if nome == "codigo":
        from ..integrations.gitnexus import consultar
        return json.dumps((impl.get("codigo") or consultar)(papel, str(a.get("comando")), str(a.get("alvo", ""))[:200]),
                          ensure_ascii=False)[:30000]
    if nome == "estado":
        return (impl.get("estado") or _estado)()
    raise AcessoNegado(nome)


def tratar(msg: dict, papel: str, impl: dict | None = None) -> dict | None:
    mid, met = msg.get("id"), msg.get("method")
    if mid is None:
        return None  # notificação
    if met == "initialize":
        res = {"protocolVersion": (msg.get("params") or {}).get("protocolVersion", "2025-03-26"),
               "capabilities": {"tools": {}}, "serverInfo": {"name": "pqbr", "version": VERSAO},
               "instructions": f"Papel: {papel}. Chame `onboarding` primeiro. Tudo é só leitura."}
    elif met == "ping":
        res = {}
    elif met == "tools/list":
        res = {"tools": [{"name": n, "description": FERR[n][0], "inputSchema": {"type": "object",
                "properties": {k: {"type": v} for k, v in FERR[n][2].items()}, "required": list(FERR[n][2])}}
               for n in ferramentas_do_papel(papel)]}
    elif met == "tools/call":
        p = msg.get("params") or {}
        try:
            texto, erro = executar(papel, p.get("name", ""), p.get("arguments") or {}, impl), False
        except AcessoNegado as e:
            texto, erro = f"negado: {e}", True
        except Exception as e:
            texto, erro = f"erro: {type(e).__name__}", True
        from ..seguranca.barreira import exigir_limpo
        try:
            exigir_limpo(texto, "log")
        except Exception:
            texto, erro = "resposta bloqueada pela barreira", True
        res = {"content": [{"type": "text", "text": texto}], "isError": erro}
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "método não suportado"}}
    return {"jsonrpc": "2.0", "id": mid, "result": res}


class Handler(BaseHTTPRequestHandler):
    server_version = "pqbr-mcp"

    def log_message(self, *a):  # nada de cabeçalhos/tokens em log
        pass

    def _enviar(self, codigo: int, corpo: Any = None):
        b = b"" if corpo is None else json.dumps(corpo, ensure_ascii=False).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/saude":
            return self._enviar(200, {"status": "ok", "versao": VERSAO})
        self._enviar(405)  # sem SSE

    def do_POST(self):
        if self.path.rstrip("/") != "/mcp":
            return self._enviar(404)
        aut = self.headers.get("Authorization", "")
        papel = papel_do_token(aut[7:] if aut.startswith("Bearer ") else None, _carregar_clientes())
        try:
            carregar().de(papel)
        except AcessoNegado:
            return self._enviar(401, {"error": "não autorizado"})
        try:
            n = min(int(self.headers.get("Content-Length", "0")), 1_000_000)
            msg = json.loads(self.rfile.read(n))
        except ValueError:
            return self._enviar(400, {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse"}})
        if isinstance(msg, list):
            out = [r for r in (tratar(m, papel) for m in msg) if r]
        else:
            out = tratar(msg, papel)
        if not out:
            return self._enviar(202)
        self._enviar(200, out)


def main() -> None:
    srv = ThreadingHTTPServer((HOST, PORTA), Handler)
    print(f"pqbr-mcp {VERSAO} em http://{HOST}:{PORTA}/mcp", file=sys.stderr, flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
