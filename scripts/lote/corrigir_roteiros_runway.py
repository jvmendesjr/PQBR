"""lote-runway: correção SEM CUSTO dos roteiros (ERR-ROT-02 + cenas curtas), 25/10/2026.
1) personagem só reage: troca trechos em que fala/explica/encara a câmera; 2) cena com clipes de 5 s que não
cobrem a fala ganha clipe extra (novo ângulo, mesma ficha, reação muda). Idempotente; guarda .bak uma vez."""
import json, math, shutil, string, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from pqbr.contratos.roteiro_terceira_pessoa import problemas_roteiro

BASE = Path("docs/pesquisas/lote-runway")
TROCAS = [
    ("gives a big thumbs-up to the camera", "gives a big thumbs-up"),
    ("gives a confident thumbs-up to the camera while smiling", "gives a confident thumbs-up while smiling silently"),
    ("explaining thoughtfully with an open palm gesture", "pondering with an open palm gesture, mouth closed"),
    ("talking animatedly with a woman", "arguing with exaggerated silent gestures with a woman"),
    ("clean-shaven explains the story", "clean-shaven, reacting with a surprised silent expression"),
    ("addressing the camera with a friendly smile", "smiling warmly with mouth closed"),
    ("explaining with animated hand gestures", "pointing with animated hand gestures"),
    ("looking directly at the camera with expressive hand gestures", "staring amazed with expressive hand gestures"),
]
SILENCIO = " Silent reaction only, mouth closed."
CLIPE_S = 5

def cobertura_minima(s):
    return max(math.ceil(len(s["fala"].split()) / 2.3 / CLIPE_S), math.ceil(float(s.get("duracao_s") or 0) / CLIPE_S))

def corrigir(j):
    mud = []
    for s in j.get("cenas", []):
        for c in s["clipes"]:
            for k in ("prompt_imagem_en", "movimento_en"):
                for a, b in TROCAS:
                    if a in c[k]: c[k] = c[k].replace(a, b); mud.append(f"{c['id']}.{k}: '{a}' → '{b}'")
            if "man" in c["prompt_imagem_en"] and SILENCIO.strip() not in c["movimento_en"]:
                c["movimento_en"] = c["movimento_en"].rstrip() + SILENCIO
        while len(s["clipes"]) < cobertura_minima(s):
            u = s["clipes"][-1]; usados = {c["id"] for c in s["clipes"]}
            nid = next(f"c{s['n']}{l}" for l in string.ascii_lowercase if f"c{s['n']}{l}" not in usados)
            novo = {"id": nid, "duracao_s": CLIPE_S,
                    "prompt_imagem_en": u["prompt_imagem_en"].replace("Medium shot", "Wide shot").replace("Close-up", "Medium shot"),
                    "movimento_en": "Different angle of the same moment: camera slowly orbits while details of the scene animate gently." + SILENCIO}
            s["clipes"].append(novo); mud.append(f"cena {s['n']}: +{nid} (cobertura {len(s['clipes'])*CLIPE_S}s)")
    return mud

if __name__ == "__main__":
    for f in sorted(BASE.glob("*/roteiro.json")):
        bak = f.with_suffix(".json.bak-pre-err-rot-02")
        if not bak.exists(): shutil.copy2(f, bak)
        j = json.loads(f.read_text()); mud = corrigir(j); f.write_text(json.dumps(j, ensure_ascii=False, indent=1))
        print(f.parent.name, len(mud), "mudanças", mud, "| restam:", problemas_roteiro(j))
