"""t168u: BriefingEfemerico + adaptador falso + trava de mídia do mestre."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from pqbr.contratos import VERSOES
from pqbr.contratos.briefing_mestre import BriefingEfemerico, PedidoBriefingMestre
from pqbr.motores.briefing_mestre import AdaptadorFalsoBriefing, parse_briefing, briefador_mestre
from pqbr.config_caderno_mestre import recusar_midia_se_mestre, gravar_id, id_mestre


MID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def _briefing(**kw):
    base = dict(
        tema="por que café fraco vira chá de bico",
        codigo="PQBR-EP1003",
        slug="cafe-fraco",
        n_cenas=6,
        caderno_mestre_id=MID,
        persona_efemero="Você é o showrunner operacional do canal Porquê BR neste caderno EFÊMERO. Siga stickman.",
        prompt_pesquisa="origem da expressão chá de bico e café fraco no Brasil",
        urls_pesquisa=["https://pt.wikipedia.org/wiki/Lista_de_express%C3%B5es_idiom%C3%A1ticas_da_l%C3%ADngua_portuguesa"],
        prompt_roteiro="Escreva o roteiro do Short sobre o tema seguindo o contrato editorial.",
        prompt_seo="Gere título, descrição e hashtags pt-BR sem pedir comentário.",
        prompt_direcao_cenas="Monte a direção das cenas em JSON CenaIndividual 2.0.0 com rótulos PQBR-EP####-S##.",
    )
    base.update(kw)
    return base


def test_versoes_registradas():
    assert VERSOES["BriefingEfemerico"] == "1.0.0"
    assert VERSOES["PedidoBriefingMestre"] == "1.0.0"
    assert VERSOES["CenaIndividual"] == "2.0.0"
    assert VERSOES["DirecaoCenas"] == "2.0.0"
    assert VERSOES["PedidoEpisodioE2E"] == "1.1.0"


def test_briefing_ok():
    b = BriefingEfemerico(**_briefing())
    assert b.pesquisa_obrigatoria and b.versao == "1.0.0"


def test_briefing_url_opcional():
    # urls_pesquisa opcional desde a correcao definitiva 2026-11-01: o mestre nao
    # inventa URLs; a descoberta web roda no efemero via add-research.
    b = BriefingEfemerico(**_briefing(urls_pesquisa=[]))
    assert b.urls_pesquisa == []
    with pytest.raises(ValidationError):
        BriefingEfemerico(**_briefing(urls_pesquisa=["ftp://x"]))


def test_adaptador_falso():
    p = PedidoBriefingMestre(tema="chá de bico no Brasil", codigo="PQBR-EP1003", slug="cha-bico", n_cenas=4)
    b = AdaptadorFalsoBriefing(MID).briefar(p)
    assert b.urls_pesquisa and b.prompt_pesquisa
    assert "CenaIndividual 2.0.0" in b.prompt_direcao_cenas
    assert briefador_mestre("falso").nome == "falso"


def test_parse_briefing_json():
    p = PedidoBriefingMestre(tema="chá de bico no Brasil", codigo="PQBR-EP1003")
    raw = json.dumps({
        "persona_efemero": "x" * 60,
        "prompt_pesquisa": "origem chá de bico",
        "urls_pesquisa": ["https://example.com/a"],
        "prompt_roteiro": "roteiro completo do short sobre o tema",
        "prompt_seo": "titulo descricao hashtags do short",
        "prompt_direcao_cenas": "direcao cenas com rotulo PQBR-EP####-S##",
    })
    b = parse_briefing(raw, p, MID)
    assert b.caderno_mestre_id == MID and b.codigo == "PQBR-EP1003"


def test_parse_briefing_lista_string():
    """Regressao 2026-11-01 (workflow ep1003-redo-20261101b): o mestre devolveu
    riscos_compliance como string unica e o parse falhava; string vira lista."""
    p = PedidoBriefingMestre(tema="chá de bico no Brasil", codigo="PQBR-EP1003")
    raw = json.dumps({
        "persona_efemero": "x" * 60,
        "prompt_pesquisa": "origem chá de bico",
        "urls_pesquisa": "https://example.com/a",
        "prompt_roteiro": "roteiro completo do short sobre o tema",
        "prompt_seo": "titulo descricao hashtags do short",
        "prompt_direcao_cenas": "direcao cenas com rotulo PQBR-EP####-S##",
        "riscos_compliance": "Citar marcas registradas ou clickbait enganoso.",
    })
    b = parse_briefing(raw, p, MID)
    assert b.urls_pesquisa == ["https://example.com/a"]
    assert b.riscos_compliance == ["Citar marcas registradas ou clickbait enganoso."]


def test_parse_briefing_descarta_placeholder_url():
    """Regressao 2026-11-01 (workflow ep1003-redo-20261101c): o chat do NotebookLM
    mascara links externos com placeholder; urls_pesquisa opcional descarta o
    placeholder e nao falha com lista vazia."""
    p = PedidoBriefingMestre(tema="chá de bico no Brasil", codigo="PQBR-EP1003")
    raw = json.dumps({
        "persona_efemero": "x" * 60,
        "prompt_pesquisa": "origem chá de bico",
        "urls_pesquisa": ["[suspicious link removed]", "https://example.com/a"],
        "prompt_roteiro": "roteiro completo do short sobre o tema",
        "prompt_seo": "titulo descricao hashtags do short",
        "prompt_direcao_cenas": "direcao cenas com rotulo PQBR-EP####-S##",
    })
    b = parse_briefing(raw, p, MID)
    assert b.urls_pesquisa == ["https://example.com/a"]
    raw2 = json.dumps({
        "persona_efemero": "x" * 60,
        "prompt_pesquisa": "origem chá de bico",
        "urls_pesquisa": ["[suspicious link removed]"],
        "prompt_roteiro": "roteiro completo do short sobre o tema",
        "prompt_seo": "titulo descricao hashtags do short",
        "prompt_direcao_cenas": "direcao cenas com rotulo PQBR-EP####-S##",
    })
    b2 = parse_briefing(raw2, p, MID)
    assert b2.urls_pesquisa == []


def test_abriefar_limpa_chat_mesmo_com_falha_de_parse(monkeypatch):
    """Regressao 2026-11-01: falha de parse nao pode deixar o chat do mestre sujo;
    a limpeza roda em finally."""
    from pqbr.motores.briefing_mestre import AdaptadorNotebookLMBriefing
    from pqbr.workflows import notebooklm as n
    chamadas = []

    async def fake_perguntar(caderno, pergunta, salvar_nota=True):
        return json.dumps({"persona_efemero": "curto"})  # parse vai falhar (campos faltando)

    async def fake_limpar(caderno):
        chamadas.append(caderno)
        return "chat mestre limpo"

    monkeypatch.setattr(n, "nlm_mestre_perguntar", fake_perguntar)
    monkeypatch.setattr(n, "nlm_mestre_limpar_chat", fake_limpar)
    p = PedidoBriefingMestre(tema="chá de bico no Brasil", codigo="PQBR-EP1003", caderno_mestre_id=MID)
    with pytest.raises(ValidationError):
        asyncio.run(AdaptadorNotebookLMBriefing().abriefar(p))
    assert chamadas == [MID]


def test_activity_falso(monkeypatch):
    from pqbr.workflows import notebooklm as n
    out = asyncio.run(n.nlm_mestre_briefing({
        "tema": "chá de bico no Brasil",
        "codigo": "PQBR-EP1003",
        "slug": "cha-bico",
        "n_cenas": 4,
        "adaptador": "falso",
    }))
    assert out["versao"] == "1.0.0"
    assert out["urls_pesquisa"]


def test_trava_midia_mestre(tmp_path, monkeypatch):
    cfg = tmp_path / "caderno_mestre.json"
    cfg.write_text(json.dumps({
        "titulo": "PQBR - Mestre canônico",
        "caderno_mestre_id": MID,
        "proibido_midia": True,
        "mestres_legado_proibidos": ["c35d7b24-5d4f-4eee-afc4-7a0eadc860bf"],
    }), encoding="utf-8")
    import pqbr.config_caderno_mestre as c
    monkeypatch.setattr(c, "_CFG", cfg)
    assert id_mestre() == MID
    with pytest.raises(RuntimeError, match="nunca gera mídia"):
        recusar_midia_se_mestre(MID)
    # legado continua proibido via helper notebooklm
    assert nlm_legado_bloqueado()


def nlm_legado_bloqueado():
    from pqbr.workflows.notebooklm import _eh_proibido, MESTRES_PROIBIDOS
    assert "c35d7b24-5d4f-4eee-afc4-7a0eadc860bf" in MESTRES_PROIBIDOS
    assert _eh_proibido("c35d7b24-5d4f-4eee-afc4-7a0eadc860bf")
    return True
