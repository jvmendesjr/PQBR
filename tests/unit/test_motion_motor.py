"""motor.js e catálogo rodando no Node: mola fechada, ruído com semente, determinismo, slugs e zonas seguras."""
import json, os, shutil, subprocess
from pathlib import Path
import pytest
from pqbr.pos.motion.catalogo import arquivos_js, carregar_catalogo, RAIZ

NODE = shutil.which("node") or (str(Path.home() / ".local/bin/node") if (Path.home() / ".local/bin/node").exists() else None)
pytestmark = pytest.mark.skipif(NODE is None, reason="node ausente")

# Canvas 2D falso: mede texto por tamanho da fonte e registra as chamadas; basta para zona segura e determinismo.
STUB = r"""
function ctxFalso(log) {
  const ctx = { font: "700 64px x", fillStyle: "", strokeStyle: "", lineWidth: 1, lineCap: "", textBaseline: "", textAlign: "", globalAlpha: 1 };
  const tam = () => parseFloat((ctx.font.match(/(\d+(?:\.\d+)?)px/) || [0, 64])[1]);
  ctx.measureText = (s) => ({ width: String(s).length * tam() * 0.55 });
  for (const m of ["fillRect","clearRect","beginPath","moveTo","lineTo","arcTo","arc","closePath","fill","stroke","save","restore","drawImage"])
    ctx[m] = (...a) => log.push(m + ":" + a.map(v => typeof v === "object" ? "img" : Math.round(v * 1000) / 1000).join(","));
  ctx.fillText = (s, x, y) => log.push("fillText:" + s + "," + Math.round(x) + "," + Math.round(y));
  return ctx;
}
"""


