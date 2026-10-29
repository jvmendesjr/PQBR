"""Render do motion: Chrome headless (Playwright, executável do sistema) captura quadro a quadro.

Cada quadro é `seek(t)` na página: função pura do tempo. A mesma t dá o mesmo PNG (conferido).
Saída: sequência PNG por camada (`tela_cheia/q00000.png`, `sobre/q00000.png`), relatório JSON com
violações de zona segura e hashes de determinismo. Sem Chromium do Playwright: usa /usr/bin/google-chrome."""
from __future__ import annotations
import base64, hashlib, json, os, shutil
from dataclasses import dataclass, field, asdict
from pathlib import Path
from .catalogo import arquivos_js
from ...contratos.motion import PlanoMotion
from ...pipeline import banco_fichas
from . import fontes as banco_fontes

CHROME = os.environ.get("PQBR_CHROME", "/usr/bin/google-chrome")
W, H = 1080, 1920

PAGINA = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0;background:transparent}canvas{display:block}
%(face)s</style></head>
<body><canvas id="c" width="%(w)d" height="%(h)d"></canvas>
%(scripts)s
<script>
const PLANO = %(plano)s;
const RECURSOS = {};
PQBRMotion.FONTE = %(fonte)s;
window.carregarFonte = async function (familia, pesos) {
  const spec = p => p + " 48px '" + familia + "'";
  for (const p of pesos) await document.fonts.load(spec(p), "Aáçãõ0123456789");
  const faltou = pesos.filter(p => !document.fonts.check(spec(p)));
  if (faltou.length) throw new Error("fonte não carregou: " + familia);
  return true;
};
window.carregarRecursos = async function (mapa) {
  for (const [k, url] of Object.entries(mapa)) {
    const img = new Image();
    await new Promise((ok, erro) => { img.onload = ok; img.onerror = () => erro(new Error("imagem " + k)); img.src = url; });
    RECURSOS[k] = img;
  }
  return Object.keys(RECURSOS).length;
};
window.seek = function (t, camada) {
  const c = document.getElementById("c"), ctx = c.getContext("2d");
  const r = PQBRMotion.desenharQuadro(ctx, t, PLANO, camada, RECURSOS);
  return { png: c.toDataURL("image/png"), violacoes: r.violacoes, ativas: r.ativas };
};
window.pronto = true;
</script></body></html>"""


@dataclass
class ResultadoRender:
    pasta: str
    fps: int
    quadros_tela_cheia: int = 0
    quadros_sobre: int = 0
    violacoes: list[dict] = field(default_factory=list)
    deterministico: bool = True
    hashes: dict[str, str] = field(default_factory=dict)
    ativas_por_quadro: dict[str, list[str]] = field(default_factory=dict)

    @property
    def ok(self) -> bool: return self.deterministico and not self.violacoes


def _snap(t: float, fps: int) -> float: return round(round(t * fps) / fps, 6)


def _fichas_usadas(plano: PlanoMotion) -> list:
    return [banco_fichas.obter(pid) for pid in plano.personagens_usados()]


def montar_pagina(plano: PlanoMotion) -> str:
    scripts = "\n".join(f'<script src="file://{p}"></script>' for p in arquivos_js())
    dados = plano.model_dump(mode="json")
    # A folha do personagem sai do banco-fichas/, não de `recursos`; as poses são os recortes da ficha (retângulos normalizados).
    dados["personagens"] = {f.id: {"recurso": f"pers:{f.id}", "poses": f.recortes} for f in _fichas_usadas(plano)}
    familia = banco_fontes.familia_css(plano.fonte)
    # Fonte só por arquivo local do banco (nunca CDN); o genérico atrás é rede de segurança de layout, não escolha estética.
    pilha = f'"{familia}", "Liberation Sans", Arial, sans-serif'
    return PAGINA % {"w": W, "h": H, "scripts": scripts, "plano": json.dumps(dados, ensure_ascii=False),
                     "face": banco_fontes.fonte_css(plano.fonte), "fonte": json.dumps(pilha)}


def _png(data_url: str) -> bytes: return base64.b64decode(data_url.split(",", 1)[1])


def _abrir(pw, plano: PlanoMotion, pasta: Path, chrome: str):
    """Abre a página do plano no Chrome, com a fonte e as imagens (recursos e folhas dos personagens) já carregadas."""
    (pasta / "pagina.html").write_text(montar_pagina(plano), encoding="utf-8")
    nav = pw.chromium.launch(executable_path=chrome, headless=True, args=["--allow-file-access-from-files", "--disable-gpu", "--font-render-hinting=none"])
    pag = nav.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    pag.goto((pasta / "pagina.html").as_uri())
    pag.wait_for_function("window.pronto === true")
    pesos = banco_fontes.obter(plano.fonte)["pesos"]
    pag.evaluate("([f, p]) => window.carregarFonte(f, p)", [banco_fontes.familia_css(plano.fonte), sorted({str(pesos[0]), "700" if pesos[0] <= 700 <= pesos[1] else str(pesos[1])})])
    recursos = {k: Path(v).resolve().as_uri() for k, v in plano.recursos.items()}
    for k, v in plano.recursos.items():
        if not Path(v).is_file(): raise FileNotFoundError(f"recurso {k}: {v}")
    for f in _fichas_usadas(plano):
        arq = banco_fichas.caminho_imagem(f)
        if arq is None or not arq.is_file(): raise FileNotFoundError(f"imagem do personagem {f.id}: {arq}")
        recursos[f"pers:{f.id}"] = arq.resolve().as_uri()
    pag.evaluate("m => window.carregarRecursos(m)", recursos)
    return nav, pag


def quadros(plano: PlanoMotion, tempos: list[float], pasta: Path, camada: str = "tela_cheia", chrome: str = CHROME) -> list[dict]:
    """Prévia: só os quadros pedidos (t em segundos do vídeo final), sem gravar sequência nem compor. Serve à autocrítica
    do papel motion e aos testes; cada item traz `png` (bytes), `violacoes` e `ativas`."""
    from playwright.sync_api import sync_playwright
    pasta = Path(pasta).resolve(); pasta.mkdir(parents=True, exist_ok=True)
    saida = []
    with sync_playwright() as pw:
        nav, pag = _abrir(pw, plano, pasta, chrome)
        for t in tempos:
            r = pag.evaluate("([t, c]) => window.seek(t, c)", [_snap(t, plano.fps), camada])
            saida.append({"t": t, "camada": camada, "png": _png(r["png"]), "violacoes": r["violacoes"], "ativas": r["ativas"]})
        nav.close()
    return saida


def renderizar(plano: PlanoMotion, pasta: Path, chrome: str = CHROME, tela_cheia: bool = True, sobre: bool = True,
               conferir_determinismo: bool = True) -> ResultadoRender:
    from playwright.sync_api import sync_playwright
    pasta = Path(pasta).resolve(); pasta.mkdir(parents=True, exist_ok=True)
    fps = plano.fps
    res = ResultadoRender(pasta=str(pasta), fps=fps)
    with sync_playwright() as pw:
        nav, pag = _abrir(pw, plano, pasta, chrome)

        def quadro(t: float, camada: str) -> tuple[bytes, list[dict], list[str]]:
            r = pag.evaluate("([t, c]) => window.seek(t, c)", [t, camada])
            return _png(r["png"]), r["violacoes"], r["ativas"]

        def sequencia(camada: str, t0: float, t1: float) -> int:
            dir_ = pasta / camada; shutil.rmtree(dir_, ignore_errors=True); dir_.mkdir()
            n = int(round((t1 - t0) * fps))
            vazio = None
            for i in range(n):
                t = _snap(t0 + i / fps, fps)
                png, viol, ativas = quadro(t, camada)
                for v in viol: res.violacoes.append({"t": t, "camada": camada, **v})
                if ativas: res.ativas_por_quadro.setdefault(camada, [])
                destino = dir_ / f"q{i:05d}.png"
                if camada == "sobre" and not ativas:
                    # quadro transparente repetido: um arquivo só, com link, para não gravar centenas de PNG iguais
                    if vazio is None: vazio = dir_ / "_vazio.png"; vazio.write_bytes(png)
                    os.link(vazio, destino)
                else:
                    destino.write_bytes(png)
            return n

        if tela_cheia and plano.bloco is not None:
            res.quadros_tela_cheia = sequencia("tela_cheia", _snap(plano.bloco.inicio, fps), _snap(plano.bloco.fim, fps))
        if sobre:
            res.quadros_sobre = sequencia("sobre", 0.0, _snap(plano.duracao_video_s, fps))
        if conferir_determinismo:
            pontos = []
            if plano.bloco is not None:
                b = plano.bloco; pontos += [(_snap(b.inicio + 0.5, fps), "tela_cheia"), (_snap((b.inicio + b.fim) / 2, fps), "tela_cheia"), (_snap(b.fim - 0.5, fps), "tela_cheia")]
            pontos.append((_snap(plano.duracao_video_s / 2, fps), "sobre"))
            for t, cam in pontos:
                h1 = hashlib.sha256(quadro(t, cam)[0]).hexdigest()
                h2 = hashlib.sha256(quadro(t, cam)[0]).hexdigest()
                res.hashes[f"{cam}@{t}"] = h1
                if h1 != h2: res.deterministico = False
        nav.close()
    (pasta / "relatorio-render.json").write_text(json.dumps(asdict(res), ensure_ascii=False, indent=1), encoding="utf-8")
    return res
