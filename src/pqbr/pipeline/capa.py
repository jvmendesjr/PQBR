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
    if blur is None: mot.append("nitidez indisponível (blurdetect)")
    elif blur > NITIDEZ_MAX: mot.append(f"borrado ({blur:.1f})")
    return CandidatoCapa(arquivo=arquivo, largura=w, altura=h, luma=yavg or 0, contraste=contr, borrado=blur, ok=not mot, motivos=mot)


def escolher(quadros: list[str]) -> tuple[CandidatoCapa | None, list[CandidatoCapa]]:
    """Prioriza a cena 1 (gancho literal, §16.4) e a retomada final; depois o de maior contraste."""
    med = [medir(q) for q in quadros]
    ordem = ([med[0]] if med else []) + ([med[-1]] if len(med) > 1 else []) + sorted(med[1:-1], key=lambda c: -c.contraste)
    return next((c for c in ordem if c.ok), None), med


# ---- t466 (José 16:07): capa com foco único; detecta painéis/grade sem dependências (ffmpeg + Python puro) ----
class ChecagemPaineis(BaseModel):
    arquivo: str
    componentes: int
    razao_2o: float
    faixa_vazia: bool
    unico: bool
    motivo: str


def _pixels(arquivo: str, w: int = 90, h: int = 160) -> list[tuple[int, int, int]]:
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", arquivo, "-vf", f"scale={w}:{h},format=rgb24",
                          "-frames:v", "1", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return [tuple(raw[i:i + 3]) for i in range(0, w * h * 3, 3)]


def checar_paineis(arquivo: str, w: int = 90, h: int = 160, limiar: int = 45) -> ChecagemPaineis:
    """Fundo = mediana da borda; objeto = pixel distante do fundo. ≥ 2 blocos grandes separados por fundo, ou uma
    faixa inteira de fundo no miolo com conteúdo dos dois lados → painéis/grade (não é cena única)."""
    px = _pixels(arquivo, w, h)
    borda = [px[x] for x in range(w)] + [px[(h - 1) * w + x] for x in range(w)] + [px[y * w] for y in range(h)] + [px[y * w + w - 1] for y in range(h)]
    bg = tuple(sorted(c[i] for c in borda)[len(borda) // 2] for i in range(3))
    obj = [sum(abs(p[i] - bg[i]) for i in range(3)) > limiar for p in px]
    vistos, areas = [False] * (w * h), []
    for s in range(w * h):
        if not obj[s] or vistos[s]: continue
        pilha, n = [s], 0; vistos[s] = True
        while pilha:
            k = pilha.pop(); n += 1; y, x = divmod(k, w)
            for v in ((k - w) if y else -1, (k + w) if y < h - 1 else -1, (k - 1) if x else -1, (k + 1) if x < w - 1 else -1):
                if v >= 0 and obj[v] and not vistos[v]: vistos[v] = True; pilha.append(v)
        areas.append(n)
    grandes = sorted((a for a in areas if a >= 0.02 * w * h), reverse=True)
    razao = grandes[1] / grandes[0] if len(grandes) > 1 else 0.0
    linhas = [sum(obj[y * w:(y + 1) * w]) for y in range(h)]
    faixa = any(linhas[y] <= 1 and sum(linhas[:y]) > 0.08 * w * h and sum(linhas[y:]) > 0.08 * w * h for y in range(int(h * .2), int(h * .8)))
    motivo = ("faixa vazia separando blocos" if faixa else f"{len(grandes)} blocos (2º/1º = {razao:.2f})" if len(grandes) > 1 and razao >= 0.15 else "")
    return ChecagemPaineis(arquivo=arquivo, componentes=len(grandes), razao_2o=round(razao, 3), faixa_vazia=faixa, unico=not motivo, motivo=motivo or "cena única")
