"""TS-01/TS-02 (contratos, F3-01). Rodar: PYTHONPATH=src python -m unittest discover -s tests -t ."""
import unittest
from datetime import date, datetime, timezone
from pydantic import ValidationError
from pqbr.contratos import (RoteiroShort, DecisaoRepeticao, PontuacaoPolemica, VereditoAuditor,
    PropostaAgente, TicketManutencao, Falha, GradeDiaria, ItemGrade, RegistroConsumo, CTA)

BLOCO = dict(estilo="ilustração 2D plana de cartum, traço preto grosso, cores chapadas quentes",
             personagem="homem de ~40 anos, magro, cabelo grisalho curto, camiseta verde, bigode, expressão curiosa",
             cenas=[dict(fala="Por que a gente fala isso?", acao="ele olha a TV desligada", enquadramento="plano médio", ambiente="sala brasileira, sofá, TV de tubo, noite"),
                    dict(fala="Comenta aí", acao="ele volta ao sofá", enquadramento="plano aberto", ambiente="mesma sala, noite")])
FALAS = ["Por que a gente desliga a TV e acorda na hora?"] + ["O corpo sabe que o barulho sumiu e estranha o silêncio da sala."] * 8 + [CTA]


class Contratos(unittest.TestCase):
    def roteiro(self, **kw):
        base = dict(episodio_id="ep-0001", titulo="Por que acordamos sem a TV?", falas=FALAS, entidades_cena=["sofá", "TV"], bloco_visual=BLOCO)
        base.update(kw); return RoteiroShort(**base)

    def test_roteiro_valido(self):
        r = self.roteiro()
        self.assertTrue(15 <= r.duracao_estimada_s <= 180)

    def test_roteiro_cta_nome_comentario_duracao(self):
        for falas in ([*FALAS[:-1], "Segue a gente"], ["Zé: oi", *FALAS[1:]],
                      [*FALAS[:-1], "Comenta aí embaixo", CTA], ["Oi.", CTA]):
            with self.assertRaises(ValidationError):
                self.roteiro(falas=falas)

    def test_extra_proibido(self):
        with self.assertRaises(ValidationError):
            self.roteiro(nome_personagem="x")

    def test_repeticao_coerente(self):
        DecisaoRepeticao(repetido=True, barreira="exata", confianca=1)
        with self.assertRaises(ValidationError):
            DecisaoRepeticao(repetido=True, barreira="nenhuma", confianca=1)

    def test_polemica(self):
        self.assertTrue(PontuacaoPolemica(valor=76).aguarda_jose)
        self.assertTrue(PontuacaoPolemica(valor=60).entra_na_grade)
        self.assertFalse(PontuacaoPolemica(valor=10, bloqueio_absoluto=True).entra_na_grade)
        with self.assertRaises(ValidationError):
            PontuacaoPolemica(valor=101)

    def test_auditor_motivo(self):
        with self.assertRaises(ValidationError):
            VereditoAuditor(veredito="reprova", rodadas=1)
        with self.assertRaises(ValidationError):
            VereditoAuditor(veredito="aprova", rodadas=4)

    def test_proposta(self):
        PropostaAgente(agente="prod-analista", tipo="parametro", alvo="parametro", chave="janela_3",
                       valor_proposto="18:40", justificativa="pico de retenção 18:40")
        with self.assertRaises(ValidationError):
            PropostaAgente(agente="X!", tipo="parametro", alvo="parametro", chave="a", valor_proposto="b", justificativa="ccccc")

    def test_ticket_ordem(self):
        f = Falha(evidencia="timeout no upload", horario=datetime.now(timezone.utc))
        with self.assertRaises(ValidationError):
            TicketManutencao(localizacao="pqbr/publisher", falha=f, correcoes_sugeridas=["x"], aprovacao_merge=True)

    def test_grade_incidente_0810(self):
        d = date(2026, 10, 8)
        with self.assertRaises(ValidationError):
            GradeDiaria(data=d, itens=[ItemGrade(data=date(2026, 10, 7), janela="11:40", tema="abc tema", polemica=50, fonte="perene")])

    def test_consumo(self):
        RegistroConsumo(provedor="google", modelo="gemini", tipo_acao="roteiro", sucesso=True, tokens_entrada=10)
        with self.assertRaises(ValidationError):
            RegistroConsumo(provedor="google", modelo="g", tipo_acao="inventado", sucesso=True)


if __name__ == "__main__":
    unittest.main()


class BlocoVisualT(unittest.TestCase):
    def test_bloco_sem_2d_falha(self):
        from pqbr.contratos import BlocoVisual
        with self.assertRaises(Exception):
            BlocoVisual(**{**BLOCO, "estilo": "fotografia realista de um homem na sala"})
