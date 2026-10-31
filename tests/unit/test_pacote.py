"""t459: pacote canônico (hash determinístico, §16.7) e travas do apagamento de caderno."""
import asyncio, pytest
from pqbr.workflows import pacote, notebooklm as n
from pqbr.contratos import CATEGORIA_YOUTUBE, PacoteSEO


def test_pacote_hash_deterministico_e_bloco():
    a, b = pacote.montar_pacote(), pacote.montar_pacote()
    assert a["hash"] == b["hash"] and len(a["hash"]) == 64
    assert a["itens"]["bloco_visual_16_7"].startswith("[ESTILO]")
    assert set(a["itens"]) == {"persona", "comandos_prompts", "contrato_editorial", "bloco_visual_16_7", "catalogo_visual"}
    assert set(a["origem"]) == set(a["itens"])


def test_pacote_leva_o_catalogo_visual_e_muda_de_hash_com_ele(tmp_path):
    a = pacote.montar_pacote()
    cat = a["itens"]["catalogo_visual"]
    assert "PERS-menino-azul [protagonista masculino]" in cat and "PERS-menina-rosa [protagonista feminino]" in cat and "SIT-" in cat
    texto = pacote.texto_fonte_pacote(a)
    assert "## catalogo_visual" in texto and texto.index("## bloco_visual_16_7") < texto.index("## catalogo_visual") < texto.index("## contrato_editorial")
    # o mesmo repositório com uma ficha a mais gera outro pacote (versão nova sozinha)
    import shutil
    from pqbr.pipeline import banco_fichas as bf
    raiz = tmp_path / "repo"
    for rel in (*pacote.FONTES_PACOTE.values(), "banco-fichas/indice.json"):
        (raiz / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(pacote.RAIZ / rel, raiz / rel)
    antes = pacote.montar_pacote(raiz)
    assert antes["hash"] == a["hash"]
    bf.registrar(tipo="objeto", slug="lupa-teste", titulo="Lupa de teste do pacote", raiz=raiz / "banco-fichas",
                 trava="Lupa de cabo marrom em cartoon 2D flat colorido, contorno preto, sem texto e sem marca.")
    depois = pacote.montar_pacote(raiz)
    assert "OBJ-lupa-teste" in depois["itens"]["catalogo_visual"] and antes["hash"] != depois["hash"]


def test_categoria_educacao_e_sem_midia_sintetica():
    assert CATEGORIA_YOUTUBE == "27"
    s = PacoteSEO(titulo="Por que podre de rico?", descricao="Origem da expressão.", hashtags=["#curiosidades", "#shorts", "#pqbr"])
    assert s.categoria_id == "27" and s.contem_midia_sintetica is False


def test_titulo_caderno_exige_codigo():
    assert n.titulo_caderno("PQBR-EP0001", "podre-de-rico") == "Short - PQBR-EP0001 - podre-de-rico"
    with pytest.raises(ValueError): n.titulo_caderno("EP1", "x")


@pytest.mark.parametrize("cad,cod,tit", [
    ("c35d7b24-5d4f-4eee-afc4-7a0eadc860bf", "PQBR-EP0001", "Short - PQBR-EP0001 - x"),   # mestre
    ("c35d7b24", "PQBR-EP0001", "Short - PQBR-EP0001 - x"),                               # id parcial
    ("16e6b835-a33a-4460-ba48-035d7a58d566", "PQBR-EP0001", "PQBR - pesquisa bloco visual 2D"),  # fora da allowlist
    ("16e6b835-a33a-4460-ba48-035d7a58d566", "PQBR-EP0002", "Short - PQBR-EP0001 - x"),   # código não confere
])
def test_apagar_recusa_sem_chamar_cli(monkeypatch, cad, cod, tit):
    monkeypatch.setattr(pacote, "_cli", lambda *a, **k: pytest.fail("não pode chamar a CLI"))
    with pytest.raises(RuntimeError): asyncio.run(pacote.nlm_apagar_caderno(cad, cod, tit))


def test_apagar_confere_titulo_no_notebooklm(monkeypatch):
    cad = "11111111-2222-3333-4444-555555555555"; chamadas = []
    def cli(*a, **k):
        chamadas.append(a[0])
        return '{"notebooks": [{"id": "%s", "title": "Outro título", "is_owner": true}]}' % cad
    monkeypatch.setattr(pacote, "_cli", cli)
    with pytest.raises(RuntimeError): asyncio.run(pacote.nlm_apagar_caderno(cad, "PQBR-EP0001", "Short - PQBR-EP0001 - x"))
    assert "delete" not in chamadas


def test_fontes_estranhas_detecta_contaminacao():
    lst = {"sources": [{"id": "a" * 8 + "-0000-0000-0000-" + "0" * 12, "title": "PQBR pacote x"},
                       {"id": "b" * 8 + "-0000-0000-0000-" + "0" * 12, "title": "outro-episodio.md"}]}
    est = pacote.fontes_estranhas(lst, ["a" * 8 + "-0000-0000-0000-" + "0" * 12])
    assert [e["title"] for e in est] == ["outro-episodio.md"]
    assert pacote.fontes_estranhas(lst, [x["id"] for x in lst["sources"]]) == []


def test_conferir_fontes_bloqueia(monkeypatch):
    out = '{"sources": [{"id": "cccccccc-0000-0000-0000-000000000000", "title": "intrusa.md"}]}'
    monkeypatch.setattr(pacote, "_cli", lambda *a, **k: out)
    with pytest.raises(pacote.ContaminacaoCaderno): asyncio.run(pacote.nlm_conferir_fontes("11111111-2222-3333-4444-555555555555", []))
    assert asyncio.run(pacote.nlm_conferir_fontes("11111111-2222-3333-4444-555555555555", ["cccccccc-0000-0000-0000-000000000000"])) == 1
