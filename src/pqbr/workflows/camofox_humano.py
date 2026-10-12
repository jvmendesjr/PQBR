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
    """Clica no campo (mouse humano) e digita (curto, 70–190 ms por tecla sorteado a cada 1–3 teclas) ou cola (longo)."""
    clicar(tab, ref=ref, selector=selector, user=user)
    pausa_humana(0.4, 1.2)
    if len(texto) >= LIMITE_COLAR:
        return _post(f"/tabs/{tab}/type", {"userId": user, "ref": ref, "selector": selector, "text": texto, "mode": "fill"})
    r, i = {}, 0
    while i < len(texto):
        n = random.randint(1, 3); pedaco = texto[i:i + n]; i += n
        r = _post(f"/tabs/{tab}/type", {"userId": user, "text": pedaco, "mode": "keyboard", "delay": random.randint(70, 190)})
        if pedaco.endswith(" ") or random.random() < 0.15: pausa_humana(0.1, 0.6)
    return r


def rolar(tab: str, total: int = 900, direcao: str = "down", user: str = "pqbr") -> None:
    """Rolagem pela roda do mouse em passos irregulares (80–260 px) com pausas de leitura."""
    feito = 0
    while feito < total:
        passo = min(random.randint(80, 260), total - feito); feito += passo
        _post(f"/tabs/{tab}/scroll", {"userId": user, "direction": direcao, "amount": passo})
        pausa_humana(0.15, 0.9)
