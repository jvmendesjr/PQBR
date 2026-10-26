"""F7-02: validação local de respostas estruturadas do Gemini; sem Camofox."""
import json
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from pqbr.workflows import auditor_gemini as ag
from pqbr.workflows.auditor_gemini import validar


def cena(cid, **overrides):
    base = {
        "id": cid,
        "tem_personagem": "sim",
        "tem_texto_na_tela": "nao",
        "segue_estilo_declarado": "sim",
        "mesmo_personagem_do_bloco": "na",
        "imagem_corresponde_a_fala": "sim",
        "legivel_no_celular": "sim",
        "ambiente_brasileiro": "sim",
        "legenda_com_erro": "na",
        "parece_pessoa_real": "nao",
        "marca_real": "nao",
        "estereotipo_ofensivo": "nao",
        "texto_com_erro_de_sentido": "na",
        "foco_unico_zona_segura": "na",
        "corresponde_ao_titulo": "na",
        "legenda_cobre_foco": "na", "boca_articula_fala": "nao", "corte_oculos_cabeca": "nao", "grotesco": "nao",
    }
    base.update(overrides)
    return base


def resposta(*cenas_, rodada=1):
    return json.dumps({"rodada": rodada, "cenas": list(cenas_)}, ensure_ascii=False)


class ValidacaoGemini(unittest.TestCase):
    def test_json_valido_com_as_cenas_esperadas(self):
        r = validar(resposta(cena("S01"), cena("S02")), ["S01", "S02"])
        self.assertEqual([x["id"] for x in json.loads(r)["cenas"]], ["S01", "S02"])

    def test_rejeita_cena_ausente(self):
        with self.assertRaisesRegex(ValueError, "cenas ausentes"):
            validar(resposta(cena("S01")), ["S01", "S02"])

    def test_rejeita_ids_esperados_duplicados(self):
        with self.assertRaisesRegex(ValueError, "ids esperados duplicados"):
            validar(resposta(cena("S01")), ["S01", "S01"])

    def test_rejeita_id_duplicado(self):
        with self.assertRaisesRegex(ValueError, "cenas duplicadas"):
            validar(resposta(cena("S01"), cena("S01"), cena("S02")), ["S01", "S02"])

    def test_rejeita_id_inesperado(self):
        with self.assertRaisesRegex(ValueError, "cenas inesperadas"):
            validar(resposta(cena("S01"), cena("S02")), ["S01"])

    def test_rejeita_valor_fora_do_vocabulario(self):
        with self.assertRaises(ValidationError):
            validar(resposta(cena("S01", marca_real="talvez")), ["S01"])

    def test_auditoria_nao_persiste_no_modo_calibracao(self):
        texto = resposta(cena("S01", legenda_com_erro="sim"))
        with patch.object(ag, "preparar_pranchas", return_value=["/tmp/S01.png"]), \
             patch.object(ag, "perguntar_gemini", return_value=(texto, "https://gemini.test/chat")) as perguntar, \
             patch.object(ag, "_persistir_erros_aceitaveis") as gravar:
            resultado = ag.auditar("PQBR-TEST", "teste", ["/private/frame.mp4"], ["FALA_PRIVADA_TESTE"], "BLOCO_PRIVADO_TESTE", persistir=False, transmitir_texto=False, titulo="TITULO_PRIVADO_TESTE")
        self.assertEqual(resultado.erros_aceitaveis, 1)
        self.assertFalse(resultado.persistido)
        self.assertEqual(perguntar.call_count, 2)
        self.assertFalse(resultado.texto_enviado)
        self.assertIsNone(resultado.bruto["metricas"]["imagem_corresponde_a_fala"])
        prompt = perguntar.call_args_list[0].args[1]
        self.assertNotIn("frame.mp4", prompt)
        self.assertNotIn("FALA_PRIVADA_TESTE", prompt)
        self.assertNotIn("BLOCO_PRIVADO_TESTE", prompt)
        self.assertNotIn("TITULO_PRIVADO_TESTE", prompt)
        gravar.assert_not_called()

    def test_sem_bloco_visual_nao_contabiliza_estilo_ou_personagem(self):
        texto = resposta(cena("S01", segue_estilo_declarado="nao", mesmo_personagem_do_bloco="nao"))
        with patch.object(ag, "preparar_pranchas", return_value=["/tmp/S01.png"]), \
             patch.object(ag, "perguntar_gemini", return_value=(texto, "https://gemini.test/chat")) as perguntar, \
             patch.object(ag, "_persistir_erros_aceitaveis") as gravar:
            resultado = ag.auditar("PQBR-TEST", "teste", ["/tmp/frame.png"], ["FALA_TESTE"], "",
                                   persistir=False, transmitir_texto=True, titulo="Podre de Rico")
        prompt = perguntar.call_args_list[0].args[1]
        self.assertIn("FALA_TESTE", prompt)
        self.assertIn("Podre de Rico", prompt)
        self.assertIn("Bloco visual não enviado", prompt)
        self.assertNotIn("descrição de personagem", prompt)
        self.assertIsNone(resultado.bruto["metricas"]["segue_estilo_declarado"])
        self.assertIsNone(resultado.bruto["metricas"]["mesmo_personagem_do_bloco"])
        self.assertFalse(resultado.persistido)
        gravar.assert_not_called()

    def test_persistencia_padrao_preservada(self):
        texto = resposta(cena("S01", legenda_com_erro="sim"))
        with patch.object(ag, "preparar_pranchas", return_value=["/tmp/S01.png"]), \
             patch.object(ag, "perguntar_gemini", return_value=(texto, "https://gemini.test/chat")), \
             patch.object(ag, "_persistir_erros_aceitaveis") as gravar:
            resultado = ag.auditar("PQBR-TEST", "teste", ["frame.mp4"], ["fala"], "[ESTILO] 2D")
        self.assertTrue(resultado.persistido)
        gravar.assert_called_once()
        self.assertEqual(len(gravar.call_args.args[0]), 1)
