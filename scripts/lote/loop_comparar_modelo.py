"""t105u: LOOP do juiz Gemini num tema (inclusive descartado) com outro modelo, sem tocar no resultado oficial.
Mesmo pedido/rubrica do loop_lote2510 (auditar_loop), mesmos quadros já extraídos (quadros-loop/).
Uso: PQBR_GEMINI_MODELO="4 Argon" PQBR_GEMINI_RACIOCINIO=Baixo python scripts/lote/loop_comparar_modelo.py <dir_doc_tema> <dir_runtime> <sufixo>
Grava <dir_doc_tema>/loop-gemini-<sufixo>.json (+ evidência do seletor). Recusa sobrescrever."""
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from pqbr.workflows.auditor_loop import auditar_loop
from pqbr.workflows import auditor_gemini as ag
doc, rt, suf = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
out = doc / f"loop-gemini-{suf}.json"
if out.exists() or suf in ("", "oficial"): sys.exit(f"{out} já existe ou sufixo inválido")
ETAPA = os.environ.get("PQBR_ETAPA", "producao")
s = json.loads((doc / "seo.json").read_text()); r = json.loads((doc / "roteiro.json").read_text())["roteiro"]
fq = rt / "quadros-loop"; q = sorted(str(p) for p in fq.glob("q*.png")); capa = fq / "capa.png"
assert len(q) == len(r["falas"]) and capa.exists(), "quadros-loop incompletos"
bv = r.get("bloco_visual") or {}
t0 = time.time()
res = auditar_loop(s["codigo"], doc.name, q, r["falas"], "[ESTILO] " + str(bv.get("estilo", "")) + "\n[PERSONAGEM] " + str(bv.get("personagem", "")),
                   str(capa), s["seo"]["titulo"], persistir=False, etapa=ETAPA)
dt = round(time.time() - t0)
d = json.loads(res.model_dump_json()); d["_execucao"] = {"modelo_pedido": os.environ.get(ag.ENV_MODELO) or ag.modelo_configurado(ETAPA), "etapa": ETAPA, "raciocinio": ag.ULTIMO_RACIOCINIO,
    "tempo_total_s": dt, "evidencia_seletor": ag.EVIDENCIA, "quando": time.strftime("%Y-%m-%d %H:%M %z")}
out.write_text(json.dumps(d, ensure_ascii=False, indent=1)); print(s["codigo"], res.modelo, ag.ULTIMO_RACIOCINIO, res.veredito, res.imagem_fala, res.capa_titulo, res.loop_texto, f"{dt}s")
