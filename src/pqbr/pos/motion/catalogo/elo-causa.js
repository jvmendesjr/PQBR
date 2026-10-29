// Elo de causa: dois cartões ligados por um traço que cresce, com o conector carimbado no meio.
// Gramática de t153u (REF-MG-06): o grafo de dois nós, adaptado ao 9:16 (causa em cima, efeito embaixo).
(function () {
  const M = PQBRMotion, Z = M.ZONA, MG = M.MARGEM;
  const AW = Z.w - 2 * MG, AH = 330;
  const AY = Z.y + 150, BY = Z.y + 760, CX = MG + AW / 2;

  function cartao(g, x, y, w, h, corFaixa, texto, k) {
    g.ctx.save();
    g.ctx.translate(x + w / 2, y + h / 2);
    g.ctx.scale(0.86 + 0.14 * k, 0.86 + 0.14 * k);
    g.ctx.translate(-(x + w / 2), -(y + h / 2));
    g.cartao(x, y, w, h, M.CORES.branco, 40);
    g.caixa(x + 22, y + 26, 14, h - 52, corFaixa, 7);
    let tam = 52;
    g.ctx.font = "700 " + tam + "px " + M.FONTE;
    let ls = M.quebrarLinhas(g.ctx, texto, w - 96);
    while (ls.length * tam * 1.16 > h - 56 && tam > 34) {
      tam -= 2;
      g.ctx.font = "700 " + tam + "px " + M.FONTE;
      ls = M.quebrarLinhas(g.ctx, texto, w - 96);
    }
    const alt = ls.length * tam * 1.16;
    ls.forEach((l, i) => {
      g.texto(l, x + 58, y + (h - alt) / 2 + i * tam * 1.16, { tamanho: tam, peso: "700", semQuebra: true });
    });
    g.ctx.restore();
  }

  M.registrar({
    slug: "elo-causa", camada: "tela_cheia", ordem: 2,
    desenhar(g, t, dur, p, ctx) {
      const cor = M.corElenco(ctx.elenco);
      const ka = M.mola(t, { omega: 12, zeta: 0.8 });
      g.conferir = ka > 0.97;
      cartao(g, MG, AY, AW, AH, cor.principal, p.causa, ka);
      // traço que cresce da causa para o efeito
      const kl = M.mola(t - 0.25, { omega: 12, zeta: 0.9 });
      const y1 = AY + AH + 10, y2 = BY - 10, yf = M.lerp(y1, y2, M.clamp(kl, 0, 1));
      if (kl > 0.001) {
        g.linha(CX, y1, CX, yf, M.CORES.tinta, 8);
        if (kl > 0.85) {
          g.linha(CX, yf, CX - 20, yf - 30, M.CORES.tinta, 8);
          g.linha(CX, yf, CX + 20, yf - 30, M.CORES.tinta, 8);
        }
      }
      if (p.conector) {
        const kc = M.mola(t - 0.55, { omega: 12, zeta: 0.8 });
        if (kc > 0.001) {
          g.conferir = kc > 0.97;
          g.ctx.font = "700 40px " + M.FONTE;
          const larg = g.ctx.measureText(p.conector).width + 56, alt = 68;
          const x = CX - larg / 2, y = (y1 + y2) / 2 - alt / 2;
          g.ctx.save();
          g.ctx.translate(CX, y + alt / 2);
          g.ctx.scale(0.7 + 0.3 * kc, 0.7 + 0.3 * kc);
          g.ctx.translate(-CX, -(y + alt / 2));
          g.caixa(x - 4, y - 4, larg + 8, alt + 8, M.CORES.tinta, 38);
          g.caixa(x, y, larg, alt, M.CORES.branco, 34);
          g.texto(p.conector, x + 28, y + 15, { tamanho: 40, peso: "700", semQuebra: true, cor: cor.texto, importante: false });
          g.ctx.restore();
        }
      }
      const kb = M.mola(t - 0.7, { omega: 12, zeta: 0.8 });
      if (kb > 0.001) {
        g.conferir = kb > 0.97;
        cartao(g, MG, BY, AW, AH, cor.acento, p.efeito, kb);
      }
      g.conferir = true;
    },
  });
})();
