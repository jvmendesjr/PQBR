import json, sys
from pathlib import Path
from pqbr.workflows.auditor_gemini import auditar
cri = json.loads(Path("/tmp/pq/criativo-EP1002.json").read_text()); r = cri["roteiro"]; bv = r["bloco_visual"]
E = Path.home() / ".pqbr/episodios/a-gente-fala-que-algo-custa-os-olhos-da-cara"
q = sorted(str(x) for x in (E / "pranchas").glob("cena_*.png"))
res = auditar("PQBR-EP1002", "a-gente-fala-que-algo-custa-os-olhos-da-cara", q, r["falas"], f"[ESTILO] {bv['estilo']}\n[PERSONAGEM] {bv['personagem']}",
              str(E / "capa_nlm.png"), rodadas=int(sys.argv[1]) if len(sys.argv) > 1 else 2)
print(res.model_dump_json(indent=1))
