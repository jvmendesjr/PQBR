"""t538: workflows ligados à ponte Telegram (WorkflowEnvironment time-skipping), incluindo reinício de worker.
Telegram e banco simulados; a decisão volta pelo mesmo caminho da produção (processar_callback + sinalizar_temporal)."""
import asyncio, unittest, uuid
from datetime import datetime, timezone
from temporalio import activity
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from pqbr.contratos.ponte_telegram import EventoCallbackTelegram, MensagemSaida, PedidoAprovacao, ReciboEntrega
from pqbr.workflows import acesso as A
from pqbr.workflows.contracts import EpisodioInput, OutboxEvento, RoteiroShort
from pqbr.workflows.ponte_telegram import RepositorioMemoria, processar_callback
from pqbr.workflows.telegram_bot import sinalizar_temporal
from pqbr.workflows.workflows import EpisodioWorkflow

REPO = RepositorioMemoria(); CHAMADAS: list = []; LIGADA = {"v": True}; AVISOS: list = []


@activity.defn(name="registrar_pedido_telegram")
async def f_registrar(p: PedidoAprovacao) -> None: CHAMADAS.append("registrar"); REPO.registrar_pedido(p)
@activity.defn(name="enfileirar_telegram")
async def f_enfileirar(m: MensagemSaida) -> str:
    CHAMADAS.append("enfileirar")
    if not LIGADA["v"]: return "desligado"
    return "novo" if REPO.enfileirar(m) else "existente"
@activity.defn(name="enviar_telegram")
async def f_enviar(chave: str) -> ReciboEntrega:
    CHAMADAS.append(("enviar", chave)); return ReciboEntrega(chave=chave, estado="enviado", tentativas=1, mensagem_id=1)
@activity.defn(name="enfileirar_avisos_telegram")
async def f_avisos() -> list[str]: CHAMADAS.append("avisos"); return list(AVISOS)
@activity.defn(name="gerar_roteiro")
async def f_roteiro(inp: EpisodioInput) -> RoteiroShort:
    from pqbr.workflows.activities import gerar_roteiro
    return await gerar_roteiro(inp)
@activity.defn(name="gravar_outbox")
async def f_outbox(ev: OutboxEvento) -> bool: return True
def _estado(servico, ok=True, pausado=False, nome=None):
    @activity.defn(name=nome or f"acesso_{servico}")
    async def f() -> A.EstadoAcesso: CHAMADAS.append(("acesso", servico)); return A.EstadoAcesso(servico=servico, ok=ok, pausado=pausado, motivo="x")
    return f
@activity.defn(name="acesso_resolvido")
async def f_resolvido(s: str) -> int: CHAMADAS.append(("resolvido", s)); return 0
@activity.defn(name="pedir_jose")
async def f_pedir(p: A.PedidoJose) -> int: CHAMADAS.append(("pedir", p.servico)); return 1
@activity.defn(name="registrar_evento")
async def f_evento(e: A.EventoAcesso) -> int: CHAMADAS.append(("evento", e.servico)); return 1

COMUNS = [f_registrar, f_enfileirar, f_enviar, f_avisos, f_roteiro, f_outbox]


