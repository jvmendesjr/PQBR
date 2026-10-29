// Contador: o número do bloco conta até o valor, com rótulo em cima e selo que carimba no fim.
// Gramática de t153u (REF-MG-04/06): número grande como prova, casas em pt-BR e selo de estado.
// O valor sai do próprio texto travado; se não houver número legível, o texto aparece inteiro, sem quebrar.
(function () {
  const M = PQBRMotion, Z = M.ZONA, MG = M.MARGEM;

  function ler(txt) {
    const m = String(txt).match(/^(\D*?)(\d[\d.,]*)([\s\S]*)$/);
    if (!m) return null;
    let bruto = m[2], dec = 0;
    if (bruto.indexOf(",") >= 0) { dec = bruto.split(",")[1].length; bruto = bruto.replace(/\./g, "").replace(",", "."); }
    else bruto = bruto.replace(/\./g, "");
    const alvo = parseFloat(bruto);
    if (!isFinite(alvo)) return null;
    return { prefixo: m[1], alvo: alvo, sufixo: m[3], dec: dec };
  }

  function escrever(v, dec) {
    const s = dec > 0 ? v.toFixed(dec) : String(Math.round(v));
    const partes = s.split(".");
    return partes[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".") + (partes[1] ? "," + partes[1] : "");
  }

  M.registrar({
    slug: "numero-conta", camada: "tela_cheia", ordem: 1,
    desenhar(g, t, dur, p, ctx) {
      const cor = M.corElenco(ctx.elenco), info = ler(p.texto);
      const maxL = Z.w - 2 * MG;
      let yRot = Z.y + Z.h * 0.26;
      if (p.rotulo) {
        const kr = M.mola(t, { omega: 12, zeta: 0.9 });
        g.conferir = kr > 0.97;
        g.texto(p.rotulo, MG, yRot + (1 - kr) * 26, { tamanho: 52, peso: "600", cor: cor.texto });
        yRot += 92;
      }
      const k = M.suave(M.faixa(t, 0.08 * dur, Math.min(1.3, dur * 0.5)));
      const valor = info ? info.alvo * k : 0;
      const num = info ? escrever(valor, info.dec) : String(p.texto);
      // número grande e sufixo na mesma linha de base, encolhendo juntos se não couber
      let tam = 250, sufixoTam = 108;
      const largura = () => {
        g.ctx.font = "700 " + tam + "px " + M.FONTE;
        let w = g.ctx.measureText((info ? info.prefixo : "") + num).width;
        if (info && info.sufixo) { g.ctx.font = "700 " + sufixoTam + "px " + M.FONTE; w += g.ctx.measureText(info.sufixo).width + 14; }
        return w;
      };
      let w = largura();
      while (w > maxL && tam > 96) { const f = maxL / w; tam = Math.max(96, Math.floor(tam * f)); sufixoTam = Math.max(44, Math.floor(sufixoTam * f)); w = largura(); }
      const yNum = yRot + 40;
      g.conferir = k > 0.98;
      g.texto((info ? info.prefixo : "") + num, MG, yNum, { tamanho: tam, peso: "700", semQuebra: true });
      g.conferir = true;
      if (info && info.sufixo) {
        g.ctx.font = "700 " + tam + "px " + M.FONTE;
        const wn = g.ctx.measureText(info.prefixo + num).width;
        g.texto(info.sufixo, MG + wn + 14, yNum + tam * 0.78 - sufixoTam * 0.78, { tamanho: sufixoTam, peso: "700", semQuebra: true, cor: cor.texto });
      }
      if (p.selo) {
        const ks = M.mola(t - Math.min(1.7, dur * 0.56), { omega: 12, zeta: 0.8 });
        if (ks > 0.001) {
          const ySelo = yNum + tam * 1.05 + 40;
          g.conferir = ks > 0.97;
          g.ctx.font = "700 42px " + M.FONTE;
          const larg = g.ctx.measureText(p.selo).width + 64, alt = 76;
          const escala = 0.6 + 0.4 * ks;
          g.ctx.save();
          g.ctx.translate(MG + larg / 2, ySelo + alt / 2);
          g.ctx.scale(escala, escala);
          g.ctx.translate(-(MG + larg / 2), -(ySelo + alt / 2));
          g.caixa(MG - 4, ySelo - 4, larg + 8, alt + 8, M.CORES.tinta, 42);
          g.caixa(MG, ySelo, larg, alt, cor.texto, 38);
          g.texto(p.selo, MG + 32, ySelo + 19, { tamanho: 42, peso: "700", semQuebra: true, cor: M.CORES.branco, importante: false });
          g.ctx.restore();
        }
      }
    },
  });
})();
