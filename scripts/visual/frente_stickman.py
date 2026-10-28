"""Gera as folhas e recortes 2D chapados do banco de fichas da PQBR (t140u/t141u/t144u).

Personagens (banco-fichas/personagens/):
- Cabeça redonda branca (#ffffff) com contorno preto (#1a1a1a), membros finos de palito (#1a1a1a),
  roupa 2D chapada fixa sem volume 3D e cara com sobrancelha, olho e boca fechada de reação.
- PERS-M (mais alto): óculos redondos vermelhos (#e23b2f), camiseta azul-petróleo chapada (#2b6cb0)
  e bermuda ardósia chapada (#334155).
- PERS-F (mais baixa): coque redondo no alto à direita de quem olha, argola amarela (#e6b325) à esquerda,
  pinta preta pequena à esquerda da boca, blusa terracota chapada (#d96b43) e calça marinho chapada (#1e3a5f).
- Gera recortes individuais 9:16 (PERS-M, PERS-F) para envio ao Flow, folhas completas 16:9 com
  frente + perfil + 4 expressões (PERS-M-folha, PERS-F-folha) e comparação de altura (ELENCO-frente).

Ambientes (banco-fichas/ambientes/) e Objetos (banco-fichas/objetos/):
- Gera referências 2D chapadas limpas em PNG e SVG sem nenhuma letra/texto na imagem.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[2]
FICHAS = RAIZ / "banco-fichas"
DEST = FICHAS / "personagens"
DEST_AMB = FICHAS / "ambientes"
DEST_OBJ = FICHAS / "objetos"

FUNDO = (244, 241, 234)
TINTA = (26, 26, 26)
CABECA = (255, 255, 255)
VERMELHO = (226, 59, 47)
AMARELO = (230, 179, 37)

CAMISA_M = (43, 108, 176)    # #2b6cb0 azul-petróleo chapado
BERMUDA_M = (51, 65, 85)     # #334155 cinza-ardósia chapado
BLUSA_F = (217, 107, 67)     # #d96b43 terracota chapado
CALCA_F = (30, 58, 95)       # #1e3a5f azul-marinho chapado


def _hex(rgb: tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def _disco(d: ImageDraw.ImageDraw, xy: tuple[int, int], r: int, cor: tuple[int, int, int]) -> None:
    x, y = xy
    d.ellipse((x - r, y - r, x + r, y + r), fill=cor)


def _anel(d: ImageDraw.ImageDraw, xy: tuple[int, int], r: int, cor: tuple[int, int, int], esp: int) -> None:
    x, y = xy
    d.ellipse((x - r, y - r, x + r, y + r), outline=cor, width=esp)


def _palito(d: ImageDraw.ImageDraw, a: tuple[int, int], b: tuple[int, int], esp: int) -> None:
    d.line((a, b), fill=TINTA, width=esp)
    _disco(d, a, esp // 2, TINTA)
    _disco(d, b, esp // 2, TINTA)


def _poligono(d: ImageDraw.ImageDraw, pts: list[tuple[int, int]], recheio: tuple[int, int, int], esp: int) -> None:
    d.polygon(pts, fill=recheio)
    n = len(pts)
    for i in range(n):
        _palito(d, pts[i], pts[(i + 1) % n], esp)


def cabeca_expressao(
    d: ImageDraw.ImageDraw,
    cx: int,
    cab_y: int,
    s: float,
    qual: str,
    expressao: str = "curioso",
    perfil: bool = False,
) -> str:
    """Desenha a cabeça (PIL) e devolve o trecho SVG correspondente."""
    esp_cont = max(6, int(18 * s))
    esp_traco = max(4, int(10 * s))
    r = int(145 * s)
    partes: list[str] = []

    if qual == "F":
        coque_x = cx + (int(82 * s) if not perfil else -int(78 * s))
        coque_y = cab_y - int(115 * s)
        cr = int(50 * s)
        _disco(d, (coque_x, coque_y), cr, CABECA)
        _anel(d, (coque_x, coque_y), cr, TINTA, esp_cont)
        partes.append(
            f'<circle cx="{coque_x}" cy="{coque_y}" r="{cr}" fill="#ffffff" stroke="#1a1a1a" stroke-width="{esp_cont}"/>'
        )

    _disco(d, (cx, cab_y), r, CABECA)
    _anel(d, (cx, cab_y), r, TINTA, esp_cont)
    partes.append(
        f'<circle cx="{cx}" cy="{cab_y}" r="{r}" fill="#ffffff" stroke="#1a1a1a" stroke-width="{esp_cont}"/>'
    )

    olho_y = cab_y + int(6 * s)
    ox = int(50 * s)
    orad = max(5, int(11 * s))
    if expressao == "surpreso":
        orad = max(6, int(15 * s))

    olhos = [cx + int(42 * s)] if perfil else [cx - ox, cx + ox]
    for ex in olhos:
        _disco(d, (ex, olho_y), orad, TINTA)
        partes.append(f'<circle cx="{ex}" cy="{olho_y}" r="{orad}" fill="#1a1a1a"/>')

    # Sobrancelhas de reação (acima do aro no PERS-M para leitura imediata)
    sob_y = olho_y - (int(62 * s) if qual == "M" else int(40 * s))
    sob_w = int(26 * s)
    for idx, ex in enumerate(olhos):
        dy_esq, dy_dir = 0, 0
        if expressao == "curioso":
            dy_esq = -int(8 * s) if idx == 0 else int(2 * s)
            dy_dir = int(2 * s) if idx == 0 else -int(10 * s)
        elif expressao == "surpreso":
            dy_esq = -int(14 * s)
            dy_dir = -int(14 * s)
        elif expressao == "pensativo":
            dy_esq = int(6 * s) if idx == 0 else -int(8 * s)
            dy_dir = -int(4 * s) if idx == 0 else int(4 * s)
        elif expressao == "satisfeito":
            dy_esq = -int(6 * s)
            dy_dir = -int(6 * s)
        p1 = (ex - sob_w, sob_y + dy_esq)
        p2 = (ex + sob_w, sob_y + dy_dir)
        _palito(d, p1, p2, esp_traco)
        partes.append(
            f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" '
            f'stroke="#1a1a1a" stroke-width="{esp_traco}" stroke-linecap="round"/>'
        )

    # Boca sempre fechada (lips closed) com reação clara
    boca_y = cab_y + int(76 * s)
    bx = cx + (int(28 * s) if perfil else 0)
    bw = int(28 * s)
    if expressao == "surpreso":
        # Pequeno traço fechado contraído de espanto (sem abrir boca de fala)
        p1, p2 = (bx - int(14 * s), boca_y + int(4 * s)), (bx + int(14 * s), boca_y - int(4 * s))
        _palito(d, p1, p2, esp_traco)
        partes.append(
            f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" '
            f'stroke="#1a1a1a" stroke-width="{esp_traco}" stroke-linecap="round"/>'
        )
    elif expressao == "pensativo":
        p1, p2 = (bx - bw, boca_y + int(6 * s)), (bx + int(16 * s), boca_y - int(6 * s))
        _palito(d, p1, p2, esp_traco)
        partes.append(
            f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" '
            f'stroke="#1a1a1a" stroke-width="{esp_traco}" stroke-linecap="round"/>'
        )
    else:
        # Curioso / satisfeito: leve sorriso fechado em V suave de dois segmentos
        meio_y = boca_y + (int(12 * s) if expressao == "satisfeito" else int(7 * s))
        p1, pm, p2 = (bx - bw, boca_y), (bx, meio_y), (bx + bw, boca_y - int(3 * s))
        _palito(d, p1, pm, esp_traco)
        _palito(d, pm, p2, esp_traco)
        partes.append(
            f'<path d="M {p1[0]} {p1[1]} Q {pm[0]} {pm[1] + int(4 * s)} {p2[0]} {p2[1]}" '
            f'fill="none" stroke="#1a1a1a" stroke-width="{esp_traco}" stroke-linecap="round"/>'
        )

    if qual == "M":
        aro = int(46 * s)
        ae = max(5, int(11 * s))
        if perfil:
            gx = cx + int(42 * s)
            _anel(d, (gx, olho_y), aro, VERMELHO, ae)
            d.line((cx - int(10 * s), olho_y, gx - aro, olho_y), fill=VERMELHO, width=ae)
            partes.append(
                f'<circle cx="{gx}" cy="{olho_y}" r="{aro}" fill="none" stroke="#e23b2f" stroke-width="{ae}"/>'
            )
            partes.append(
                f'<line x1="{cx - int(10 * s)}" y1="{olho_y}" x2="{gx - aro}" y2="{olho_y}" '
                f'stroke="#e23b2f" stroke-width="{ae}" stroke-linecap="round"/>'
            )
        else:
            _anel(d, (cx - ox, olho_y), aro, VERMELHO, ae)
            _anel(d, (cx + ox, olho_y), aro, VERMELHO, ae)
            d.line((cx - ox + aro, olho_y, cx + ox - aro, olho_y), fill=VERMELHO, width=ae)
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
        arg_x = cx - r - int(5 * s) if not perfil else cx - int(18 * s)
        arg_y = cab_y + int(34 * s)
        _anel(d, (arg_x, arg_y), int(16 * s), AMARELO, ae)
        pinta_x = (cx - int(70 * s)) if not perfil else (cx + int(2 * s))
        pinta_y = boca_y - int(14 * s)
        _disco(d, (pinta_x, pinta_y), max(4, int(7 * s)), TINTA)
        partes.append(
            f'<circle cx="{arg_x}" cy="{arg_y}" r="{int(16 * s)}" fill="none" stroke="#e6b325" stroke-width="{ae}"/>'
        )
        partes.append(f'<circle cx="{pinta_x}" cy="{pinta_y}" r="{max(4, int(7 * s))}" fill="#1a1a1a"/>')

    return "\n  ".join(partes)


def figura(
    d: ImageDraw.ImageDraw,
    cx: int,
    pes_y: int,
    s: float,
    qual: str,
    expressao: str = "curioso",
    perfil: bool = False,
) -> str:
    """Desenha corpo inteiro com roupa chapada 2D e membros finos de palito; devolve SVG."""
    esp_membro = max(6, int(18 * s))
    esp_roupa = max(5, int(12 * s))
    r = int(145 * s)
    if qual == "M":
        quadril_y = pes_y - int(450 * s)
        pescoco_y = quadril_y - int(310 * s)
        meia_perna = int(125 * s) if not perfil else int(55 * s)
        cor_top, cor_bot = CAMISA_M, BERMUDA_M
        larg_top = int(92 * s) if not perfil else int(62 * s)
        larg_bot = int(86 * s) if not perfil else int(58 * s)
        alt_bot = int(165 * s)
    else:
        quadril_y = pes_y - int(320 * s)
        pescoco_y = quadril_y - int(255 * s)
        meia_perna = int(95 * s) if not perfil else int(45 * s)
        cor_top, cor_bot = BLUSA_F, CALCA_F
        larg_top = int(82 * s) if not perfil else int(56 * s)
        larg_bot = int(78 * s) if not perfil else int(52 * s)
        alt_bot = int(145 * s)

    cab_y = pescoco_y - r
    ombro_y = pescoco_y + int(36 * s)
    mao_y = ombro_y + int(220 * s)
    braco_x = int(215 * s) if not perfil else int(110 * s)
    joelho_y = quadril_y + alt_bot

    partes: list[str] = []

    # Pescoço e membros finos de palito (desenhados antes da roupa chapada para acabamento limpo)
    membros = [
        ((cx, pescoco_y - int(10 * s)), (cx, ombro_y + int(20 * s))),
        ((cx - larg_top + int(10 * s), ombro_y + int(24 * s)), (cx - braco_x, mao_y)),
        ((cx + larg_top - int(10 * s), ombro_y + int(24 * s)), (cx + braco_x, mao_y)),
        ((cx - int(meia_perna * 0.55), joelho_y - int(10 * s)), (cx - meia_perna, pes_y)),
        ((cx + int(meia_perna * 0.55), joelho_y - int(10 * s)), (cx + meia_perna, pes_y)),
    ]
    for a, b in membros:
        _palito(d, a, b, esp_membro)
        partes.append(
            f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" '
            f'stroke="#1a1a1a" stroke-width="{esp_membro}" stroke-linecap="round"/>'
        )

    # Mãos e pés simples (sem dedos, apenas terminação arredondada limpa)
    pe_w = int(28 * s)
    for px, dir_s in ((cx - meia_perna, -1 if not perfil else 1), (cx + meia_perna, 1)):
        p_fim = (px + dir_s * pe_w, pes_y)
        _palito(d, (px, pes_y), p_fim, esp_membro)
        partes.append(
            f'<line x1="{px}" y1="{pes_y}" x2="{p_fim[0]}" y2="{p_fim[1]}" '
            f'stroke="#1a1a1a" stroke-width="{esp_membro}" stroke-linecap="round"/>'
        )

    # Peça inferior chapada (bermuda/calça curta 2D)
    pts_bot = [
        (cx - larg_bot, quadril_y - int(12 * s)),
        (cx + larg_bot, quadril_y - int(12 * s)),
        (cx + larg_bot + int(8 * s), joelho_y),
        (cx + int(14 * s), joelho_y),
        (cx, quadril_y + int(42 * s)),
        (cx - int(14 * s), joelho_y),
        (cx - larg_bot - int(8 * s), joelho_y),
    ]
    _poligono(d, pts_bot, cor_bot, esp_roupa)
    pts_bot_str = " ".join(f"{x},{y}" for x, y in pts_bot)
    partes.append(
        f'<polygon points="{pts_bot_str}" fill="{_hex(cor_bot)}" stroke="#1a1a1a" '
        f'stroke-width="{esp_roupa}" stroke-linejoin="round"/>'
    )

    # Peça superior chapada (camiseta/blusa 2D com mangas curtas chapadas)
    manga_w = int(42 * s) if not perfil else int(20 * s)
    manga_h = int(78 * s)
    pts_top = [
        (cx - larg_top, ombro_y),
        (cx + larg_top, ombro_y),
        (cx + larg_top + manga_w, ombro_y + manga_h),
        (cx + larg_top - int(8 * s), ombro_y + manga_h + int(18 * s)),
        (cx + larg_bot, quadril_y),
        (cx - larg_bot, quadril_y),
        (cx - larg_top + int(8 * s), ombro_y + manga_h + int(18 * s)),
        (cx - larg_top - manga_w, ombro_y + manga_h),
    ]
    _poligono(d, pts_top, cor_top, esp_roupa)
    pts_top_str = " ".join(f"{x},{y}" for x, y in pts_top)
    partes.append(
        f'<polygon points="{pts_top_str}" fill="{_hex(cor_top)}" stroke="#1a1a1a" '
        f'stroke-width="{esp_roupa}" stroke-linejoin="round"/>'
    )

    partes.append(cabeca_expressao(d, cx, cab_y, s, qual, expressao=expressao, perfil=perfil))
    return "\n  ".join(partes)


def _gravar(pasta: Path, nome: str, largura: int, altura: int, desenhar, svg_miolo: str, fundo_rgb=FUNDO) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGB", (largura, altura), fundo_rgb)
    desenhar(ImageDraw.Draw(im))
    png = pasta / f"{nome}.png"
    svg = pasta / f"{nome}.svg"
    im.save(png, "PNG")
    svg.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
        f'viewBox="0 0 {largura} {altura}">\n'
        f'  <rect width="100%" height="100%" fill="{_hex(fundo_rgb)}"/>\n  {svg_miolo}\n</svg>\n',
        encoding="utf-8",
    )
    print(png.relative_to(RAIZ), im.size)


def gerar_personagens() -> None:
    for qual, nome in (("M", "PERS-M"), ("F", "PERS-F")):
        svg_holder: list[str] = []

        def desenhar_recorte(d: ImageDraw.ImageDraw, q: str = qual) -> None:
            svg_holder.append(figura(d, 540, 1700, 1.15, q, expressao="curioso", perfil=False))

        _gravar(DEST, nome, 1080, 1920, desenhar_recorte, "")
        # Regrava SVG com o miolo gerado durante o desenho
        (DEST / f"{nome}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">\n'
            f'  <rect width="100%" height="100%" fill="{_hex(FUNDO)}"/>\n  {svg_holder[0]}\n</svg>\n',
            encoding="utf-8",
        )

        # Folha completa 16:9: frente, perfil e 4 cabeças de expressão (sem texto)
        svg_folha: list[str] = []

        def desenhar_folha(d: ImageDraw.ImageDraw, q: str = qual) -> None:
            svg_folha.append(figura(d, 370, 960, 0.72, q, expressao="curioso", perfil=False))
            svg_folha.append(figura(d, 870, 960, 0.72, q, expressao="curioso", perfil=True))
            expressoes = [("curioso", 1320, 310), ("surpreso", 1680, 310), ("pensativo", 1320, 740), ("satisfeito", 1680, 740)]
            for exp, ex_x, ex_y in expressoes:
                svg_folha.append(cabeca_expressao(d, ex_x, ex_y, 0.72, q, expressao=exp, perfil=False))

        _gravar(DEST, f"{nome}-folha", 1920, 1080, desenhar_folha, "")
        (DEST / f"{nome}-folha.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">\n'
            f'  <rect width="100%" height="100%" fill="{_hex(FUNDO)}"/>\n  ' + "\n  ".join(svg_folha) + "\n</svg>\n",
            encoding="utf-8",
        )

    svg_elenco: list[str] = []

    def desenhar_elenco(d: ImageDraw.ImageDraw) -> None:
        svg_elenco.append(figura(d, 520, 980, 0.74, "M", expressao="curioso", perfil=False))
        svg_elenco.append(figura(d, 1400, 980, 0.74, "F", expressao="satisfeito", perfil=False))

    _gravar(DEST, "ELENCO-frente", 1920, 1080, desenhar_elenco, "")
    (DEST / "ELENCO-frente.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">\n'
        f'  <rect width="100%" height="100%" fill="{_hex(FUNDO)}"/>\n  ' + "\n  ".join(svg_elenco) + "\n</svg>\n",
        encoding="utf-8",
    )


def gerar_ambientes() -> None:
    # AMB-cozinha (1080x1920, 2D chapado, luz da manhã, parede creme, azulejos verde-água pálido, bancada/mesa madeira)
    def des_cozinha(d: ImageDraw.ImageDraw) -> None:
        d.rectangle((0, 0, 1080, 1320), fill=(244, 241, 234))
        d.rectangle((0, 1320, 1080, 1920), fill=(230, 222, 208), outline=TINTA, width=8)
        # Faixa de azulejos geométricos simples
        d.rectangle((0, 760, 1080, 1080), fill=(220, 234, 229), outline=TINTA, width=8)
        for x in range(0, 1080, 180):
            d.line((x, 760, x, 1080), fill=TINTA, width=5)
        d.line((0, 920, 1080, 920), fill=TINTA, width=5)
        # Janela com luz da manhã
        d.rectangle((140, 220, 560, 660), fill=(255, 253, 244), outline=TINTA, width=10)
        d.line((350, 220, 350, 660), fill=TINTA, width=8)
        d.line((140, 440, 560, 440), fill=TINTA, width=8)
        # Mesa/bancada de madeira clara chapada na frente
        d.rectangle((90, 1180, 990, 1250), fill=(212, 163, 115), outline=TINTA, width=10)
        d.rectangle((150, 1250, 210, 1740), fill=(181, 131, 90), outline=TINTA, width=10)
        d.rectangle((870, 1250, 930, 1740), fill=(181, 131, 90), outline=TINTA, width=10)

    svg_cozinha = (
        '<rect x="0" y="1320" width="1080" height="600" fill="#e6ded0" stroke="#1a1a1a" stroke-width="8"/>\n'
        '  <rect x="0" y="760" width="1080" height="320" fill="#dceae5" stroke="#1a1a1a" stroke-width="8"/>\n'
        '  <rect x="140" y="220" width="420" height="440" fill="#fffdf4" stroke="#1a1a1a" stroke-width="10"/>\n'
        '  <line x1="350" y1="220" x2="350" y2="660" stroke="#1a1a1a" stroke-width="8"/>\n'
        '  <line x1="140" y1="440" x2="560" y2="440" stroke="#1a1a1a" stroke-width="8"/>\n'
        '  <rect x="90" y="1180" width="900" height="70" fill="#d4a373" stroke="#1a1a1a" stroke-width="10"/>\n'
        '  <rect x="150" y="1250" width="60" height="490" fill="#b5835a" stroke="#1a1a1a" stroke-width="10"/>\n'
        '  <rect x="870" y="1250" width="60" height="490" fill="#b5835a" stroke="#1a1a1a" stroke-width="10"/>'
    )
    _gravar(DEST_AMB, "AMB-cozinha", 1080, 1920, des_cozinha, svg_cozinha)

    # AMB-sala (1080x1920, 2D chapado, sala brasileira à noite com luz acolhedora de abajur, sofá e TV)
    def des_sala(d: ImageDraw.ImageDraw) -> None:
        d.rectangle((0, 0, 1080, 1360), fill=(239, 236, 230))
        d.rectangle((0, 1360, 1080, 1920), fill=(214, 203, 187), outline=TINTA, width=8)
        # Abajur de piso com cúpula amarela suave
        d.line((210, 740, 210, 1460), fill=TINTA, width=10)
        d.rectangle((150, 1450, 270, 1480), fill=(51, 65, 85), outline=TINTA, width=8)
        _poligono(d, [(130, 740), (290, 740), (255, 600), (165, 600)], (246, 224, 94), 10)
        # Sofá azul-acinzentado chapado
        d.rectangle((140, 1060, 940, 1360), fill=(100, 116, 139), outline=TINTA, width=10)
        d.rectangle((100, 1160, 200, 1440), fill=(71, 85, 105), outline=TINTA, width=10)
        d.rectangle((880, 1160, 980, 1440), fill=(71, 85, 105), outline=TINTA, width=10)
        d.rectangle((180, 1240, 900, 1440), fill=(100, 116, 139), outline=TINTA, width=10)
        # Rack e TV simples em perfil lateral/frontal limpo
        d.rectangle((660, 680, 960, 880), fill=(30, 41, 59), outline=TINTA, width=10)

    svg_sala = (
        '<rect x="0" y="1360" width="1080" height="560" fill="#d6cbbb" stroke="#1a1a1a" stroke-width="8"/>\n'
        '  <line x1="210" y1="740" x2="210" y2="1460" stroke="#1a1a1a" stroke-width="10"/>\n'
        '  <polygon points="130,740 290,740 255,600 165,600" fill="#f6e05e" stroke="#1a1a1a" stroke-width="10"/>\n'
        '  <rect x="660" y="680" width="300" height="200" fill="#1e293b" stroke="#1a1a1a" stroke-width="10"/>\n'
        '  <rect x="140" y="1060" width="800" height="300" fill="#64748b" stroke="#1a1a1a" stroke-width="10"/>\n'
        '  <rect x="100" y="1160" width="100" height="280" fill="#475569" stroke="#1a1a1a" stroke-width="10"/>\n'
        '  <rect x="880" y="1160" width="100" height="280" fill="#475569" stroke="#1a1a1a" stroke-width="10"/>\n'
        '  <rect x="180" y="1240" width="720" height="200" fill="#64748b" stroke="#1a1a1a" stroke-width="10"/>'
    )
    _gravar(DEST_AMB, "AMB-sala", 1080, 1920, des_sala, svg_sala, fundo_rgb=(239, 236, 230))


def gerar_objetos() -> None:
    # OBJ-chaleira (1080x1080, azul-esmalte chapado #3b82f6, bico à vista, alça preta)
    def des_chaleira(d: ImageDraw.ImageDraw) -> None:
        _anel(d, (540, 360), 150, TINTA, 22)
        _poligono(d, [(720, 620), (880, 470), (920, 510), (760, 700)], (59, 130, 246), 12)
        _poligono(d, [(280, 780), (800, 780), (720, 480), (360, 480)], (59, 130, 246), 12)
        d.rectangle((410, 440, 670, 485), fill=(37, 99, 235), outline=TINTA, width=10)
        _disco(d, (540, 415), 28, TINTA)

    svg_chaleira = (
        '<circle cx="540" cy="360" r="150" fill="none" stroke="#1a1a1a" stroke-width="22"/>\n'
        '  <polygon points="720,620 880,470 920,510 760,700" fill="#3b82f6" stroke="#1a1a1a" stroke-width="12"/>\n'
        '  <polygon points="280,780 800,780 720,480 360,480" fill="#3b82f6" stroke="#1a1a1a" stroke-width="12"/>\n'
        '  <rect x="410" y="440" width="260" height="45" fill="#2563eb" stroke="#1a1a1a" stroke-width="10"/>\n'
        '  <circle cx="540" cy="415" r="28" fill="#1a1a1a"/>'
    )
    _gravar(DEST_OBJ, "OBJ-chaleira", 1080, 1080, des_chaleira, svg_chaleira)

    # OBJ-xicara (1080x1080, xícara branca lisa #ffffff com alça simples e pires)
    def des_xicara(d: ImageDraw.ImageDraw) -> None:
        _anel(d, (730, 540), 95, TINTA, 20)
        _disco(d, (730, 540), 75, FUNDO)
        _poligono(d, [(310, 390), (730, 390), (670, 720), (370, 720)], CABECA, 12)
        d.rectangle((220, 720, 820, 770), fill=CABECA, outline=TINTA, width=12)

    svg_xicara = (
        '<circle cx="730" cy="540" r="95" fill="none" stroke="#1a1a1a" stroke-width="20"/>\n'
        '  <polygon points="310,390 730,390 670,720 370,720" fill="#ffffff" stroke="#1a1a1a" stroke-width="12"/>\n'
        '  <rect x="220" y="720" width="600" height="50" fill="#ffffff" stroke="#1a1a1a" stroke-width="12"/>'
    )
    _gravar(DEST_OBJ, "OBJ-xicara", 1080, 1080, des_xicara, svg_xicara)

    # OBJ-filtro-pano (1080x1080, coador de pano em algodão cru #ede0d4 com aro e cabo #334155)
    def des_filtro(d: ImageDraw.ImageDraw) -> None:
        _palito(d, (180, 340), (360, 340), 20)
        _poligono(d, [(360, 340), (820, 340), (660, 820), (520, 820)], (237, 224, 212), 12)
        d.rectangle((345, 320, 835, 360), fill=(51, 65, 85), outline=TINTA, width=10)

    svg_filtro = (
        '<line x1="180" y1="340" x2="360" y2="340" stroke="#1a1a1a" stroke-width="20" stroke-linecap="round"/>\n'
        '  <polygon points="360,340 820,340 660,820 520,820" fill="#ede0d4" stroke="#1a1a1a" stroke-width="12"/>\n'
        '  <rect x="345" y="320" width="490" height="40" fill="#334155" stroke="#1a1a1a" stroke-width="10"/>'
    )
    _gravar(DEST_OBJ, "OBJ-filtro-pano", 1080, 1080, des_filtro, svg_filtro)

    # OBJ-controle-remoto (1080x1080, corpo cinza-chumbo #374151 com tira de fita adesiva amarela #fde047)
    def des_controle(d: ImageDraw.ImageDraw) -> None:
        d.rectangle((360, 180, 720, 900), fill=(55, 65, 81), outline=TINTA, width=12)
        _disco(d, (450, 270), 26, VERMELHO)
        _anel(d, (450, 270), 26, TINTA, 8)
        for by in (380, 470, 560):
            for bx in (440, 540, 640):
                d.rectangle((bx - 28, by - 22, bx + 28, by + 22), fill=(156, 163, 175), outline=TINTA, width=6)
        # Detalhe obrigatório da ficha: tira de fita adesiva atravessada na parte inferior
        _poligono(d, [(335, 720), (745, 680), (755, 760), (345, 800)], (253, 224, 71), 10)

    svg_controle = (
        '<rect x="360" y="180" width="360" height="720" fill="#374151" stroke="#1a1a1a" stroke-width="12"/>\n'
        '  <circle cx="450" cy="270" r="26" fill="#e23b2f" stroke="#1a1a1a" stroke-width="8"/>\n'
        '  <polygon points="335,720 745,680 755,760 345,800" fill="#fde047" stroke="#1a1a1a" stroke-width="10"/>'
    )
    _gravar(DEST_OBJ, "OBJ-controle-remoto", 1080, 1080, des_controle, svg_controle)


def main() -> None:
    gerar_personagens()
    gerar_ambientes()
    gerar_objetos()


if __name__ == "__main__":
    main()
