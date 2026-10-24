"""t517: confere se o mapa (docs/mapa/*.mmd) cobre o código. Só lista divergências; NUNCA edita o mapa
(agentes não mudam o mapa sozinhos — mudança só por proposta aprovada pelo José).
Uso: python scripts/mapa/verificar_mapa.py   → exit 1 e lista o que falta."""
from __future__ import annotations
import re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
WF = RAIZ / "src/pqbr/workflows"
MAPA = RAIZ / "docs/mapa"
COBERTURA = {  # workflow → (arquivo do código, diagrama)
    "EpisodioWorkflow": ("episodio.py", "01-episodio.mmd"),
    "PublicacaoWorkflow": ("episodio.py", "01-episodio.mmd"),
    "ReposicaoTemasWorkflow": ("temas.py", "02-reposicao-temas.mmd"),
    "AcessosWorkflow": ("acesso.py", "03-acessos.mmd"),
    "DescartarCadernoTesteWorkflow": ("descarte.py", "04-descarte.mmd"),
    "ApagarCadernoWorkflow": ("pacote.py", "04-descarte.mmd"),
    "VigiaAtualizacoesWorkflow": ("atualizacoes.py", "05-vigia-atualizacoes.mmd"),
}
FORA = {"NotebookLMWorkflow", "CamofoxSaudeWorkflow", "GradeDiariaWorkflow", "EpisodioProducaoWorkflow",
        "RetencaoConsumoWorkflow", "CorrecaoAutonomaWorkflow", "PonteTemporalPaperclipWorkflow",
        "AtorSessaoCandidato", "CorrecaoCandidata"}  # fora do mapa por ora (decisão)


def corpo_classe(src: str, nome: str) -> str:
    m = re.search(rf"^class {nome}\b.*?(?=^class |\Z)", src, re.S | re.M)
    return m.group(0) if m else ""


def divergencias() -> list[str]:
    out = []
    todos = set()
    for f in WF.glob("*.py"):
        todos |= set(re.findall(r"@workflow\.defn[^\n]*\n\s*class (\w+)", f.read_text(encoding="utf-8")))
    for w in sorted(todos - set(COBERTURA) - FORA):
        out.append(f"workflow novo fora do mapa: {w}")
    for w, (arq, mmd) in COBERTURA.items():
        corpo = corpo_classe((WF / arq).read_text(encoding="utf-8"), w)
        if not corpo:
            out.append(f"{w}: não encontrado em {arq}"); continue
        texto = (MAPA / mmd).read_text(encoding="utf-8")
        nomes = set(re.findall(r"execute_activity\(\s*\"?(\w+)", corpo))
        for n in sorted(nomes):
            if n not in texto:
                out.append(f"{mmd}: falta a activity {n} ({w})")
    return out


if __name__ == "__main__":
    d = divergencias()
    print("\n".join(d) or "mapa cobre o código")
    sys.exit(1 if d else 0)
