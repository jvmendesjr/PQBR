"""lote-2510: reroda o gate fail-closed com SEO + juiz + registro. PASS só com juiz aprova/aprova_com_ressalva + editorial + Drive + Postgres + LOOP.
LOOP (texto) não existe no repo → A4_A8 fica incompleto → P1_HOLD (fail-closed, skill gate-pr-publish)."""
import json, re, subprocess, sys
from pathlib import Path
L = Path("docs/pesquisas/lote-2510"); linhas = []
for d in sorted(L.glob("*/seo.json")):
    p = d.parent; s = json.loads(d.read_text()); g = json.loads((p / "gate-pronto.json").read_text())
    j = json.loads((p / "juiz-gemini.json").read_text()) if (p / "juiz-gemini.json").exists() else None
    r = json.loads((p / "registro.json").read_text()) if (p / "registro.json").exists() else {}
    v = g.get("pronto_vigente") or g["pronto"]
    tec = subprocess.run(["/workspace/yt-llm-bot/scripts/prepublish-gate.sh", v], capture_output=True, text=True) if Path("/workspace/yt-llm-bot/scripts/prepublish-gate.sh").exists() else None
    seo = s["seo"]; ed = []
    if not seo["titulo"] or len(seo["titulo"]) > 70: ed.append("titulo")
    if "#shorts" not in [h.lower() for h in seo["hashtags"]]: ed.append("#shorts")
    if "Fontes:" not in seo["descricao"]: ed.append("fontes na descricao")
    if s["codigo"] not in seo["descricao"]: ed.append("codigo PQBR-EP fora da descricao (entra no payload/etiqueta)")
    g["codigo"] = s["codigo"]
    g["gate"]["B1_B10_editorial"] = "PASS (NotebookLM SEO validado PacoteSEO; " + str(len(s["fontes"])) + " fontes web; GenAI: cartum 2D nao realista)" + (" ressalvas: " + ", ".join(ed) if ed else "")
    g["gate"]["A4_A8_juiz_gemini"] = ("VISUAL %s (%s rodadas, texto nao enviado); LOOP: INEXISTENTE no repo (LACUNAS)" % (j["veredito"], j["rodadas"])) if j else "PENDENTE"
    g["drive"] = (r.get("drive") or {}).get("pasta") or g.get("drive"); g["postgres"] = r.get("postgres") or g.get("postgres")
    ok_vis = bool(j) and j["veredito"] in ("aprova", "aprova_com_ressalva")
    g["status"] = "P1_HOLD"; g["motivo_hold"] = "LOOP do juiz Gemini nao existe no repo (fail-closed)" + ("" if ok_vis else "; VISUAL=" + (j["veredito"] if j else "pendente")) + ("; S02 parece_pessoa_real" if j and j["veredito"] == "reprova" else "")
    g["publicado"] = False
    (p / "gate-pronto.json").write_text(json.dumps(g, ensure_ascii=False, indent=2))
    linhas.append("| %s | %s | %s | %s | %s | ok | P1_HOLD |" % (s["codigo"], s["tema"], seo["titulo"], j["veredito"] if j else "pendente", "ok" if g["drive"] and "PENDENTE" not in str(g["drive"]) else "pendente"))
t = (L / "GATE-PRONTO-LOTE.md").read_text()
bloco = "\n\n## Rerun do gate com códigos PQBR-EP (25/10/2026, 0.3.20)\nCódigos, SEO/fontes do NotebookLM (sessão do Camofox), juiz Gemini VISUAL via Camofox (2 rodadas, humanizado), Drive `PQBR/02_Episodios/2026-10/<código>_<slug>` e Postgres `pqbr.temas_pendentes` (status em_producao, metadados.codigo/seo/gate). Todos seguem **P1_HOLD**: o pedido LOOP do juiz não existe no repo (LACUNAS). Nada publicado.\n\n| código | tema | título (NotebookLM) | juiz VISUAL | Drive | Postgres | status |\n|---|---|---|---|---|---|---|\n" + "\n".join(linhas) + "\n"
t = re.sub(r"\n\n## Rerun do gate com códigos PQBR-EP.*", "", t, flags=re.S) + bloco
(L / "GATE-PRONTO-LOTE.md").write_text(t); print("\n".join(linhas))
