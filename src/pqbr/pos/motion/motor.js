// Motor de motion graphics da PQBR (REGRAS §26, t145u).
// O quadro é função pura do tempo: seek(t) desenha sempre o mesmo pixel para o mesmo t.
// Sem timer, sem requestAnimationFrame, sem transição CSS, sem Math.random.
// Roda no Chrome headless (render.py) e no Node (testes), por isso não toca o DOM aqui.
(function (raiz) {
  "use strict";
  const W = 1080, H = 1920;
  // Zonas seguras 9:16: topo 14%, base 20%, direita 12%.
  const ZONA = { x: 0, y: Math.round(H * 0.14), w: Math.round(W * 0.88), h: Math.round(H * (1 - 0.14 - 0.20)) };
  const MARGEM = 72;
  // Paleta do padrão flat colorido (t148u/t150u): o mesmo conjunto de PALETA em catalogo.py, que um teste confere.
  // `texto` é o tom escuro do principal, só para letra sobre fundo claro (o rosa chapado dá 2,3:1 no creme).
  // `apoio` só entra como `cor` de peça (cortina, barra); nenhuma peça o desenha por conta própria.
  const CORES = {
    fundo: "#f6f1e7", fichaFundo: "#f7f7f2", tinta: "#1f2328", tintaClara: "#6b7280", branco: "#ffffff", marca: "#0f766e", apoio: "#f6c956",
    masculino: { principal: "#4b83ba", acento: "#e03837", texto: "#2c5f93" },
    feminino: { principal: "#ee7e91", acento: "#826caf", texto: "#b83a5d" },
  };
  const FONTE = '"Liberation Sans", "DejaVu Sans", Arial, sans-serif';

  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, k) => a + (b - a) * k;
  const suave = (k) => { k = clamp(k, 0, 1); return k * k * (3 - 2 * k); };
  // progresso 0..1 de t dentro de [a, b]
  const faixa = (t, a, b) => (b <= a ? (t >= b ? 1 : 0) : clamp((t - a) / (b - a), 0, 1));

  // Mola de forma fechada (resposta ao degrau), sem estado entre quadros.
  // omega = rigidez (rad/s), zeta = amortecimento (<1 passa do alvo e volta; 1 = crítico).
  function mola(t, opt) {
    const o = opt || {};
    const omega = o.omega == null ? 14 : o.omega, zeta = o.zeta == null ? 0.78 : o.zeta;
    const tt = t - (o.atraso || 0);
    if (tt <= 0) return 0;
    if (zeta >= 1) return 1 - (1 + omega * tt) * Math.exp(-omega * tt);
    const wd = omega * Math.sqrt(1 - zeta * zeta);
    const e = Math.exp(-zeta * omega * tt);
    return 1 - e * (Math.cos(wd * tt) + (zeta * omega / wd) * Math.sin(wd * tt));
  }

  // PRNG determinístico (mulberry32) para ruído com semente.
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function hash1(i, semente) { return mulberry32((i * 374761393 + semente * 668265263) | 0)(); }
  // Ruído de valor 1D em [-1, 1], contínuo em x, igual para a mesma semente.
  function ruido(x, semente) {
    const s = semente | 0, i = Math.floor(x), f = x - i;
    const a = hash1(i, s) * 2 - 1, b = hash1(i + 1, s) * 2 - 1;
    return lerp(a, b, suave(f));
  }

  function quebrarLinhas(ctx, texto, maxLargura) {
    const palavras = String(texto).split(/\s+/).filter(Boolean), linhas = [];
    let atual = "";
    for (const p of palavras) {
      const tent = atual ? atual + " " + p : p;
      if (ctx.measureText(tent).width <= maxLargura || !atual) atual = tent;
      else { linhas.push(atual); atual = p; }
    }
    if (atual) linhas.push(atual);
    return linhas;
  }

  // Média da cor da folha nos quatro cantos do recorte. A moldura do personagem usa essa cor de fundo, senão cada
  // folha (papel de tom próprio) apareceria como um retângulo de outro tom em volta do desenho. Sem DOM (Node), usa o padrão.
  const _amostras = new WeakMap();
  function fundoDoRecorte(img, r) {
    if (typeof document === "undefined" || !img || !r || !img.width) return CORES.fichaFundo;
    const chave = r.join(","), cache = _amostras.get(img) || {};
    _amostras.set(img, cache);
    if (!cache[chave]) {
      const c = document.createElement("canvas"); c.width = c.height = 1;
      const k = c.getContext("2d", { willReadFrequently: true }), soma = [0, 0, 0];
      for (const x of [r[0] * img.width + 3, r[2] * img.width - 4]) for (const y of [r[1] * img.height + 3, r[3] * img.height - 4]) {
        k.clearRect(0, 0, 1, 1); k.drawImage(img, Math.round(x), Math.round(y), 1, 1, 0, 0, 1, 1);
        const d = k.getImageData(0, 0, 1, 1).data; soma[0] += d[0]; soma[1] += d[1]; soma[2] += d[2];
      }
      cache[chave] = "rgb(" + soma.map((v) => Math.round(v / 4)).join(",") + ")";
    }
    return cache[chave];
  }

  // Desenho com registro: tudo o que é "importante" tem o retângulo conferido contra a ZONA.
  function criarGrafico(ctx) {
    // g.conferir = false enquanto o elemento ainda está entrando (fora da tela de propósito); a zona só vale assentado.
    const g = { violacoes: [], ocupados: [], ctx, conferir: true };
    function registrar(nome, x, y, w, h) {
      if (g.conferir === false) return;
      const dentro = x >= ZONA.x - 0.5 && y >= ZONA.y - 0.5 && x + w <= ZONA.x + ZONA.w + 0.5 && y + h <= ZONA.y + ZONA.h + 0.5;
      if (!dentro) g.violacoes.push({ nome, x: Math.round(x), y: Math.round(y), w: Math.round(w), h: Math.round(h) });
      g.ocupados.push({ nome, x, y, w, h });
    }
    // Peça que se encaixa no layout (personagem na moldura) confere que não cobre o que as peças anteriores já
    // desenharam; por isso fica por último na ordem. Só vale assentado, como a zona segura.
    g.semSobreposicao = function (nome, x, y, w, h) {
      if (g.conferir === false) return;
      const o = g.ocupados.find((r) => x < r.x + r.w && x + w > r.x && y < r.y + r.h && y + h > r.y);
      if (o) g.violacoes.push({ nome: nome + " cobre " + o.nome, x: Math.round(x), y: Math.round(y), w: Math.round(w), h: Math.round(h) });
    };
    g.fundo = function (cor) {
      if (!cor) { ctx.clearRect(0, 0, W, H); return; }
      ctx.fillStyle = cor; ctx.fillRect(0, 0, W, H);
    };
    // Retângulo decorativo que pode sair da zona (cortina, faixa de fundo).
    g.decorativo = function (x, y, w, h, cor) { ctx.fillStyle = cor; ctx.fillRect(x, y, w, h); };
    g.caixa = function (x, y, w, h, cor, raio, importante) {
      const r = Math.min(raio == null ? 28 : raio, w / 2, h / 2);
      ctx.fillStyle = cor; ctx.beginPath();
      ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
      ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); ctx.fill();
      if (importante !== false) registrar("caixa", x, y, w, h);
    };
    // Cartão no traço do stickman: contorno preto e sombra chapada deslocada, sem desfoque (cartum 2D flat).
    g.cartao = function (x, y, w, h, cor, raio) {
      const r = Math.min(raio == null ? 32 : raio, w / 2, h / 2), esp = 5, desl = 10;
      const caminho = (dx, dy) => {
        ctx.beginPath(); ctx.moveTo(x + dx + r, y + dy); ctx.arcTo(x + dx + w, y + dy, x + dx + w, y + dy + h, r);
        ctx.arcTo(x + dx + w, y + dy + h, x + dx, y + dy + h, r); ctx.arcTo(x + dx, y + dy + h, x + dx, y + dy, r);
        ctx.arcTo(x + dx, y + dy, x + dx + w, y + dy, r); ctx.closePath();
      };
      ctx.fillStyle = CORES.tinta; caminho(0, desl); ctx.fill();
      ctx.fillStyle = cor; caminho(0, 0); ctx.fill();
      ctx.strokeStyle = CORES.tinta; ctx.lineWidth = esp; ctx.lineJoin = "round"; ctx.stroke();
      registrar("cartao", x, y, w, h + desl);
    };
    g.linha = function (x1, y1, x2, y2, cor, esp) {
      ctx.strokeStyle = cor; ctx.lineWidth = esp || 6; ctx.lineCap = "round";
      ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
      registrar("linha", Math.min(x1, x2), Math.min(y1, y2), Math.abs(x2 - x1), Math.abs(y2 - y1));
    };
    g.circulo = function (x, y, r, cor) {
      ctx.fillStyle = cor; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
      registrar("circulo", x - r, y - r, 2 * r, 2 * r);
    };
    // Texto com quebra de linha; devolve a altura ocupada. alinh: "esq" | "centro" | "dir".
    g.texto = function (txt, x, y, opt) {
      const o = opt || {}, tam = o.tamanho || 64, peso = o.peso || "700", alinh = o.alinh || "esq";
      const maxL = o.maxLargura || (ZONA.x + ZONA.w - MARGEM - x), entre = o.entrelinha || 1.15;
      ctx.font = peso + " " + tam + "px " + raiz.PQBRMotion.FONTE; ctx.fillStyle = o.cor || CORES.tinta;
      ctx.textBaseline = "top"; ctx.textAlign = alinh === "centro" ? "center" : alinh === "dir" ? "right" : "left";
      const linhas = o.semQuebra ? [String(txt)] : quebrarLinhas(ctx, txt, maxL);
      let maior = 0;
      linhas.forEach((l, i) => {
        ctx.fillText(l, x, y + i * tam * entre);
        maior = Math.max(maior, ctx.measureText(l).width);
      });
      const alt = linhas.length * tam * entre;
      const x0 = alinh === "centro" ? x - maior / 2 : alinh === "dir" ? x - maior : x;
      if (o.importante !== false) registrar("texto:" + String(txt).slice(0, 24), x0, y, maior, alt);
      return alt;
    };
    g.imagem = function (img, x, y, w, h, alpha) {
      if (!img) return;
      const a = ctx.globalAlpha; ctx.globalAlpha = alpha == null ? 1 : alpha;
      ctx.drawImage(img, x, y, w, h); ctx.globalAlpha = a;
      registrar("imagem", x, y, w, h);
    };
    // Recorte [x0, y0, x1, y1] (normalizado) de uma folha, ajustado dentro de (x, y, w, h) sem deformar e apoiado
    // na borda de baixo. espelhar vira o desenho no eixo vertical, para o personagem olhar para o conteúdo.
    g.recorte = function (img, r, x, y, w, h, espelhar) {
      if (!img || !r) return;
      const sx = r[0] * img.width, sy = r[1] * img.height, sw = (r[2] - r[0]) * img.width, sh = (r[3] - r[1]) * img.height;
      const esc = Math.min(w / sw, h / sh), dw = sw * esc, dh = sh * esc, dx = x + (w - dw) / 2, dy = y + h - dh;
      if (espelhar) { ctx.save(); ctx.translate(dx + dw, 0); ctx.scale(-1, 1); ctx.drawImage(img, sx, sy, sw, sh, 0, dy, dw, dh); ctx.restore(); }
      else ctx.drawImage(img, sx, sy, sw, sh, dx, dy, dw, dh);
      registrar("recorte", dx, dy, dw, dh);
    };
    return g;
  }

  const CATALOGO = {};
  function registrar(modelo) {
    if (!modelo || !modelo.slug || typeof modelo.desenhar !== "function") throw new Error("modelo inválido");
    CATALOGO[modelo.slug] = modelo;
  }

  // Desenha o quadro no tempo absoluto t. camada: "tela_cheia" | "sobre".
  // plano.pecas: [{modelo, inicio, fim, parametros}] em segundos absolutos do vídeo final.
  function desenharQuadro(ctx, t, plano, camada, recursos) {
    const g = criarGrafico(ctx);
    const opaco = camada === "tela_cheia";
    g.fundo(opaco ? (plano.fundo || CORES.fundo) : null);
    const ativas = (plano.pecas || [])
      .filter((p) => t >= p.inicio && t < p.fim)
      .map((p) => ({ p, m: CATALOGO[p.modelo] }))
      .filter((x) => x.m && (x.m.camada === camada || x.m.camada === "ambas"))
      .sort((a, b) => (a.m.ordem || 1) - (b.m.ordem || 1));
    for (const { p, m } of ativas) {
      ctx.save(); g.conferir = true;
      m.desenhar(g, t - p.inicio, p.fim - p.inicio, p.parametros || {}, { recursos: recursos || {}, elenco: plano.elenco || "masculino", t, plano });
      ctx.restore(); g.conferir = true;
    }
    return { violacoes: g.violacoes, ativas: ativas.map((x) => x.p.modelo) };
  }

  function corElenco(elenco) { return CORES[elenco] || CORES.masculino; }

  raiz.PQBRMotion = { W, H, ZONA, MARGEM, CORES, FONTE, clamp, lerp, suave, faixa, mola, ruido, mulberry32,
    quebrarLinhas, criarGrafico, registrar, CATALOGO, desenharQuadro, corElenco, fundoDoRecorte };
})(typeof window !== "undefined" ? window : globalThis);
