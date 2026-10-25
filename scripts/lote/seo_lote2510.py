"""lote-2510: códigos PQBR-EP + SEO/fontes pelo NotebookLM (sessão só do Camofox) + registro do caderno. Sem geração paga."""
import asyncio, json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
os.environ.setdefault("NOTEBOOKLM_DISABLE_KEEPALIVE_POKE", "1"); os.environ.setdefault("NOTEBOOKLM_HEADLESS_REAUTH", "0")
from pqbr.workflows.notebooklm import nlm_perguntar, _cli, _json, _ids
from pqbr.workflows.criativo import PROMPT_SEO, validar_seo, escolher_fontes
from pqbr.workflows.pacote import registro_caderno, registro_fonte
L = Path("docs/pesquisas/lote-2510")
CODIGOS = {"a-gente-fala-que-algo-custa-os-olhos-da-cara": ("olhos-da-cara", "PQBR-EP1002"),
 "chamamos-cafe-fraco-de-cha-de-bico-de-chaleira": ("cafe-fraco", "PQBR-EP1003"),
 "formiga-corre-em-fila-reta-ate-o-pote-de-acucar": ("formiga", "PQBR-EP1004"),
 "o-liquidificador-brasileiro-tem-15-velocidades-mas-a-ge": ("liquidificador", "PQBR-EP1005"),
 "o-brasileiro-confere-a-fechadura-tres-vezes-antes-de-sa": ("fechadura", "PQBR-EP1006"),
 "o-brigadeiro-so-existe-no-brasil": ("brigadeiro", "PQBR-EP1007"),
 "a-gente-fala-nao-e-bem-assim-pra-discordar-sem-brigar": ("nao-e-bem-assim", "PQBR-EP1008"),
 "o-brasileiro-poe-garrafa-de-agua-em-cima-do-relogio-de": ("garrafa", "PQBR-EP1009"),
 "o-brasileiro-raspa-a-panela-de-arroz-ate-sair-a-crostin": ("crostinha", "PQBR-EP1010")}

async def um(slug, sem):
    tema, cod = CODIGOS[slug]; d = L / slug; out = d / "seo.json"
    if out.exists(): return slug, "ja"
    meta = json.loads((d / "meta.json").read_text()); nb = meta["caderno"]
    rot = json.loads((d / "roteiro.json").read_text())
    async with sem:
        lst = _json(await asyncio.to_thread(_cli, "source", "list", "-n", nb, "--json", timeout=120))
        fontes = [{"id": f["id"], "titulo": f.get("title") or "", "url": f["url"]} for f in _ids(lst.get("sources", lst) if isinstance(lst, dict) else lst)
                  if str(f.get("url") or "").startswith("http")]
        fontes = escolher_fontes(rot.get("fontes") or rot.get("roteiro", {}).get("fontes") or [], fontes)
        await registro_caderno(nb, cod, slug, None)
        for f in fontes: await registro_fonte(nb, f["id"], "pesquisa", f["titulo"][:200])
        erro = ""; seo = None
        for _ in range(2):
            txt = await nlm_perguntar(nb, PROMPT_SEO + (f" Corrija: {erro}" if erro else ""))
            (d / "resposta-seo-notebooklm.txt").write_text(txt)
            try: seo = await validar_seo(txt, fontes); break
            except Exception as e: erro = str(e)[:300]
    if not seo: return slug, "SEO invalido: " + erro
    out.write_text(json.dumps({"codigo": cod, "tema": tema, "caderno": nb, "seo": seo | {"_origem": "notebooklm"}, "fontes": fontes}, ensure_ascii=False, indent=1))
    return slug, "ok"

async def main():
    sem = asyncio.Semaphore(3)
    for r in await asyncio.gather(*(um(s, sem) for s in CODIGOS), return_exceptions=True): print(r if not isinstance(r, Exception) else ("ERRO", str(r)[:300]))
asyncio.run(main())
