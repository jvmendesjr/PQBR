"""Reclassifica o bank Hindsight `pqbr` por papel (t90u, José: opção A).

Determinístico e idempotente:
- tags de conteúdo pela origem (contexto do retain) + palavras-chave, só tags que existem em config/politica_papeis.json;
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
TAG_OBS = "obsoleto_candidato"

# decisões vigentes que tornam afirmações antigas conflitantes (padrão, decisão)
CONFLITOS = [
    (r"\b(runway|manus)\b", "Runway e Manus descartados para vídeo (26/10/2026)"),
    (r"\bpaperclip\b", "ADR-011/t474–t476: Paperclip em retirada, parado e desabilitado"),
    (r"\bdiscord\b", "t474: revogada a t464 (sem canal Discord)"),
    (r"\bhermes\b[^.\n]{0,120}\b(telegram|callback|pedidos|aprova)|\b(telegram|callback|pedidos)\b[^.\n]{0,120}\bhermes\b",
     "t538: ponte Telegram por bot próprio via Temporal (Hermes desconsiderado)"),
    (r"gemini[^.\n]{0,40}\b(1\.5|2\.0|2\.5|3\.0|3 pro|3\.5|flash[- ]lite)\b", "t544: juiz Gemini fixado no 3.8 Flash"),
    (r"olhos[- ]da[- ]cara|\bEP1002\b", "t75u–t77u: EP1002 olhos-da-cara reprovado e descartado (tema volta a proposto)"),
    (r"caderno[- ]mestre", "t459/ADR-003: cadernos efêmeros por episódio (sem caderno mestre)"),
]
PALAVRAS = {
    "editorial": r"roteiro|editorial|\btemas?\b|narra|estilo|personage|storyboard|\bcapa\b|\bcta\b|elenco",
    "publicacao": r"youtube|upload|publica|publishat|agendad",
    "seguranca": r"segredo|\btoken|oauth|credencia|tailnet|barreira|\.env\b|chmod|2sv|sess[aã]o google",
    "compliance": r"compliance|direitos? autora|copyright|licen[cç]a|fair use",
    "auditoria": r"auditor|auditoria|gate a9|veredito|\bloop\b|\bvisual\b",
    "incidente": r"incidente|crash|\bqueda\b",
    "pesquisa": r"pesquisa|etimologia|notebooklm|\bfontes?\b",
    "licao": r"li[cç][aã]o|li[cç][oõ]es|aprendizado",
}


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


def fonte(ctx: str):
    """(tipo, caminho_fonte|None, tags_base)"""
    if ctx.startswith("PQBR evolução — commit"): return "commit", None, {"commit"}
    m = re.match(r"PQBR (decisao|incidente) — DECISOES-LOG: (.*)", ctx)
    if m: return "log", "docs/DECISOES-LOG.md", {m.group(1)}
    m = re.match(r"PQBR doc canônico — ([^:]+):", ctx)
    if m:
        p, t = m.group(1), {"doc"}
        if "CONTRATO-EDITORIAL" in p or "estilo" in p or "teste-capa" in p: t |= {"editorial"}
        if p.startswith("docs/pesquisas/"): t |= {"pesquisa"}
        if "gate-a9" in p: t |= {"editorial", "auditoria"}
        if "REFERENCIA-sessao-google" in p: t |= {"seguranca"}
        if "/adr-" in p or "ARQUITETURA" in p: t |= {"decisao"}
        if "playbooks" in p: t |= {"playbook"}
        return "doc", p, t
    m = re.match(r"PQBR playbook/lição — (.*)", ctx)
    if m: return "playbook", f"company/playbooks/{m.group(1).strip()}.md", {"playbook", "licao"}
    if ctx.startswith("PQBR decisão-chave"): return "memoria", "scripts/hindsight/memorias.json", {"decisao"}
    if "lição registrada" in ctx: return "licao", None, {"licao"}
    if ctx.startswith("PQBR incidente"): return "incidente", None, {"incidente"}
    if "caderno de teste" in ctx: return "caderno", None, {"pesquisa"}
    return "outro", None, {"doc"}


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
        tipo, p, tags = fonte(ctx)
        base = txt.lower()
        for t, rx in PALAVRAS.items():
            if re.search(rx, base): tags.add(t)
        if tipo == "log" and re.search(r"incidente", ctx, re.I): tags.add("incidente")
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
            for rx, dec in CONFLITOS:
                if re.search(rx, txt, re.I): decisoes.append(dec)
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
