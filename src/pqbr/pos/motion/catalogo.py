"""Catálogo do papel motion (REGRAS §26). `indice.json` é a fonte para o Python; cada `*.js` registra o mesmo slug no motor."""
from __future__ import annotations
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
INDICE = RAIZ / "catalogo" / "indice.json"
MOTOR_JS = RAIZ / "motor.js"

# Cores do elenco (banco-fichas, t144u) e da marca. Qualquer cor fora daqui é recusada pelo contrato.
PALETA = {
    "#2b6cb0", "#e23b2f", "#334155",   # PERS-M: camiseta, óculos, bermuda
    "#d96b43", "#e6b325", "#1e3a5f",   # PERS-F: camiseta, argola, bermuda
    "#0f766e", "#1f2328", "#6b7280", "#f6f1e7", "#ffffff",   # marca, tinta, tinta clara, fundo, branco
}
ZONA_SEGURA = {"topo": 0.14, "base": 0.20, "direita": 0.12}


@dataclass(frozen=True)
class ModeloCatalogo:
    slug: str
    descricao: str
    camada: str                       # tela_cheia | sobre | ambas
    parametros: dict[str, dict]

    @property
    def arquivo_js(self) -> Path: return RAIZ / "catalogo" / f"{self.slug}.js"


@lru_cache(maxsize=1)
def carregar_catalogo() -> dict[str, ModeloCatalogo]:
    dados = json.loads(INDICE.read_text(encoding="utf-8"))
    cat = {}
    for slug, m in dados["modelos"].items():
        if m["camada"] not in ("tela_cheia", "sobre", "ambas"): raise ValueError(f"{slug}: camada inválida")
        cat[slug] = ModeloCatalogo(slug, m["descricao"], m["camada"], m["parametros"])
    return cat


def arquivos_js() -> list[Path]:
    """motor.js primeiro, depois um arquivo por modelo, na ordem do índice."""
    return [MOTOR_JS] + [m.arquivo_js for m in carregar_catalogo().values()]
