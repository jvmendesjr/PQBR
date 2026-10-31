// Leque: nó central e dois a quatro itens em leque, com as linhas saindo do centro uma a uma.
// Gramática de t153u (REF-MG-06): o hub e os satélites do diagrama radial, adaptados ao 9:16
// (o leque abre na diagonal, não em círculo, para caber na zona segura).
(function () {
  const M = PQBRMotion, Z = M.ZONA, MG = M.MARGEM;
  const R = 150;                       // raio do nó central
  const CX = MG + R + 6, CY = Z.y + 330;
  const PX = 520, PW = 410, PH = 112, GAP = 88;

  M.registrar({
    slug: "leque", camada: "tela_cheia", ordem: 2,
    desenhar(g, t, dur, p, ctx) {
      const cor = M.corElenco(ctx.elenco);
      const itens = p.itens || [];
      // linhas do centro para cada satélite: o satélite chega primeiro e a linha corre até ele
      itens.forEach((_, i) => {
        const k = M.mola(t - 0.22 - i * 0.16, { omega: 12, zeta: 0.85 });
        if (k <= 0.001) return;
        const y2 = Z.y + 520 + i * (PH + GAP) + PH / 2;
        const x1 = CX + R, y1 = CY;
        const xf = M.lerp(x1, PX, M.clamp(k, 0, 1));
        const yf = M.lerp(y1, y2, M.clamp(k, 0, 1));
        g.linha(x1, y1, xf, yf, cor.texto, 7);
        if (k > 0.9) g.circulo(xf, yf, 9, cor.acento);
      });
      // nó central
      const kn = M.mola(t, { omega: 12, zeta: 0.8 });
      g.conferir = kn > 0.97;
      g.ctx.save();
      g.ctx.translate(CX, CY);
      g.ctx.scale(0.7 + 0.3 * kn, 0.7 + 0.3 * kn);
      g.ctx.translate(-CX, -CY);
      g.circulo(CX, CY, R + 6, M.CORES.tinta);
      g.circulo(CX, CY, R, cor.principal);
      g.ctx.font = "700 52px " + M.FONTE;
      const linhas = M.quebrarLinhas(g.ctx, p.centro, R * 1.55).slice(0, 3);
      const yT = CY - (linhas.length * 52 * 1.12) / 2;
      linhas.forEach((l, i) => {
        g.texto(l, CX, yT + i * 52 * 1.12, { tamanho: 52, peso: "700", semQuebra: true, alinh: "centro", cor: M.CORES.tinta });
      });
      g.ctx.restore();
      // satélites
      itens.forEach((item, i) => {
        const k = M.mola(t - 0.14 - i * 0.16, { omega: 13, zeta: 0.72 });
        if (k <= 0.001) return;
        const x = PX, y = Z.y + 520 + i * (PH + GAP);
        g.conferir = k > 0.97;
        g.ctx.save();
        g.ctx.translate(x + PW / 2, y + PH / 2);
        g.ctx.scale(0.72 + 0.28 * k, 0.72 + 0.28 * k);
        g.ctx.translate(-(x + PW / 2), -(y + PH / 2));
        g.caixa(x - 5, y - 5, PW + 10, PH + 10, M.CORES.tinta, 60);
        g.caixa(x, y, PW, PH, M.CORES.branco, 56);
        let tam = 42;
        g.ctx.font = "700 " + tam + "px " + M.FONTE;
        let ls = M.quebrarLinhas(g.ctx, item, PW - 56);
        while (ls.length * tam * 1.15 > PH - 26 && tam > 28) {
          tam -= 2;
          g.ctx.font = "700 " + tam + "px " + M.FONTE;
          ls = M.quebrarLinhas(g.ctx, item, PW - 56);
        }
        const alt = ls.length * tam * 1.15;
        ls.forEach((l, n) => {
          g.texto(l, x + 28, y + (PH - alt) / 2 + n * tam * 1.15, { tamanho: tam, peso: "700", semQuebra: true });
        });
        g.ctx.restore();
      });
    },
  });
})();
