import pytest
from pydantic import ValidationError
from pqbr.contratos.roteiro_terceira_pessoa import RoteiroTerceiraPessoa, problemas_roteiro

OK = {"falas": ["Por que a gente dobra o saco de pão?", "Tem quem diga que é mania. Segue o Porquê BR!"],
      "cenas": [{"n": 1, "fala": "Por que a gente dobra o saco de pão?", "clipes": [{"id": "c1a",
      "prompt_imagem_en": "man folding a paper bag, curious face", "movimento_en": "he scratches his head, slow zoom"}]}]}

def test_ok_terceira_pessoa_e_a_gente():
    assert problemas_roteiro(OK) == []
    RoteiroTerceiraPessoa(**OK)

@pytest.mark.parametrize("fala", ["Eu sempre levo flores.", "Na minha casa é assim.", "Ele me contou tudo."])
def test_reprova_primeira_singular(fala):
    with pytest.raises(ValidationError): RoteiroTerceiraPessoa(falas=[fala])

@pytest.mark.parametrize("fala", ["— Olha o gás!", "Zé: que pato!", '"Paguei o pato", disse o marido.'])
def test_reprova_dialogo(fala):
    assert problemas_roteiro({"falas": [fala]})

@pytest.mark.parametrize("mov", ["the man explains the rule", "he talks to the viewer", "looking at the camera smiling",
                                 "character speaking with lip sync", "presents to camera"])
def test_reprova_personagem_falando(mov):
    r = {"falas": ["ok."], "cenas": [{"n": 1, "fala": "ok.", "clipes": [{"id": "c1a", "prompt_imagem_en": "x", "movimento_en": mov}]}]}
    assert any("c1a.movimento_en" in x for x in problemas_roteiro(r))

def test_nao_confunde_palavras():
    assert problemas_roteiro({"falas": ["Mesmo no meio do mês, o mel é bom."]}) == []
