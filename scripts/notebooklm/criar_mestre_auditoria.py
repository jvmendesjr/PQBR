#!/usr/bin/env python3
"""Cria o Mestre de Auditoria PQBR no NotebookLM (perfil pqbr / Camofox).

Espelha scripts/notebooklm/criar_mestre_canonico.py (t168u), com as
travas do t170u:
- NOTEBOOKLM_DISABLE_KEEPALIVE_POKE=1 NOTEBOOKLM_HEADLESS_REAUTH=0
- Sessão só do Camofox PQBR; nunca login em outro navegador
- Ações espaçadas/humanizadas
- NÃO apaga nada; NÃO gera mídia; NÃO gera episódio
- Grava ID em config/caderno_mestre_auditoria.json
- Idempotente por título e por título de fonte: reexecutar reusa.
"""
from __future__ import annotations
import json, os, random, subprocess, sys, time
from pathlib import Path

HOME = Path.home() / ".pqbr/notebooklm"
CLI = str(HOME / "venv/bin/notebooklm")
PERFIL = "pqbr"
REPO = Path(__file__).resolve().parents[2]
TITULO = "PQBR - Mestre de Auditoria"
CFG = REPO / "config/caderno_mestre_auditoria.json"


def pause(a=2.0, b=5.0):
    time.sleep(random.uniform(a, b))


def cli(*args: str, timeout: int = 300) -> str:
    env = {**os.environ, "NOTEBOOKLM_HOME": str(HOME),
           "NOTEBOOKLM_DISABLE_KEEPALIVE_POKE": "1", "NOTEBOOKLM_HEADLESS_REAUTH": "0"}
    r = subprocess.run([CLI, "-p", PERFIL, "--quiet", *args], capture_output=True, text=True, timeout=timeout, env=env)
    if r.returncode != 0:
        raise RuntimeError("notebooklm rc=" + str(r.returncode) + ": " + (r.stderr or r.stdout)[-500:])
    return r.stdout


def js(s: str):
    s = s.strip()
    i = min(x for x in (s.find("{"), s.find("[")) if x >= 0)
    return json.loads(s[i:])


def add_text(nb: str, title: str, texto: str):
    """Injeta texto como ARQUIVO (t170u, correção do bug do --type text).

    Bug encontrado no teste: --type text com caminho ingere só o caminho
    como texto (fulltext = caminho, 50-70 chars), não o conteúdo.
    O script do mestre criativo (t168u) tem o mesmo padrão e o mesmo
    problema nas fontes texto dele — registrado, sem tocar no mestre
    criativo nesta entrega. Aqui usamos --type file e renomeamos para
    o título canônico, porque o CLI ignora --title em arquivo.
    O tmp é mantido até a verificação, não apagado cegamente.
    """
    tmp = HOME / "tmp" / f"auditoria-{title}.txt"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(texto[:480_000], encoding="utf-8")
    pause(1.5, 3.5)
    out = cli("source", "add", "-n", nb, "--type", "file", "--title", title, str(tmp), "--json", timeout=180)
    try:
        sid = js(out).get("source", {}).get("id")
        if sid:
            cli("source", "rename", "-n", nb, sid, title, timeout=120)
    except Exception:
        pass


def add_file(nb: str, title: str, path: Path):
    if not path.is_file():
        raise FileNotFoundError(path)
    pause(1.5, 3.5)
    out = cli("source", "add", "-n", nb, "--type", "file", "--title", title, str(path), "--json", timeout=180)
    try:
        sid = js(out).get("source", {}).get("id")
        if sid:
            cli("source", "rename", "-n", nb, sid, title, timeout=120)
    except Exception:
        pass


