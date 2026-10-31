import pytest
from pqbr.workflows import auditor_gemini as ag


class Relogio:
    def __init__(self): self.t = 1000.0; self.dormiu = []
    def agora(self): return self.t
    def dormir(self, s): self.dormiu.append(s); self.t += s


def test_espera_e_memoria(monkeypatch):
    r = Relogio(); monkeypatch.setattr(ag, "ULTIMO_FECHAMENTO", 990.0)
    mems = iter([1600, 1500, 1300])
    assert ag.aguardar_folga(r.agora, r.dormir, lambda: next(mems), {"gemini_espera_s": 90, "gemini_mem_abrir_mb": 1400}) == 1300
    assert r.dormiu[0] == 80 and r.dormiu[1:] == [10, 10]


def test_falha_fechada(monkeypatch):
    r = Relogio(); monkeypatch.setattr(ag, "ULTIMO_FECHAMENTO", 0.0)
    with pytest.raises(ag.MemoriaAlta):
        ag.aguardar_folga(r.agora, r.dormir, lambda: 1800, {"gemini_mem_abrir_mb": 1400, "gemini_mem_timeout_s": 60})
    with pytest.raises(ag.MemoriaAlta):
        ag.aguardar_folga(r.agora, r.dormir, lambda: None, {"gemini_mem_timeout_s": 30})
