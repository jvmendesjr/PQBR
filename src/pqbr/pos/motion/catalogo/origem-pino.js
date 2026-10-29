// Origem: cartão com pino que cai e quica (mola), nome do lugar e um detalhe. Sem mapa geográfico.
(function () {
  const M = PQBRMotion, Z = M.ZONA, MG = M.MARGEM;
  M.registrar({
    slug: "origem-pino", camada: "tela_cheia", ordem: 1,
    desenhar(g, t, dur, p, ctx) {
      const cor = M.corElenco(ctx.elenco);
      const cx = Z.x + Z.w / 2, w = Z.w - 2 * MG, h = Math.min(Z.h * 0.5, 820), y = Z.y + (Z.h - h) / 2 - 60;
      const kc = M.mola(t, { omega: 12, zeta: 0.85 });
      g.conferir = kc > 0.97;
      g.cartao(cx - w / 2, y + (1 - kc) * 60, w, h, M.CORES.branco, 40);
      const kp = M.mola(t, { omega: 11, zeta: 0.45, atraso: 0.2 });
      const py = y + h * 0.42 - (1 - kp) * 500;
      g.conferir = kp > 0.97;
      g.circulo(cx, py - 70, 54, cor.acento);
      g.ctx.fillStyle = cor.acento; g.ctx.beginPath();
      g.ctx.moveTo(cx - 44, py - 40); g.ctx.lineTo(cx + 44, py - 40); g.ctx.lineTo(cx, py + 40); g.ctx.closePath(); g.ctx.fill();
      g.circulo(cx, py - 70, 20, M.CORES.branco);
      const sombra = M.clamp(kp, 0, 1);
      g.caixa(cx - 60 * sombra, py + 48, 120 * sombra, 16, "#e5e0d6", 8, false);
      const kt = M.mola(t, { omega: 12, zeta: 0.9, atraso: 0.5 });
      if (kt > 0.02) {
        g.conferir = kt > 0.97;
        const alt = g.texto(p.lugar, cx, py + 110 + (1 - kt) * 30, { tamanho: 76, peso: "700", alinh: "centro", maxLargura: w - 2 * MG });
        if (p.detalhe) g.texto(p.detalhe, cx, py + 130 + alt, { tamanho: 44, peso: "500", alinh: "centro", maxLargura: w - 2 * MG, cor: M.CORES.tintaClara });
      }
    },
  });
})();
