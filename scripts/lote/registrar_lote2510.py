"""lote-2510: Drive (02_Episodios/AAAA-MM/<código>_<slug>) + Postgres (temas_pendentes.metadados/caminhos). Sem publicar."""
import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from pqbr.workflows.episodio import drive_enviar
from pqbr.storage import banco
L = Path("docs/pesquisas/lote-2510")
modo = sys.argv[1] if len(sys.argv) > 1 else "tudo"
for d in sorted(L.glob("*/seo.json")):
    s = json.loads(d.read_text()); p = d.parent; g = json.loads((p / "gate-pronto.json").read_text()); meta = json.loads((p / "meta.json").read_text())
    v = g.get("pronto_vigente") or g["pronto"]; slug = p.name
    reg = p / "registro.json"; r = json.loads(reg.read_text()) if reg.exists() else {}
    if modo in ("tudo", "drive") and "drive" not in r:
        arqs = [str(p / "seo.json"), str(p / "roteiro.json"), str(p / "gate-pronto.json")] + ([str(p / "juiz-gemini.json")] if (p / "juiz-gemini.json").exists() else []) + [str(Path(v).resolve())]
        r["drive"] = asyncio.run(drive_enviar(s["codigo"], slug, arqs))
    if modo in ("tudo", "pg"):
        with banco.conectar("pqbr_app") as c:
            cur = c.execute("select slug from pqbr.temas_pendentes where id = %s", (meta["tema_id"],)).fetchone()
            if cur and cur[0] != slug: print("slug difere no banco:", cur[0], "vs", slug)
            n = c.execute("update pqbr.temas_pendentes set status = %s, metadados = metadados || %s::jsonb, caminhos = caminhos || %s::jsonb, fontes = %s::jsonb where id = %s",
                ("em_producao", json.dumps({"codigo": s["codigo"], "caderno": s["caderno"], "seo": s["seo"], "gate": "P1_HOLD", "lote": "lote-2510"}, ensure_ascii=False),
                 json.dumps({"final": v, "drive": (r.get("drive") or {}).get("pasta")}), json.dumps([{"titulo": f["titulo"], "url": f["url"]} for f in s["fontes"]], ensure_ascii=False),
                 meta["tema_id"])).rowcount
            c.commit(); r["postgres"] = {"temas_pendentes_id": meta["tema_id"], "linhas": n}
    reg.write_text(json.dumps(r, ensure_ascii=False, indent=1)); print(s["codigo"], {k: (bool(x) if k == "drive" else x) for k, x in r.items()}, flush=True)
