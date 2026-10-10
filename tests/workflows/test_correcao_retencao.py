"""TS-11 (correção autônoma) e TS-12 (retenção) no ambiente de teste do Temporal (tempo acelerado).
Rodar: PYTHONPATH=src python -m unittest discover -s tests/workflows -t ."""
import asyncio, unittest, uuid
from temporalio import activity
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from pqbr.workflows import correcao as C
from pqbr.workflows import manutencao as M

REGISTROS = []


@activity.defn(name="registrar_correcao")
async def registrar_falso(r):
    REGISTROS.append(r)


@activity.defn(name="reter_consumo")
async def reter_falso(p: M.PedidoRetencao) -> M.ResultadoRetencao:
    return M.ResultadoRetencao(corte_bruto=p.hoje, corte_resumo=p.hoje, grupos_resumidos=1, brutas_apagadas=2, resumo_apagado=0)


class Fluxos(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.env = await WorkflowEnvironment.start_time_skipping(data_converter=pydantic_data_converter)
        self.fila = f"t-{uuid.uuid4().hex[:8]}"
        self.w = Worker(self.env.client, task_queue=self.fila,
                        workflows=[C.CorrecaoAutonomaWorkflow, M.RetencaoConsumoWorkflow],
                        activities=[C.triagem_jev, C.intervir_agente, C.verificar_jev, registrar_falso, reter_falso])
        await self.w.__aenter__()
        REGISTROS.clear()

    async def asyncTearDown(self):
        await self.w.__aexit__(None, None, None)
        await self.env.shutdown()

    async def corrigir(self, **kw):
        sim = kw.pop("sim", None)
        p = C.PedidoCorrecao(ferramenta=kw.pop("ferramenta", "camofox"), passo=kw.pop("passo", "clicar em Agendar"),
                             erro="SiteMudou: botão não encontrado", simulacao=sim)
        return await self.env.client.execute_workflow(C.CorrecaoAutonomaWorkflow.run, p, id=f"c-{uuid.uuid4().hex[:6]}", task_queue=self.fila)

    async def test_corrige_na_primeira(self):
        r = await self.corrigir(sim=C.Simulacao())
        self.assertEqual((r.resultado, r.tentativas, r.chamar_jose), ("corrigido", 1, False))
        self.assertTrue(r.proposta_script)

    async def test_corrige_na_terceira(self):
        r = await self.corrigir(sim=C.Simulacao(intervencoes=[False, False, True]))
        self.assertEqual((r.resultado, r.tentativas), ("corrigido", 3))

    async def test_verificacao_reprova_esgota(self):
        r = await self.corrigir(sim=C.Simulacao(verificacoes=[False]))
        self.assertEqual((r.resultado, r.tentativas, r.chamar_jose), ("esgotado", 3, True))

    async def test_sensivel_sem_agente(self):
        r = await self.corrigir(passo="fazer login de novo", sim=C.Simulacao())
        self.assertEqual((r.resultado, r.tentativas, r.chamar_jose), ("sensivel", 0, True))
        r = await self.corrigir(sim=C.Simulacao(triagem="sensivel"))
        self.assertEqual(r.resultado, "sensivel")

    async def test_conta_divergente_para(self):
        r = await self.corrigir(sim=C.Simulacao(conta_confere=False))
        self.assertEqual((r.resultado, r.motivo), ("sensivel", "conta/sessão divergente"))

    async def test_sem_backend_nao_executa(self):
        from temporalio.client import WorkflowFailureError
        with self.assertRaises(WorkflowFailureError):
            await self.corrigir(sim=None)

    async def test_retencao_hoje_fortaleza(self):
        r = await self.env.client.execute_workflow(M.RetencaoConsumoWorkflow.run, None, id="ret", task_queue=self.fila)
        self.assertEqual(r.brutas_apagadas, 2)
        self.assertRegex(r.corte_bruto, r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(len(REGISTROS), 0)


class Relatorio(unittest.TestCase):
    def test_secao_consumo(self):
        hoje = [dict(modelo="gemini", tipo_acao="roteiro", chamadas=10, falhas=1, tokens_entrada=100, tokens_saida=50, custo_estimado_micro_usd=2_000_000),
                dict(modelo="jev", tipo_acao="jev_triagem", chamadas=4, falhas=0)]
        semana = [dict(chamadas=7)] * 7
        s = M.secao_consumo(hoje, semana)
        self.assertIn("14 chamadas, 1 falhas, US$ 2.00", s)
        self.assertIn("+100%", s)
        self.assertIn("- gemini: 10 chamadas", s)


if __name__ == "__main__":
    unittest.main()
