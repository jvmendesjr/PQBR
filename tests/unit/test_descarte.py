import pytest
from pqbr.workflows.descarte import PedidoDescarteTeste, CopiasVerificadas, tipo_arquivo
from pqbr.workflows.acesso import causa_provavel


def test_pedido_descarte_valida():
    PedidoDescarteTeste(caderno="f757e751-8b9f-4e6b-bcd0-a853c4811e1f", rotulo="ep1001-descartado", motivo="reclassificado teste (José 18:06)")
    with pytest.raises(Exception): PedidoDescarteTeste(caderno="f757e751", rotulo="x", motivo="curto")


def test_copias_completas():
    assert CopiasVerificadas(postgres=5, drive=5, repo=5, hindsight=True, bytes=1).completas
    assert not CopiasVerificadas(postgres=5, drive=4, repo=5, hindsight=True, bytes=1).completas
    assert not CopiasVerificadas(postgres=5, drive=5, repo=5, hindsight=False, bytes=1).completas
    assert not CopiasVerificadas(postgres=0, drive=0, repo=0, hindsight=True, bytes=0).completas


def test_tipo_arquivo():
    assert tipo_arquivo("a.mp4") == "video" and tipo_arquivo("respostas.json") == "resposta" and tipo_arquivo("fonte_01.md") == "fonte"


def test_causa_provavel():
    assert "divergente" in causa_provavel("a", "b", True)
    assert "SID" in causa_provavel("a", "a", False)
