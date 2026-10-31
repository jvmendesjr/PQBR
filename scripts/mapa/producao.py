"""Aba Produção de episódios do painel (José pt162u). Gera HTML de docs/mapa/producao-episodios.json."""
from __future__ import annotations
import html, json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "docs/mapa/producao-episodios.json"

SELO = {
    "ativo": ("Ativo no worker", "#e8f5e9", "#2e7d32"),
    "codigo_falta_reinicio": ("Em código · falta reinício", "#fff3e0", "#ef6c00"),
    "desligado_pausado": ("Desligado / pausado", "#eceff1", "#546e7a"),
    "nao_existe": ("Não existe", "#fdecea", "#c62828"),
}


def carregar(path: Path | None = None) -> dict:
    return json.loads((path or DADOS).read_text(encoding="utf-8"))


def _selo(status: str) -> str:
    rotulo, bg, fg = SELO.get(status, ("?", "#eee", "#333"))
    return (
        f'<span class="selo" style="background:{bg};color:{fg};border:1px solid {fg}33">'
        f"{html.escape(rotulo)}</span>"
    )


def _tab(rows: list[str], heads: list[str]) -> str:
    th = "".join(f"<th>{html.escape(h)}</th>" for h in heads)
    return (
        f'<div class="wrap"><table class="prod"><thead><tr>{th}</tr></thead>'
        f"<tbody>{chr(10).join(rows)}</tbody></table></div>"
    )


CSS = (
    "<style>"
    ".prod{width:100%;border-collapse:collapse;font-size:12.5px}"
    ".prod th,.prod td{border:1px solid var(--l);padding:6px 8px;vertical-align:top;text-align:left}"
    ".prod th{background:#f4f6f8;font-weight:600}"
    ".selo{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600;white-space:nowrap}"
    ".prod .n{width:2.2em;color:var(--m)}"
    "</style>"
)


def secao(d: dict | None = None) -> str:
    d = d or carregar()
    rows_e = []
    for e in d["etapas"]:
        rows_e.append(
            "<tr>"
            f'<td class="n">{e["n"]}</td>'
            f'<td><b>{html.escape(e["nome"])}</b><br><span class="nota">{html.escape(e["objetivo"])}</span></td>'
            f'<td><code>{html.escape(e["wf_activity"])}</code><br><span class="nota">fila {html.escape(e["fila"])}</span></td>'
            f'<td>{html.escape(e["responsavel"])}</td>'
            f'<td>{html.escape(e["contratos"])}</td>'
            f'<td>{_selo(e["status"])}</td>'
            "</tr>"
        )
    rows_o = []
    for w in d["outros_workflows"]:
        rows_o.append(
            "<tr>"
            f'<td><code>{html.escape(w["nome"])}</code></td>'
            f'<td>{html.escape(w["fila"])}</td>'
            f'<td>{html.escape(w["funcao"])}</td>'
            f'<td>{_selo(w["status"])}</td>'
            "</tr>"
        )
    mer = html.escape(d["mermaid"].strip())
    return (
        f'<section id="producao" class="prodsec"><h2>{html.escape(d["titulo"])}</h2>'
        f'<p class="nota">{html.escape(d["nota"])} · dados v{html.escape(d["versao"])} · '
        f'<span class="arq">producao-episodios.json</span></p>'
        + CSS
        + "<h3>Etapas (tema → publicação)</h3>"
        + _tab(rows_e, ["#", "Etapa / objetivo", "Workflow ou activity · fila", "Responsável", "Contratos", "Status"])
        + "<h3>Outros workflows</h3>"
        + _tab(rows_o, ["Workflow", "Fila", "Função", "Status"])
        + f'<h3>Fluxo</h3><div class="wrap"><pre class="mermaid">\n{mer}\n</pre></div></section>'
    )


if __name__ == "__main__":
    s = secao()
    assert 'id="producao"' in s and "direcao_cenas_nlm" in s
    print("ok", len(s))
