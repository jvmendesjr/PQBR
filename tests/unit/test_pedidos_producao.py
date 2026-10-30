"""pt162u: PedidoEpisodioE2E e PedidoNotebookLM em VERSOES 1.0.0."""
from pqbr.contratos import VERSOES, PedidoEpisodioE2E, PedidoNotebookLM


def test_versoes_pedidos_producao():
    assert VERSOES["PedidoEpisodioE2E"] == "1.0.0"
    assert VERSOES["PedidoNotebookLM"] == "1.0.0"
    assert PedidoEpisodioE2E.model_fields["versao"].default == "1.0.0"
    assert PedidoNotebookLM.model_fields["versao"].default == "1.0.0"


def test_pedido_episodio_e2e_minimo():
    p = PedidoEpisodioE2E(
        slug="cafe-fraco",
        codigo="PQBR-EP1003",
        roteiro_texto="x" * 50,
        n_cenas=8,
    )
    assert p.versao == "1.0.0" and p.dry_run is True


def test_pedido_notebooklm_minimo():
    p = PedidoNotebookLM(tipo="short", slug="cafe-fraco", fonte="y" * 20)
    assert p.versao == "1.0.0" and p.tipo == "short"
