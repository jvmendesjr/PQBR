"""Barreira de segredos/PII antes de todo escritor (F3-02, RNF-03, REGRAS §17).

- `exigir_limpo(obj, destino)`: percorre str/dict/list/modelos Pydantic e levanta
  `SegredoDetectado` (erro não repetível no Temporal) se achar segredo ou dado pessoal.
- `FiltroLog`: filtro de logging que **mascara** em vez de bloquear (log nunca derruba o fluxo).
Destinos: hindsight, ticket (Paperclip), banco (app), log, commit (pre-commit)."""
from __future__ import annotations
import logging
from typing import Any, Iterator
from .segredos import SegredoDetectado, encontrar, REGRAS

DESTINOS = {"hindsight", "ticket", "banco", "log", "commit", "notebooklm", "telegram"}


def _textos(obj: Any, prefixo: str = "") -> Iterator[tuple[str, str]]:
    if obj is None or isinstance(obj, (bool, int, float)):
        return
    if hasattr(obj, "model_dump"):
        obj = obj.model_dump(mode="json")
    if isinstance(obj, str):
        yield prefixo or "valor", obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _textos(str(k), f"{prefixo}.{k}<chave>")
            yield from _textos(v, f"{prefixo}.{k}" if prefixo else str(k))
    elif isinstance(obj, (list, tuple, set)):
        for i, v in enumerate(obj):
            yield from _textos(v, f"{prefixo}[{i}]")
    else:
        yield prefixo or "valor", str(obj)


def exigir_limpo(obj: Any, destino: str) -> Any:
    if destino not in DESTINOS:
        raise ValueError(f"destino desconhecido: {destino}")
    achados = [f"{campo}: {a}" for campo, t in _textos(obj) for a in encontrar(t)]
    if achados:
        raise SegredoDetectado(f"bloqueado antes de {destino}: " + "; ".join(achados))
    return obj


def mascarar(texto: str) -> str:
    for nome, rx in REGRAS:
        texto = rx.sub(f"[{nome} oculto]", texto)
    return texto


class FiltroLog(logging.Filter):
    """Instale em todo handler: `handler.addFilter(FiltroLog())`."""
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        limpo = mascarar(msg)
        if limpo != msg:
            record.msg, record.args = limpo, None
        return True


def instalar_no_logging(raiz: logging.Logger | None = None) -> None:
    raiz = raiz or logging.getLogger()
    for h in raiz.handlers or []:
        if not any(isinstance(f, FiltroLog) for f in h.filters):
            h.addFilter(FiltroLog())
    if not any(isinstance(f, FiltroLog) for f in raiz.filters):
        raiz.addFilter(FiltroLog())
