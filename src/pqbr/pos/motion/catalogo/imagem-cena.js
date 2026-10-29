// Imagem ou quadro de vídeo dentro do gráfico (corrige ou melhora a cena), com moldura e legenda travada.
(function () {
  const M = PQBRMotion, Z = M.ZONA, MG = M.MARGEM;
  M.registrar({
    slug: "imagem-cena", camada: "tela_cheia", ordem: 0,
    desenhar(g, t, dur, p, ctx) {
      const cor = M.corElenco(ctx.elenco), img = (ctx.recursos || {})[p.imagem];
      const k = M.mola(t, { omega: 12, zeta: 0.85 });
      const w = Z.w - 2 * MG, maxH = Z.h * 0.7;
      let iw = w - 40, ih = img ? iw * (img.height / img.width) : iw * 1.2;
      if (ih > maxH - 40) { ih = maxH - 40; iw = img ? ih * (img.width / img.height) : ih / 1.2; }
      const x = Z.x + Z.w / 2 - (iw + 40) / 2, y = Z.y + MG + (1 - k) * 40;
      g.conferir = k > 0.97;
      g.cartao(x, y, iw + 40, ih + 40, M.CORES.branco, 36);
      if (img) g.imagem(img, x + 20, y + 20, iw, ih);
      g.caixa(x, y + ih + 40 - 12, iw + 40, 12, cor.principal, 6, false);
      if (p.legenda) {
        const kt = M.mola(t, { omega: 12, zeta: 0.9, atraso: 0.25 });
        g.conferir = kt > 0.97;
        if (kt > 0.02) g.texto(p.legenda, Z.x + Z.w / 2, y + ih + 40 + 36 + (1 - kt) * 20, { tamanho: 58, peso: "700", alinh: "centro", maxLargura: w, cor: M.CORES.tinta });
      }
    },
  });
})();
