"""t126u: o registro de cliques começa vazio. Elemento só entra com data de observação."""
import json
from pathlib import Path

ARQ = Path(__file__).resolve().parents[2] / "config/mapa_cliques.json"


def test_registro_comeca_vazio_e_exige_data():
    reg = json.loads(ARQ.read_text(encoding="utf-8"))
    assert reg["versao"] == "0.1.0" and reg["sitios"] == []
    assert "ainda não foram mapeados" in reg["regra"]

    def aceitar(item: dict) -> None:
        for k in ("sitio", "elemento", "onde", "observado_em"):
            if not item.get(k):
                raise ValueError(k)
        if len(item["observado_em"]) != 10:
            raise ValueError("observado_em")

    try:
        aceitar({"sitio": "studio", "elemento": "enviar", "onde": "rodapé"})
        raise AssertionError("aceitou sem data")
    except ValueError as e:
        assert str(e) == "observado_em"
    aceitar({"sitio": "studio", "elemento": "enviar", "onde": "rodapé", "observado_em": "2026-10-26"})
