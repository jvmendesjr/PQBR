"""F7-02: contrato textual LOOP; testes sintéticos sem provedor."""
import json
import unittest

from pqbr.pipeline import auditor_texto as at


class AuditorLoop(unittest.TestCase):
    def resposta(self, continuidade="sim", cortada="nao"):
        return json.dumps({"ultima_continua_na_primeira": continuidade,
                           "fala_final_cortada_no_meio": cortada})

    def test_aprova_loop_e_fala_inteiros(self):
        r = at.decidir(self.resposta())
        self.assertEqual(r.veredito, "aprova")
        self.assertEqual(r.motivos, ["loop_textual_ok"])

    def test_reprova_quando_ultima_nao_emenda(self):
        r = at.decidir(self.resposta(continuidade="nao"))
        self.assertEqual(r.veredito, "reprova")
        self.assertIn("ultima_fala_nao_emenda_na_primeira", r.motivos)

    def test_reprova_fala_final_truncada(self):
        r = at.decidir(self.resposta(cortada="sim"))
        self.assertEqual(r.veredito, "reprova")
        self.assertIn("fala_final_cortada_no_meio", r.motivos)

    def test_registra_as_duas_falhas(self):
        r = at.decidir(self.resposta("nao", "sim"))
        self.assertEqual(set(r.motivos), {"ultima_fala_nao_emenda_na_primeira", "fala_final_cortada_no_meio"})

    def test_json_invalido_ou_incompleto_pede_terceira_rodada(self):
        self.assertEqual(at.decidir("não sei").veredito, "terceira_rodada")
        self.assertEqual(at.decidir('{"ultima_continua_na_primeira":"sim"}').veredito, "terceira_rodada")

    def test_prompt_mostra_somente_as_duas_frases_fornecidas(self):
        p = at.montar_prompt("INICIO_PRIVADO", "FIM_PRIVADO")
        self.assertIn("INICIO_PRIVADO", p)
        self.assertIn("FIM_PRIVADO", p)
        self.assertNotIn("TRANSCRICAO_COMPLETA", p)
        with self.assertRaises(ValueError):
            at.montar_prompt("", "fim")
