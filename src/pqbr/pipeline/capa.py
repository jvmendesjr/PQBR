"""Gate A9 (capa/frame do Short), parte técnica por código (t427; critérios em docs/sdd/gate-a9.md).
Escolhe o melhor candidato entre os quadros extraídos: 9:16, nem escuro nem estourado, contraste, nitidez.
A parte de juízo (foco único, legível a ~120 px, segurança §16.6) vai ao juiz visual junto do pedido VISUAL."""
from __future__ import annotations
import json, re, subprocess
from pydantic import BaseModel

LUMA = (40.0, 215.0)      # média Y (0–255)
CONTRASTE_MIN = 28.0      # desvio aproximado (YHIGH-YLOW)/2
NITIDEZ_MAX = 9.0         # blurdetect: maior = mais borrado


class CandidatoCapa(BaseModel):
    arquivo: str
    largura: int
    altura: int
    luma: float
    contraste: float
    borrado: float | None
    ok: bool
    motivos: list[str]


def medir(arquivo: str) -> CandidatoCapa:
    p = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                   "-of", "json", arquivo], capture_output=True, text=True, check=True).stdout)["streams"][0]
    log = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", arquivo, "-vf", "signalstats,metadata=print,blurdetect,metadata=print",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    g = lambda k: float(m.group(1)) if (m := re.search(rf"{k}=([0-9.]+)", log)) else None
    yavg, ylow, yhigh, blur = g("lavfi.signalstats.YAVG"), g("lavfi.signalstats.YLOW"), g("lavfi.signalstats.YHIGH"), g("lavfi.blur")
    w, h = int(p["width"]), int(p["height"]); mot = []
    if abs(w / h - 9 / 16) > 0.02: mot.append("não é 9:16")
    if h < 640: mot.append("altura < 640 px")
    if yavg is None or not LUMA[0] <= yavg <= LUMA[1]: mot.append(f"luma fora da faixa ({yavg})")
    contr = ((yhigh or 0) - (ylow or 0)) / 2
    if contr < CONTRASTE_MIN: mot.append(f"contraste baixo ({contr:.0f})")
    if blur is not None and blur > NITIDEZ_MAX: mot.append(f"borrado ({blur:.1f})")
    return CandidatoCapa(arquivo=arquivo, largura=w, altura=h, luma=yavg or 0, contraste=contr, borrado=blur, ok=not mot, motivos=mot)


def escolher(quadros: list[str]) -> tuple[CandidatoCapa | None, list[CandidatoCapa]]:
    """Prioriza a cena 1 (gancho literal, §16.4) e a retomada final; depois o de maior contraste."""
    med = [medir(q) for q in quadros]
    ordem = ([med[0]] if med else []) + ([med[-1]] if len(med) > 1 else []) + sorted(med[1:-1], key=lambda c: -c.contraste)
    return next((c for c in ordem if c.ok), None), med
