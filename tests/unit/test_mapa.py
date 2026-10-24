import importlib.util
from pathlib import Path

R = Path(__file__).resolve().parents[2]


def test_mapa_cobre_o_codigo():
    """Se falhar: o código mudou e o mapa não. Um humano atualiza docs/mapa/ (agente só com OK do José)."""
    spec = importlib.util.spec_from_file_location("vm", R / "scripts/mapa/verificar_mapa.py")
    vm = importlib.util.module_from_spec(spec); spec.loader.exec_module(vm)
    assert vm.divergencias() == []
