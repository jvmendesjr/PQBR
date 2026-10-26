"""Reclassifica o bank Hindsight `pqbr` por papel (t90u, José: opção A).

Determinístico e idempotente:
- tags de conteúdo pela regra única `pqbr.storage.hindsight_tags` (a mesma do indexador);
- autor `papel:indexador` quando não houver `papel:*` (memórias legadas vieram do indexador);
- `obsoleto_candidato` quando a memória é versão superada (o texto não existe mais na fonte vigente) ou
  menciona decisão revogada sem fonte vigente que a sustente. NADA é apagado (deleção exige OK do José).
As tags no Hindsight são por documento (PATCH /documents/{id} substitui o conjunto); observações são derivadas e
herdam na reconsolidação. Uso: python scripts/hindsight/reclassificar.py [--aplicar] [--relatorio caminho.json]
Sem --aplicar = dry-run. Antes de aplicar: export do bank (POST /transfer/export) em ~/.pqbr/hindsight/backup/."""
from __future__ import annotations
import argparse, json, re, subprocess, sys, time, urllib.request
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
B = "http://127.0.0.1:8890/v1/default/banks/pqbr"
sys.path.insert(0, str(RAIZ / "src"))
from pqbr.storage.hindsight_tags import TAG_OBS, conflitos, fonte, tags_conteudo  # noqa: E402


def http(metodo, url, corpo=None):
    req = urllib.request.Request(url, data=json.dumps(corpo).encode() if corpo is not None else None, method=metodo,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310 (só localhost)
        return json.loads(r.read() or b"{}")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def politica_tags() -> set[str]:
    p = json.loads((RAIZ / "config/politica_papeis.json").read_text(encoding="utf-8"))
    return {t for v in p["papeis"].values() for k in ("leitura", "escrita") for t in v[k]}


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--relatorio", default=str(Path.home() / ".pqbr/hindsight/reclassificacao.json"))
    a = ap.parse_args()
    validas = politica_tags() | {TAG_OBS}
    docs, o = [], 0
    while True:
        r = http("GET", f"{B}/documents?limit=200&offset={o}"); docs += r["items"]; o += 200
        if o >= r["total"]: break
    commits = set(subprocess.run(["git", "-C", str(RAIZ), "log", "--all", "--pretty=%h"], capture_output=True, text=True).stdout.split())
    cache: dict[str, str | None] = {}

    def texto_fonte(p):
        if p not in cache:
            f = RAIZ / p
            cache[p] = norm(f.read_text(encoding="utf-8")) if f.exists() else None
        return cache[p]

    saida, mudar, cont = [], 0, Counter()
    for d in docs:
        det = http("GET", f"{B}/documents/{d['id']}")
        txt, ctx = det.get("original_text") or "", (d.get("retain_params") or {}).get("context", "")
        tipo, p, _ = fonte(ctx)
        tags = tags_conteudo(ctx, txt, validas)
        motivos, decisoes = [], []
        vigente = None
        if tipo == "commit":
            h = re.search(r"Commit (\w+)", txt); vigente = bool(h and h.group(1) in commits)
            if not vigente: motivos.append("commit não existe mais no repositório")
        elif p:
            ft = texto_fonte(p)
            if tipo == "memoria":
                vigente = ft is not None and norm(txt) in ft
            else:
                vigente = ft is not None and norm(txt) in ft
            if ft is None: motivos.append(f"fonte {p} ausente/movida")
            elif not vigente: motivos.append(f"versão superada: texto não existe mais em {p}")
        if ctx.startswith("teste diag"): motivos.append("memória de teste de diagnóstico")
        if tipo != "commit":
            decisoes = conflitos(txt)
        candidato = bool(motivos) or (bool(decisoes) and vigente is not True and tipo != "commit")
        if candidato and decisoes and not motivos: motivos.append("cita decisão revogada sem fonte vigente")
        atuais = set(d.get("tags") or [])
        autor = {t for t in atuais if t.startswith("papel:")} or {"papel:indexador"}
        novas = {t for t in tags if t in validas} | autor | {t for t in atuais if t in validas}
        novas.discard(TAG_OBS)
        if candidato: novas.add(TAG_OBS)
        for t in novas: cont[t] += det.get("memory_unit_count", 0) or 0
        altera = novas != atuais
        saida.append({"id": d["id"], "contexto": ctx[:160], "resumo": norm(txt)[:180], "tags_antes": sorted(atuais),
                      "tags_depois": sorted(novas), "obsoleto_candidato": candidato, "motivos": motivos,
                      "conflitos": decisoes, "fonte_vigente": vigente, "unidades": det.get("memory_unit_count", 0)})
        if altera:
            mudar += 1
            if a.aplicar:
                http("PATCH", f"{B}/documents/{d['id']}", {"tags": sorted(novas)}); time.sleep(0.2)
    vig_ctx = {i["contexto"] for i in saida if i["fonte_vigente"]}
    for i in saida:
        i["substituta_no_bank"] = (not i["fonte_vigente"]) and i["contexto"] in vig_ctx
    Path(a.relatorio).parent.mkdir(parents=True, exist_ok=True)
    Path(a.relatorio).write_text(json.dumps({"aplicado": a.aplicar, "documentos": len(docs), "alterados": mudar,
                                             "unidades_por_tag": cont, "itens": saida}, ensure_ascii=False, indent=1))
    print(json.dumps({"modo": "aplicar" if a.aplicar else "dry-run", "documentos": len(docs), "alterar": mudar,
                      "candidatos": sum(i["obsoleto_candidato"] for i in saida), "unidades_por_tag": cont}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
