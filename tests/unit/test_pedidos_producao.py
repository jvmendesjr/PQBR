"""pt162u / t168u: PedidoEpisodioE2E e PedidoNotebookLM em VERSOES 1.1.0."""
from pqbr.contratos import VERSOES, PedidoEpisodioE2E, PedidoNotebookLM


def test_versoes_pedidos_producao():
    assert VERSOES["PedidoEpisodioE2E"] == "1.1.0"
    assert VERSOES["PedidoNotebookLM"] == "1.1.0"
    assert PedidoEpisodioE2E.model_fields["versao"].default == "1.1.0"
    assert PedidoNotebookLM.model_fields["versao"].default == "1.1.0"


def test_pedido_episodio_e2e_minimo():
    p = PedidoEpisodioE2E(
        slug="cafe-fraco",
        codigo="PQBR-EP1003",
        roteiro_texto="x" * 50,
        n_cenas=6,
        usar_mestre=True,
    )
    assert p.usar_mestre is True
    assert p.versao == "1.1.0"


def test_pedido_notebooklm_papel_mestre():
    p = PedidoNotebookLM(
        tipo="briefing",
        slug="cafe-fraco",
        fonte="y" * 30,
        papel="mestre",
        episodio="PQBR-EP1003",
    )
    assert p.papel == "mestre" and p.tipo == "briefing"
