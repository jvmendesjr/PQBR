from pqbr.workflows.temas import ler_proposta, filtrar, ALVO

def test_ler_proposta():
    v = "expressao: Por que se diz 'pagar o pato'? || habito_mania: Por que o brasileiro guarda sacola de mercado? || lixo || politica: x"
    r = ler_proposta(v)
    assert [x["categoria"] for x in r] == ["expressao", "habito_mania"] and ALVO == 28

def test_filtrar_repetido_e_sazonal():
    props = [{"categoria": "expressao", "tema": "Por que o PIX se chama PIX?"},
             {"categoria": "sazonal", "tema": "Por que tem quadrilha na festa junina?"},
             {"categoria": "expressao", "tema": "Por que se diz que alguém pagou o pato?"}]
    ok, rec = filtrar(props, ["Por que o PIX se chama PIX?"], [])
    assert [x["tema"] for x in ok] == ["Por que se diz que alguém pagou o pato?"] and len(rec) == 2
