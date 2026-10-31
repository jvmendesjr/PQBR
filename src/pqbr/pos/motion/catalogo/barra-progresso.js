// Barra de progresso discreta: fina, na borda de baixo da zona segura, na cor do elenco. Camada "sobre".
(function () {
  const M = PQBRMotion, Z = M.ZONA, MG = M.MARGEM;
  M.registrar({
    slug: "barra-progresso", camada: "sobre", ordem: 0,
    desenhar(g, t, dur, p, ctx) {
      const cor = p.cor || M.corElenco(ctx.elenco).principal, esp = p.espessura || 8;
      const total = (ctx.plano && ctx.plano.duracao_video_s) || dur;
      const k = M.faixa(ctx.t, 0, total);
      const x = Z.x + MG, w = Z.w - 2 * MG, y = Z.y + Z.h - esp - 6;
      g.caixa(x, y, w, esp, "rgba(31,35,40,0.18)", esp / 2);
      g.caixa(x, y, Math.max(esp, w * k), esp, cor, esp / 2);
    },
  });
})();
