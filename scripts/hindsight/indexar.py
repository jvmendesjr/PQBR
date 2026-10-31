"""Indexa no Hindsight (bank `pqbr`) a evolução do projeto (t427): DECISOES-LOG (por seção), commits do git,
incidentes e lições dos playbooks. Idempotente (hash por item em ~/.pqbr/hindsight/indexados.json).
Tudo passa pela barreira (storage.hindsight.reter). Uso: python -m scripts... ou via timer pqbr-hindsight-indexar."""
from __future__ import annotations
import hashlib, json, re, subprocess, sys
from pathlib import Path

RAIZ = Path("/home/pc/Workspace/PQBR"); sys.path.insert(0, str(RAIZ / "src"))
from pqbr.storage.hindsight import reter  # noqa: E402
from pqbr.storage.hindsight_tags import tags_conteudo  # noqa: E402
from pqbr.contratos.politica import carregar  # noqa: E402


def tags_indexador(ctx: str, texto: str) -> list[str]:
    """Mesma regra da reclassificação (t90u), limitada ao que o indexador pode escrever."""
    return sorted(tags_conteudo(ctx, texto, set(carregar().de("indexador").escrita))) or ["doc"]

DOCS = ["docs/ESTADO-ATUAL.md", "docs/REFERENCIA-sessao-google.md", "docs/CONTRATO-EDITORIAL.md", "docs/ARQUITETURA.md", "docs/ROADMAP.md", "docs/SPEC.md",
        "docs/AGENTES.md", "docs/pesquisas/mapa-drive-rede.md", "docs/pesquisas/estilo-2d-referencias.md", "docs/sdd/gate-a9.md",
        "docs/sdd/adr-003-cadernos-efemeros.md", "docs/pesquisas/estilo-2d-deep-research-relatorio.md", "docs/pesquisas/cadernos-inventario-20261012.md", "docs/pesquisas/teste-capa-e-persona-20261012.md", "docs/pesquisas/pesquisa-caderno-mestre.md", "company/playbooks/nlm-cadernos.md"]
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

    for rel in DOCS:
        f = RAIZ / rel
        if not f.exists(): continue
        txt = f.read_text(encoding="utf-8")
        for sec in re.split(r"\n(?=##+ )", txt):
            if len(sec.strip()) < 80: continue
            tit = sec.strip().splitlines()[0].lstrip("# ").strip()[:80]
            for i in range(0, len(sec), 3500):
                yield f"doc:{rel}:{tit}:{i}", sec[i:i + 3500], f"PQBR doc canônico — {rel}: {tit}"
    mem = RAIZ / "scripts/hindsight/memorias.json"
    if mem.exists():
        for chave, texto in json.loads(mem.read_text(encoding="utf-8")):
            yield chave, texto, "PQBR decisão-chave (memória)"


def validar_estado(feitos: object) -> dict:
    if not isinstance(feitos, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in feitos.items()):
        raise ValueError("estado inválido")
    from pqbr.seguranca.barreira import exigir_limpo
    exigir_limpo(feitos, "log")
    return feitos

def main() -> int:
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    feitos = validar_estado(json.loads(ESTADO.read_text()) if ESTADO.exists() else {})
    n = 0
    for chave, texto, ctx in itens():
        h = hashlib.sha256(texto.encode()).hexdigest()[:16]
        if feitos.get(chave) == h: continue
        try:
            reter(texto, ctx, papel="indexador", tags=tags_indexador(ctx, texto)); feitos[chave] = h; n += 1
        except Exception as e:  # barreira bloqueou ou API fora: pula o item, registra
            print(f"pulado: {type(e).__name__}", file=sys.stderr)
    feitos = validar_estado(feitos)
    ESTADO.write_text(json.dumps(feitos)); print(f"indexados {n} novos; total {len(feitos)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