def main() -> int:
    sync = Path.home() / ".pqbr/camofox/nlm-sync.sh"
    if sync.is_file():
        r = subprocess.run([str(sync)], capture_output=True, timeout=90)
        if r.returncode != 0:
            print(json.dumps({"ok": False, "erro": "sessão Camofox/nlm-sync falhou", "rc": r.returncode}, ensure_ascii=False))
            return 2
    pause(2, 4)
    try:
        notebooks = js(cli("list", "--json", timeout=120))
    except Exception as e:
        print(json.dumps({"ok": False, "erro": f"sessão notebooklm falhou: {e}"}, ensure_ascii=False))
        return 2
    lista = notebooks.get("notebooks") or []
    existentes = [n for n in lista if n.get("title") == TITULO]
    if existentes:
        nb = existentes[0]["id"]
        print(json.dumps({"ok": True, "reuse": True, "id": nb, "titulo": TITULO}, ensure_ascii=False))
    else:
        created = js(cli("create", TITULO, "--json", timeout=180))
        nb = created.get("id") or (created.get("notebook") or {}).get("id")
        if not nb:
            print(json.dumps({"ok": False, "erro": "create sem id", "raw": str(created)[:200]}, ensure_ascii=False))
            return 1
        print(json.dumps({"ok": True, "created": True, "id": nb}, ensure_ascii=False), flush=True)
    persona = (REPO / "templates/notebooklm/persona-auditoria-mestre.txt").read_text(encoding="utf-8").strip()[:10000]
    pause()
    cli("configure", "-n", nb, "--persona", persona, timeout=120)
    sys.path.insert(0, str(REPO / "src"))
    from pqbr.auditoria_cadernos import snapshot_regras_mestre
    fontes = [
        ("000-INDICE-AUDITORIA", "Índice do Mestre de Auditoria PQBR (t170u).\nFontes: 001 persona auditoria, 002 snapshot regras 1.0.0, 003 contrato editorial, 004 regras editoriais (recorte), 005 estilo stickman, 006 checklist cena, 007 erros recorrentes.\nPapel: só auditar, contra estas fontes. Nunca gerar mídia, nunca gerar episódio, nunca veredito de episódio específico neste caderno."),
        ("001-PERSONA-AUDITORIA", persona),
        ("002-SNAPSHOT-REGRAS-1.0.0", snapshot_regras_mestre("1.0.0")),
    ]
    arquivos = [
        ("003-CONTRATO-EDITORIAL", REPO / "docs/CONTRATO-EDITORIAL.md"),
        ("005-PROCESSO-CRIACAO", REPO / "docs/processos/CRIACAO-README.md"),
    ]
    atuais = js(cli("source", "list", "-n", nb, "--json"))
    titulos = {s.get("title") for s in (atuais.get("sources") or [])}
    for title, texto in fontes:
        if title in titulos:
            continue
        add_text(nb, title, texto)
        print("fonte", title, flush=True)
    for title, path in arquivos:
        if title in titulos or not path.is_file():
            continue
        add_file(nb, title, path)
        print("arquivo", title, flush=True)
    if "004-REGRAS-EDITORIAIS" not in titulos:
        regras = (REPO / "docs/REGRAS.md").read_text(encoding="utf-8")
        add_text(nb, "004-REGRAS-EDITORIAIS", regras[:120_000])
        print("fonte 004", flush=True)
    if "005-ESTILO-STICKMAN" not in titulos:
        try:
            from pqbr.contratos import ESTILO_PADRAO_STICKMAN
            add_text(nb, "005-ESTILO-STICKMAN", ESTILO_PADRAO_STICKMAN)
        except Exception:
            add_text(nb, "005-ESTILO-STICKMAN", "Cartoon 2D flat colorido stickman, contorno preto, cabeça redonda.")
        print("fonte 005-estilo", flush=True)
    d = json.loads(CFG.read_text(encoding="utf-8")) if CFG.is_file() else {}
    d["caderno_mestre_auditoria_id"] = nb
    d["titulo"] = TITULO
    d["proibido_midia"] = True
    CFG.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "id": nb, "titulo": TITULO, "config": str(CFG)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
