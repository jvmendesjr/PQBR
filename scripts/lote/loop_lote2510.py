"""lote-2510 (t540): pedido LOOP do juiz Gemini (imagem×fala, capa×título, loop textual) pelo Camofox PQBR,
humanizado, sem login novo. Também serve de 3ª rodada do VISUAL (formiga/fechadura), já com texto.
Uso: python scripts/lote/loop_lote2510.py <tema> [<tema> ...]  — grava loop-gemini.json; não publica nada."""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from pqbr.workflows.auditor_loop import auditar_loop
L = Path("docs/pesquisas/lote-2510"); R = Path("runtime/lote-saldo"); alvo = set(sys.argv[1:])
for d in sorted(L.glob("*/seo.json")):
    s = json.loads(d.read_text())
    if s["tema"] not in alvo: continue
    out = d.parent / "loop-gemini.json"
    if out.exists(): print(s["codigo"], "já feito", flush=True); continue
    g = json.loads((d.parent / "gate-pronto.json").read_text()); v = Path(g.get("pronto_vigente") or g["pronto"])
    r = json.loads((d.parent / "roteiro.json").read_text())["roteiro"]
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v)]).decode())
    fq = R / s["tema"] / "quadros-loop"; fq.mkdir(exist_ok=True); n = len(r["falas"]); q = []
    for i in range(n):
        f = fq / f"q{i + 1:02d}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{dur * (i + 0.5) / n:.2f}", "-i", str(v), "-frames:v", "1", str(f)], check=True); q.append(str(f))
    capa = fq / "capa.png"; subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.5", "-i", str(v), "-frames:v", "1", str(capa)], check=True)
    bv = r.get("bloco_visual") or {}
    try:
        res = auditar_loop(s["codigo"], d.parent.name, q, r["falas"],
                           "[ESTILO] " + str(bv.get("estilo", "")) + "\n[PERSONAGEM] " + str(bv.get("personagem", "")),
                           str(capa), s["seo"]["titulo"])
        out.write_text(res.model_dump_json(indent=1)); print(s["codigo"], s["tema"], res.veredito, res.imagem_fala, res.capa_titulo, res.loop_texto, flush=True)
    except Exception as e:
        print(s["codigo"], "ERRO", type(e).__name__, str(e)[:300], flush=True)
