"""Regra de compliance do canal (proposta 2026-11-01): a essência irônica/hiperbólica,
o personagem histórico do passado, a história política do passado e a hipótese com incerteza
não são motivo de reprova; as travas de segurança continuam valendo."""

from pqbr.workflows.criativo import PROMPT_COMPLIANCE


def test_compliance_permite_essencia_do_canal():
    for trecho in (
        "irônico e hiperbólico",
        "personagem histórico do passado",
        "história política do passado",
        "linguagem de incerteza",
        "hipérbole coloquial",
    ):
        assert trecho in PROMPT_COMPLIANCE


def test_compliance_mantem_travas_de_seguranca():
    for trecho in (
        "pessoa real viva",
        "difamação",
        "marca real",
        "estereótipo ofensivo",
        "política atual ou partidária",
        "afirmação falsa apresentada como certa sem atenuador",
        "pedido de comentário",
        "conselho especializado",
    ):
        assert trecho in PROMPT_COMPLIANCE
