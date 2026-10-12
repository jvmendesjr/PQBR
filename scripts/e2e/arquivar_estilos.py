"""Arquiva (Postgres + Drive + disco), VERIFICA as 3 cópias e só então apaga os 3 cadernos do teste de estilos (classe 'pesquisa')."""
import hashlib, json, subprocess, sys
from pathlib import Path
from pqbr.workflows.pacote import _banco
from pqbr.integrations import drive
sys.path.insert(0, "scripts/e2e"); import teste_estilos as T
est = json.loads((T.OUT / "estado.json").read_text())
nb = {n["id"]: n for n in T.js(T.cli("list", "--json"))["notebooks"]} if isinstance(T.js(T.cli("list", "--json")), dict) else {n["id"]: n for n in T.js(T.cli("list", "--json"))}
for k, v in est.items():
    cad = v["caderno"]; n = nb.get(cad)
    if not n: print(k, "não existe mais"); continue
    titulo = n.get("title"); d = Path.home() / f".pqbr/cadernos-arquivo/ESTILO-{k}_{cad[:8]}"; d.mkdir(parents=True, exist_ok=True)
    arqs = []
    (d / "metadados.json").write_text(T.cli("metadata", "-n", cad, "--json")); arqs.append(d / "metadados.json")
    srcs = T.js(T.cli("source", "list", "-n", cad, "--json")); srcs = srcs.get("sources", srcs) if isinstance(srcs, dict) else srcs
    for i, s in enumerate(srcs):
        f = d / f"fonte_{i + 1:02d}_{s['id'][:8]}.md"; f.write_text(f"# {s.get('title', '')}\n{s.get('url') or ''}\n\n" + T.cli("source", "fulltext", "-n", cad, s["id"])); arqs.append(f)
    (d / "respostas.json").write_text(T.cli("history", "-n", cad, "--json", "--show-all")); arqs.append(d / "respostas.json")
    (d / "steering.txt").write_text(v["steering"]); arqs.append(d / "steering.txt")
    arqs.append(T.OUT / f"{k}_raw.mp4")
    pasta = drive.garantir_pasta(f"PQBR/estilos-teste-20261012/caderno-{k}")
    with _banco() as c:
        c.execute("insert into pqbr.cadernos_episodio (caderno_id, classe, titulo, slug) values (%s, 'pesquisa', %s, %s) on conflict (caderno_id) do nothing", (cad, titulo, f"estilo-teste-{k.lower()}"))
        for f in arqs:
            b = f.read_bytes(); tipo = "video" if f.suffix == ".mp4" else "resposta" if f.name.startswith("respostas") else "metadados" if f.name.startswith("metadados") else "nota" if f.name == "steering.txt" else "fonte"
            did = drive.enviar(str(f), pasta)["id"]
            c.execute("insert into pqbr.arquivo_caderno (caderno_id, tipo, nome, sha256, bytes, drive_id, conteudo) values (%s,%s,%s,%s,%s,%s,%s)"
                      " on conflict (caderno_id, tipo, nome) do update set sha256=excluded.sha256, bytes=excluded.bytes, drive_id=excluded.drive_id",
                      (cad, tipo, f.name, hashlib.sha256(b).hexdigest(), len(b), did, None if tipo == "video" else b.decode("utf-8", "replace")))
        c.execute("update pqbr.cadernos_episodio set arquivado_em = now() where caderno_id = %s", (cad,)); c.commit()
        rows = c.execute("select nome, bytes, drive_id from pqbr.arquivo_caderno where caderno_id = %s", (cad,)).fetchall()
        ok = len(rows) >= len(arqs) and all(r[2] for r in rows) and all(f.is_file() and f.stat().st_size == dict((r[0], r[1]) for r in rows)[f.name] for f in arqs)
        if not ok: print(k, "NÃO VERIFICADO — não apago"); continue
        copias = {"postgres": len(rows), "drive": len(rows), "disco": len(arqs), "bytes": sum(r[1] for r in rows)}
        c.execute("update pqbr.cadernos_episodio set verificado_em = now(), copias = %s where caderno_id = %s", (json.dumps(copias), cad)); c.commit()
    if T.js(T.cli("list", "--json")) and n.get("is_owner") is False: print(k, "não é dono"); continue
    T.cli("delete", "-n", cad, "-y")
    with _banco() as c: c.execute("update pqbr.cadernos_episodio set apagado_em = now() where caderno_id = %s", (cad,)); c.commit()
    print(k, cad, titulo, copias, "APAGADO")
