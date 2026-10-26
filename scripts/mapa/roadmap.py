"""t120u: aba Roadmap do painel (só leitura), gerada de docs/ROADMAP.md e docs/ESTADO-ATUAL.md.
Feito = itens `- [x]` do ROADMAP + pendências P* marcadas **Feito**; Falta = itens `- [ ]` do ROADMAP;
Próximos passos = "Próximo passo" do ESTADO-ATUAL + pendências P* abertas, na ordem da tabela. Nada digitado à mão."""
from __future__ import annotations
import html, re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ITEM = re.compile(r"^- \[( |x|X)\] (.+)$")


def _limpo(t: str, n: int = 220) -> str:
    t = re.sub(r"~~(.+?)~~", r"\1", t)
    t = re.sub(r"\*\*|__|`", "", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t).strip()
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def parse_roadmap(md: str) -> dict[str, list[tuple[str, str]]]:
    """{"feito": [(fase, texto)], "falta": [...]}: só itens de 1º nível, até o Anexo."""
    fase, out = "", {"feito": [], "falta": []}
    for l in md.splitlines():
        if l.startswith("## "):
            if l.startswith("## Anexo"):
                break
            fase = _limpo(l[3:], 90)
            continue
        m = ITEM.match(l)
        if m:
            out["feito" if m.group(1).lower() == "x" else "falta"].append((fase, _limpo(m.group(2))))
    return out


def parse_estado(md: str) -> dict:
    prox = re.search(r"^## Próximo passo\s*\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    pend = []
    for l in md.splitlines():
        if not l.startswith("| P"):
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) >= 5 and re.fullmatch(r"P\d+", c[0]):
            pend.append({"id": c[0], "texto": _limpo(c[1]), "dono": _limpo(c[3], 40), "bloqueio": _limpo(c[4], 80),
                         "feito": c[1].lstrip("* ").lower().startswith("feito")})
    return {"proximo": _limpo(" ".join(prox.group(1).split()), 400) if prox else "", "pendencias": pend}


def dados(roadmap: str | None = None, estado: str | None = None) -> dict:
    r = parse_roadmap(roadmap if roadmap is not None else (RAIZ / "docs/ROADMAP.md").read_text(encoding="utf-8"))
    e = parse_estado(estado if estado is not None else (RAIZ / "docs/ESTADO-ATUAL.md").read_text(encoding="utf-8"))
    feito = r["feito"] + [("ESTADO-ATUAL", f"{p['id']} {p['texto']}") for p in e["pendencias"] if p["feito"]]
    prox = ([("Próximo passo", e["proximo"])] if e["proximo"] else []) + \
           [(p["id"], f"{p['texto']} — {p['dono']} · {p['bloqueio']}") for p in e["pendencias"] if not p["feito"]]
    return {"feito": feito, "falta": r["falta"], "proximos": prox}


def _grupos(itens: list[tuple[str, str]], aberto: bool) -> str:
    g: dict[str, list[str]] = {}
    for k, t in itens:
        g.setdefault(k or "Geral", []).append(t)
    op = " open" if aberto else ""
    return "".join(f"<details{op}><summary>{html.escape(k)} ({len(ts)})</summary><ul>"
                   + "".join(f"<li>{html.escape(t)}</li>" for t in ts) + "</ul></details>" for k, ts in g.items())


CSS = ("<style>.rm h3{font-size:14px;margin:12px 0 4px}.rm details{margin:2px 0}.rm summary{cursor:pointer;color:var(--a);font-size:13px}"
       ".rm ul,.rm ol{margin:4px 0 8px 18px;padding:0;font-size:13px}.rm .ok{color:#2e7d32}.rm .fa{color:#b26a00}.rm .px{color:#33506b}</style>")


def secao(d: dict | None = None) -> str:
    d = d or dados()
    prox = "<ol>" + "".join(f"<li><b>{html.escape(g)}</b>: {html.escape(t)}</li>" for g, t in d["proximos"]) + "</ol>"
    return ('<section id="roadmap" class="rm"><h2>Roadmap</h2><p class="nota">Só leitura. Gerado de docs/ROADMAP.md e '
            "docs/ESTADO-ATUAL.md (editados só pelos agentes) a cada geração do index.</p>" + CSS
            + f'<h3 class="px">Próximos passos ({len(d["proximos"])})</h3>{prox}'
            + f'<h3 class="fa">Falta ({len(d["falta"])})</h3>{_grupos(d["falta"], True)}'
            + f'<h3 class="ok">Feito ({len(d["feito"])})</h3>{_grupos(d["feito"], False)}</section>')
