"""Barreira antes dos escritores (F3-02, RNF-03, REGRAS §17).

Logs contaminados são descartados inteiros, inclusive exceções e campos extra.
"""
from __future__ import annotations

import logging
import traceback
from collections.abc import Mapping
from typing import Any, Iterator

from .segredos import SegredoDetectado, encontrar, REGRAS

DESTINOS = {"hindsight", "ticket", "banco", "log", "commit", "notebooklm", "telegram"}


def _textos(obj: Any) -> Iterator[str]:
    if obj is None or isinstance(obj, (bool, int, float)):
        return
    if hasattr(obj, "model_dump"):
        obj = obj.model_dump(mode="json")
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, (bytes, bytearray, memoryview)):
        yield bytes(obj).decode("utf-8", errors="replace")
    elif isinstance(obj, Mapping):
        for k, v in obj.items():
            yield from _textos(str(k))
            # Uma senha opaca isolada pode não ter prefixo reconhecível.
            if isinstance(v, (str, int, float, bytes, bytearray, memoryview)):
                valor = bytes(v).decode("utf-8", errors="replace") if isinstance(v, (bytes, bytearray, memoryview)) else str(v)
                yield f"{k}={valor}"
            yield from _textos(v)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for v in obj:
            yield from _textos(v)
    else:
        yield str(obj)


def exigir_limpo(obj: Any, destino: str) -> Any:
    if destino not in DESTINOS:
        raise ValueError("destino desconhecido")
    regras = sorted({a.regra for t in _textos(obj) for a in encontrar(t)})
    if regras:
        # Nem valores, nem chaves/caminhos controlados pela entrada vão ao erro.
        raise SegredoDetectado(f"bloqueado antes de {destino}: " + ", ".join(regras))
    return obj


def mascarar(texto: str) -> str:
    for nome, rx in REGRAS:
        texto = rx.sub(f"[{nome} oculto]", texto)
    return texto


class FiltroLog(logging.Filter):
    """Bloqueia antes do formatter/handler, sem derrubar o fluxo."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            exigir_limpo(record.getMessage(), "log")
            exigir_limpo(record.__dict__, "log")
            if record.exc_info:
                exigir_limpo("".join(traceback.format_exception(*record.exc_info)), "log")
        except Exception:
            # Falha de formatação/inspeção também não emite dados não validados.
            return False
        return True


def instalar_no_logging(raiz: logging.Logger | None = None) -> None:
    """Instale após configurar handlers; reaplique se adicionar outros handlers."""
    raiz = raiz or logging.getLogger()
    for h in raiz.handlers:
        if not any(isinstance(f, FiltroLog) for f in h.filters):
            h.addFilter(FiltroLog())
    if not any(isinstance(f, FiltroLog) for f in raiz.filters):
        raiz.addFilter(FiltroLog())
