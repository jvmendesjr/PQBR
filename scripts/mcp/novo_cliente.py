"""Cria um token de cliente do MCP da PQBR (t89u). Uso: python scripts/mcp/novo_cliente.py <nome> <papel>
Grava só o sha256 em ~/.pqbr/secrets/mcp_clientes.json (600) e o token em ~/.pqbr/secrets/mcp_token_<nome> (600).
Nunca imprime o token."""
import hashlib, json, os, secrets, sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(RAIZ / "src"))
from pqbr.contratos.politica import carregar  # noqa: E402
nome, papel = sys.argv[1], sys.argv[2]
carregar().de(papel)
if papel != "mantenedor":
    sys.exit("t114u: o MCP externo é exclusivo do papel mantenedor")
d = Path.home() / ".pqbr/secrets"; d.mkdir(parents=True, exist_ok=True); os.chmod(d, 0o700)
arq = d / "mcp_clientes.json"
dados = json.loads(arq.read_text()) if arq.exists() else {"clientes": []}
tok = secrets.token_urlsafe(32)
dados["clientes"] = [c for c in dados["clientes"] if c["nome"] != nome] + [{"nome": nome, "papel": papel, "sha256": hashlib.sha256(tok.encode()).hexdigest()}]
fd = os.open(arq, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600); os.write(fd, json.dumps(dados, indent=1).encode()); os.close(fd); os.chmod(arq, 0o600)
t = d / f"mcp_token_{nome}"; fd = os.open(t, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600); os.write(fd, tok.encode()); os.close(fd); os.chmod(t, 0o600)
print(f"cliente {nome} → papel {papel}; token em {t} (600)")
