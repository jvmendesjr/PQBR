// Pincelada: transição de pincel chapado atravessando a tela, com a borda na cor de acento do elenco.
// Gramática de t153u (REF-MG-02): a pincelada grossa do OmaPhoto, redesenhada como pincel de cartum.
// Usa dentro do bloco (entre sub-blocos); a transição padrão de entrada e saída do bloco continua sendo a cortina.
(function () {
  const M = PQBRMotion;
  // Borda de pincel: diagonal (o topo fica atrás, a base à frente) com ondulação larga e farpas finas.
  function bordaX(y, x0) {
    const amp = 34 + 22 * Math.sin((y / M.H) * Math.PI);
    return x0 + (y / M.H - 0.5) * 130 + Math.sin(y / 104 + 1.3) * amp + Math.sin(y / 23) * 7;
  }
  function borda(ctx, x0) {
    for (let y = -30; y <= M.H + 30; y += 18) ctx.lineTo(bordaX(y, x0), y);
  }
  M.registrar({
    slug: "transicao-pincelada", camada: "ambas", ordem: 9,
    desenhar(g, t, dur, p, ctx) {
      const cor = p.cor || M.corElenco(ctx.elenco).principal, acento = M.corElenco(ctx.elenco).acento;
      const k = M.suave(M.faixa(t, 0, dur)), x = M.W * k, c = g.ctx;
      c.fillStyle = cor;
      c.beginPath();
      if (p.fase === "cobre") {
        c.moveTo(0, -30);
        borda(c, x);
        c.lineTo(0, M.H + 30);
        c.closePath();
      } else {
        c.moveTo(M.W, -30);
        borda(c, x);
        c.lineTo(M.W, M.H + 30);
        c.closePath();
      }
      c.fill();
      // a borda da pincelada: traço grosso na cor de acento, sem brilho
      c.strokeStyle = acento;
      c.lineWidth = 30;
      c.lineCap = "round";
      c.beginPath();
      for (let y = -30; y <= M.H + 30; y += 18) {
        const xb = bordaX(y, x);
        if (y === -30) c.moveTo(xb, y); else c.lineTo(xb, y);
      }
      c.stroke();
    },
  });
})();
