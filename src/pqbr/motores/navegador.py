"""Adaptador NavegadorIdentidade (ADR-012, t526). Workflows falam com esta porta, nunca com a porta TCP do Camofox.
NÃO ligado em produção: acesso.py/camofox.py continuam como estão até a migração (runbook)."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Protocol
from ..contratos import InstanciaNavegador, SaudeNavegador

CONFIG = Path(__file__).resolve().parents[3] / "config/camofox_instancias.json"


def instancias(caminho: Path = CONFIG) -> list[InstanciaNavegador]:
    d = json.loads(caminho.read_text(encoding="utf-8"))
    out = [InstanciaNavegador.model_validate(i) for i in d["instancias"]]
    portas = [i.porta for i in out]
    if len(set(portas)) != len(portas): raise ValueError("porta repetida entre instâncias")
    if sum(i.estado == "ativa" for i in out) > d.get("limite_simultaneas", 3): raise ValueError("acima do limite de instâncias")
    return out


def instancia(conta: str, caminho: Path = CONFIG) -> InstanciaNavegador:
    for i in instancias(caminho):
        if i.conta == conta: return i
    raise KeyError(conta)


class NavegadorIdentidade(Protocol):
    conta: str
    def saude(self) -> SaudeNavegador: ...


class NavegadorCamofox:
    """Implementação HTTP mínima (só /health, leitura). Reservada/não instalada → recusa sem tocar a rede."""
    def __init__(self, inst: InstanciaNavegador, timeout: float = 5.0):
        self.inst, self.conta, self.timeout = inst, inst.conta, timeout

    def saude(self) -> SaudeNavegador:
        if self.inst.estado == "reservada":
            return SaudeNavegador(conta=self.conta, porta=self.inst.porta, ok=False, motivo="instância reservada (não instalada)")
        import urllib.request
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{self.inst.porta}/health", timeout=self.timeout) as r:
                d = json.load(r)
            return SaudeNavegador(conta=self.conta, porta=self.inst.porta, ok=bool(d.get("ok")),
                                  navegador=bool(d.get("browserRunning")), motivo=d.get("reason") or "")
        except Exception as e:
            return SaudeNavegador(conta=self.conta, porta=self.inst.porta, ok=False, motivo=type(e).__name__)