def rodar(js: str) -> dict:
    cab = "\n".join(f"new Function(require('fs').readFileSync({json.dumps(str(p))}, 'utf8'))();" for p in arquivos_js())
    r = subprocess.run([NODE, "-e", cab + STUB + js], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_slugs_do_js_batem_com_o_indice():
    r = rodar("console.log(JSON.stringify({slugs: Object.keys(PQBRMotion.CATALOGO).sort(), camadas: Object.fromEntries(Object.values(PQBRMotion.CATALOGO).map(m => [m.slug, m.camada]))}))")
    cat = carregar_catalogo()
    assert r["slugs"] == sorted(cat)
    assert r["camadas"] == {s: m.camada for s, m in cat.items()}


def test_mola_fechada_sai_do_zero_assenta_em_um_e_critica_nao_passa():
    r = rodar("""const M = PQBRMotion; const ts = Array.from({length: 61}, (_, i) => i / 20);
      console.log(JSON.stringify({sub: ts.map(t => M.mola(t, {omega: 14, zeta: 0.78})), crit: ts.map(t => M.mola(t, {omega: 14, zeta: 1})), atraso: M.mola(0.2, {atraso: 0.5})}))""")
    assert r["sub"][0] == 0 and r["atraso"] == 0
    assert max(r["sub"]) > 1.0 and abs(r["sub"][-1] - 1) < 1e-3          # passa um pouco do alvo e assenta
    assert all(0 <= v <= 1.0 + 1e-9 for v in r["crit"]) and abs(r["crit"][-1] - 1) < 1e-3
    assert all(b >= a - 1e-12 for a, b in zip(r["crit"], r["crit"][1:]))  # crítica é monótona


def test_ruido_com_semente_e_deterministico_e_limitado():
    r = rodar("""const M = PQBRMotion; const xs = Array.from({length: 200}, (_, i) => i / 10);
      const a = xs.map(x => M.ruido(x, 7)), b = xs.map(x => M.ruido(x, 7)), c = xs.map(x => M.ruido(x, 8));
      console.log(JSON.stringify({igual: JSON.stringify(a) === JSON.stringify(b), diferente: JSON.stringify(a) !== JSON.stringify(c), min: Math.min(...a), max: Math.max(...a)}))""")
    assert r["igual"] and r["diferente"] and -1 <= r["min"] and r["max"] <= 1


PLANO_JS = """
const plano = {elenco: "PERS-F", duracao_video_s: 40, fps: 30, bloco: {inicio: 10, fim: 30}, pecas: [
  {modelo: "transicao-cortina", inicio: 9.6, fim: 10, parametros: {fase: "cobre"}},
  {modelo: "transicao-cortina", inicio: 10, fim: 10.4, parametros: {fase: "revela"}},
  {modelo: "titulo-expressao", inicio: 10, fim: 14, parametros: {texto: "Chá de bico de chaleira", rotulo: "A versão mais aceita"}},
  {modelo: "linha-tempo", inicio: 14, fim: 19, parametros: {marcos: ["Século XIX", "Anos 1950", "Hoje"], rotulo: "Passagem"}},
  {modelo: "origem-pino", inicio: 19, fim: 22, parametros: {lugar: "Minas Gerais", detalhe: "Fazendas de café"}},
  {modelo: "versus", inicio: 22, fim: 26, parametros: {titulo_a: "A versão mais aceita", texto_a: "Reaproveitar o mesmo pó no filtro até sair só líquido claro", titulo_b: "Tem quem diga", texto_b: "Água quente no bico da chaleira pra aproveitar a borra", entrada_b: 0.6}},
  {modelo: "recorte-aponta", inicio: 26, fim: 28, parametros: {imagem: "pm", texto: "Chá de bico de chaleira"}},
  {modelo: "imagem-cena", inicio: 28, fim: 30, parametros: {imagem: "pm", legenda: "Chá de bico de chaleira"}},
  {modelo: "barra-progresso", inicio: 0, fim: 40, parametros: {}},
]};
const recursos = {pm: {width: 1080, height: 1920}};
"""


def test_zonas_seguras_respeitadas_quando_assentado_e_quadro_e_funcao_pura_do_tempo():
    r = rodar(PLANO_JS + """
      const M = PQBRMotion;
      // assentado: 2,5 s depois da entrada de cada peça (as molas já pararam)
      const tempos = [12.5, 17.5, 21.5, 25.5, 27.9, 29.9];
      const viol = tempos.map(t => { const log = []; const r = M.desenharQuadro(ctxFalso(log), t, plano, "tela_cheia", recursos); return {t, v: r.violacoes, ativas: r.ativas}; });
      const sobre = (() => { const log = []; return M.desenharQuadro(ctxFalso(log), 20, plano, "sobre", recursos); })();
      const a = [], b = []; M.desenharQuadro(ctxFalso(a), 23.3, plano, "tela_cheia", recursos); M.desenharQuadro(ctxFalso(b), 23.3, plano, "tela_cheia", recursos);
      console.log(JSON.stringify({viol, sobre, puro: JSON.stringify(a) === JSON.stringify(b), nDesenhos: a.length}))""")
    for q in r["viol"]:
        assert q["ativas"], q["t"]
        assert q["v"] == [], (q["t"], q["v"])
    assert r["sobre"]["ativas"] == ["barra-progresso"] and r["sobre"]["violacoes"] == []
    assert r["puro"] and r["nDesenhos"] > 5


def test_camada_sobre_nao_desenha_pecas_de_tela_cheia_e_vice_versa():
    r = rodar(PLANO_JS + """
      const M = PQBRMotion; const log = [];
      const s = M.desenharQuadro(ctxFalso(log), 12, plano, "sobre", recursos);
      const c = M.desenharQuadro(ctxFalso([]), 9.8, plano, "sobre", recursos);
      const d = M.desenharQuadro(ctxFalso([]), 12, plano, "tela_cheia", recursos);
      console.log(JSON.stringify({sobre: s.ativas, cortina: c.ativas, cheia: d.ativas, limpa: log[0]}))""")
    assert r["sobre"] == ["barra-progresso"]
    assert r["cortina"] == ["barra-progresso", "transicao-cortina"]   # a cortina "cobre" entra por cima do vídeo
    assert "barra-progresso" not in r["cheia"] and "titulo-expressao" in r["cheia"]
    assert r["limpa"].startswith("clearRect")                          # camada sobre começa transparente


def test_arquivos_js_sem_timer_nem_aleatorio():
    for p in arquivos_js():
        src = "\n".join(l for l in p.read_text(encoding="utf-8").splitlines() if not l.strip().startswith("//"))
        for proibido in ("setTimeout", "setInterval", "requestAnimationFrame", "Math.random", "transition:", "Date.now"):
            assert proibido not in src, (p.name, proibido)
