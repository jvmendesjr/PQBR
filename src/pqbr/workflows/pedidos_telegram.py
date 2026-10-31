"""Pedidos ao José (acesso/aviso) → outbox `pqbr.saida_telegram` (rascunho t536, conserto do avisado_em).

Antes: marcava `avisado_em` ANTES de imprimir; se o consumidor (cron Hermes) falhasse, o pedido ficava
"avisado" sem entrega. Agora: enfileira com chave idempotente por item e janela de 6 h e liga
`revisao_humana.chave_saida`; `avisado_em` só é gravado quando a activity `enviar_telegram` confirma a
entrega (ver ponte_telegram.py / migração 0018). Formatação pura (testada); nunca imprime segredo."""
from __future__ import annotations
from datetime import datetime, timezone


def formatar(linhas: list[tuple]) -> str:
    if not linhas: return ""
    out = ["PQBR — acessos:"]
    for i, ref, acao, cam in linhas:
        motivo = (cam or {}).get("motivo", "") if isinstance(cam, dict) else ""
        out.append(f"#{i} {ref.replace('acesso:', 'acesso ')}: {acao}" + (f" (motivo: {motivo[:120]})" if motivo else ""))
    out.append("Responda aqui pelo Telegram.")
    return "\n".join(out)


def chave_aviso(row_id: int, agora: datetime) -> str:
    """Uma chave por item e janela de 6 h: o lembrete de 6 h é outra mensagem, o reenvio da mesma não."""
    a = agora.astimezone(timezone.utc)
    return f"acesso:{row_id}:{a:%Y%m%d}{a.hour // 6}"


def enfileirar(c, agora: datetime | None = None) -> list[str]:
    """Só grava na outbox (mesma transação); quem envia e marca avisado_em é a activity."""
    from ..seguranca.barreira import exigir_limpo
    agora = agora or datetime.now(timezone.utc)
    rows = c.execute("select id, item_ref, observacao_jose, caminhos_tentados from pqbr.revisao_humana where (status = 'pendente' and (avisado_em is null or avisado_em < now() - interval '6 hours'))"
                     " or (item_ref like 'aviso:%%' and avisado_em is null) order by id").fetchall()
    chaves = []
    for r in rows:
        txt = formatar([r]); exigir_limpo(txt, "telegram"); k = chave_aviso(r[0], agora)
        c.execute("insert into pqbr.saida_telegram (chave, classe, texto) values (%s, 'pedido_acesso', %s) on conflict (chave) do nothing", (k, txt))
        c.execute("update pqbr.revisao_humana set chave_saida = %s where id = %s", (k, r[0]))
        chaves.append(k)
    c.commit()
    return chaves


def main() -> None:
    raise SystemExit("t536: saída por stdout aposentada; use enfileirar() + activity enviar_telegram (migração 0018 não aplicada)")


if __name__ == "__main__":
    main()
