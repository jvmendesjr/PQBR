// Versus: "a versão mais aceita" × "tem quem diga". Dois cartões empilhados (9:16); B entra em p.entrada_b s.
(function () {
  const M = PQBRMotion, Z = M.ZONA, MG = M.MARGEM;
  function cartao(g, ctx, titulo, texto, img, x, y, w, h, k, corTitulo, deLado) {
    const dx = (1 - k) * (deLado === "esq" ? -w : w);
    g.conferir = k > 0.97;
    g.caixa(x + dx, y, w, h, M.CORES.branco, 40);
    const pad = 44;
    let ty = y + pad;
    let larg = w - 2 * pad, tx = x + dx + pad;
    if (img) {
      const ih = h - 2 * pad, iw = Math.min(w * 0.36, ih * (img.width / img.height));
      g.imagem(img, x + dx + w - pad - iw, y + pad, iw, ih);
      larg -= iw + pad;
    }
    ty += g.texto(titulo, tx, ty, { tamanho: 40, peso: "600", cor: corTitulo, maxLargura: larg }) + 22;
    g.texto(texto, tx, ty, { tamanho: 62, peso: "700", maxLargura: larg, cor: M.CORES.tinta, entrelinha: 1.2 });
  }
  M.registrar({
    slug: "versus", camada: "tela_cheia", ordem: 1,
    desenhar(g, t, dur, p, ctx) {
      const cor = M.corElenco(ctx.elenco), r = ctx.recursos || {};
      const w = Z.w - 2 * MG, gap = 150, h = (Z.h - 2 * MG - gap) / 2;
      const x = Z.x + MG, yA = Z.y + MG, yB = yA + h + gap;
      const kA = M.mola(t, { omega: 12, zeta: 0.8 });
      const tB = p.entrada_b == null ? dur * 0.45 : p.entrada_b;
      const kB = M.mola(t, { omega: 12, zeta: 0.8, atraso: tB });
      cartao(g, ctx, p.titulo_a, p.texto_a, r[p.imagem_a], x, yA, w, h, kA, cor.principal, "esq");
      const kx = M.mola(t, { omega: 10, zeta: 0.6, atraso: tB - 0.15 });
      g.conferir = kx > 0.97;
      if (kx > 0.01) g.texto("×", Z.x + Z.w / 2, yA + h + gap / 2 - 60, { tamanho: Math.max(8, 120 * Math.min(1, kx)), peso: "800", alinh: "centro", cor: cor.acento, semQuebra: true });
      if (kB > 0.001) cartao(g, ctx, p.titulo_b, p.texto_b, r[p.imagem_b], x, yB, w, h, kB, cor.acento, "dir");
    },
  });
})();
