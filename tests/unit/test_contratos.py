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


class ContratosT436(unittest.TestCase):
    def test_veredito_vocabulario_do_auditor(self):
        from pqbr.contratos import VEREDITOS
        from pqbr.pipeline.auditor_visual import ORDEM
        assert set(VEREDITOS) == set(ORDEM)
        VereditoAuditor(veredito="aprova_com_ressalva", motivos=["legenda"], rodadas=2)
        with self.assertRaises(ValidationError):
            VereditoAuditor(veredito="ressalva", motivos=["x"], rodadas=2)

    def test_tema_pendente(self):
        from pqbr.contratos import TemaPendente
        TemaPendente(slug="podre-de-rico", tema="Podre de rico", tema_normalizado="podre de rico", categoria="expressao")
        with self.assertRaises(ValidationError):
            TemaPendente(slug="natal", tema="Natal", tema_normalizado="natal", categoria="sazonal")
        with self.assertRaises(ValidationError):
            TemaPendente(slug="x-y", tema="xyz", tema_normalizado="xyz", categoria="expressao", status="aprovado", fontes=["a"])

    def test_erro_aceitavel_bate_com_auditor(self):
        import json as _j
        from pqbr.contratos import ErroAceitavel
        from pqbr.pipeline import auditor_visual as av
        r = {"veredito": "aprova_com_ressalva", "erros_aceitaveis": [("S01", "legenda_com_erro")], "metricas": {}, "rodada_unica": False}
        for l in av.linhas_erros_aceitaveis(r, episodio_codigo="PQBR-EP0001"):
            ErroAceitavel(**{**l, "evidencia": _j.loads(l["evidencia"])})
        with self.assertRaises(ValidationError):
            ErroAceitavel(categoria="legenda", chave="x1", descricao="abc", veredito_auditor="reprova", tema_slug="ab")


class ContratosT437(unittest.TestCase):
    CANON = ("Ilustração 2D plana de cartum, traço preto nítido, cores chapadas quentes. Proibido: fotorrealismo, 3D, "
             "rosto de pessoa real, texto escrito dentro das imagens. Formato vertical 9:16, sem fotorrealismo.")

    def _bv(self, estilo, **kw):
        from pqbr.contratos import BlocoVisual, CenaVisual
        c = CenaVisual(fala="oi", acao="acena", enquadramento="plano médio", ambiente="cozinha")
        return BlocoVisual(estilo=estilo, personagem="adulto de 35 anos, camiseta verde", cenas=[c, c], **kw)

    def test_bloco_visual_3d_realismo(self):
        self._bv(self.CANON)
        with self.assertRaises(ValidationError):
            self._bv("Animação 3D estilo Pixar com iluminação suave e personagem fofo")
        with self.assertRaises(ValidationError):
            self._bv("Ilustração 2D mas com rosto fotorrealista e pele detalhada")
        self._bv("Animação 3D estilo Pixar com iluminação suave e personagem fofo", pedido_3d_ou_realista=True)
        with self.assertRaises(ValidationError):
            self._bv("Desenho de cartum plano, traço preto, cores chapadas")   # sem 2D declarado

    def test_jev_email(self):
        from pqbr.contratos import ClassificacaoEmailYouTube as E
        E(categoria="upload_status", gravidade="informativo", acao="registrar", confianca=0.9)
        with self.assertRaises(ValidationError):
            E(categoria="strike", gravidade="critico", acao="abrir_ticket", confianca=0.9)
        with self.assertRaises(ValidationError):
            E(categoria="claim", gravidade="informativo", acao="registrar", confianca=0.9)
        with self.assertRaises(ValidationError):
            E(categoria="other", gravidade="informativo", acao="ignorar", confianca=1.2)
        with self.assertRaises(ValidationError):
            E(categoria="other", gravidade="informativo", acao="ignorar", confianca=0.5, extra=1)

    def test_jev_popup(self):
        from pqbr.contratos import ClassificacaoPopupCamofox as P
        P(categoria="cookie_consent", acao="aceitar", confianca=0.8)
        for kw in ({"categoria": "captcha", "acao": "fechar"}, {"categoria": "login_required", "acao": "fechar"},
                   {"categoria": "promo", "acao": "aceitar"}):
            with self.assertRaises(ValidationError):
                P(confianca=0.8, **kw)

    def test_seo(self):
        from pqbr.contratos import PacoteSEO
        p = PacoteSEO(titulo="Por que a gente fala podre de rico?", descricao="A origem da expressão. #curiosidades",
                      tags=["expressões brasileiras", "curiosidades"], hashtags=["#shorts", "#curiosidades", "#brasil"])
        assert p.snippet_status()["status"]["containsSyntheticMedia"] is False and p.idioma == "pt-BR"
        with self.assertRaises(ValidationError):
            PacoteSEO(titulo="Título ok aqui", descricao="descrição ok", hashtags=["shorts", "#a1", "#b2"])
        with self.assertRaises(ValidationError):
            PacoteSEO(titulo="Título ok aqui", descricao="descrição ok", hashtags=["#ab", "#cd", "#ef"], tags=["x" * 60] * 9)
        with self.assertRaises(ValidationError):
            PacoteSEO(titulo="x" * 101, descricao="descrição ok", hashtags=["#ab", "#cd", "#ef"])
