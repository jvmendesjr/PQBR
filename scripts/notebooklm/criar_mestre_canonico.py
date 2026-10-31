#!/usr/bin/env python3
"""Cria o caderno mestre canônico NOVO no NotebookLM (perfil pqbr / Camofox 9387).

- NOTEBOOKLM_DISABLE_KEEPALIVE_POKE=1 NOTEBOOKLM_HEADLESS_REAUTH=0
- Sessão só do Camofox PQBR; nunca login em outro navegador
- Ações espaçadas/humanizadas
- NÃO apaga nada; NÃO gera mídia; grava ID em config/caderno_mestre.json
José 31/10/2026 (t168u).
"""
from __future__ import annotations
import json, os, random, subprocess, sys, time
from pathlib import Path

HOME = Path(os.environ.get("PQBR_NOTEBOOKLM_HOME", Path.home() / ".pqbr/notebooklm"))
CLI = str(HOME / "venv/bin/notebooklm")
PERFIL = "pqbr"
REPO = Path(__file__).resolve().parents[2]
TITULO = "PQBR - Mestre canônico"
CFG = REPO / "config/caderno_mestre.json"


def pause(a=2.0, b=5.0):
    time.sleep(random.uniform(a, b))


def cli(*args: str, timeout: int = 300) -> str:
    env = {
        **os.environ,
        "NOTEBOOKLM_HOME": str(HOME),
        "NOTEBOOKLM_DISABLE_KEEPALIVE_POKE": "1",
        "NOTEBOOKLM_HEADLESS_REAUTH": "0",
    }
    r = subprocess.run([CLI, "-p", PERFIL, "--quiet", *args], capture_output=True, text=True, timeout=timeout, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"notebooklm {' '.join(args[:4])} rc={r.returncode}: {(r.stderr or r.stdout)[-500:]}")
    return r.stdout


def js(s: str):
    s = s.strip()
    i = min(x for x in (s.find("{"), s.find("[")) if x >= 0)
    return json.loads(s[i:])


def add_text(nb: str, title: str, texto: str):
    tmp = HOME / "tmp" / f"mestre-{title.replace('/', '-')[:40]}.txt"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(texto[:480_000], encoding="utf-8")
    pause(1.5, 3.5)
    cli("source", "add", "-n", nb, "--type", "text", "--title", title, str(tmp), "--json", timeout=180)
    try:
        tmp.unlink()
    except OSError:
        pass


def add_file(nb: str, title: str, path: Path):
    if not path.is_file():
        raise FileNotFoundError(path)
    pause(1.5, 3.5)
    cli("source", "add", "-n", nb, "--type", "file", "--title", title, str(path), "--json", timeout=180)


