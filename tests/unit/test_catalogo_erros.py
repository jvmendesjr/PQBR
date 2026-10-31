import pytest
from pydantic import ValidationError
from pqbr.contratos.catalogo_erros import ErroCatalogo, CATALOGO_ERROS_VERSAO
from pqbr.pipeline.catalogo_erros_leitura import catalogo_erros_para_papel, prevencoes_para_prompt

BASE = dict(codigo="ERR-PER-01", categoria="personagem", descricao="Personagem muda entre cenas.",
            prevencao="Repetir a ficha do personagem em todo prompt.", severidade="alta", papeis_interessados=["auditor"])


def test_contrato_valido_e_versionado():
    e = ErroCatalogo(**BASE)
    assert e.versao == CATALOGO_ERROS_VERSAO == "1.0.0" and e.ativo


@pytest.mark.parametrize("campo,valor", [("codigo", "erro-1"), ("categoria", "outra"), ("severidade", "critica"),
                                         ("papeis_interessados", []), ("papeis_interessados", ["jose"])])
def test_contrato_recusa(campo, valor):
    with pytest.raises(ValidationError):
        ErroCatalogo(**{**BASE, campo: valor})


class _Cur:
    def __init__(self, rows): self.rows = rows
    def fetchall(self): return self.rows


class _Conn:
    def __init__(self, rows): self.rows, self.args = rows, None
    def execute(self, sql, args): self.args = (sql, args); return _Cur(self.rows)


def test_leitura_por_papel_filtra_e_formata():
    c = _Conn([(1, "ERR-CMP-02", "compliance", "Pessoa real nomeada na fala.", {"tema": "x"}, "Trocar por papel genérico.",
                "bloqueante", ["auditor"], True, None)])
    erros = catalogo_erros_para_papel("auditor", conn=c)
    assert c.args[1] == ("auditor",) and "ativo" in c.args[0]
    assert erros[0].codigo == "ERR-CMP-02"
    assert prevencoes_para_prompt(erros) == "- [ERR-CMP-02/bloqueante] Trocar por papel genérico."
