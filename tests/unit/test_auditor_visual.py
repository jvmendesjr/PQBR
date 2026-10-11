"""F7-02: auditor VISUAL 2D sem fichas (t399–t403)."""
import json, unittest
from pqbr.pipeline import auditor_visual as av

IDS = ["S01", "S02"]


def cena(i, **kw):
    base = {"id": i, "tem_personagem": "sim", "tem_texto_na_tela": "nao",
            **{m: "sim" for m in av.METRICAS}, **{s: "nao" for s in av.SEGURANCA}}
    base["texto_com_erro_de_sentido"] = "na"
    base.update(kw)
    return base


def resp(*cenas, rodada=1):
    return json.dumps({"rodada": rodada, "cenas": list(cenas)})



class AuditorVisual(unittest.TestCase):
    def test_aprova(self):
        r = av.decidir([resp(cena("S01"), cena("S02"))] * 2, IDS)
        assert r["veredito"] == "aprova" and r["metricas"]["legivel_no_celular"] == 1.0


    def test_seguranca_concordante_reprova(self):
        x = resp(cena("S01", parece_pessoa_real="sim"), cena("S02"))
        r = av.decidir([x, x], IDS)
        assert r["veredito"] == "reprova" and r["falhas"] == [("S01", "parece_pessoa_real")]


    def test_seguranca_divergente_terceira_rodada(self):
        a = resp(cena("S01", marca_real="sim"), cena("S02"))
        b = resp(cena("S01"), cena("S02"))
        assert av.decidir([a, b], IDS)["veredito"] == "terceira_rodada"


    def test_rodada_unica_falha_vale(self):
        r = av.decidir([resp(cena("S01", estereotipo_ofensivo="sim"), cena("S02"))], IDS)
        assert r["veredito"] == "reprova" and r["rodada_unica"]


    def test_metrica_nunca_reprova(self):
        x = resp(cena("S01", segue_estilo_declarado="nao", imagem_corresponde_a_fala="nao"), cena("S02"))
        r = av.decidir([x, x], IDS)
        assert r["veredito"] == "aprova_com_ressalva"
        assert r["metricas"]["segue_estilo_declarado"] == 0.5


    def test_texto_erro_de_sentido_reprova(self):
        x = resp(cena("S01", tem_texto_na_tela="sim", texto_com_erro_de_sentido="sim"), cena("S02"))
        assert av.decidir([x, x], IDS)["veredito"] == "reprova"


    def test_na_sem_personagem_ok_e_na_invalido(self):
        x = resp(cena("S01", tem_personagem="nao", mesmo_personagem_do_bloco="na"), cena("S02"))
        assert av.decidir([x, x], IDS)["veredito"] == "aprova"
        y = resp(cena("S01", marca_real="na"), cena("S02"))
        assert av.decidir([y, y], IDS)["veredito"] == "terceira_rodada"


    def test_cerca_json_e_cena_ausente(self):
        x = "```json\n" + resp(cena("S01")) + "\n```"
        r = av.decidir([x, x], IDS)
        assert r["veredito"] == "terceira_rodada" and "r1:S02:ausente" in r["problemas"]


    def test_json_invalido(self):
        assert av.decidir(["não sei"], IDS)["veredito"] == "terceira_rodada"


    def test_prompt_preenchido(self):
        p = av.montar_prompt("[ESTILO] 2D", [("S01", "saiu do banho")], 2)
        assert "__" not in p and "Rodada: 2" in p and "- S01: saiu do banho" in p


if __name__ == "__main__":
    unittest.main()
