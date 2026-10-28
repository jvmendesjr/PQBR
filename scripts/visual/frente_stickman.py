"""Desenho recusado em 28/10 (t140u). Não é referência e não vai para o Flow.

Foi a frente de tubos sem roupa (t139u). Regravar este arquivo não reabre a ficha.

Roda a partir da raiz do repositório e regrava os PNG e os SVG em banco-fichas/personagens/.
Sem texto dentro da imagem: o modelo copia letra se a referência tiver letra.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[2]
DEST = RAIZ / "banco-fichas" / "personagens"
FUNDO = (244, 241, 234)
TINTA = (26, 26, 26)
CABECA = (255, 255, 255)
VERMELHO = (226, 59, 47)
AMARELO = (230, 179, 37)


def _disco(d: ImageDraw.ImageDraw, xy, r, cor):
    x, y = xy
    d.ellipse((x - r, y - r, x + r, y + r), fill=cor)


def _anel(d: ImageDraw.ImageDraw, xy, r, cor, esp):
    x, y = xy
    d.ellipse((x - r, y - r, x + r, y + r), outline=cor, width=esp)


def _tubo(d: ImageDraw.ImageDraw, a, b, esp):
    d.line((a, b), fill=TINTA, width=esp)
    _disco(d, a, esp // 2, TINTA)
    _disco(d, b, esp // 2, TINTA)


def figura(d: ImageDraw.ImageDraw, cx: int, pes_y: int, s: float, qual: str):
    """qual: 'M' ou 'F'. Os pés encostam em pes_y. A cabeça tem o mesmo raio nos dois."""
    esp = max(8, int(36 * s))
    r = int(150 * s)
    if qual == "M":
        quadril_y = pes_y - int(460 * s)
        pescoco_y = quadril_y - int(300 * s)
        meia_perna = int(150 * s)
    else:
        quadril_y = pes_y - int(320 * s)
        pescoco_y = quadril_y - int(250 * s)
        meia_perna = int(110 * s)
    cab_y = pescoco_y - r
    ombro_y = pescoco_y + int(90 * s)
    mao_y = ombro_y + int(150 * s)
    braco_x = int(250 * s)
    _tubo(d, (cx, pescoco_y), (cx, quadril_y), esp)
    _tubo(d, (cx, ombro_y), (cx - braco_x, mao_y), esp)
    _tubo(d, (cx, ombro_y), (cx + braco_x, mao_y), esp)
    _tubo(d, (cx, quadril_y), (cx - meia_perna, pes_y), esp)
    _tubo(d, (cx, quadril_y), (cx + meia_perna, pes_y), esp)
    _disco(d, (cx, cab_y), r, CABECA)
    _anel(d, (cx, cab_y), r, TINTA, esp)
    if qual == "F":
        coque = (cx + int(78 * s), cab_y - int(118 * s))
        _disco(d, coque, int(52 * s), CABECA)
        _anel(d, coque, int(52 * s), TINTA, max(6, int(esp * 0.75)))
    olho_y = cab_y + int(8 * s)
    olho_x = int(52 * s)
    olho_r = max(4, int(10 * s))
    _disco(d, (cx - olho_x, olho_y), olho_r, TINTA)
    _disco(d, (cx + olho_x, olho_y), olho_r, TINTA)
    boca_y = cab_y + int(78 * s)
    boca = int(28 * s)
    d.line((cx - boca, boca_y, cx + boca, boca_y), fill=TINTA, width=max(4, int(8 * s)))
    if qual == "M":
        aro = int(58 * s)
        ae = max(6, int(14 * s))
        _anel(d, (cx - olho_x, olho_y), aro, VERMELHO, ae)
        _anel(d, (cx + olho_x, olho_y), aro, VERMELHO, ae)
        ponte_y = olho_y
        d.line((cx - olho_x + aro, ponte_y, cx + olho_x - aro, ponte_y), fill=VERMELHO, width=ae)
    else:
        arg = (cx - r - int(6 * s), cab_y + int(36 * s))
        _anel(d, arg, int(16 * s), AMARELO, max(4, int(8 * s)))
        _disco(d, (cx - int(72 * s), boca_y - int(16 * s)), max(4, int(7 * s)), TINTA)


def _svg_figura(cx, pes_y, s, qual) -> str:
    """O mesmo desenho, em SVG, para quem for editar o traço sem abrir o PNG."""
    esp = max(8, int(36 * s))
    r = int(150 * s)
    if qual == "M":
        quadril_y = pes_y - int(460 * s)
        pescoco_y = quadril_y - int(300 * s)
        meia = int(150 * s)
    else:
        quadril_y = pes_y - int(320 * s)
        pescoco_y = quadril_y - int(250 * s)
        meia = int(110 * s)
    cab_y = pescoco_y - r
    ombro_y = pescoco_y + int(90 * s)
    mao_y = ombro_y + int(150 * s)
    bx = int(250 * s)
    linhas = [
        (cx, pescoco_y, cx, quadril_y),
        (cx, ombro_y, cx - bx, mao_y),
        (cx, ombro_y, cx + bx, mao_y),
        (cx, quadril_y, cx - meia, pes_y),
        (cx, quadril_y, cx + meia, pes_y),
    ]
    partes = []
    for x1, y1, x2, y2 in linhas:
        partes.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1a1a1a" '
            f'stroke-width="{esp}" stroke-linecap="round"/>'
        )
    partes.append(
        f'<circle cx="{cx}" cy="{cab_y}" r="{r}" fill="#ffffff" stroke="#1a1a1a" stroke-width="{esp}"/>'
    )
    if qual == "F":
        cr = int(52 * s)
        partes.append(
            f'<circle cx="{cx + int(78 * s)}" cy="{cab_y - int(118 * s)}" r="{cr}" '
            f'fill="#ffffff" stroke="#1a1a1a" stroke-width="{max(6, int(esp * 0.75))}"/>'
        )
    olho_y = cab_y + int(8 * s)
    ox = int(52 * s)
    orad = max(4, int(10 * s))
    for sinal in (-1, 1):
        partes.append(f'<circle cx="{cx + sinal * ox}" cy="{olho_y}" r="{orad}" fill="#1a1a1a"/>')
    boca_y = cab_y + int(78 * s)
    boca = int(28 * s)
    bw = max(4, int(8 * s))
    partes.append(
        f'<line x1="{cx - boca}" y1="{boca_y}" x2="{cx + boca}" y2="{boca_y}" '
        f'stroke="#1a1a1a" stroke-width="{bw}" stroke-linecap="round"/>'
    )
    if qual == "M":
        aro = int(58 * s)
        ae = max(6, int(14 * s))
        partes.append(
            f'<circle cx="{cx - ox}" cy="{olho_y}" r="{aro}" fill="none" stroke="#e23b2f" stroke-width="{ae}"/>'
        )
        partes.append(
            f'<circle cx="{cx + ox}" cy="{olho_y}" r="{aro}" fill="none" stroke="#e23b2f" stroke-width="{ae}"/>'
        )
        partes.append(
            f'<line x1="{cx - ox + aro}" y1="{olho_y}" x2="{cx + ox - aro}" y2="{olho_y}" '
            f'stroke="#e23b2f" stroke-width="{ae}" stroke-linecap="round"/>'
        )
    else:
        ae = max(4, int(8 * s))
        partes.append(
            f'<circle cx="{cx - r - int(6 * s)}" cy="{cab_y + int(36 * s)}" r="{int(16 * s)}" '
            f'fill="none" stroke="#e6b325" stroke-width="{ae}"/>'
        )
        partes.append(
            f'<circle cx="{cx - int(72 * s)}" cy="{boca_y - int(16 * s)}" r="{max(4, int(7 * s))}" fill="#1a1a1a"/>'
        )
    return "\n  ".join(partes)


def _gravar(nome: str, largura: int, altura: int, desenhar, svg_miolo: str):
    im = Image.new("RGB", (largura, altura), FUNDO)
    desenhar(ImageDraw.Draw(im))
    png = DEST / f"{nome}.png"
    svg = DEST / f"{nome}.svg"
    im.save(png, "PNG")
    svg.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
        f'viewBox="0 0 {largura} {altura}">\n'
        f'  <rect width="100%" height="100%" fill="#f4f1ea"/>\n  {svg_miolo}\n</svg>\n',
        encoding="utf-8",
    )
    print(png.relative_to(RAIZ), im.size)


def main():
    DEST.mkdir(parents=True, exist_ok=True)

    def um(qual, nome):
        def desenhar(d):
            figura(d, 540, 1680, 1.15, qual)
        _gravar(nome, 1080, 1920, desenhar, _svg_figura(540, 1680, 1.15, qual))

    um("M", "PERS-M")
    um("F", "PERS-F")

    def dois(d):
        figura(d, 480, 980, 0.72, "M")
        figura(d, 1440, 980, 0.72, "F")

    miolo = _svg_figura(480, 980, 0.72, "M") + "\n  " + _svg_figura(1440, 980, 0.72, "F")
    _gravar("ELENCO-frente", 1920, 1080, dois, miolo)


if __name__ == "__main__":
    main()
