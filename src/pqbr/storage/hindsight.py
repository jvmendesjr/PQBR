"""Escritor do Hindsight (bank único da PQBR): toda memória passa pela barreira antes.
O endpoint fica em HINDSIGHT_URL (127.0.0.1:8890 no pc); o transporte é injetável para teste."""
from __future__ import annotations
import json, os, urllib.request
from typing import Callable
from ..seguranca.barreira import exigir_limpo

BANK = os.environ.get("PQBR_HINDSIGHT_BANK", "pqbr")
URL = os.environ.get("HINDSIGHT_URL", "http://127.0.0.1:8890")


def _http(url: str, corpo: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (só localhost)
        return json.loads(r.read() or b"{}")


def reter(conteudo: str, contexto: str = "", transporte: Callable[[str, dict], dict] = _http) -> dict:
    exigir_limpo({"conteudo": conteudo, "contexto": contexto}, "hindsight")
    return transporte(f"{URL}/v1/default/banks/{BANK}/memories",
                      {"items": [{"content": conteudo, "context": contexto}]})
