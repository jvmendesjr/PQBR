"""Linha de comando do motion: lê um PlanoMotion em JSON, renderiza, compõe sobre o vídeo original e gera
folha de contato e teste a 360 px. Uso:
  PYTHONPATH=src .venv/bin/python -m pqbr.pos.motion.cli plano.json --original video.mp4 --saida pasta/
Nada aqui publica, envia ao Drive ou gasta crédito externo."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from ...contratos.motion import PlanoMotion
from .render import renderizar
from .compor import compor, folha_contato, teste_360


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="motion graphics do pós (REGRAS §26)")
    ap.add_argument("plano"); ap.add_argument("--original", required=True); ap.add_argument("--saida", required=True)
    ap.add_argument("--cortes", help="JSON com durações dos clipes, para contar os substituídos")
    ap.add_argument("--sem-sobre", action="store_true", help="não aplica a camada sobre o vídeo (barra, cortina externa)")
    a = ap.parse_args(argv)
    plano = PlanoMotion.model_validate_json(Path(a.plano).read_text(encoding="utf-8"))
    saida = Path(a.saida); saida.mkdir(parents=True, exist_ok=True)
    r = renderizar(plano, saida / "render", sobre=not a.sem_sobre)
    print(f"render: tela_cheia={r.quadros_tela_cheia} sobre={r.quadros_sobre} deterministico={r.deterministico} violacoes={len(r.violacoes)}")
    if not r.ok:
        print("render reprovado: veja relatorio-render.json", file=sys.stderr); return 2
    cortes = json.loads(Path(a.cortes).read_text()) if a.cortes else None
    if isinstance(cortes, dict): cortes = cortes.get("cortes_s")
    c = compor(plano, Path(a.original), saida / "render", saida / "piloto-motion.mp4", cortes=cortes, com_sobre=not a.sem_sobre)
    folha_contato(saida / "piloto-motion.mp4", saida / "folha-contato.png")
    teste_360(saida / "piloto-motion.mp4", saida / "piloto-motion-360.mp4")
    print(f"saida: {c.saida} bloco={c.bloco} clipes_substituidos={c.clipes_substituidos}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
