"""t98u/t99u: ESTADO-ATUAL obrigatório (hook) e handoff no registrar_alteracao."""
import pytest
from pqbr.governanca.estado_atual import ESTADO, exige_estado, proximo_passo
from pqbr.mcp.escrita import registrar
from pqbr.mcp import onboarding

TXT = "# E\n\n## Próximo passo\nJosé assiste o EP1003.\n\n## Pendências abertas\nx"


def test_trivial_nao_exige():
    assert exige_estado(["src/pqbr/x.py", "docs/REGRAS.md"]) == []


@pytest.mark.parametrize("g", ["docs/ROADMAP.md", "docs/LACUNAS-fluxo.md", "docs/DECISOES-LOG.md", "CHANGELOG.md"])
def test_gatilho_sem_estado_bloqueia(g):
    assert exige_estado([g, "src/a.py"]) == [g]
    assert exige_estado([g, ESTADO]) == []


def test_proximo_passo():
    assert proximo_passo(TXT) == "José assiste o EP1003."
    assert proximo_passo("sem seção") == "ver docs/ESTADO-ATUAL.md"


def _reg(tipo, arqs, papel="mantenedor"):
    gravados = []
    r = registrar(papel, "cli", {"conteudo": "corrigi a pendência X do fluxo", "commit": "abc1234", "tipo": tipo},
                  exige_commit=True, reter=lambda *a, **k: gravados.append((a, k)), verificar_commit=lambda h: True,
                  listar_arquivos=lambda h: arqs, estado_txt=TXT)
    return r, gravados


def test_pendencia_resolvida_exige_estado_no_commit():
    with pytest.raises(ValueError, match="ESTADO-ATUAL"):
        _reg("pendencia_resolvida", ["docs/ROADMAP.md"])
    with pytest.raises(ValueError):
        _reg("correcao", [])


def test_handoff_gravado_com_tag_estado():
    r, g = _reg("pendencia_resolvida", [ESTADO, "docs/ROADMAP.md"])
    assert r.handoff_registrado and len(g) == 2
    (txt, ctx), k = g[1]
    assert k["tags"] == ["estado"] and k["autor"] == "cli" and "José assiste o EP1003." in txt and "abc1234" in txt


def test_alteracao_simples_nao_exige_estado_mas_grava_handoff():
    r, g = _reg("alteracao", ["src/a.py"])
    assert r.handoff_registrado and len(g) == 2


def test_registrar_memoria_sem_handoff():
    g = []
    r = registrar("mantenedor", "cli", {"conteudo": "uma lição registrada sem commit"}, reter=lambda *a, **k: g.append(k))
    assert not r.handoff_registrado and len(g) == 1


def test_onboarding_comeca_pelo_estado():
    p = onboarding.pacote()
    assert p.index("ESTADO ATUAL") < p.index("## BRIEFING")
    assert "Atualizar docs/ESTADO-ATUAL.md a cada correção" in p
