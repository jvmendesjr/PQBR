"""lote-2510: juiz Gemini Web VISUAL (2 rodadas) pelo Camofox PQBR, humanizado (auditor_gemini.auditar). Quadros do pronto vigente."""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from pqbr.workflows.auditor_gemini import auditar
L = Path("docs/pesquisas/lote-2510"); R = Path("runtime/lote-saldo")
for d in sorted(L.glob("*/seo.json")):
    s = json.loads(d.read_text()); g = json.loads((d.parent / "gate-pronto.json").read_text())
    out = d.parent / "juiz-gemini.json"
    if out.exists(): continue
    v = Path(g.get("pronto_vigente") or g["pronto"]); r = json.loads((d.parent / "roteiro.json").read_text())["roteiro"]
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v)]).decode())
    fq = R / s["tema"] / "quadros-juiz"; fq.mkdir(exist_ok=True); n = len(r["falas"]); q = []
    for i in range(n):
        t = dur * (i + 0.5) / n; f = fq / f"q{i + 1:02d}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(v), "-frames:v", "1", str(f)], check=True); q.append(str(f))
    capa = fq / "capa.png"; subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.5", "-i", str(v), "-frames:v", "1", str(capa)], check=True)
    bv = r.get("bloco_visual") or {}
    try:
        res = auditar(s["codigo"], d.parent.name, q, r["falas"], "[ESTILO] " + str(bv.get("estilo", "")) + "\n[PERSONAGEM] " + str(bv.get("personagem", "")), str(capa), rodadas=2)
        out.write_text(res.model_dump_json(indent=1)); print(s["codigo"], res.veredito, flush=True)
    except Exception as e:
        print(s["codigo"], "ERRO", str(e)[:300], flush=True)
