#!/usr/bin/env python3
"""Exporta (somente leitura) as fontes do mestre legado c35d7b24 para o repo.

Bypass intencional de MESTRES_PROIBIDOS: este script chama o CLI direto, sem passar
pelas activities de produção. NÃO gera mídia, NÃO apaga, NÃO imprime segredos.
José 31/10/2026 (t168u).
"""
from __future__ import annotations
import json, os, re, subprocess, sys, time, random
from pathlib import Path

HOME = Path(os.environ.get("PQBR_NOTEBOOKLM_HOME", Path.home() / ".pqbr/notebooklm"))
CLI = str(HOME / "venv/bin/notebooklm")
PERFIL = "pqbr"
LEGAADO = "c35d7b24-5d4f-4eee-afc4-7a0eadc860bf"
REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "docs/pesquisas/mestre-antigo-c35d7b24"
SEGREDO = re.compile(
    r"(api[_-]?key|password|secret|token|cookie|authorization|bearer\s+[a-z0-9._\-]+|"
    r"-----BEGIN|SID=|PSID|__Secure)",
    re.I,
)


def cli(*args: str, timeout: int = 300) -> str:
    env = {
        **os.environ,
        "NOTEBOOKLM_HOME": str(HOME),
        "NOTEBOOKLM_DISABLE_KEEPALIVE_POKE": "1",
        "NOTEBOOKLM_HEADLESS_REAUTH": "0",
    }
    r = subprocess.run([CLI, "-p", PERFIL, "--quiet", *args], capture_output=True, text=True, timeout=timeout, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"notebooklm {' '.join(args[:3])} rc={r.returncode}: {(r.stderr or r.stdout)[-400:]}")
    return r.stdout


def js(s: str):
    s = s.strip()
    i = min(x for x in (s.find("{"), s.find("[")) if x >= 0)
    return json.loads(s[i:])


def slug(titulo: str, i: int) -> str:
    t = re.sub(r"[^a-zA-Z0-9._\-]+", "-", (titulo or f"fonte-{i}")).strip("-")[:80] or f"fonte-{i}"
    return f"{i:03d}-{t}"


def redigir(texto: str) -> tuple[str, bool]:
    if SEGREDO.search(texto or ""):
        return "[REDACTED: possível segredo — conteúdo omitido na exportação]\n", True
    return texto, False


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    # sync Camofox → notebooklm-py (única fonte de sessão)
    sync = Path.home() / ".pqbr/camofox/nlm-sync.sh"
    if sync.is_file():
        subprocess.run([str(sync)], capture_output=True, timeout=90)
    time.sleep(random.uniform(1.5, 3.0))

    fontes = js(cli("source", "list", "-n", LEGAADO, "--json"))
    lista = fontes.get("sources") or fontes.get("items") or []
    if isinstance(fontes, list):
        lista = fontes
    meta = {"caderno": LEGAADO, "titulo_export": "mestre-legado-somente-leitura", "n_fontes": len(lista), "fontes": []}
    redacted = 0
    for i, f in enumerate(lista, start=1):
        fid = f.get("id") or f.get("source_id") or ""
        titulo = f.get("title") or f.get("name") or f"fonte-{i}"
        url = f.get("url") or f.get("original_url") or ""
        entry = {"i": i, "id": fid[:12] + "…" if fid else "", "title": titulo, "url": url, "arquivo": None, "redacted": False}
        time.sleep(random.uniform(1.2, 2.8))
        corpo = ""
        try:
            if fid:
                corpo = cli("source", "fulltext", "-n", LEGAADO, fid, timeout=180)
        except Exception as e:  # noqa: BLE001
            corpo = f"[fulltext indisponível: {type(e).__name__}]\n"
            try:
                g = cli("source", "get", "-n", LEGAADO, fid, "--json", timeout=120)
                corpo += g
            except Exception:  # noqa: BLE001
                pass
        texto, foi = redigir(corpo)
        if foi:
            redacted += 1
            entry["redacted"] = True
        nome = slug(titulo, i) + ".md"
        (OUT / nome).write_text(
            f"# {titulo}\n\n- id_parcial: {entry['id']}\n- url: {url or '—'}\n- caderno_legado: {LEGAADO}\n\n---\n\n{texto}",
            encoding="utf-8",
        )
        entry["arquivo"] = nome
        meta["fontes"].append(entry)
        print(f"ok {i}/{len(lista)} {nome}", flush=True)

    meta["redacted"] = redacted
    (OUT / "INDICE.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# Exportação somente-leitura do mestre legado `{LEGAADO}`\n\n"
        f"Data: 2026-10-31 (t168u). Sem segredos. Sem mídia gerada. Caderno **não** apagado.\n\n"
        f"- Fontes: {len(lista)}\n- Redigidas: {redacted}\n- Ver `INDICE.json`.\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "n": len(lista), "redacted": redacted, "out": str(OUT)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
