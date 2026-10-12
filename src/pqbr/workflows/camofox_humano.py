"""Ações humanizadas no Camofox PQBR (REGRAS §157/t186, José 12/10: regra canônica para TODA automação de navegador).
- Mouse: só via `/tabs/:id/click`; o Camoufox roda com `humanize: true` (cursor com trajetória humana, server.js).
- Texto curto (< LIMITE_COLAR): `/type` mode=keyboard, cadência humana (delay por tecla sorteado) e pausas.
- Texto longo: "colar" = `/type` mode=fill (um insert, como Ctrl+V), precedido de clique no campo e pausa.
- Toda ação é separada por pausa humana sorteada. Proibido: fill para texto curto, cliques via JS, rajadas sem pausa."""
from __future__ import annotations
import json, random, time, urllib.request
from .camofox import BASE, _chave

LIMITE_COLAR = 80


def pausa_humana(a: float = 0.8, b: float = 2.6) -> None:
    time.sleep(random.uniform(a, b))


def _post(path: str, corpo: dict) -> dict:
    req = urllib.request.Request(BASE + path, data=json.dumps(corpo).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + _chave(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def clicar(tab: str, *, ref: str | None = None, selector: str | None = None, user: str = "pqbr") -> dict:
    pausa_humana()
    return _post(f"/tabs/{tab}/click", {"userId": user, "ref": ref, "selector": selector})


def escrever(tab: str, texto: str, *, ref: str | None = None, selector: str | None = None, user: str = "pqbr") -> dict:
    """Clica no campo (mouse humano) e digita (curto) ou cola (longo)."""
    clicar(tab, ref=ref, selector=selector, user=user)
    pausa_humana(0.4, 1.2)
    if len(texto) >= LIMITE_COLAR:
        return _post(f"/tabs/{tab}/type", {"userId": user, "ref": ref, "selector": selector, "text": texto, "mode": "fill"})
    r = {}
    for pedaco in texto.split(" "):   # rajadas por palavra, delay por tecla variável
        r = _post(f"/tabs/{tab}/type", {"userId": user, "text": pedaco + " ", "mode": "keyboard",
                                        "delay": random.randint(70, 190)})
        pausa_humana(0.05, 0.45)
    return r
