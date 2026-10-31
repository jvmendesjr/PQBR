// Transição padrão: cortina na cor do elenco varre a tela. fase "cobre" (sobre o vídeo, antes do corte)
// e fase "revela" (dentro do bloco, depois do corte). Decorativa: pode sair da zona segura.
(function () {
  const M = PQBRMotion;
  M.registrar({
    slug: "transicao-cortina", camada: "ambas", ordem: 9,
    desenhar(g, t, dur, p, ctx) {
      const cor = p.cor || M.corElenco(ctx.elenco).principal, acento = M.corElenco(ctx.elenco).acento;
      const k = M.suave(M.faixa(t, 0, dur));
      if (p.fase === "cobre") {
        const w = M.W * k;
        g.decorativo(0, 0, w, M.H, cor);
        g.decorativo(Math.max(0, w - 18), 0, 18, M.H, acento);
      } else {
        const x = M.W * k;
        g.decorativo(x, 0, M.W - x, M.H, cor);
        g.decorativo(x, 0, 18, M.H, acento);
      }
    },
  });
})();
