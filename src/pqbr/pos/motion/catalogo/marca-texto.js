// Marca-texto: a frase do bloco é lida palavra por palavra e um marca-texto chapado assenta na palavra-chave.
// Gramática de t153u (REF-MG-03/04/07): leitura por cursor e destaque por trás da palavra, sem brilho e sem fade.
// `destaque` é um trecho de `texto` (o contrato confere), então nada de texto novo entra na tela.
(function () {
  const M = PQBRMotion, Z = M.ZONA, MG = M.MARGEM;

  // Layout por palavra: cada item guarda a posição dentro da linha para o cursor e o marca-texto acharem a caixa.
  function medir(g, texto, tam, maxL) {
    const ctx = g.ctx;
    ctx.font = "700 " + tam + "px " + M.FONTE;
    const espaco = ctx.measureText(" ").width;
    const palavras = String(texto).split(/\s+/).filter(Boolean);
    const linhas = [];
    let atual = { itens: [], largura: 0 };
    for (const w of palavras) {
      const lw = ctx.measureText(w).width;
      if (atual.itens.length && atual.largura + espaco + lw > maxL) { linhas.push(atual); atual = { itens: [], largura: 0 }; }
      const x = atual.largura + (atual.itens.length ? espaco : 0);
      atual.itens.push({ w: w, x: x, largura: lw });
      atual.largura = x + lw;
    }
    if (atual.itens.length) linhas.push(atual);
    return { linhas: linhas, altura: linhas.length * tam * 1.12, tam: tam, espaco: espaco };
  }

  // Caixa do trecho: palavras consecutivas iguais ao destaque, dentro da mesma linha.
  function caixa(L, destaque) {
    const alvo = String(destaque || "").trim().split(/\s+/).filter(Boolean);
    if (!alvo.length) return null;
    for (let li = 0; li < L.linhas.length; li++) {
      const itens = L.linhas[li].itens;
      for (let i = 0; i + alvo.length <= itens.length; i++) {
        let ok = true;
        for (let n = 0; n < alvo.length; n++) if (itens[i + n].w !== alvo[n]) { ok = false; break; }
        if (ok) {
          const a = itens[i], b = itens[i + alvo.length - 1];
          return { linha: li, indice: i, n: alvo.length, x: a.x, largura: b.x + b.largura - a.x };
        }
      }
    }
    return null;
  }

  M.registrar({
    slug: "marca-texto", camada: "tela_cheia", ordem: 1,
    desenhar(g, t, dur, p, ctx) {
      const cor = M.corElenco(ctx.elenco);
      let L = medir(g, p.texto, 92, Z.w - 2 * MG);
      while (L.linhas.length > 4 && L.tam > 64) L = medir(g, p.texto, L.tam - 6, Z.w - 2 * MG);
      const tam = L.tam;
      let y0 = Z.y + Z.h * 0.42 - L.altura / 2;
      if (p.rotulo) {
        const kr = M.mola(t, { omega: 12, zeta: 0.9 });
        g.conferir = kr > 0.97;
        g.texto(p.rotulo, MG, y0 - 88 + (1 - kr) * 26, { tamanho: 48, peso: "600", cor: cor.texto });
        y0 += 24;
      }
      const alvo = caixa(L, p.destaque);
      const total = L.linhas.reduce((n, l) => n + l.itens.length, 0);
      let alvoIdx = 0;
      if (alvo) {
        for (let i = 0; i < alvo.linha; i++) alvoIdx += L.linhas[i].itens.length;
        alvoIdx += alvo.indice;
      }
      // 1) o marca-texto nasce atrás da palavra-chave e cresce com mola
      const kh = M.mola(t - Math.min(1.5, dur * 0.45), { omega: 12, zeta: 0.9 });
      if (alvo && kh > 0.001) {
        const larg = Math.max(8, (alvo.largura + 14) * M.suave(Math.min(1, kh)));
        g.caixa(MG + alvo.x - 7, y0 + alvo.linha * tam * 1.12 - 5, larg, tam * 1.02, cor.texto, 10);
      }
      // 2) as palavras (as que o marca-texto já cobriu vão em branco para manter o contraste)
      g.conferir = true;
      const coberto = alvo && kh > 0.85;
      L.linhas.forEach((linha, li) => {
        linha.itens.forEach((it, i) => {
          const dentro = coberto && li === alvo.linha && i >= alvo.indice && i < alvo.indice + alvo.n;
          g.texto(it.w, MG + it.x, y0 + li * tam * 1.12, { tamanho: tam, peso: "700", semQuebra: true, cor: dentro ? M.CORES.branco : undefined });
        });
      });
      // 3) o cursor de leitura corre até a palavra-chave e sai quando o destaque assenta
      const kc = M.faixa(t, 0.08 * dur, Math.min(1.25, dur * 0.5));
      if (kc < 1 && total > 0) {
        const idx = Math.min(total - 1, Math.floor(kc * (alvo ? alvoIdx + 1 : total)));
        let restante = idx, li = 0;
        while (li < L.linhas.length - 1 && restante >= L.linhas[li].itens.length) { restante -= L.linhas[li].itens.length; li += 1; }
        const it = L.linhas[li].itens[Math.min(restante, L.linhas[li].itens.length - 1)];
        g.caixa(MG + it.x - 8, y0 + li * tam * 1.12 - 4, 7, tam * 1.04, cor.texto, 3);
      }
    },
  });
})();
