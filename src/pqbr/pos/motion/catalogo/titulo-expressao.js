// Título da expressão: texto grande alinhado à esquerda, uma linha por vez com mola; traço na cor do elenco.
// O grupo (rótulo + título + traço) senta no terço superior-médio da zona, não colado no topo.
(function () {
  const M = PQBRMotion, Z = M.ZONA, MG = M.MARGEM;
  M.registrar({
    slug: "titulo-expressao", camada: "tela_cheia", ordem: 1,
    desenhar(g, t, dur, p, ctx) {
      const cor = M.corElenco(ctx.elenco);
      const tam = p.tamanho || 112, tamRot = 48;
      g.ctx.font = "800 " + tam + "px " + M.FONTE;
      const linhas = M.quebrarLinhas(g.ctx, p.texto, Z.w - 2 * MG);
      const altura = (p.rotulo ? tamRot * 1.15 + 28 : 0) + linhas.length * tam * 1.1 + 28 + 14;
      let y = Z.y + Math.max(MG, Z.h * 0.5 - altura / 2 - Z.h * 0.08);
      if (p.rotulo) {
        const k = M.mola(t, { omega: 12, zeta: 0.9 });
        g.conferir = k > 0.97;
        y += g.texto(p.rotulo, MG, y + (1 - k) * 30, { tamanho: tamRot, peso: "600", cor: cor.texto }) + 28;
      }
      linhas.forEach((l, i) => {
        const k = M.mola(t, { omega: 13, zeta: 0.8, atraso: 0.1 + i * 0.09 });
        g.conferir = k > 0.97;
        g.texto(l, MG, y + i * tam * 1.1 + (1 - k) * 40, { tamanho: tam, peso: "800", semQuebra: true, cor: M.CORES.tinta });
      });
      const yTr = y + linhas.length * tam * 1.1 + 28;
      const kt = M.mola(t, { omega: 10, zeta: 1, atraso: 0.25 + linhas.length * 0.09 });
      g.conferir = true;
      g.caixa(MG, yTr, Math.max(2, (Z.w - 2 * MG) * 0.42 * kt), 14, cor.principal, 7);
    },
  });
})();
