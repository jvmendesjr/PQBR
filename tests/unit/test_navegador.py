import json, pytest
from pydantic import ValidationError
from pqbr.contratos import InstanciaNavegador, SaudeNavegador, VERSOES
from pqbr.motores.navegador import instancias, instancia, NavegadorCamofox


def test_config_real_reserva():
    i = {x.conta: x for x in instancias()}
    assert i["pqbr"].porta == 9387 and i["pqbr"].estado == "individual"
    assert i["proxima"].porta == 9397 and i["proxima"].estado == "reservada"


def test_reservada_nao_toca_rede():
    s = NavegadorCamofox(instancia("proxima")).saude()
    assert s.ok is False and "reservada" in s.motivo


def test_contrato_recusa(tmp_path):
    with pytest.raises(ValidationError):
        InstanciaNavegador(conta="X Y", porta=80, estado="ativa", unit="u")
    f = tmp_path / "c.json"
    f.write_text(json.dumps({"instancias": [{"conta": "a1", "porta": 9397, "estado": "reservada", "unit": "camofox@a1"},
                                            {"conta": "b1", "porta": 9397, "estado": "reservada", "unit": "camofox@b1"}]}))
    with pytest.raises(ValueError):
        instancias(f)
    assert {"InstanciaNavegador", "SaudeNavegador"} <= set(VERSOES)
