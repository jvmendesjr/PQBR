"""t459: pacote canônico (hash determinístico, §16.7) e travas do apagamento de caderno."""
import asyncio, pytest
from pqbr.workflows import pacote, notebooklm as n
from pqbr.contratos import CATEGORIA_YOUTUBE, PacoteSEO


def test_pacote_hash_deterministico_e_bloco():
    a, b = pacote.montar_pacote(), pacote.montar_pacote()
    assert a["hash"] == b["hash"] and len(a["hash"]) == 64
    assert a["itens"]["bloco_visual_16_7"].startswith("[ESTILO]")
    assert set(a["itens"]) == {"persona", "comandos_prompts", "contrato_editorial", "bloco_visual_16_7"}


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
