"""Acompanhamento de mudanças, sem agente novo (F6-02, P14).

Ordem do aceite do ROADMAP: (1) vigia de fallbacks; (2) dev_diagnosticar
no fim de cada vigia, com aviso e sinal aprovacao_jose; (3) deriva de
contrato por fixture; (4) canário de interface no Camofox (login Google e
as surpresas do Flow; o NotebookLM fica fora, é CLI). O Dev entrega um
rascunho de diff do mapa — rascunho, não aplicação. CorrecaoAutonoma
só para sessão e fila.

Este módulo é puro e só leitura: não escreve no mapa, não escreve no
banco, não envia sinal e não abre sessão Camofox por conta própria.
O verificador do canário é injetado (adaptador real na produção,
falso nos testes). Registrar este acompanhamento como workflow/atividade
no worker exige reinício do worker, que NÃO foi feito nesta entrega:
o código está pronto e testado, o registro fica para autorização à parte.
"""
from __future__ import annotations
from collections.abc import Callable

from ..contratos import VERSOES

SINAL_APROVACAO = "aprovacao_jose"


def resumir_fallbacks(metas: list[dict]) -> dict:
    """Vigia de fallbacks a partir dos metas de agentes.rodar (papel, combo, modelo, fallback)."""
    por_papel: dict[str, int] = {}
    eventos = []
    for m in metas or []:
        if m.get("fallback"):
            por_papel[m.get("papel", "?")] = por_papel.get(m.get("papel", "?"), 0) + 1
            eventos.append({"papel": m.get("papel"), "combo": m.get("combo"), "modelo": m.get("modelo")})
    return {"total": len(metas or []), "com_fallback": len(eventos),
            "por_papel": por_papel, "eventos": eventos}


def deriva_contratos(fixture: dict, atuais: dict | None = None) -> list[dict]:
    """Deriva de contrato por fixture: compara versões esperadas (fixture) com contratos.VERSOES."""
    atual = dict(atuais if atuais is not None else VERSOES)
    out = []
    for nome, esperado in (fixture or {}).items():
        if nome not in atual:
            out.append({"contrato": nome, "tipo": "ausente_no_codigo", "fixture": esperado, "atual": None})
        elif atual[nome] != esperado:
            out.append({"contrato": nome, "tipo": "versao_diferente", "fixture": esperado, "atual": atual[nome]})
    for nome in atual:
        if nome not in (fixture or {}):
            out.append({"contrato": nome, "tipo": "ausente_na_fixture", "fixture": None, "atual": atual[nome]})
    return out


def canario_interface(verificador: Callable[[], dict]) -> dict:
    """Canário de interface no Camofox, via verificador injetado. Nunca verifica o NotebookLM.

    O verificador devolve login_google (bool) e surpresas_flow (lista).
    Qualquer chave notebooklm vinda dele é descartada: o NotebookLM é CLI
    e fica fora do canário, por decisão registrada no ROADMAP.
    """
    r = verificador() or {}
    surpresas = list(r.get("surpresas_flow") or [])
    login = bool(r.get("login_google"))
    return {"status": "ok" if login and not surpresas else "falha",
            "login_google": login, "surpresas_flow": surpresas,
            "notebooklm_verificado": False}


def dev_diagnosticar(acompanhamento: dict, mapa_mmd: str) -> dict:
    """Dev no fim da vigia: aviso + sinal (dados, não envio) + rascunho de diff do mapa (não aplicado).

    O sinal é devolvido como dado para o workflow que o enviará; este
    módulo não tem cliente Temporal nem Telegram e não envia nada.
    """
    fb = acompanhamento.get("fallbacks", {}).get("com_fallback", 0)
    can = acompanhamento.get("canario", {}).get("status", "?")
    resumo = "fallbacks: " + str(fb) + "; deriva: " + str(len(acompanhamento.get("deriva", []))) + "; canario: " + str(can)
    return {"aviso": f"Acompanhamento de mudanças concluído. {resumo} — aguardar OK do José antes de qualquer aplicação.",
            "sinal": {"tipo": SINAL_APROVACAO, "tarefa": "acompanhamento_mudancas", "resumo": resumo},
            "rascunho_diff_mapa": f"--- rascunho, não aplicado ---\n{mapa_mmd[:500]}\n# sugestão do Dev: revisar os itens acima no mapa antes de qualquer mudança",
            "aplicado": False}


def acompanhar(metas: list[dict], fixture_versoes: dict, verificador_canario: Callable[[], dict],
               mapa_mmd: str) -> dict:
    """Executa a ordem do aceite e devolve o relatório. Só leitura, sem registro no worker."""
    fallbacks = resumir_fallbacks(metas)
    deriva = deriva_contratos(fixture_versoes)
    canario = canario_interface(verificador_canario)
    parcial = {"fallbacks": fallbacks, "deriva": deriva, "canario": canario}
    return {"ordem": ["fallbacks", "deriva", "canario", "dev_diagnosticar"],
            **parcial, "diagnostico": dev_diagnosticar(parcial, mapa_mmd),
            "correcao_autonoma_escopo": "sessao_e_fila",
            "registrado_no_worker": False}
