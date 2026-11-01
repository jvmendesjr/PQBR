"""Proposta 2026-11-01 (pendente de OK do José): regras e contratos mais permissivos
para o estilo do canal — ironia/hipérbole, personagem histórico do passado, história política
do passado e hipótese com incerteza — sem afrouxar as travas de segurança."""

from pqbr.contratos.catalogo_visual import PROIBIDO_PADRAO
from pqbr.pipeline.grade import bloqueio_absoluto
from pqbr.workflows.temas import PEDIDO


def test_temas_permite_historia_do_passado():
    assert "personagem histórico do passado" in PEDIDO
    assert "pessoa real viva" in PEDIDO
    assert "Sem política, religião, tragédia, marca ou pessoa real;" not in PEDIDO


def test_grade_cargo_historico_nao_e_partidario_mas_atual_continua_bloqueado():
    assert bloqueio_absoluto("Por que o senador Pinheiro Machado servia chimarrão?") is None
    assert bloqueio_absoluto("Por que o Bolsonaro fala assim?") == "politica_partidaria"
    assert bloqueio_absoluto("Por que a gente guarda pote de sorvete?") is None


def test_visual_stickman_historico_nao_e_rosto_real():
    assert "pessoa realista" in PROIBIDO_PADRAO
    assert "nome de personagem" in PROIBIDO_PADRAO
    assert "stickman que representa figura histórica não é rosto real" in PROIBIDO_PADRAO
