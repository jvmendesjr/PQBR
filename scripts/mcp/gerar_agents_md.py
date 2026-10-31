"""Gera AGENTS.md na raiz a partir do onboarding do MCP (t89u). Uso: PYTHONPATH=src python scripts/mcp/gerar_agents_md.py"""
import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(RAIZ / "src"))
from pqbr.mcp.onboarding import pacote  # noqa: E402
from pqbr.seguranca.barreira import exigir_limpo  # noqa: E402
txt = pacote(); exigir_limpo(txt, "log")
(RAIZ / "AGENTS.md").write_text(txt + "\n", encoding="utf-8"); print(f"AGENTS.md: {len(txt)} chars")
