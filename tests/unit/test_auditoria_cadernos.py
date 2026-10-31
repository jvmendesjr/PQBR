"""t170u: cadernos de auditoria — puro, sem rede."""
import pytest
from pqbr.auditoria_cadernos import (
    CHECKLIST_CENA, ERROS_RECORRENTES, VereditoCenaAuditoria,
    eh_titulo_auditoria, snapshot_regras_mestre, titulo_efemero_auditoria,
)
from pqbr.config_caderno_mestre_auditoria import titulo_mestre_auditoria


def test_titulo_efemero_distinto_do_criativo():
    t = titulo_efemero_auditoria("PQBR-EP1003", "cafe-fraco")
    assert t == "Auditoria - PQBR-EP1003 - cafe-fraco"
    assert not t.startswith("Short - ")
    assert eh_titulo_auditoria(t)


def test_titulo_invalido_falha_fechado():
    with pytest.raises(ValueError):
        titulo_efemero_auditoria("EP1003", "cafe-fraco")
    with pytest.raises(ValueError):
        titulo_efemero_auditoria("PQBR-EP1003", "Café Fraco!")


def test_snapshot_tem_regras_e_versao():
    s = snapshot_regras_mestre("1.0.0")
    assert "AUD-SNAP versao=1.0.0" in s
    assert "mulher jovem adulta" in s
    assert "chaleira sem mão" in s
    assert "boca_articula_fala" in s
    assert len(CHECKLIST_CENA) >= 15
    assert any("banquinho" in e for e in ERROS_RECORRENTES)


def test_mestre_titulo_e_veredito():
    assert titulo_mestre_auditoria() == "PQBR - Mestre de Auditoria"
    v = VereditoCenaAuditoria(id="S05", veredito="reprova", motivos=["braços realistas extras"], fontes_citadas=["AUD-SNAP"])
    assert v.veredito == "reprova"
    with pytest.raises(Exception):
        VereditoCenaAuditoria(id="S05", veredito="talvez")
