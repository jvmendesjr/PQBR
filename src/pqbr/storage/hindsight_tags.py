"""Regra única de tags do Hindsight (t90u): usada pelo indexador (memórias novas) e pela reclassificação (legado).
Tags de conteúdo pela origem do item (contexto do retain) + palavras-chave do texto, filtradas pelas tags da política;
`obsoleto_candidato` só pela reclassificação. Puro e determinístico (sem rede)."""
from __future__ import annotations
import re

TAG_OBS = "obsoleto_candidato"

# decisões vigentes que tornam afirmações antigas conflitantes (padrão, decisão)
CONFLITOS: list[tuple[str, str]] = [
    (r"\b(runway|manus)\b", "Runway e Manus descartados para vídeo (26/10/2026)"),
    (r"\bpaperclip\b", "ADR-011/t474–t476: Paperclip em retirada, parado e desabilitado"),
    (r"\bdiscord\b", "t474: revogada a t464 (sem canal Discord)"),
    (r"\bhermes\b[^.\n]{0,120}\b(telegram|callback|pedidos|aprova)|\b(telegram|callback|pedidos)\b[^.\n]{0,120}\bhermes\b",
     "t538: ponte Telegram por bot próprio via Temporal (Hermes desconsiderado)"),
    (r"gemini[^.\n]{0,40}\b(1\.5|2\.0|2\.5|3\.0|3 pro|3\.5|flash[- ]lite)\b", "t544: juiz Gemini fixado no 3.8 Flash"),
    (r"olhos[- ]da[- ]cara|\bEP1002\b", "t75u–t77u: EP1002 olhos-da-cara reprovado e descartado (tema volta a proposto)"),
    (r"caderno[- ]mestre", "t459/ADR-003: cadernos efêmeros por episódio (sem caderno mestre)"),
]
PALAVRAS: dict[str, str] = {
    "editorial": r"roteiro|editorial|\btemas?\b|narra|estilo|personage|storyboard|\bcapa\b|\bcta\b|elenco",
    "publicacao": r"youtube|upload|publica|publishat|agendad",
    "seguranca": r"segredo|\btoken|oauth|credencia|tailnet|barreira|\.env\b|chmod|2sv|sess[aã]o google",
    "compliance": r"compliance|direitos? autora|copyright|licen[cç]a|fair use",
    "auditoria": r"auditor|auditoria|gate a9|veredito|\bloop\b|\bvisual\b",
    "incidente": r"incidente|crash|\bqueda\b",
    "pesquisa": r"pesquisa|etimologia|notebooklm|\bfontes?\b",
    "licao": r"li[cç][aã]o|li[cç][oõ]es|aprendizado",
}


def fonte(ctx: str) -> tuple[str, str | None, set[str]]:
    """(tipo, caminho_fonte|None, tags_base) a partir do contexto do retain."""
    if ctx.startswith("PQBR evolução — commit"): return "commit", None, {"commit"}
    m = re.match(r"PQBR (decisao|incidente) — DECISOES-LOG: (.*)", ctx)
    if m:
        t = {m.group(1)} | ({"incidente"} if re.search(r"incidente", m.group(2), re.I) else set())
        return "log", "docs/DECISOES-LOG.md", t
    m = re.match(r"PQBR doc canônico — ([^:]+):", ctx)
    if m:
        p, t = m.group(1), {"doc"}
        if "CONTRATO-EDITORIAL" in p or "estilo" in p or "teste-capa" in p: t |= {"editorial"}
        if p.startswith("docs/pesquisas/"): t |= {"pesquisa"}
        if "gate-a9" in p: t |= {"editorial", "auditoria"}
        if p == "docs/ESTADO-ATUAL.md": t |= {"estado"}
        if "REFERENCIA-sessao-google" in p: t |= {"seguranca"}
        if "/adr-" in p or "ARQUITETURA" in p: t |= {"decisao"}
        if "playbooks" in p: t |= {"playbook"}
        return "doc", p, t
    m = re.match(r"PQBR playbook/lição — (.*)", ctx)
    if m: return "playbook", f"company/playbooks/{m.group(1).strip()}.md", {"playbook", "licao"}
    if ctx.startswith("PQBR decisão-chave"): return "memoria", "scripts/hindsight/memorias.json", {"decisao"}
    if "lição registrada" in ctx: return "licao", None, {"licao"}
    if ctx.startswith("PQBR incidente"): return "incidente", None, {"incidente"}
    if "caderno de teste" in ctx: return "caderno", None, {"pesquisa"}
    return "outro", None, {"doc"}


def tags_conteudo(ctx: str, texto: str, validas: set[str] | None = None) -> set[str]:
    """Tags de conteúdo (sem `papel:*`). `validas` = tags da política; fora dela é descartada."""
    _, _, tags = fonte(ctx)
    base = texto.lower()
    tags |= {t for t, rx in PALAVRAS.items() if re.search(rx, base)}
    tags.discard(TAG_OBS)
    return {t for t in tags if validas is None or t in validas}


def conflitos(texto: str) -> list[str]:
    return [dec for rx, dec in CONFLITOS if re.search(rx, texto, re.I)]