def main() -> int:
    sync = Path.home() / ".pqbr/camofox/nlm-sync.sh"
    if sync.is_file():
        r = subprocess.run([str(sync)], capture_output=True, timeout=90)
        if r.returncode != 0:
            print(json.dumps({"ok": False, "erro": "sessão Camofox/nlm-sync falhou", "rc": r.returncode}, ensure_ascii=False))
            return 2
    pause(2, 4)

    # sanity: list must work
    try:
        notebooks = js(cli("list", "--json", timeout=120))
    except Exception as e:  # noqa: BLE001
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

    # persona
    persona = (REPO / "templates/notebooklm/persona-mestre.txt").read_text(encoding="utf-8").strip()[:10000]
    pause()
    cli("configure", "-n", nb, "--persona", persona, timeout=120)

    # fontes canônicas (proposta §2.3)
    fontes = [
        ("000-INDICE-MESTRE", "Índice do Caderno Mestre Canônico PQBR.\n"
         "Fontes: 001 persona mestre, 002 persona efêmero, 003 comandos, 004 contrato editorial,\n"
         "005 processo criação, 006 regras editoriais (recorte), 007 estilo stickman,\n"
         "008 catálogo visual resumo, 009 contrato cena 2.0.0, 010 protocolo briefing.\n"
         "Papel: nortear efêmeros. Nunca gerar mídia neste caderno."),
        ("001-PERSONA-MESTRE", persona),
        ("010-PROTOCOLO-BRIEFING-EFEMERO",
         "Protocolo briefing_efemero (t168u).\n"
         "Entrada: {tema, codigo?, slug?, n_cenas?}.\n"
         "Saída JSON: persona_efemero, prompt_pesquisa, modo_pesquisa, urls_pesquisa (≥1),\n"
         "fontes_mestre_a_copiar, refs_catalogo_sugeridas, prompt_roteiro, prompt_seo,\n"
         "prompt_direcao_cenas, prompt_compliance?, riscos_compliance, modelo_sugerido,\n"
         "rotulo_episodio_prefix, pesquisa_obrigatoria=true.\n"
         "Após briefing: salvar nota útil; limpar chat com ask --new -y.\n"
         "Rótulo de cena: PQBR-EP####-S## (CenaIndividual 2.0.0)."),
    ]
    arquivos = [
        ("002-PERSONA-EFEMERO-BASE", REPO / "templates/notebooklm/persona-pqbr.txt"),
        ("003-COMANDOS-E-PROMPTS", REPO / "templates/notebooklm/comandos-pqbr.md"),
        ("004-CONTRATO-EDITORIAL", REPO / "docs/CONTRATO-EDITORIAL.md"),
        ("005-PROCESSO-CRIACAO", REPO / "docs/processos/CRIACAO-README.md"),
    ]
    # já existentes?
    atuais = js(cli("source", "list", "-n", nb, "--json"))
    titulos = {s.get("title") for s in (atuais.get("sources") or [])}

    for title, texto in fontes:
        if title in titulos:
            continue
        add_text(nb, title, texto)
        print("fonte", title, flush=True)

    for title, path in arquivos:
        if title in titulos:
            continue
        if path.is_file():
            add_file(nb, title, path)
            print("arquivo", title, flush=True)

    # 006 REGRAS recorte (sem secrets)
    if "006-REGRAS-EDITORIAIS" not in titulos:
        regras = (REPO / "docs/REGRAS.md").read_text(encoding="utf-8")
        # só primeiras seções editoriais / notebooklm — truncar seguro
        add_text(nb, "006-REGRAS-EDITORIAIS", regras[:120_000])
        print("fonte 006", flush=True)

    # 007 estilo
    if "007-ESTILO-STICKMAN" not in titulos:
        try:
            sys.path.insert(0, str(REPO / "src"))
            from pqbr.contratos import ESTILO_PADRAO_STICKMAN
            add_text(nb, "007-ESTILO-STICKMAN", ESTILO_PADRAO_STICKMAN)
        except Exception:  # noqa: BLE001
            add_text(nb, "007-ESTILO-STICKMAN", "Cartoon 2D flat colorido stickman, contorno preto, cabeça redonda.")
        print("fonte 007", flush=True)

    # 008 catálogo
    if "008-CATALOGO-VISUAL-RESUMO" not in titulos:
        try:
            from pqbr.pipeline import banco_fichas as bf
            add_text(nb, "008-CATALOGO-VISUAL-RESUMO", bf.resumo_para_prompt())
        except Exception as e:  # noqa: BLE001
            add_text(nb, "008-CATALOGO-VISUAL-RESUMO", f"Catálogo indisponível offline: {type(e).__name__}")
        print("fonte 008", flush=True)

    # 009 contrato cena
    if "009-CONTRATO-CENA-INDIVIDUAL" not in titulos:
        add_text(
            nb,
            "009-CONTRATO-CENA-INDIVIDUAL",
            "CenaIndividual 2.0.0 + DirecaoCenas 2.0.0.\n"
            "Rótulo canônico: PQBR-EP####-S## (ex. PQBR-EP1003-S04).\n"
            "stem do arquivo == rótulo. Sem board. lips closed obrigatório.\n"
            "refs: PERS/AMB/OBJ/ANIM/FIG/SIT. PERS-menina-rosa = mulher jovem adulta (nunca girl).",
        )
        print("fonte 009", flush=True)

    # gravar config
    d = json.loads(CFG.read_text(encoding="utf-8")) if CFG.is_file() else {}
    d["caderno_mestre_id"] = nb
    d["titulo"] = TITULO
    d["proibido_midia"] = True
    CFG.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "id": nb, "titulo": TITULO, "config": str(CFG)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
