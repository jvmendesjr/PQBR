// Troca seca de frases curtas no mesmo lugar, com a marca que carimba a cada troca.
// Gramática de t153u (REF-MG-03/05/06): a frase anterior sai de quadro num corte seco, sem fade nem crossfade;
// a nova entra com mola e a marca do elenco cresce embaixo. Os pontinhos mostram em que passo da sequência está.
(function () {
  const M = PQBRMotion, Z = M.ZONA, MG = M.MARGEM;
  M.registrar({
    slug: "frase-troca", camada: "tela_cheia", ordem: 1,
    desenhar(g, t, dur, p, ctx) {
      const cor = M.corElenco(ctx.elenco);
      const frases = p.frases || [];
      if (!frases.length) return;
      const passo = dur / frases.length;
      const i = Math.min(frases.length - 1, Math.max(0, Math.floor(t / passo)));
      const local = t - i * passo;
      const k = M.mola(local, { omega: 14, zeta: 0.75 });
      let tam = 104, linhas = [];
      for (; tam >= 64; tam -= 8) {
        g.ctx.font = "700 " + tam + "px " + M.FONTE;
        linhas = M.quebrarLinhas(g.ctx, frases[i], Z.w - 2 * MG);
        if (linhas.length <= 4) break;
      }
      const altura = linhas.length * tam * 1.08;
      let y0 = Z.y + Z.h * 0.42 - altura / 2;
      if (p.rotulo) {
        const kr = M.mola(t, { omega: 12, zeta: 0.9 });
        g.conferir = kr > 0.97;
        g.texto(p.rotulo, MG, y0 - 92 + (1 - kr) * 26, { tamanho: 48, peso: "600", cor: cor.texto });
      }
      g.conferir = k > 0.97;
      linhas.forEach((l, n) => {
        g.texto(l, MG, y0 + n * tam * 1.08 + (1 - k) * 34, { tamanho: tam, peso: "700", semQuebra: true });
      });
      g.conferir = true;
      const km = M.mola(local - 0.1, { omega: 12, zeta: 1 });
      g.caixa(MG, y0 + altura + 28, Math.max(2, 200 * km), 16, cor.principal, 8);
      // passo da sequência: um ponto por frase, o ativo chapado
      const dy = y0 + altura + 104;
      frases.forEach((_, n) => {
        g.circulo(MG + 14 + n * 34, dy, n === i ? 11 : 7, n === i ? cor.principal : M.CORES.tintaClara);
      });
    },
  });
})();
