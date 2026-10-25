"""Repositório Postgres da ponte Telegram (migração 0018). Mesma semântica do `RepositorioMemoria`.
Escreve como `pqbr_app` (RLS). `conectar` devolve uma conexão psycopg (padrão: `storage.banco.conectar`)."""
from __future__ import annotations
from typing import Callable
from ..contratos.ponte_telegram import EventoCallbackTelegram, MensagemSaida, PedidoAprovacao, ReciboEntrega
from .ponte_telegram import novo_token


class RepositorioPostgres:
    def __init__(self, conectar: Callable | None = None):
        if conectar is None:
            from ..storage.banco import conectar as _c
            conectar = _c
        self._conectar = conectar

    def _um(self, sql, params=()):
        with self._conectar() as c:
            cur = c.execute(sql, params)
            row = cur.fetchone() if cur.description else None
            c.commit()
            return row

    def enfileirar(self, m: MensagemSaida) -> bool:
        return self._um("insert into pqbr.saida_telegram (chave, classe, texto, ref_pedido) values (%s,%s,%s,%s)"
                        " on conflict (chave) do nothing returning chave", (m.chave, m.classe, m.texto, m.ref_pedido)) is not None

    def reivindicar(self, chave):
        claim = novo_token()
        r = self._um("update pqbr.saida_telegram set estado='enviando', tentativas=tentativas+1, claim_token=%s,"
                     " claim_ate=now()+interval '2 min' where chave=%s and estado in ('pendente','falhou') returning tentativas",
                     (claim, chave))
        return None if r is None else (claim, r[0], r[0] > 1)

    def reenviar_incerto(self, chave):
        self._um("update pqbr.saida_telegram set estado='falhou' where chave=%s and estado='incerto'", (chave,))

    def vencer_claims(self) -> int:
        """Observador: claim vencido em 'enviando' vira 'incerto' (nunca reenvio automático)."""
        with self._conectar() as c:
            n = c.execute("update pqbr.saida_telegram set estado='incerto', claim_token=null, motivo='claim_vencido'"
                          " where estado='enviando' and claim_ate < now()").rowcount
            c.commit(); return n

    def confirmar(self, chave, claim, mid):
        with self._conectar() as c:
            n = c.execute("update pqbr.saida_telegram set estado='enviado', mensagem_id=%s, enviado_em=now(), claim_token=null"
                          " where chave=%s and claim_token=%s", (mid, chave, claim)).rowcount
            if n:
                c.execute("update pqbr.revisao_humana set avisado_em=now() where chave_saida=%s and avisado_em is null", (chave,))
            c.commit()

    def marcar(self, chave, claim, estado, motivo):
        self._um("update pqbr.saida_telegram set estado=%s, motivo=%s, claim_token=null where chave=%s and claim_token=%s",
                 (estado, motivo[:200], chave, claim))

    def mensagem(self, chave):
        r = self._um("select chave, classe, texto, ref_pedido from pqbr.saida_telegram where chave=%s", (chave,))
        return MensagemSaida(chave=r[0], classe=r[1], texto=r[2], ref_pedido=r[3])

    def recibo(self, chave):
        r = self._um("select estado, tentativas, mensagem_id, motivo from pqbr.saida_telegram where chave=%s", (chave,))
        return ReciboEntrega(chave=chave, estado=r[0], tentativas=r[1], mensagem_id=r[2], motivo=r[3])

    def registrar_pedido(self, p: PedidoAprovacao):
        self._um("insert into pqbr.pedido_aprovacao (token, workflow_id, etapa, tarefa, expira_em) values (%s,%s,%s,%s,%s)"
                 " on conflict (token) do nothing", (p.token, p.workflow_id, p.etapa, p.tarefa, p.expira_em))

    def pedido(self, ref):
        r = self._um("select token, workflow_id, etapa, tarefa, expira_em from pqbr.pedido_aprovacao where token=%s", (ref,))
        return None if r is None else PedidoAprovacao(token=r[0], workflow_id=r[1], etapa=r[2], tarefa=r[3], expira_em=r[4])

    def registrar_entrada(self, e: EventoCallbackTelegram) -> str:
        with self._conectar() as c:
            if c.execute("select 1 from pqbr.entrada_telegram where update_id=%s", (e.update_id,)).fetchone():
                return "update_repetido"
            r = c.execute("insert into pqbr.entrada_telegram (update_id, ref_pedido, decisao) values (%s,%s,%s)"
                          " on conflict do nothing returning update_id", (e.update_id, e.ref_pedido, e.decisao)).fetchone()
            c.commit()
            return "novo" if r else "token_decidido"

    def atualizar_entrada(self, ref, status, tentativas, motivo):
        self._um("update pqbr.entrada_telegram set status=%s, tentativas=%s, motivo=%s where ref_pedido=%s",
                 (status, tentativas, motivo[:200], ref))

    def abrir_ticket(self, chave, resumo):
        self._um("insert into pqbr.tickets (titulo, localizacao, falha) select %s, %s, %s"
                 " where not exists (select 1 from pqbr.tickets where localizacao=%s)",
                 ("ponte Telegram", chave[:200], resumo[:500], chave[:200]))
