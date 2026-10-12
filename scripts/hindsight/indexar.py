"""Indexa no Hindsight (bank `pqbr`) a evolução do projeto (t427): DECISOES-LOG (por seção), commits do git,
incidentes e lições dos playbooks. Idempotente (hash por item em ~/.pqbr/hindsight/indexados.json).
Tudo passa pela barreira (storage.hindsight.reter). Uso: python -m scripts... ou via timer pqbr-hindsight-indexar."""
from __future__ import annotations
import hashlib, json, re, subprocess, sys
from pathlib import Path

RAIZ = Path("/home/pc/Workspace/PQBR"); sys.path.insert(0, str(RAIZ / "src"))
from pqbr.storage.hindsight import reter  # noqa: E402

ESTADO = Path.home() / ".pqbr/hindsight/indexados.json"


def itens():
    log = (RAIZ / "docs/DECISOES-LOG.md").read_text(encoding="utf-8")
    for sec in re.split(r"\n(?=## )", log):
        if sec.startswith("## ") and len(sec) > 80:
            tit = sec.splitlines()[0][3:].strip()
            tipo = "incidente" if re.search(r"incidente", tit, re.I) else "decisao"
            for i in range(0, len(sec), 3500):
                yield f"{tipo}:{tit}:{i}", sec[i:i + 3500], f"PQBR {tipo} — DECISOES-LOG: {tit}"
    out = subprocess.run(["git", "-C", str(RAIZ), "log", "--since=2026-10-01", "--pretty=format:%h|%cI|%s"], capture_output=True, text=True).stdout
    for l in out.splitlines():
        h, d, s = l.split("|", 2)
        yield f"commit:{h}", f"Commit {h} em {d}: {s}", "PQBR evolução — commit do repositório"
    for f in sorted((RAIZ / "company/playbooks").glob("*.md")):
        yield f"playbook:{f.name}", f.read_text(encoding="utf-8")[:3500], f"PQBR playbook/lição — {f.stem}"


def main() -> int:
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    feitos = json.loads(ESTADO.read_text()) if ESTADO.exists() else {}
    n = 0
    for chave, texto, ctx in itens():
        h = hashlib.sha256(texto.encode()).hexdigest()[:16]
        if feitos.get(chave) == h: continue
        try:
            reter(texto, ctx); feitos[chave] = h; n += 1
        except Exception as e:  # barreira bloqueou ou API fora: pula o item, registra
            print(f"pulado {chave}: {type(e).__name__}", file=sys.stderr)
    ESTADO.write_text(json.dumps(feitos)); print(f"indexados {n} novos; total {len(feitos)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
