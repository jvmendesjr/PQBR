"""F7-02: auditor VISUAL 2D sem fichas (t399–t403)."""
import json, unittest
from pqbr.pipeline import auditor_visual as av

IDS = ["S01", "S02"]


def cena(i, **kw):
    base = {"id": i, "tem_personagem": "sim", "tem_texto_na_tela": "nao",
            **{m: "sim" for m in av.METRICAS}, **{s: "nao" for s in av.SEGURANCA + av.BLOQUEIO_VISUAL}}
    base.update({"foco_unico_zona_segura": "na", "corresponde_ao_titulo": "na", "legenda_cobre_foco": "na"})
    base["texto_com_erro_de_sentido"] = "na"
    base["legenda_com_erro"] = "nao"
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
        p = av.montar_prompt("[ESTILO] 2D", [("S01", "saiu do banho")], 2, titulo="Título", transmitir_texto=True)
        assert "__" not in p and "Rodada: 2" in p and "- S01: saiu do banho" in p




    def test_prompt_somente_visual_nao_vaza_texto(self):
        p = av.montar_prompt("BLOCO_PRIVADO", [("S01", "FALA_PRIVADA")], 1,
                             titulo="TITULO_PRIVADO", transmitir_texto=False)
        assert "BLOCO_PRIVADO" not in p and "FALA_PRIVADA" not in p and "TITULO_PRIVADO" not in p
        assert "SOMENTE VISUAL" in p

    def test_metricas_a9_nao_reprovam(self):
        x = resp(cena("CAPA", foco_unico_zona_segura="nao", corresponde_ao_titulo="nao",
                      legenda_cobre_foco="sim", tem_texto_na_tela="sim", legivel_no_celular="nao"))
        r = av.decidir([x, x], ["CAPA"])
        assert r["veredito"] == "aprova_com_ressalva" and not r["falhas"]
        assert r["metricas"]["foco_unico_zona_segura"] == 0.0
        assert set(r["ressalvas"]) >= {("CAPA", "foco_unico_zona_segura"),
                                      ("CAPA", "corresponde_ao_titulo"),
                                      ("CAPA", "legenda_cobre_foco"),
                                      ("CAPA", "tem_texto_na_tela")}

    def test_legenda_com_erro_aceita_e_registra(self):
        x = resp(cena("S01", legenda_com_erro="sim"), cena("S02"))
        r = av.decidir([x, x], IDS)
        assert r["veredito"] == "aprova_com_ressalva"
        assert r["erros_aceitaveis"] == [("S01", "legenda_com_erro")]
        ls = av.linhas_erros_aceitaveis(r, episodio_codigo="PQBR-EP0001")
        assert ls[0]["categoria"] == "legenda" and ls[0]["veredito_auditor"] == "aprova_com_ressalva"


    def test_legenda_que_muda_sentido_reprova(self):
        x = resp(cena("S01", legenda_com_erro="sim", texto_com_erro_de_sentido="sim"), cena("S02"))
        r = av.decidir([x, x], IDS)
        assert r["veredito"] == "reprova" and r["erros_aceitaveis"] == []


    def test_texto_na_imagem_sem_erro_registra_sem_ressalva(self):
        x = resp(cena("S01", tem_texto_na_tela="sim", texto_com_erro_de_sentido="nao"), cena("S02"))
        r = av.decidir([x, x], IDS)
        assert r["veredito"] == "aprova" and r["erros_aceitaveis"] == [("S01", "tem_texto_na_tela")]

if __name__ == "__main__":
    unittest.main()
