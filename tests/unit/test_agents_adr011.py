import asyncio
from pydantic_ai.models.test import TestModel
from pqbr.agents import persona, criar_agente, rodar, REGISTRO
from pqbr.contratos import PropostaTemas
from pqbr.workflows.temas import propostas_de, PEDIDO


def test_persona_sem_frontmatter():
    p = persona("lider-editorial")
    assert p.startswith("# Líder Editorial") and "reportsTo" not in p


def test_registro_combo():
    _, combos = criar_agente("lider-editorial", PropostaTemas, model=TestModel())
    assert combos[0] == "core-medio" and "lider-editorial" in REGISTRO


def test_rodar_testmodel_saida_tipada():
    tm = TestModel(custom_output_args={"temas": [
        {"categoria": "expressao", "tema": "Por que se diz 'pagar o pato'?"},
        {"categoria": "habito_mania", "tema": "Por que o brasileiro guarda sacola de mercado?"}],
        "justificativa": "perenes"})
    out, meta = asyncio.run(rodar("lider-editorial", PropostaTemas, PEDIDO.format(faltam=2, alvo=28, usados="- x"), model=tm))
    assert isinstance(out, PropostaTemas) and meta["combo"] == "core-medio"
    assert [p["categoria"] for p in propostas_de(out)] == ["expressao", "habito_mania"]


def test_contrato_recusa_sazonal_e_sem_por_que():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        PropostaTemas(temas=[{"categoria": "sazonal", "tema": "Por que tem quadrilha?"}], justificativa="x")
    with pytest.raises(ValidationError):
        PropostaTemas(temas=[{"categoria": "expressao", "tema": "Origem do pagar o pato"}], justificativa="x")
