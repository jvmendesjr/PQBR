"""lote-runway: fluxo de roteiro (substitui runtime/lote-runway/consolidar.py). Extrai o JSON da resposta do
NotebookLM (só com --extrair e se roteiro.json não existir), valida e renderiza roteiro.md/resumo.json.
Fail-closed: ERR-ROT-02 (narração fora da 3ª pessoa / personagem falando) e cobertura curta → exit 1."""
import json, math, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from pqbr.contratos.roteiro_terceira_pessoa import problemas_roteiro

base = Path("docs/pesquisas/lote-runway"); linhas = []; falhou = False
for d in sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith("_")):
    rj = d / "roteiro.json"
    if not rj.exists():
        if "--extrair" not in sys.argv: print(d.name, "sem roteiro.json"); falhou = True; continue
        m = re.search(r"\{.*\}", (d / "resposta-notebooklm.txt").read_text(), re.S); rj.write_text(json.dumps(json.loads(m.group(0)), ensure_ascii=False, indent=1))
    j = json.loads(rj.read_text())
    falas = j.get("falas", []); cta = j.get("cta_final", "")
    pal = sum(len(f.split()) for f in falas); dur = round(pal / 2.3, 1)
    clipes = [c for s in j.get("cenas", []) for c in s.get("clipes", [])]
    prob = [f"ERR-ROT-02 {p}" for p in problemas_roteiro(j)]
    if not cta.rstrip().lower().endswith("segue o porquê br!"): prob.append("CTA não termina em segue o Porquê BR!")
    if falas and falas[-1].strip() != cta.strip(): prob.append("última fala != cta_final")
    for s in j.get("cenas", []):
        need = max(math.ceil(len(s['fala'].split()) / 2.3 / 5), math.ceil(float(s.get("duracao_s") or 0) / 5))
        if len(s.get("clipes", [])) < need: prob.append(f"cena {s['n']}: {len(s['clipes'])} clipes < {need} (risco imagem parada)")
    if len(clipes) * 5 < dur: prob.append(f"cobertura {len(clipes)*5}s < narração {dur}s")
    md = [f"# {j.get('titulo')}", "", f"Palavras: {pal} · narração estimada: {dur} s · clipes de 5 s: {len(clipes)} ({len(clipes)*5} s)", "",
          "Narração em 3ª pessoa (Larissa narra; o personagem só reage, sem fala nem sincronia labial — ERR-ROT-02).", "", "## Roteiro", ""]
    md += [f"{i+1}. {f}" for i, f in enumerate(falas)] + ["", f"**CTA personalizado:** {cta}", "", "## Decupagem"]
    for s in j.get("cenas", []):
        md += ["", f"### Cena {s['n']} ({s.get('duracao_s')} s) — {s.get('cenario','')}", f"Fala: {s['fala']}"]
        for c in s.get("clipes", []): md += [f"- **{c['id']}** (5 s) imagem: {c['prompt_imagem_en']}", f"  movimento: {c['movimento_en']}"]
    md += ["", "## Fontes"] + [f"- {x}" for x in j.get("fontes", [])] + ["", "## Riscos (catálogo)"] + [f"- {x}" for x in j.get("riscos", [])]
    md += ["", "## Validação automática"] + ([f"- ⚠ {p}" for p in prob] or ["- OK: 3ª pessoa (ERR-ROT-02), CTA personalizado e cobertura ≥ narração"])
    (d / "roteiro.md").write_text("\n".join(md) + "\n")
    falhou |= bool(prob); linhas.append(dict(slug=d.name, titulo=j.get('titulo'), palavras=pal, dur_s=dur, clipes=len(clipes), cta=cta, problemas=prob))
    print(d.name, "|", pal, "pal", dur, "s |", len(clipes), "clipes |", prob or "OK")
json.dump(linhas, open(base / "resumo.json", "w"), ensure_ascii=False, indent=1)
sys.exit(1 if falhou else 0)
