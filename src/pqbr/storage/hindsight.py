"""Hindsight (bank único da PQBR): toda memória passa pela barreira e pela política por papel (t84u–t85u).
Escrita: só tags que o papel pode escrever. Leitura: recall filtrado pelas tags do papel (no pedido e na volta).
O endpoint fica em HINDSIGHT_URL (127.0.0.1:8890 no pc); o transporte é injetável para teste.

t154u: a escrita do MCP passa a ser **assíncrona com `operation_id` determinístico**. O retain síncrono
esperava a indexação e estourava o timeout de 30 s (o servidor gravava mesmo assim e um retry duplicava).
Com `async: true` + `operation_id`, o POST aceita na hora e reenviar a mesma operação não enfileira de novo.
"""
from __future__ import annotations
import json, os, re, urllib.request, uuid
from typing import Callable
from ..seguranca.barreira import exigir_limpo
from ..contratos.politica import carregar

BANK = os.environ.get("PQBR_HINDSIGHT_BANK", "pqbr")
URL = os.environ.get("HINDSIGHT_URL", "http://127.0.0.1:8890")
TIMEOUT = float(os.environ.get("PQBR_HINDSIGHT_TIMEOUT", "120"))


def _http(url: str, corpo: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:  # noqa: S310 (só localhost)
        return json.loads(r.read() or b"{}")


def id_da_operacao(*partes: str) -> str:
    """UUID determinístico: a mesma escrita (cliente, commit, conteúdo) gera sempre o mesmo id.
    Reenviar a operação depois de um timeout devolve a original e não cria memória nova."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "pqbr:" + "|".join(partes)))


def reter(conteudo: str, contexto: str = "", *, papel: str, tags: list[str], autor: str | None = None,
          operacao_id: str | None = None, transporte: Callable[[str, dict], dict] = _http) -> dict:
    """`autor` (opcional, ex.: cliente MCP) vira a tag de proveniência `autor:<nome>`, como `papel:<papel>`.
    `operacao_id` liga o modo assíncrono idempotente (o handshake do MCP usa; a indexação do canal não)."""
    carregar().exigir_escrita(papel, tags)
    if autor is not None and not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,40}", autor):
        raise ValueError("autor inválido")
    exigir_limpo({"conteudo": conteudo, "contexto": contexto}, "hindsight")
    corpo: dict = {"items": [{"content": conteudo, "context": contexto,
                              "tags": [*tags, f"papel:{papel}", *([f"autor:{autor}"] if autor else [])]}]}
    if operacao_id:
        corpo["async"] = True
        corpo["operation_id"] = operacao_id
    return transporte(f"{URL}/v1/default/banks/{BANK}/memories", corpo)


def recuperar(consulta: str, *, papel: str, transporte: Callable[[str, dict], dict] = _http) -> list[dict]:
    permitidas = set(carregar().tags_leitura(papel))
    r = transporte(f"{URL}/v1/default/banks/{BANK}/memories/recall",
                   {"query": consulta, "tags": sorted(permitidas), "tags_match": "any"})
    # defesa em profundidade: descarta o que voltar sem tag permitida
    return [m for m in r.get("results", []) if permitidas & set(m.get("tags") or [])]
