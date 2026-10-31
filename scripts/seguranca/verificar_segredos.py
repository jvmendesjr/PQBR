#!/usr/bin/env python3
"""Verificador local de segredos/PII (sem CI). Uso:
  verificar_segredos.py --staged   # linhas adicionadas no commit (usado pelo pre-commit)
  verificar_segredos.py --tudo     # todos os arquivos versionados
  verificar_segredos.py ARQ...     # arquivos avulsos
Exceções: .segredos-permitidos (linhas "caminho_glob:regra" ou "caminho_glob:*"), revisadas pelo José.
Sai com 1 se achar algo. Nunca imprime o valor inteiro."""
from __future__ import annotations
import fnmatch, subprocess, sys
from pathlib import Path

RAIZ = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or ".")
sys.path.insert(0, str(RAIZ / "src"))
from pqbr.seguranca.segredos import encontrar  # noqa: E402

PULAR_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".mp4", ".mp3", ".wav", ".zip", ".gz", ".ico", ".woff", ".woff2"}


def permitidos() -> list[tuple[str, str]]:
    p = RAIZ / ".segredos-permitidos"
    out = []
    if p.exists():
        for l in p.read_text().splitlines():
            l = l.strip()
            if l and not l.startswith("#") and ":" in l:
                g, r = l.rsplit(":", 1)
                out.append((g.strip(), r.strip()))
    return out


def ok(caminho: str, regra: str, perm) -> bool:
    return any(fnmatch.fnmatch(caminho, g) and r in ("*", regra) for g, r in perm)


def linhas_staged() -> dict[str, list[tuple[int, str]]]:
    diff = subprocess.run(["git", "diff", "--cached", "-U0", "--no-color", "--diff-filter=ACMR"],
                          capture_output=True, text=True, cwd=RAIZ).stdout
    res: dict[str, list[tuple[int, str]]] = {}
    arq, n = None, 0
    for l in diff.splitlines():
        if l.startswith("+++ "):
            arq = l[6:] if l.startswith("+++ b/") else None
        elif l.startswith("@@"):
            n = int(l.split("+")[1].split(",")[0].split(" ")[0]) - 1
        elif arq and l.startswith("+") and not l.startswith("+++"):
            n += 1
            res.setdefault(arq, []).append((n, l[1:]))
    return res


def linhas_arquivos(arqs) -> dict[str, list[tuple[int, str]]]:
    res = {}
    for a in arqs:
        p = RAIZ / a
        if p.suffix.lower() in PULAR_EXT or not p.is_file():
            continue
        try:
            res[a] = list(enumerate(p.read_text(errors="ignore").splitlines(), 1))
        except OSError:
            pass
    return res


def main(argv: list[str]) -> int:
    if not argv or argv[0] == "--staged":
        alvo = linhas_staged()
    elif argv[0] == "--tudo":
        alvo = linhas_arquivos(subprocess.run(["git", "ls-files"], capture_output=True, text=True, cwd=RAIZ).stdout.split())
    else:
        alvo = linhas_arquivos(argv)
    perm, total = permitidos(), 0
    for arq, linhas in alvo.items():
        if Path(arq).suffix.lower() in PULAR_EXT:
            continue
        for n, txt in linhas:
            for a in encontrar(txt):
                if not ok(arq, a.regra, perm):
                    total += 1
                    print(f"  {arq}:{n}: {a}")
    if total:
        print(f"\nBLOQUEADO: {total} possível(is) segredo(s)/PII. Remova, ou peça ao José para registrar a exceção em .segredos-permitidos.")
        return 1
    print("verificar_segredos: nada encontrado.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
