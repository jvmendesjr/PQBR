"""TS-02/TS-04 (F5-02): grade do dia, episódio, vigia de prazo — tempo acelerado, sem publicar."""
import unittest, uuid
from datetime import date, datetime, timedelta, timezone
from temporalio.client import WorkflowFailureError
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from pqbr.contratos import ItemGrade
from pqbr.workflows import producao as P

FUSO = timezone(timedelta(hours=-3))
PUB = ["Por Que a Gente Só Acorda Quando Desligam a TV?", "Por que todo brasileiro guarda feijão no pote de sorvete?"]
CANDS = [(PUB[0], "em_alta"), ("Por que brasileiro aplaude quando o avião pousa?", "em_alta"),
         ("Por que a gente fala 'vou ali' e demora duas horas?", "em_alta"), (PUB[1].upper(), "perene"),
         ("Por que toda casa tem uma gaveta de fios velhos?", "perene"), ("Por que o brasileiro dá tchau três vezes na porta?", "em_alta")]


class Producao(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.env = await WorkflowEnvironment.start_time_skipping(data_converter=pydantic_data_converter)
        self.fila = f"p-{uuid.uuid4().hex[:8]}"
        self.w = Worker(self.env.client, task_queue=self.fila,
                        workflows=[P.GradeDiariaWorkflow, P.EpisodioProducaoWorkflow], activities=P.ATIVIDADES)
        await self.w.__aenter__()

    async def asyncTearDown(self):
        await self.w.__aexit__(None, None, None); await self.env.shutdown()

    def run_(self, wf, arg):
        return self.env.client.execute_workflow(wf, arg, id=f"w-{uuid.uuid4().hex[:6]}", task_queue=self.fila)

    def item(self, horas=6, **kw):
        t = (datetime.now(FUSO) + timedelta(hours=horas))
        jan = "21:15"
        d = t.date() if t.strftime("%H:%M") < jan else t.date() + timedelta(days=1)
        return ItemGrade(data=d, janela=jan, tema="Por que a gente guarda sacola?", polemica=55, fonte="perene", **kw)

    async def test_grade_do_dia_sem_repetidos(self):
        g = await self.run_(P.GradeDiariaWorkflow.run, P.PedidoGrade(dia=date(2026, 10, 8), simulacao=P.SimProducao(candidatos=CANDS, publicados=PUB)))
        self.assertEqual(g.data, date(2026, 10, 8))
        self.assertEqual(len(g.itens), 4)
        self.assertNotIn(PUB[0], [i.tema for i in g.itens])
        self.assertEqual(g.itens[-1].fonte, "perene")

    async def test_episodio_agendado(self):
        r = await self.run_(P.EpisodioProducaoWorkflow.run, P.PedidoEpisodio(item=self.item(), codigo="PQBR-EP0001", simulacao=P.SimProducao()))
        self.assertEqual(r.estado, "agendado")

    async def test_reprovado_nunca_publica(self):
        r = await self.run_(P.EpisodioProducaoWorkflow.run, P.PedidoEpisodio(item=self.item(), codigo="PQBR-EP0002", simulacao=P.SimProducao(veredito="reprova")))
        self.assertEqual(r.estado, "reprovado")

    async def test_vigia_prazo(self):
        # E2E 12/10: o prazo depende do relógio (janela 21:15 de hoje ou de amanhã). O atraso passa a ser calculado a partir
        # da própria janela do item (sempre 1 h depois dela), então o teste não depende mais da hora em que roda.
        it = self.item()
        jan = datetime.combine(it.data, datetime.strptime(it.janela, "%H:%M").time(), FUSO)
        atraso = int((jan - datetime.now(FUSO)).total_seconds()) + 3600
        r = await self.run_(P.EpisodioProducaoWorkflow.run, P.PedidoEpisodio(item=self.item(), codigo="PQBR-EP0003", simulacao=P.SimProducao(atraso_producao_s=atraso, tem_reserva=False)))
        self.assertEqual(r.estado, "cancelado")
        r = await self.run_(P.EpisodioProducaoWorkflow.run, P.PedidoEpisodio(item=self.item(), codigo="PQBR-EP0004", simulacao=P.SimProducao(atraso_producao_s=atraso)))
        self.assertEqual(r.estado, "reserva_usada")

    async def test_polemica_espera_jose(self):
        r = await self.run_(P.EpisodioProducaoWorkflow.run, P.PedidoEpisodio(item=self.item(status="aguardando_jose"), codigo="PQBR-EP0005", simulacao=P.SimProducao()))
        self.assertEqual(r.estado, "aguardando_jose")

    async def test_sem_simulacao_nao_publica_nem_chama_notebooklm(self):
        with self.assertRaises(WorkflowFailureError):
            await self.run_(P.EpisodioProducaoWorkflow.run, P.PedidoEpisodio(item=self.item(), codigo="PQBR-EP0006"))


if __name__ == "__main__":
    unittest.main()
