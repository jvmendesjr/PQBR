"""Pacote de onboarding do agente externo (t89u). Fonte única do AGENTS.md gerado (scripts/mcp/gerar_agents_md.py).
Recortes dos docs canônicos, sem duplicar conteúdo: o pacote aponta e resume, os docs continuam a fonte."""
from __future__ import annotations
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
LIMITE = 6000


def _ler(rel: str) -> str:
    p = RAIZ / rel
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _secoes(txt: str, nivel: str = "## ") -> list[str]:
    return [s for s in re.split(rf"\n(?={nivel})", txt) if s.startswith(nivel)]


def pacote() -> str:
    roadmap = _ler("docs/ROADMAP.md")
    estado = next((s for s in _secoes(roadmap) if s.startswith("## Estado em")), "")
    fase = next((s for s in _secoes(roadmap) if "Conhecimento e agente externo" in s.splitlines()[0]), "")
    decisoes = _secoes(_ler("docs/DECISOES-LOG.md"))[-5:]
    mapa = sorted(p.name for p in (RAIZ / "docs/mapa").glob("*.mmd"))
    partes = [
        "# PQBR — onboarding do agente (gerado; não editar à mão)",
        "Fontes canônicas: docs/BRIEFING-novo-agente-pqbr.md, docs/REGRAS.md, docs/DECISOES-LOG.md, docs/ROADMAP.md, "
        "docs/LACUNAS-fluxo.md, docs/ARQUITETURA.md, docs/mapa/. Em conflito, vale o doc canônico.",
        _ler("docs/operacao/AGENTS-base.md"),  # instruções operacionais manuais (ex-AGENTS.md)
        "## Conexão MCP", "Servidor MCP da PQBR (só leitura, só tailnet): porta HTTPS 8791 do host pc na tailnet (nome MagicDNS fora do repo), caminho /mcp, Streamable HTTP, Bearer token por cliente. Ferramentas: onboarding, buscar_memoria, codigo, estado — conforme o papel.",
        "## BRIEFING", _ler("docs/BRIEFING-novo-agente-pqbr.md")[:LIMITE],
        "## REGRAS (início)", _ler("docs/REGRAS.md")[:LIMITE],
        "## Decisões recentes", "\n\n".join(d[:1500] for d in decisoes),
        "## Estado do ROADMAP", estado[:LIMITE], fase,
        "## LACUNAS (início)", _ler("docs/LACUNAS-fluxo.md")[:LIMITE // 2],
        "## Mapa visual", "docs/mapa/index.html (servido em :8088) — diagramas: " + ", ".join(mapa),
    ]
    return "\n\n".join(p for p in partes if p)
