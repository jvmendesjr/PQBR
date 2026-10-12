"""Saída do cron no-agent `pqbr-pedidos-jose` (Hermes pqbr → Telegram): pedidos novos e lembrete a cada 6 h. Marca avisado_em.
Puro na formatação (testado); nunca imprime segredo (barreira)."""
from __future__ import annotations
import json


def formatar(linhas: list[tuple]) -> str:
    if not linhas: return ""
    out = ["PQBR — acessos:"]
    for i, ref, acao, cam in linhas:
        motivo = (cam or {}).get("motivo", "") if isinstance(cam, dict) else ""
        out.append(f"#{i} {ref.replace('acesso:', 'acesso ')}: {acao}" + (f" (motivo: {motivo[:120]})" if motivo else ""))
    out.append("Responda aqui ou no painel do Paperclip.")
    return "\n".join(out)


def main() -> None:
    from .pacote import _banco
    from ..seguranca.barreira import exigir_limpo
    with _banco() as c:
        rows = c.execute("select id, item_ref, observacao_jose, caminhos_tentados from pqbr.revisao_humana where (status = 'pendente' and (avisado_em is null or avisado_em < now() - interval '6 hours'))"
                         " or (item_ref like 'aviso:%%' and avisado_em is null) order by id").fetchall()
        txt = formatar(rows)
        if txt:
            exigir_limpo(txt, "telegram")
            c.execute("update pqbr.revisao_humana set avisado_em = now() where id = any(%s)", ([r[0] for r in rows],)); c.commit()
    if txt: print(txt)


if __name__ == "__main__":
    main()
