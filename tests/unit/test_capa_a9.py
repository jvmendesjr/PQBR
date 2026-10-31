"""F7-02/A9: seleção determinística de quadros, sem mídia ou serviços externos."""
import json
import subprocess
import unittest
from unittest.mock import patch

from pqbr.pipeline import capa
from pqbr.pipeline.capa import CandidatoCapa


def candidato(nome, ok, contraste):
    return CandidatoCapa(arquivo=nome, largura=1080, altura=1920, luma=100.0,
                         contraste=contraste, borrado=3.0, ok=ok,
                         motivos=[] if ok else ["métrica reprovada"])


class GateA9(unittest.TestCase):
    def test_prefere_primeiro_quadro_aprovado_na_ordem_de_selecao(self):
        first = candidato("S01", False, 40)
        middle = candidato("S02", True, 110)
        last = candidato("S03", True, 35)
        with patch.object(capa, "medir", side_effect=[first, middle, last]):
            escolhido, todos = capa.escolher(["S01", "S02", "S03"])
        self.assertEqual(escolhido.arquivo, "S03")
        self.assertEqual(len(todos), 3)

    def test_sem_candidato_que_passe_retorna_none_sem_bloquear_video(self):
        candidatos = [candidato("S01", False, 20), candidato("S02", False, 25)]
        with patch.object(capa, "medir", side_effect=candidatos):
            escolhido, todos = capa.escolher(["S01", "S02"])
        self.assertIsNone(escolhido)
        self.assertEqual(len(todos), 2)

    def medir_com_log(self, log):
        probe = subprocess.CompletedProcess([], 0, stdout=json.dumps({"streams": [{"width": 1080, "height": 1920}]}), stderr="")
        ffmpeg = subprocess.CompletedProcess([], 0, stdout="", stderr=log)
        with patch.object(capa.subprocess, "run", side_effect=[probe, ffmpeg]):
            return capa.medir("frame.png")

    def test_blurdetect_ausente_nao_e_aprovado(self):
        c = self.medir_com_log("lavfi.signalstats.YAVG=100\nlavfi.signalstats.YLOW=10\nlavfi.signalstats.YHIGH=200")
        self.assertFalse(c.ok)
        self.assertIsNone(c.borrado)
        self.assertIn("nitidez indisponível", c.motivos[0])

    def test_quadro_com_medidas_validas_passa(self):
        c = self.medir_com_log("lavfi.signalstats.YAVG=100\nlavfi.signalstats.YLOW=10\nlavfi.signalstats.YHIGH=200\nlavfi.blur=8.0")
        self.assertTrue(c.ok)
        self.assertEqual(c.borrado, 8.0)

    def test_blur_maior_que_limite_e_metricamente_rejeitado(self):
        c = self.medir_com_log("lavfi.signalstats.YAVG=100\nlavfi.signalstats.YLOW=10\nlavfi.signalstats.YHIGH=200\nlavfi.blur=10.0")
        self.assertFalse(c.ok)
        self.assertTrue(any("borrado" in motivo for motivo in c.motivos))
