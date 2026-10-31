"""Regra única de tags do Hindsight (t90u): indexador e reclassificação concordam."""
import importlib.util, sys
from pathlib import Path
from pqbr.storage.hindsight_tags import TAG_OBS, conflitos, fonte, tags_conteudo
from pqbr.contratos.politica import carregar

RAIZ = Path(__file__).resolve().parents[2]


def _modulo(nome, rel):
    spec = importlib.util.spec_from_file_location(nome, RAIZ / rel)
    m = importlib.util.module_from_spec(spec); sys.modules[nome] = m; spec.loader.exec_module(m); return m


def test_origem_define_base():
    assert fonte("PQBR evolução — commit do repositório")[2] == {"commit"}
    assert fonte("PQBR incidente — DECISOES-LOG: t415 incidente de credencial")[2] == {"incidente"}
    tipo, p, t = fonte("PQBR doc canônico — docs/CONTRATO-EDITORIAL.md: 18. Storyboard")
    assert (tipo, p) == ("doc", "docs/CONTRATO-EDITORIAL.md") and {"doc", "editorial"} <= t


def test_palavras_e_filtro_da_politica():
    t = tags_conteudo("PQBR doc canônico — docs/SPEC.md: F08", "Upload no YouTube com OAuth e roteiro")
    assert {"doc", "publicacao", "seguranca", "editorial"} <= t and TAG_OBS not in t
    assert tags_conteudo("x", "upload youtube", {"doc"}) == {"doc"}


def test_tags_validas_na_politica():
    todas = {t for v in carregar().papeis.values() for k in ("leitura", "escrita") for t in getattr(v, k)}
    assert tags_conteudo("PQBR evolução — commit", "auditoria loop incidente pesquisa licença lição", None) <= todas | {"commit"}


def test_conflitos():
    assert any("Paperclip" in c for c in conflitos("agentes no Paperclip"))
    assert conflitos("tudo pelo Temporal") == []


def test_indexador_usa_a_mesma_regra_e_a_politica_aceita():
    ix = _modulo("indexar_t90u", "scripts/hindsight/indexar.py")
    ctx, txt = "PQBR doc canônico — docs/SPEC.md: F08", "Upload no YouTube com OAuth e roteiro"
    tags = ix.tags_indexador(ctx, txt)
    assert set(tags) == tags_conteudo(ctx, txt)
    carregar().exigir_escrita("indexador", tags)  # não levanta
