"""Adaptador MotorIntelectual → NotebookLM (notebooklm-py PQBR, perfil pqbr, sessão do Camofox 9387).
Regras: caderno EFÊMERO "Short - <sessao>" (nunca mestre/raiz: MESTRES_PROIBIDOS), persona antes de tudo,
contexto como fonte, nunca `ask --new`, contador diário + quota. Sem re-login headless e sem keepalive poke
(NOTEBOOKLM_DISABLE_KEEPALIVE_POKE=1, NOTEBOOKLM_HEADLESS_REAUTH=0 forçados aqui e no unit)."""
from __future__ import annotations
import asyncio, os
from . import PedidoMotor, RespostaMotor

os.environ["NOTEBOOKLM_DISABLE_KEEPALIVE_POKE"] = "1"
os.environ["NOTEBOOKLM_HEADLESS_REAUTH"] = "0"


class MotorNotebookLM:
    nome = "notebooklm"

    def consultar(self, pedido: PedidoMotor) -> RespostaMotor:
        return asyncio.run(self.aconsultar(pedido))

    async def aconsultar(self, pedido: PedidoMotor) -> RespostaMotor:
        from ..workflows import notebooklm as n
        await n.nlm_checar_saldo("chat")
        cad = await n.nlm_caderno(pedido.sessao)              # sem código → efêmero "Short - <sessao>", reusa por título
        if cad in n.MESTRES_PROIBIDOS: raise RuntimeError("caderno mestre proibido")
        await n.nlm_persona(cad)
        fontes = []
        if pedido.contexto:
            fontes.append(await n.nlm_fonte(cad, f"{pedido.sessao}-{pedido.tarefa}", pedido.contexto))
        if pedido.pesquisa_web:
            await n.nlm_pesquisa_web(cad, pedido.pesquisa_web)
        txt = await n.nlm_perguntar(cad, pedido.pergunta)
        return RespostaMotor(motor=self.nome, sessao_id=cad, texto=txt[:20000],
                             meta={"titulo": f"Short - {pedido.sessao}", "fontes": fontes})
