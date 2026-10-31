// Recorte do stickman entra de baixo e "aponta" para uma caixa de texto. A imagem vem do banco de recortes.
(function () {
  const M = PQBRMotion, Z = M.ZONA, MG = M.MARGEM;
  M.registrar({
    slug: "recorte-aponta", camada: "tela_cheia", ordem: 2,
    desenhar(g, t, dur, p, ctx) {
      const cor = M.corElenco(ctx.elenco), img = (ctx.recursos || {})[p.imagem];
      const k = M.mola(t, { omega: 11, zeta: 0.75 });
      const ih = Z.h * 0.42, iw = img ? ih * (img.width / img.height) : ih * 0.56;
      const lado = p.lado || "esq";
      const ix = lado === "esq" ? Z.x + MG : Z.x + Z.w - MG - iw;
      const iy = Z.y + Z.h - MG - ih + (1 - k) * (ih + MG);
      g.conferir = k > 0.97;
      if (img) g.imagem(img, ix, iy, iw, ih);
      const kt = M.mola(t, { omega: 12, zeta: 0.85, atraso: 0.3 });
      if (kt > 0.02) {
        g.conferir = kt > 0.97;
        const cw = Z.w - 2 * MG - iw - 40, cx = lado === "esq" ? ix + iw + 40 : Z.x + MG;
        const cy = Z.y + Z.h - MG - ih + 40;
        g.ctx.font = "700 50px " + M.FONTE;
        const linhas = M.quebrarLinhas(g.ctx, p.texto, cw - 80);
        const ch = linhas.length * 50 * 1.2 + 80;
        g.cartao(cx, cy + (1 - kt) * 30, cw, ch, M.CORES.branco, 32);
        g.texto(p.texto, cx + 40, cy + 40 + (1 - kt) * 30, { tamanho: 50, peso: "700", maxLargura: cw - 80, cor: M.CORES.tinta, entrelinha: 1.2 });
        g.caixa(cx, cy + (1 - kt) * 30, 14, ch, cor.principal, 7, false);
      }
    },
  });
})();