class Ponte(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        global REPO
        REPO = RepositorioMemoria(); CHAMADAS.clear(); AVISOS.clear(); LIGADA["v"] = True
        self.env = await WorkflowEnvironment.start_time_skipping(data_converter=pydantic_data_converter)
        self.fila = f"t-{uuid.uuid4().hex[:8]}"

    async def asyncTearDown(self):
        await self.env.shutdown()

    def worker(self, extras=(), fila=None, wfs=(EpisodioWorkflow,)):
        # sem cache/sticky: cada tarefa é replay a partir do histórico (equivale a reiniciar o worker toda vez)
        return Worker(self.env.client, task_queue=fila or self.fila, workflows=list(wfs), activities=[*COMUNS, *extras],
                      max_cached_workflows=0)

    async def esperar(self, cond, n=200):
        for _ in range(n):
            if cond(): return
            await asyncio.sleep(0.05)
        self.fail("timeout esperando condição")

    async def test_pedido_vai_ao_telegram_e_callback_conclui_apos_reinicio_do_worker(self):
        wid = f"ep-{uuid.uuid4().hex[:6]}"
        inp = EpisodioInput(episodio_id="ep-t538", tema="por que o céu é azul", timer_segundos=1, falhas_simuladas=0, espera_aprovacao_segundos=3600)
        async with self.worker():
            h = await self.env.client.start_workflow(EpisodioWorkflow.run, inp, id=wid, task_queue=self.fila)
            await self.esperar(lambda: any(isinstance(c, tuple) and c[0] == "enviar" for c in CHAMADAS))
            self.assertEqual(await h.query("etapa"), "aguardando_aprovacao")
        # worker caiu e voltou: replay não reexecuta as activities da ponte
        (ref, pedido), = REPO.pedidos.items()
        self.assertEqual((pedido.workflow_id, pedido.etapa), (wid, "aguardando_aprovacao"))
        chave, = REPO.saida
        self.assertEqual(REPO.saida[chave]["m"].ref_pedido, ref)
        async with self.worker():
            ev = EventoCallbackTelegram(update_id=1, remetente_id="42", ref_pedido=ref, decisao="aprovar")
            r = await processar_callback(REPO, "42", ev, sinalizar_temporal(self.env.client))
            self.assertEqual(r.status, "sinalizado")
            res = await h.result()
        self.assertEqual(res.etapa, "concluido")
        self.assertEqual([c for c in CHAMADAS if c in ("registrar", "enfileirar")], ["registrar", "enfileirar"])
        r2 = await processar_callback(REPO, "42", ev, sinalizar_temporal(self.env.client))
        self.assertEqual(r2.status, "duplicado")

    async def test_saida_desligada_nao_envia(self):
        LIGADA["v"] = False
        inp = EpisodioInput(episodio_id="ep-t538b", tema="tema desligado", timer_segundos=1, falhas_simuladas=0, espera_aprovacao_segundos=5)
        async with self.worker():
            res = await self.env.client.execute_workflow(EpisodioWorkflow.run, inp, id=f"ep-{uuid.uuid4().hex[:6]}", task_queue=self.fila)
        self.assertEqual(res.etapa, "expirado_sem_aprovacao")
        self.assertFalse(any(isinstance(c, tuple) and c[0] == "enviar" for c in CHAMADAS))

    async def test_soak_automatico_nao_chama_ponte(self):
        inp = EpisodioInput(episodio_id="ep-t538c", tema="soak", timer_segundos=1, falhas_simuladas=0, aprovacao_automatica=True)
        async with self.worker():
            res = await self.env.client.execute_workflow(EpisodioWorkflow.run, inp, id=f"ep-{uuid.uuid4().hex[:6]}", task_queue=self.fila)
        self.assertEqual(res.etapa, "concluido"); self.assertNotIn("registrar", CHAMADAS)

    async def acessos(self, paperclip_pausado):
        AVISOS.extend(["acesso:7:202610250"])
        reg = [_estado("google_camofox"), _estado("notebooklm"), _estado("paperclip_cli", nome="acesso_paperclip", ok=False, pausado=paperclip_pausado),
               f_resolvido, f_pedir, f_evento]
        async with self.worker(wfs=(A.AcessosWorkflow,)), \
                   Worker(self.env.client, task_queue=A.FILA_CAMOFOX, activities=[reg[0]]), \
                   Worker(self.env.client, task_queue=A.FILA_NLM, activities=[reg[1]]), \
                   Worker(self.env.client, task_queue=A.FILA_REG, activities=reg[2:]):
            return await self.env.client.execute_workflow(A.AcessosWorkflow.run, id=f"ac-{uuid.uuid4().hex[:6]}", task_queue=self.fila)

    async def test_acessos_paperclip_pausado_nao_pede_e_avisos_saem(self):
        r = await self.acessos(True)
        self.assertTrue(r[2]["pausado"])
        self.assertNotIn(("pedir", "paperclip_cli"), CHAMADAS); self.assertNotIn(("evento", "paperclip_cli"), CHAMADAS)
        self.assertIn("avisos", CHAMADAS); self.assertIn(("enviar", "acesso:7:202610250"), CHAMADAS)

    async def test_acessos_paperclip_ativo_caido_continua_pedindo(self):
        await self.acessos(False)
        self.assertIn(("pedir", "paperclip_cli"), CHAMADAS)


class PaperclipConfig(unittest.TestCase):
    def test_config_padrao_ativo_e_flag(self):
        import json, os, tempfile
        self.assertFalse(A.paperclip_pausado())
        d = tempfile.mkdtemp(); p = os.path.join(d, "c.json")
        json.dump({"estado": "parado_proposital"}, open(p, "w")); self.assertTrue(A.paperclip_pausado(p))
        self.assertFalse(A.paperclip_pausado(os.path.join(d, "nada.json")))
