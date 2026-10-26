"""ESTADO-ATUAL (t98u/t99u): verificação determinística de que o handoff acompanha as mudanças de governança.
Regra: commit que toca ROADMAP/LACUNAS/DECISOES-LOG/CHANGELOG precisa tocar docs/ESTADO-ATUAL.md também.
Commits triviais (código, outros docs) não são afetados. Puro; o git fica no script/hook."""
from __future__ import annotations
import re
from pathlib import Path

ESTADO = "docs/ESTADO-ATUAL.md"
GATILHOS = frozenset({"docs/ROADMAP.md", "docs/LACUNAS-fluxo.md", "docs/DECISOES-LOG.md", "CHANGELOG.md"})
TIPOS_EXIGEM = frozenset({"correcao", "pendencia_resolvida"})
RAIZ = Path(__file__).resolve().parents[3]


def exige_estado(arquivos) -> list[str]:
    """Gatilhos tocados sem ESTADO-ATUAL junto (vazio ⇒ ok)."""
    a = set(arquivos)
    return [] if ESTADO in a else sorted(a & GATILHOS)


def proximo_passo(txt: str | None = None) -> str:
    if txt is None:
        p = RAIZ / ESTADO
        txt = p.read_text(encoding="utf-8") if p.is_file() else ""
    m = re.search(r"^## Próximo passo\n+(.+?)(?:\n\n|\n## |\Z)", txt, re.S | re.M)
    return " ".join(m.group(1).split())[:400] if m else "ver docs/ESTADO-ATUAL.md"
