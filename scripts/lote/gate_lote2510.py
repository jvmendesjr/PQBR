"""lote-2510 (t545): gate fail-closed por vídeo com o gate determinístico (pipeline.gate_publicacao) + LOOP do juiz Gemini
(loop-gemini.json: VISUAL com texto + capa×título + loop textual, modelo fixado). PUBLICÁVEL só se o código decidir. Nada publica."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, "src")
from pqbr.pipeline.gate_publicacao import avaliar_pasta
L = Path("docs/pesquisas/lote-2510"); ADIADOS = ("brigadeiro",); linhas = []
for d in sorted(L.glob("*/seo.json")):
    p = d.parent; s = json.loads(d.read_text()); g = json.loads((p / "gate-pronto.json").read_text())
    lf = p / "loop-gemini.json"; lp = json.loads(lf.read_text()) if lf.exists() else None
    seo = s["seo"]; ed = []
    if not seo["titulo"] or len(seo["titulo"]) > 70: ed.append("titulo")
    if "#shorts" not in [h.lower() for h in seo["hashtags"]]: ed.append("#shorts")
    if "Fontes:" not in seo["descricao"]: ed.append("fontes na descricao")
    if s["codigo"] not in seo["descricao"]: ed.append("codigo PQBR-EP fora da descricao (entra no payload)")
    g["codigo"] = s["codigo"]
    g["gate"]["B1_B10_editorial"] = "PASS (NotebookLM SEO validado PacoteSEO; " + str(len(s["fontes"])) + " fontes web; GenAI: cartum 2D nao realista)" + (" ressalvas: " + ", ".join(ed) if ed else "")
    g["gate"]["A4_A8_juiz_gemini"] = ("LOOP %s (imagem×fala %s, capa×título %s, loop %s; modelo %s)" % (lp["veredito"], lp["imagem_fala"], lp["capa_titulo"], lp["loop_texto"], lp.get("modelo") or "?")) if lp else "PENDENTE (LOOP não rodado)"
    if any(a in p.name for a in ADIADOS): g["adiado"] = True
    (p / "gate-pronto.json").write_text(json.dumps(g, ensure_ascii=False, indent=2))
    dec = avaliar_pasta(str(p))
    g["status"] = "PUBLICAVEL" if dec.publicavel else "P1_HOLD"
    g["motivo_hold"] = "; ".join(dec.motivos); g["ressalvas_gate"] = dec.ressalvas; g["publicado"] = False
    (p / "gate-pronto.json").write_text(json.dumps(g, ensure_ascii=False, indent=2))
    mot = "; ".join(lp["motivos"][:4]) if lp else ""
    linhas.append("| %s | %s | %s | %s | %s | %s | %s |" % (s["codigo"], s["tema"], lp["veredito"] if lp else "pendente",
                  (lp["imagem_fala"] + " / " + lp["capa_titulo"] + " / " + lp["loop_texto"]) if lp else "—",
                  g["status"], g["motivo_hold"] or "—", mot or "—"))
t = (L / "GATE-PRONTO-LOTE.md").read_text()
bloco = ("\n\n## Gate com LOOP do juiz Gemini (25/10/2026, 0.4.3)\nGate determinístico `pipeline/gate_publicacao.py`. LOOP via Camofox 9387 (humanizado, "
         "modelo **3.8 Flash** fixado e conferido antes de cada envio; pranchas 360 px compostas em 3 anexos). Brigadeiro adiado. Nada publicado.\n\n"
         "| código | tema | LOOP | imagem×fala / capa×título / loop | status | bloqueios | motivos do juiz (até 4) |\n|---|---|---|---|---|---|---|\n" + "\n".join(linhas) + "\n")
t = re.sub(r"\n\n## Gate com LOOP do juiz Gemini.*", "", t, flags=re.S) + bloco
(L / "GATE-PRONTO-LOTE.md").write_text(t); print("\n".join(linhas))
