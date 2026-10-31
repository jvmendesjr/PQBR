"""TS-01 / V4: grade, 3 barreiras, R10, polêmica; teste do incidente de 08/10 (F5-01)."""
import csv, unittest
from datetime import date
from pathlib import Path
from pqbr.pipeline.grade import (Candidato, checar_repeticao, montar_grade, normalizar, pontuar_polemica,
                                 bloqueio_absoluto, grade_reaproveitada)

CSV = Path(__file__).resolve().parents[2] / "db" / "seeds" / "temas-publicados.csv"
PUBLICADOS = [r["titulo_publicado"] for r in csv.DictReader(open(CSV, encoding="utf-8-sig"))]


class Grade(unittest.TestCase):
    def test_normalizar(self):
        self.assertEqual(normalizar("Por Que  a Gente Só Acorda?"), "por que a gente so acorda")

    def test_barreira_exata_e_variacao(self):
        t = PUBLICADOS[0]
        self.assertEqual(checar_repeticao(t.upper(), PUBLICADOS).barreira, "exata")
        v = checar_repeticao("Por que a gente só acorda quando alguém desliga a TV?", PUBLICADOS)
        self.assertTrue(v.repetido, v)
        self.assertFalse(checar_repeticao("Por que todo mundo guarda sacola dentro de sacola?", ["Por que o chinelo some?"]).repetido)

    def test_variacoes_do_contrato(self):
        # R10 cita: chuveiro elétrico x tomada do chuveiro; sacola de sacolas x sacola bonita
        self.assertTrue(checar_repeticao("Por que o chuveiro elétrico dá choque?", ["Por que a tomada do chuveiro elétrico esquenta?"]).repetido)

    def test_bloqueio_e_polemica(self):
        self.assertEqual(bloqueio_absoluto("Por que o Bolsonaro fala assim?"), "politica_partidaria")
        self.assertIsNone(bloqueio_absoluto("Por que a gente guarda pote de sorvete?"))
        self.assertTrue(pontuar_polemica("x tema", {"divisao_opiniao": 100, "estereotipo": 100, "regionalismo": 100}).aguarda_jose)
        p = pontuar_polemica("Por que a gente guarda pote de sorvete?", {"divisao_opiniao": 60})
        self.assertTrue(p.entra_na_grade)

    def test_incidente_0810(self):
        """08/10: o fluxo não iniciou, a grade do dia 7 foi reaproveitada e 3 de 4 temas eram repetidos."""
        d8 = date(2026, 10, 8)
        candidatos = [Candidato(PUBLICADOS[1], "em_alta"), Candidato(PUBLICADOS[2], "em_alta"),
                      Candidato(PUBLICADOS[3].lower(), "perene"),
                      Candidato("Por que brasileiro aplaude quando o avião pousa?", "em_alta"),
                      Candidato("Por que a gente fala 'vou ali' e demora duas horas?", "em_alta"),
                      Candidato("Por que toda casa tem uma gaveta de fios velhos?", "perene"),
                      Candidato("Por que a gente esquenta comida no forno de micro-ondas e esquece?", "em_alta"),
                      Candidato(PUBLICADOS[1], "em_alta", sugerido_por_jose=True)]
        g, recusas = montar_grade(d8, candidatos, PUBLICADOS)
        self.assertEqual(len(g.itens), 4)
        self.assertTrue(all(i.data == d8 for i in g.itens))
        self.assertFalse(grade_reaproveitada(g, d8))
        for i in g.itens:
            self.assertFalse(checar_repeticao(i.tema, PUBLICADOS).repetido, i.tema)
        self.assertEqual(sum(r.motivo.startswith("r10") or r.motivo == "duplicado_no_lote" for r in recusas), 4)
        self.assertEqual(g.itens[-1].fonte, "perene")
        self.assertEqual([i.janela for i in g.itens], ["11:40", "14:40", "18:35", "21:15"])

    def test_polemica_alta_aguarda(self):
        g, _ = montar_grade(date(2026, 10, 9), [Candidato("Por que carioca e paulista brigam pelo biscoito?", "em_alta",
                            {"divisao_opiniao": 100, "regionalismo": 100, "estereotipo": 90})], [])
        self.assertEqual(g.itens[0].status, "aguardando_jose")


    def test_mistura_configuravel_t378(self):
        per = ["Por que dizemos podre de rico?", "De onde vem o santo do pau oco?", "Por que falamos onde Judas perdeu as botas?", "Por que chamamos de conto do vigário?"]
        alta = ["Por que o pix caiu ontem?", "Por que o calor bateu recorde?", "Por que a novela parou o país?", "Por que o jogo atrasou?"]
        cands = [Candidato(t, "perene") for t in per] + [Candidato(t, "em_alta") for t in alta]
        g, _ = montar_grade(date(2026, 12, 1), cands, [], fracao_perene=0.8)
        self.assertEqual(sum(i.fonte == "perene" for i in g.itens), 3)


if __name__ == "__main__":
    unittest.main()
