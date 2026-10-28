// Linha do tempo / passagem de tempo: marcos aparecem de cima para baixo ao longo da duração.
(function () {
  const M = PQBRMotion, Z = M.ZONA, MG = M.MARGEM;
  M.registrar({
    slug: "linha-tempo", camada: "tela_cheia", ordem: 1,
    desenhar(g, t, dur, p, ctx) {
      const cor = M.corElenco(ctx.elenco), marcos = p.marcos || [];
      let y0 = Z.y + MG * 1.5;
      if (p.rotulo) y0 += g.texto(p.rotulo, MG, y0, { tamanho: 40, peso: "500", cor: M.CORES.tintaClara }) + 40;
      const x = MG + 30, y1 = Z.y + Z.h - MG * 1.5, n = Math.max(1, marcos.length);
      const passo = (y1 - y0) / n;
      const kTotal = M.faixa(t, 0.2, dur * 0.8);
      g.linha(x, y0, x, y0 + (y1 - y0 - passo * 0.5) * M.suave(kTotal) + 1, M.CORES.tintaClara, 6);
      marcos.forEach((m, i) => {
        const tIn = 0.3 + (dur * 0.7) * (i / n);
        const k = M.mola(t, { omega: 14, zeta: 0.7, atraso: tIn });
        if (k <= 0) return;
        const y = y0 + passo * i + passo * 0.25;
        g.conferir = k > 0.97;
        g.circulo(x, y, 18 * Math.min(1, k), i === marcos.length - 1 ? cor.acento : cor.principal);
        g.texto(m, x + 60 + (1 - Math.min(1, k)) * 30, y - 30, { tamanho: 54, peso: "700", maxLargura: Z.w - x - 60 - MG, cor: M.CORES.tinta });
      });
    },
  });
})();
