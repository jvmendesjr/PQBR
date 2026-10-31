// Personagem presente no layout do bloco: um recorte da ficha do catálogo num "quadradinho" num canto da zona segura.
// `pose` é o nome do recorte da ficha (giro-*, exp-*). Entra com mola, respira de leve e sai encolhendo.
// Fica por último na ordem de desenho para conferir que não cobre texto nem cartão das outras peças.
(function () {
  const M = PQBRMotion, Z = M.ZONA, MG = M.MARGEM;
  const semente = (s) => Array.from(String(s)).reduce((a, c) => (a * 31 + c.charCodeAt(0)) | 0, 7);
  M.registrar({
    slug: "personagem-moldura", camada: "tela_cheia", ordem: 8,
    desenhar(g, t, dur, p, ctx) {
      const cor = M.corElenco(ctx.elenco), c2d = g.ctx;
      const info = ((ctx.plano || {}).personagens || {})[p.personagem];
      const img = info && (ctx.recursos || {})[info.recurso];
      const poses = info ? info.poses : {};
      const pose = poses[p.pose] || poses[Object.keys(poses)[0]];
      const tam = M.clamp(p.tamanho == null ? 340 : p.tamanho, 220, 460), pad = 22;
      const canto = p.canto || "inf-dir";
      const x = canto.endsWith("esq") ? Z.x + MG : Z.x + Z.w - MG - tam;
      const y = canto.startsWith("sup") ? Z.y + MG : Z.y + Z.h - MG - tam;
      const entra = M.mola(t, { omega: 12, zeta: 0.6 });
      const sai = M.suave(M.faixa(t, dur - 0.25, dur));
      const sem = semente(p.personagem + (p.pose || ""));
      const escala = (0.55 + 0.45 * entra) * (1 - 0.4 * sai);
      const respira = M.ruido(t * 0.8, sem) * 5, inclina = M.ruido(t * 0.6 + 40, sem) * 0.012 - (entra - 1) * 0.1;
      g.conferir = entra > 0.97 && sai === 0;
      g.semSobreposicao("personagem " + p.personagem, x, y, tam, tam);
      const cx = x + tam / 2, cy = y + tam / 2;
      c2d.globalAlpha = 1 - sai;
      c2d.translate(cx, cy + respira); c2d.rotate(inclina); c2d.scale(escala, escala); c2d.translate(-cx, -cy);
      g.caixa(x - 10, y - 10, tam + 20, tam + 20, cor.principal, 54, false);
      g.caixa(x, y, tam, tam, M.fundoDoRecorte(img, pose), 44);
      g.recorte(img, pose, x + pad, y + pad, tam - 2 * pad, tam - 2 * pad, p.espelhar === "sim");
    },
  });
})();
