"""Aba Portões do painel :8088 (José, 31/10/2026, proposta em branch, SÓ LEITURA).

Gera HTML a partir de fontes já existentes no repositório, no mesmo padrão
modular de producao.py / roadmap.py: uma função secao() importada por
gerar_index.py. Nada aqui escreve: não há POST, formulário, botão de ação,
acesso a banco, sinal do Temporal, nem uso da tabela de revisão humana.
A "ação" de cada card é apenas texto: a ordem exata a dar no chat ou no
Telegram (ou o sinal do Temporal a enviar por quem já tem esse canal).
A aba não envia nada sozinha.

Fontes (só leitura):
- config/flow_projetos.json (piloto atual);
- banco-fichas/indice.json (catálogo principal);
- banco-fichas/referencias-motion/indice.json (referências de motion);
- docs/ESTADO-ATUAL.md (pendências P* cujo dono inclui o José).

Vocabulário: veredito do auditor só aparece quando o item é auditoria, e
sempre nos termos canônicos (aprova, aprova_com_ressalva, terceira_rodada,
reprova). Os gates oficiais citados são boca_articula_fala,
corte_oculos_cabeca e grotesco, cada um reprovando sozinho.

Nenhum contrato Pydantic novo foi criado para esta aba, de propósito: ela
não cria dado que cruze fronteira de agente ou ferramenta, apenas apresenta
fontes existentes. Criar um contrato aqui seria inventar uma fronteira que
não existe no fluxo.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FLOW = RAIZ / "config/flow_projetos.json"
FICHAS = RAIZ / "banco-fichas/indice.json"
REF_MOTION = RAIZ / "banco-fichas/referencias-motion/indice.json"
ESTADO = RAIZ / "docs/ESTADO-ATUAL.md"

_FECHADO = ("feito", "substituída", "substituido", "superado", "superada")


def _limpo(t: str, n: int = 520) -> str:
    t = re.sub(r"\*\*|__|`", "", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t).strip()
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def _contar(fichas: list, estado: str) -> list[str]:
    return [str(f.get("id", "")) for f in fichas if f.get("estado") == estado]


def parse_pendencias(md: str) -> list[dict]:
    """Pendências P* do ESTADO-ATUAL, com flag de aberta/fechada.

    Fechada = texto começa por Feito / Substituída / Superado (após tirar
    o negrito). Qualquer outra linha é portão aberto, mesmo que o texto
    mencione algo já feito no meio: o bloqueio é que manda.
    """
    out = []
    for linha in md.splitlines():
        if not linha.startswith("| P"):
            continue
        c = [x.strip() for x in linha.strip().strip("|").split("|")]
        if len(c) < 5 or not re.fullmatch(r"P\d+", c[0]):
            continue
        texto = _limpo(c[1])
        aberta = not texto.lstrip("* ").lower().startswith(_FECHADO)
        out.append(
            {
                "id": c[0],
                "texto": texto,
                "dono": _limpo(c[3], 40),
                "bloqueio": _limpo(c[4], 160),
                "aberta": aberta,
            }
        )
    return out


def dados(
    flow: dict | None = None,
    fichas: dict | None = None,
    ref_motion: dict | None = None,
    estado_md: str | None = None,
) -> dict:
    """Lê as quatro fontes e devolve só dados para renderizar."""
    flow = flow if flow is not None else json.loads(FLOW.read_text(encoding="utf-8"))
    fichas = fichas if fichas is not None else json.loads(FICHAS.read_text(encoding="utf-8"))
    ref_motion = (
        ref_motion
        if ref_motion is not None
        else json.loads(REF_MOTION.read_text(encoding="utf-8"))
    )
    estado_md = estado_md if estado_md is not None else ESTADO.read_text(encoding="utf-8")

    projetos = flow.get("projetos", {}) or {}
    piloto = projetos.get("EP1003") or (next(iter(projetos.values()), None) if projetos else None)
    lista_fichas = fichas.get("fichas", []) or []
    refs = ref_motion.get("referencias", []) or []
    pend = parse_pendencias(estado_md)
    portoes = [p for p in pend if "José" in p["dono"] and p["aberta"]]
    portoes.sort(key=lambda p: int(p["id"][1:]))
    return {
        "piloto": piloto,
        "fichas_versao": fichas.get("versao", ""),
        "fichas_aguardando": _contar(lista_fichas, "aguardando_ok_jose"),
        "fichas_permanente": len(_contar(lista_fichas, "permanente")),
        "fichas_sugestao": _contar(lista_fichas, "sugestao"),
        "refs_versao": ref_motion.get("versao", ""),
        "refs_aguardando": _contar(refs, "aguardando_ok_jose"),
        "refs_aprovadas": len(_contar(refs, "aprovada")),
        "portoes": portoes,
        "pendencias_fechadas_jose": [p["id"] for p in pend if "José" in p["dono"] and not p["aberta"]],
    }


# Recomendação técnica e ordem exata (texto, nunca ação) por portão.
# O bloqueio registrado no ESTADO-ATUAL é a fonte; aqui só se explicita
# o que ele já diz, para o card ficar legível sem abrir o documento.
_PORTOES_TEXTO: dict[str, tuple[str, str]] = {
    "P1": (
        "Lote do saldo continua parado: não apagar mídia e não publicar o lote antigo. Refação (MG-11) só depois de Flow, depois MG-05, depois o José assistir, e só então o lote. Confirmado 31/10/2026.",
        "Ordem no chat/Telegram: “Manter o lote do saldo parado, sem publicar e sem apagar nada.”",
    ),
    "P11": (
        "Fechada 31/10/2026 como incorporada: a branch já era ancestral da main; nenhum merge novo foi feito. Esta aba não faz merge.",
        "Nenhuma ordem nova: a P11 está fechada. Não mergear a branch de novo.",
    ),
    "P13": (
        "Implementada 31/10/2026 (F1-05): ferramentas só leitura em src/pqbr/agents/ferramentas.py, sem reinício, sem MCP interno.",
        "Nenhuma ordem nova: a P13 está fechada. A ferramenta já está no código, sem efeito externo.",
    ),
    "P14": (
        "Implementada e testada 31/10/2026 (F6-02), sem reinício: vigia de fallbacks, dev_diagnosticar, deriva de contrato e canário Camofox. O registro no worker exige reinício, autorizado à parte e não feito.",
        "Ordem separada, quando o José decidir: “OK para reiniciar o worker e registrar o acompanhamento.” Até lá, nada reinicia.",
    ),
    "P16": (
        "Em espera 31/10/2026: aguardar o painel ficar pronto, outras melhorias e testes (como os cadernos), antes de gerar os clipes. Nada do v2 nem do projeto antigo é apagado.",
        "Ordem em espera: nenhum clipe agora. O próximo passo só depois que o painel e os testes estiverem prontos.",
    ),
    "P17": (
        "Em espera 31/10/2026: o usuário ainda não decidiu os sub-itens, um por vez (folha nº 1, mídia das SIT-*, OK MG-12/merge). A revisão de stills do piloto já está registrada como aprovada no arquivo do projeto; o texto antigo de P16/P17 ainda diz “falta revisão”.",
        "Ordem no chat/Telegram, um item por vez, por exemplo: “OK MG-12” ou “Produzir a folha nº 1”. Nada em bloco e nada por clique.",
    ),
    "P18": (
        "Combo core-ultra já criado e testado (HTTP 200), mas a troca de motion de core-alto para core-ultra mais o reinício ficam para confirmação separada junto com o piloto. Não fazer agora. Até lá, motion segue core-alto. Medir o custo real em pqbr.consumo_modelos no piloto.",
        "Ordem separada, junto com o piloto: “OK MG-12: trocar motion de core-alto para core-ultra em config/modelos_9router.json e reiniciar o worker.” Troca e reinício na mesma ordem explícita.",
    ),
}
_GENERICO = (
    "Seguir o bloqueio registrado no ESTADO-ATUAL. Nenhuma ação "
    "automática a partir desta aba.",
    "Ordem no chat/Telegram, explícita e específica para este portão, "
    "antes de qualquer mudança.",
)


def _selo(texto: str, bg: str, fg: str) -> str:
    return (
        f'<span class="pt-selo" style="background:{bg};color:{fg}">'
        f"{html.escape(texto)}</span>"
    )


def _card(titulo: str, selo: str, linhas: list[tuple[str, str]]) -> str:
    corpo = "".join(
        f"<p><b>{html.escape(rot)}:</b> {html.escape(val)}</p>" for rot, val in linhas
    )
    return f'<article class="pt-card"><h3>{html.escape(titulo)}</h3>{selo}{corpo}</article>'


CSS = (
    "<style>.pt-card{border:1px solid var(--l);border-radius:8px;padding:10px 12px;margin:10px 0}"
    ".pt-card h3{margin:0 0 6px;font-size:14px}.pt-card p{margin:6px 0;font-size:13px}"
    ".pt-selo{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600}"
    ".pt-aviso{background:#fff8e6;border:1px solid #f0dca8;border-radius:8px;padding:10px;font-size:13px}"
    ".pt-lista{font-size:13px}</style>"
)


def _secao_piloto(p: dict | None) -> str:
    if not p:
        return _card(
            "Piloto atual",
            _selo("sem piloto registrado", "#eceff1", "#546e7a"),
            [("Contexto", "config/flow_projetos.json não traz projeto de episódio.")],
        )
    videos = p.get("videos", []) or []
    imagens = p.get("imagens_inicio", []) or []
    return _card(
        f"Piloto {p.get('codigo', '')} — {p.get('slug', '')} (projeto v3)",
        _selo("imagens aprovadas · próximo gate: clipes", "#e8f5e9", "#2e7d32"),
        [
            (
                "Contexto",
                f"Projeto {p.get('titulo', '')} ({p.get('id', '')}), "
                f"{len(imagens)} imagens de início S01..S08, prompts de movimento "
                "registrados, fichas entregues: "
                + ", ".join(p.get("fichas_entregues", []) or [])
                + ".",
            ),
            (
                "Status / veredito atual",
                "imagens_revisadas: true. José aprovou as imagens em 30/10/2026, "
                "incluindo as novas versões de S03, S04 e S07 (e S05), e autorizou "
                "o vídeo piloto: 1 clipe contínuo por cena, a partir das imagens "
                "aprovadas, com os prompts de movimento registrados. Vídeos "
                f"registrados no repo: {len(videos)}. Montagem/motion (MG-05) "
                "segue segurado e fora deste passo.",
            ),
            (
                "Divergência anotada, não resolvida por palpite",
                "P16 e P17 no ESTADO-ATUAL ainda escrevem “falta revisão”. O "
                "arquivo do projeto (commit 03ec319, aprovação do piloto) diz o "
                "contrário. A aba mostra o arquivo do projeto; o texto do ESTADO "
                "precisa de correção explícita, não de leitura silenciosa.",
            ),
            (
                "Auditoria (caderno t170u, fundamentação, não decisão do worker)",
                "S04 nova = aprova_com_ressalva (faltam stills/quadros-chave); "
                "S05 original = reprova (banquinho, braços realistas, chaleira "
                "sem mão). Veredito final continua fora do caderno, validado "
                "por contrato.",
            ),
            (
                "Recomendação técnica",
                "Gerar os clipes só a partir das imagens aprovadas. Não "
                "reutilizar as versões originais com problema de S03/S04/S05/S07, "
                "que permanecem na biblioteca sem apagar. Antes de qualquer "
                "publicação, o clipe passa pelos gates oficiais: "
                "boca_articula_fala, corte_oculos_cabeca e grotesco, cada um "
                "reprovando sozinho.",
            ),
            (
                "Ação / comando exato (texto — a aba não executa)",
                "Ordem no chat/Telegram: “Gerar os clipes do piloto EP1003 a "
                "partir das imagens aprovadas (novas S03/S04/S05/S07), 1 clipe "
                "contínuo por cena, com os prompts de movimento registrados; "
                "MG-05 fora deste passo.”",
            ),
        ],
    )


def secao(d: dict | None = None) -> str:
    d = d or dados()
    piloto = _secao_piloto(d["piloto"])

    if d["fichas_aguardando"]:
        selo_f = _selo(
            f"{len(d['fichas_aguardando'])} aguardando_ok_jose", "#fff3e0", "#ef6c00"
        )
        aguardando_txt = ", ".join(d["fichas_aguardando"])
    else:
        selo_f = _selo("nenhuma aguardando_ok_jose", "#e8f5e9", "#2e7d32")
        aguardando_txt = "nenhuma"
    fichas = _card(
        "Fichas — catálogo principal (banco-fichas)",
        selo_f,
        [
            (
                "Contexto",
                f"Índice v{d['fichas_versao']}: {d['fichas_permanente']} "
                "permanentes. Aguardando_ok_jose: " + aguardando_txt + ".",
            ),
            (
                "SIT-* em sugestao (sem mídia)",
                ", ".join(d["fichas_sugestao"]) or "nenhuma",
            ),
            (
                "Status / veredito atual",
                "Sugestao não é portão de aprovação: é ideia sem mídia, pronta "
                "para o agente produzir a imagem ou o vídeo. Ao anexar mídia, "
                "a ficha vira aguardando_ok_jose e aí sim só o José aprova "
                "ou manda descartar, pelo pipeline (banco_fichas.aprovar), "
                "nunca por esta aba.",
            ),
            (
                "Recomendação técnica",
                "Não aprovar SIT-* por clique: primeiro produzir a mídia. "
                "Quando houver ficha em aguardando_ok_jose, ela aparece "
                "nesta seção automaticamente na próxima geração do painel.",
            ),
            (
                "Ação / comando exato (texto — a aba não executa)",
                "Ordem no chat/Telegram: “Produzir mídia das SIT-* e deixar "
                "em aguardando_ok_jose para minha aprovação.” A aprovação em "
                "si vem depois, em ordem explícita.",
            ),
        ],
    )

    if d["refs_aguardando"]:
        selo_r = _selo(
            f"{len(d['refs_aguardando'])} aguardando_ok_jose", "#fff3e0", "#ef6c00"
        )
        refs_txt = ", ".join(d["refs_aguardando"])
    else:
        selo_r = _selo("nenhuma aguardando_ok_jose", "#e8f5e9", "#2e7d32")
        refs_txt = "nenhuma"
    refs = _card(
        "Referências de motion",
        selo_r,
        [
            (
                "Contexto",
                f"Índice v{d['refs_versao']}: {d['refs_aprovadas']} referências "
                "aprovadas (REF-MG-00..07). Aguardando_ok_jose: " + refs_txt + ".",
            ),
            (
                "Status / veredito atual",
                "Nenhum portão de referência de motion aberto no momento. "
                "Regra vigente: referência nova só vira aprovada com OK do "
                "José; as atuais já o têm.",
            ),
            (
                "Ação / comando exato (texto — a aba não executa)",
                "Se surgir referência nova em aguardando_ok_jose, ordem no "
                "chat/Telegram: “Aprovar a referência REF-MG-__” ou “Descartar "
                "a referência REF-MG-__.”",
            ),
        ],
    )

    cards_portoes = []
    for p in d["portoes"]:
        rec, acao = _PORTOES_TEXTO.get(p["id"], _GENERICO)
        cards_portoes.append(
            _card(
                f"{p['id']} — portão do José",
                _selo("portão aberto", "#fff3e0", "#ef6c00"),
                [
                    ("Contexto", p["texto"]),
                    ("Bloqueio registrado", p["bloqueio"]),
                    ("Recomendação técnica", rec),
                    ("Ação / comando exato (texto — a aba não executa)", acao),
                ],
            )
        )
    fechadas = (
        ", ".join(d["pendencias_fechadas_jose"]) or "nenhuma"
    )
    return (
        '<section id="portoes" class="portsec"><h2>Portões — decisões do José</h2>'
        '<p class="nota">Só leitura. Painel executivo de curadoria e desbloqueio, '
        "gerado de config/flow_projetos.json, banco-fichas/indice.json, "
        "banco-fichas/referencias-motion/indice.json e docs/ESTADO-ATUAL.md. "
        "Nada nesta aba aprova, escreve, reinicia ou faz merge.</p><p class='nota'><b>Decisões de 31/10/2026:</b> P11 incorporada, P13 implementada, P14 implementada sem reinício, P16/P17 em espera, P18 para confirmação separada junto com o piloto, AR Board adiado para decisão canônica. A aba continua só leitura.</p>"
        + CSS
        + '<div class="pt-aviso"><b>O que esta aba NÃO faz:</b> não envia sinal '
        "do Temporal, não escreve em banco, não aprova ficha, não reinicia "
        "worker e não faz merge. Cada card traz a ordem exata em texto; a "
        "decisão acontece no chat ou no Telegram, com ordem explícita do José."
        "</div><h3>Piloto atual</h3>" + piloto
        + "<h3>Fichas e referências</h3>" + fichas + refs
        + "<h3>Portões abertos do José (ESTADO-ATUAL)</h3>"
        + "".join(cards_portoes)
        + f'<p class="nota">Pendências do José já fechadas ou superadas no '
        f"ESTADO-ATUAL (não são portões abertos): {html.escape(fechadas)}.</p>"
        "</section>"
    )
