"""render.py e compor.py: página montada, comando FFmpeg e, se houver Chrome, um render curto determinístico."""
import os, shutil
from pathlib import Path
import pytest
from pqbr.contratos.motion import PlanoMotion, PecaMotion, BlocoNumeros, FaixaBloco, transicao_padrao
from pqbr.pos.motion import render, compor

ITENS = ["Chá de bico de chaleira", "A versão mais aceita"]


def plano(dur=14.0, fps=24):
    b = FaixaBloco(inicio=4, fim=10)
    return PlanoMotion(episodio="PQBR-EP1003", duracao_video_s=dur, fps=fps, elenco="PERS-F", bloco_numeros=BlocoNumeros(itens=ITENS), bloco=b,
                       pecas=transicao_padrao(b) + [PecaMotion(modelo="titulo-expressao", inicio=4, fim=10, parametros={"texto": ITENS[0], "rotulo": ITENS[1]}),
                                                   PecaMotion(modelo="barra-progresso", inicio=0, fim=dur)])


def test_pagina_carrega_motor_e_catalogo_e_leva_o_plano():
    html = render.montar_pagina(plano())
    assert "motor.js" in html and "titulo-expressao.js" in html and "barra-progresso.js" in html
    assert '"episodio": "PQBR-EP1003"' in html and "window.seek" in html
    assert "setTimeout" not in html and "requestAnimationFrame" not in html


def test_comando_ffmpeg_troca_o_trecho_e_copia_o_audio():
    cmd = compor.comando_compor(plano(), Path("orig.mp4"), Path("r"), Path("saida.mp4"))
    fc = cmd[cmd.index("-filter_complex") + 1]
    assert "trim=end=4.0" in fc and "trim=start=10.0" in fc and "concat=n=3" in fc and "overlay=0:0" in fc
    assert cmd[cmd.index("-c:a") + 1] == "copy" and "0:a?" in cmd
    sem_bloco = compor.comando_compor(plano().model_copy(update={"bloco": None, "pecas": [PecaMotion(modelo="barra-progresso", inicio=0, fim=14)]}), Path("o.mp4"), Path("r"), Path("s.mp4"))
    assert "concat" not in sem_bloco[sem_bloco.index("-filter_complex") + 1]


def test_snap_alinha_ao_quadro():
    assert render._snap(14.9, 30) == 14.9 and render._snap(14.91, 30) == 14.9 and render._snap(0.333333, 30) == 0.333333


CHROME = os.environ.get("PQBR_CHROME", "/usr/bin/google-chrome")


@pytest.mark.skipif(not Path(CHROME).exists() or shutil.which("ffmpeg") is None, reason="sem Chrome ou FFmpeg")
def test_render_curto_e_deterministico_sem_violacao(tmp_path):
    pytest.importorskip("playwright")
    p = plano(dur=14.0, fps=24)
    r = render.renderizar(p, tmp_path / "r", sobre=False)
    assert r.quadros_tela_cheia == 6 * 24 and r.deterministico and r.violacoes == []
    assert (tmp_path / "r" / "tela_cheia" / "q00000.png").stat().st_size > 1000
    assert (tmp_path / "r" / "relatorio-render.json").exists()
    assert r.hashes["tela_cheia@4.5"] != r.hashes["tela_cheia@7.0"]   # entrando × assentado; assentado repete o mesmo quadro


def test_pagina_usa_a_fonte_do_plano_por_arquivo_local():
    html = render.montar_pagina(plano())
    assert 'font-family:"PQBR-fredoka"' in html and "src:url(\"file:///" in html and "fredoka.ttf" in html
    assert "http://" not in html.replace("http://www.w3.org", "") and "fonts.googleapis" not in html
    assert 'PQBRMotion.FONTE = "\\"PQBR-fredoka\\"' in html


@pytest.mark.skipif(not Path(CHROME).exists(), reason="sem Chrome")
def test_fonte_do_plano_carrega_de_verdade_no_chrome(tmp_path):
    sync = pytest.importorskip("playwright.sync_api")
    (tmp_path / "p.html").write_text(render.montar_pagina(plano()), encoding="utf-8")
    with sync.sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROME, headless=True, args=["--allow-file-access-from-files"])
        pag = nav.new_page()
        pag.goto((tmp_path / "p.html").as_uri())
        pag.wait_for_function("window.pronto === true")
        assert pag.evaluate("() => window.carregarFonte('PQBR-fredoka', ['700'])") is True
        assert pag.evaluate("() => PQBRMotion.FONTE").startswith('"PQBR-fredoka"')
        nav.close()
