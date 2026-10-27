"""Pacote de onboarding do agente externo (t89u). Fonte única do AGENTS.md gerado (scripts/mcp/gerar_agents_md.py).
Recortes dos docs canônicos, sem duplicar conteúdo: o pacote aponta e resume, os docs continuam a fonte."""
from __future__ import annotations
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
LIMITE = 6000
PROTOCOLO = """1. `onboarding` (este pacote).
2. `buscar_memoria` sobre o assunto antes de agir; em conflito, vale o doc canônico.
3. Implementar no checkout com commit local (sem push) e registrar a decisão em docs/DECISOES-LOG.md e a versão em CHANGELOG.md (SemVer).
4. Atualizar docs/ESTADO-ATUAL.md a cada correção ou pendência resolvida (o hook pre-commit exige quando ROADMAP/LACUNAS/DECISOES-LOG/CHANGELOG mudam).
5. Ao final, `registrar_alteracao` com o hash do commit e `tipo` (alteracao | correcao | pendencia_resolvida), citando arquivos; ele grava também o handoff. Sem commit, `registrar_memoria`. Sem esse registro a alteração não conta como entregue."""


def _ler(rel: str) -> str:
    p = RAIZ / rel
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _secoes(txt: str, nivel: str = "## ") -> list[str]:
    return [s for s in re.split(rf"\n(?={nivel})", txt) if s.startswith(nivel)]


def pacote() -> str:
    roadmap = _ler("docs/ROADMAP.md")
    fase = next((s for s in _secoes(roadmap) if "Conhecimento e agente externo" in s.splitlines()[0]), "")
    decisoes = _secoes(_ler("docs/DECISOES-LOG.md"))[-5:]
    mapa = sorted(p.name for p in (RAIZ / "docs/mapa").glob("*.mmd"))
    partes = [
        "# PQBR — onboarding do agente (gerado; não editar à mão)",
        _ler("docs/ESTADO-ATUAL.md").replace("# ESTADO ATUAL", "## ESTADO ATUAL", 1)[:LIMITE],
        "Fontes canônicas: docs/ESTADO-ATUAL.md (onde estamos), docs/REGRAS.md, docs/DECISOES-LOG.md, docs/ROADMAP.md, "
        "docs/LACUNAS-fluxo.md, docs/ARQUITETURA.md, docs/AGENTES.md, docs/mapa/. Em conflito, vale o doc canônico. "
        "O briefing do YT-LLM está em docs/_obsoleto/BRIEFING-novo-agente-pqbr.md e não é procedimento.",
        _ler("docs/operacao/AGENTS-base.md"),  # instruções operacionais manuais (ex-AGENTS.md)
        "## Conexão MCP", "Servidor MCP da PQBR (só tailnet): porta HTTPS 8791 do host pc na tailnet (nome MagicDNS fora do repo), caminho /mcp, Streamable HTTP, Bearer token por cliente. Ferramentas conforme o papel: onboarding, buscar_memoria, codigo, estado (leitura) e registrar_memoria, registrar_alteracao (única escrita: Hindsight).",
        "## Protocolo obrigatório do agente externo (t95u/t96u)", PROTOCOLO,
        "## BRIEFING", "Histórico, fora do procedimento: docs/_obsoleto/BRIEFING-novo-agente-pqbr.md (herança do YT-LLM, 24/10/2026). O que vale está em REGRAS, CONTRATO-EDITORIAL e ESTADO-ATUAL.",
        "## REGRAS (início)", _ler("docs/REGRAS.md")[:LIMITE],
        "## Decisões recentes", "\n\n".join(d[:1500] for d in decisoes),
        "## Fase atual do ROADMAP", fase,
        "## LACUNAS (início)", _ler("docs/LACUNAS-fluxo.md")[:LIMITE // 2],
        "## Mapa visual", "docs/mapa/index.html (servido em :8088) — diagramas: " + ", ".join(mapa) + " · aba Roadmap gerada de ROADMAP + ESTADO-ATUAL (scripts/mapa/roadmap.py; edite as fontes, nunca o HTML)",
    ]
    return "\n\n".join(p for p in partes if p)
