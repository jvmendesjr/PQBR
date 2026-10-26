"""Adaptador GitNexus por papel (t84u–t86u). O GitNexus é global no servidor (~/.local/bin/gitnexus, fora do repo);
a PQBR só registra o índice dela. Toda resposta é filtrada pelos caminhos que o papel pode ver; papel
desconhecido ou sem a ferramenta `gitnexus_consultar` => negado. Só CLI/stdio local; nada de --http."""
from __future__ import annotations
import json, os, subprocess
from pathlib import Path
from typing import Any, Callable
from ..contratos.politica import carregar

BIN = os.environ.get("PQBR_GITNEXUS_BIN", str(Path.home() / ".local/bin/gitnexus"))
REPO = str(Path(__file__).resolve().parents[3])
COMANDOS = {"query", "context", "impact"}


def _cli(args: list[str]) -> Any:
    r = subprocess.run([BIN, *args], cwd=REPO, capture_output=True, text=True, timeout=120, check=True)
    return json.loads(r.stdout[r.stdout.find("{"):] or "{}")


def _filtrar(no: Any, ve: Callable[[str], bool]) -> Any:
    if isinstance(no, dict):
        fp = no.get("filePath")
        if fp is not None and not ve(fp):
            return None
        return {k: v for k, v in ((k, _filtrar(v, ve)) for k, v in no.items()) if v is not None}
    if isinstance(no, list):
        return [x for x in (_filtrar(i, ve) for i in no) if x is not None]
    return no


def consultar(papel: str, comando: str, alvo: str, executor: Callable[[list[str]], Any] = _cli) -> Any:
    pol = carregar()
    pol.exigir_ferramenta(papel, "gitnexus_consultar")
    if comando not in COMANDOS:
        raise ValueError(f"comando não permitido: {comando}")
    return _filtrar(executor([comando, alvo]), lambda c: pol.ve_caminho(papel, c)) or {}
