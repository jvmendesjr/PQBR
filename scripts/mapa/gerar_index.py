"""Regenera docs/mapa/index.html a partir de todos os docs/mapa/*.mmd (t78u). Uso: python scripts/mapa/gerar_index.py"""
from __future__ import annotations
import html, re
from datetime import datetime
from pathlib import Path

MAPA = Path(__file__).resolve().parents[2] / "docs/mapa"
TITULOS = {"00": "Visão geral", "01": "Episódio", "02": "Reposição de temas", "03": "Acessos / Camofox", "04": "Descarte",
           "05": "Vigia de atualizações", "06": "Runs presos", "07": "Cadeia de vídeo", "08": "Identidade Camofox",
           "09": "Agentes", "10": "Catálogo de erros", "11": "Publicação", "12": "Storyboard e elenco"}


def gerar() -> str:
    antigo = (MAPA / "index.html").read_text()
    cabeca = antigo[:antigo.index("<header>")]
    pe = antigo[antigo.index("</main>"):]
    m = re.search(r'<div class="regra">.*?</div>', antigo, re.S)
    regra = m.group(0) if m else ""
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    nav, secoes = [], []
    for f in sorted(MAPA.glob("*.mmd")):
        n = f.name[:2]; t = TITULOS.get(n, f.stem); src = f.read_text()
        notas = " ".join(l[2:].strip() for l in src.splitlines() if l.startswith("%%"))[:600]
        corpo = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("%%"))
        nav.append(f'<a href="#d{n}">{t}</a>')
        secoes.append(f'<section id="d{n}"><h2>{t}</h2><p class="nota">{html.escape(notas)} <span class="arq">{f.name}</span></p>'
                      f'<div class="wrap"><pre class="mermaid">\n{html.escape(corpo)}\n</pre></div></section>')
    return (cabeca + f'<header><h1>PQBR — mapa do sistema</h1><p>Regenerado de docs/mapa/*.mmd em {agora} · ⚠ = não confirmado no código / pendente</p></header>'
            + "<nav>" + "".join(nav) + "</nav><main>" + regra + "".join(secoes) + pe)


if __name__ == "__main__":
    (MAPA / "index.html").write_text(gerar()); print("ok", len(list(MAPA.glob("*.mmd"))), "diagramas")
