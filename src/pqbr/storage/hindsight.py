"""Hindsight (bank único da PQBR): toda memória passa pela barreira e pela política por papel (t84u–t85u).
Escrita: só tags que o papel pode escrever. Leitura: recall filtrado pelas tags do papel (no pedido e na volta).
O endpoint fica em HINDSIGHT_URL (127.0.0.1:8890 no pc); o transporte é injetável para teste."""
from __future__ import annotations
import json, os, urllib.request
from typing import Callable
from ..seguranca.barreira import exigir_limpo
from ..contratos.politica import carregar

BANK = os.environ.get("PQBR_HINDSIGHT_BANK", "pqbr")
URL = os.environ.get("HINDSIGHT_URL", "http://127.0.0.1:8890")


def _http(url: str, corpo: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (só localhost)
        return json.loads(r.read() or b"{}")


def reter(conteudo: str, contexto: str = "", *, papel: str, tags: list[str],
          transporte: Callable[[str, dict], dict] = _http) -> dict:
    carregar().exigir_escrita(papel, tags)
    exigir_limpo({"conteudo": conteudo, "contexto": contexto}, "hindsight")
    return transporte(f"{URL}/v1/default/banks/{BANK}/memories",
                      {"items": [{"content": conteudo, "context": contexto, "tags": [*tags, f"papel:{papel}"]}]})


def recuperar(consulta: str, *, papel: str, transporte: Callable[[str, dict], dict] = _http) -> list[dict]:
    permitidas = set(carregar().tags_leitura(papel))
    r = transporte(f"{URL}/v1/default/banks/{BANK}/memories/recall",
                   {"query": consulta, "tags": sorted(permitidas), "tags_match": "any"})
    # defesa em profundidade: descarta o que voltar sem tag permitida
    return [m for m in r.get("results", []) if permitidas & set(m.get("tags") or [])]
