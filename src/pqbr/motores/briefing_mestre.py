"""Porta + adaptadores do briefing do Caderno Mestre (José 31/10/2026, t168u).

Porta: `BriefadorMestre`. Adaptador real: NotebookLM (activities). Adaptador falso: testes sem rede.
O mestre NUNCA gera mídia."""
from __future__ import annotations
import json, re
from typing import Protocol, runtime_checkable
from pqbr.contratos.briefing_mestre import BriefingEfemerico, PedidoBriefingMestre
from pqbr.contratos.gasto import AutorizacaoGasto

GASTO_BRIEFING_MESTRE = AutorizacaoGasto(
    etapa="briefing_mestre",
    modelo="notebooklm-chat",
    pode_gastar=True,
    meio="chat_caderno",
    deterministico="JSON vira BriefingEfemerico 1.0.0; limpa chat do mestre; sem midia",
    agente="o ask devolve o JSON; nao escolhe generate",
)

_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def _obj(texto: str) -> dict:
    t = re.sub(r"```(?:json)?", "", texto or "")
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        raise ValueError("briefing sem JSON")
    return json.loads(t[i : j + 1])


def montar_pergunta_briefing(pedido: PedidoBriefingMestre) -> str:
    partes = [
        "Com base nas fontes deste caderno mestre, emita o BRIEFING do caderno efêmero.",
        "Responda SÓ um JSON (sem texto fora), campos:",
        "persona_efemero, prompt_pesquisa, modo_pesquisa (fast|deep), urls_pesquisa (≥1 URL http),",
        "fontes_mestre_a_copiar (títulos), refs_catalogo_sugeridas, prompt_roteiro, prompt_seo,",
        "prompt_direcao_cenas, prompt_compliance (opcional), riscos_compliance, modelo_sugerido,",
        "rotulo_episodio_prefix, pesquisa_obrigatoria=true.",
        f"Tema: {pedido.tema}",
    ]
    if pedido.codigo:
        partes.append(f"Código: {pedido.codigo}")
    if pedido.slug:
        partes.append(f"Slug: {pedido.slug}")
    if pedido.n_cenas:
        partes.append(f"n_cenas: {pedido.n_cenas}")
    partes.append(
        "A pesquisa do tema roda no EFÊMERO com prompt_pesquisa; este mestre não gera mídia."
    )
    return " ".join(partes)


def parse_briefing(texto: str, pedido: PedidoBriefingMestre, caderno_mestre_id: str) -> BriefingEfemerico:
    d = _obj(texto)
    d = dict(d)
    d["versao"] = "1.0.0"
    d["tema"] = pedido.tema
    d["caderno_mestre_id"] = caderno_mestre_id
    if pedido.codigo:
        d.setdefault("codigo", pedido.codigo)
    if pedido.slug:
        d.setdefault("slug", pedido.slug)
    if pedido.n_cenas:
        d.setdefault("n_cenas", pedido.n_cenas)
    d.setdefault("pesquisa_obrigatoria", True)
    d.setdefault("modelo_sugerido", "notebooklm-chat")
    d.setdefault("modo_pesquisa", "fast")
    if pedido.codigo:
        d.setdefault("rotulo_episodio_prefix", pedido.codigo)
    return BriefingEfemerico.model_validate(d)


@runtime_checkable
class BriefadorMestre(Protocol):
    nome: str

    def briefar(self, pedido: PedidoBriefingMestre) -> BriefingEfemerico: ...


class AdaptadorFalsoBriefing:
    """Sem rede: devolve briefing mínimo válido."""
    nome = "falso"

    def __init__(self, caderno_mestre_id: str = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"):
        self.caderno_mestre_id = caderno_mestre_id

    def briefar(self, pedido: PedidoBriefingMestre) -> BriefingEfemerico:
        if not GASTO_BRIEFING_MESTRE.pode_gastar or GASTO_BRIEFING_MESTRE.meio != "chat_caderno":
            raise RuntimeError("gasto briefing mestre não autoriza")
        mid = pedido.caderno_mestre_id or self.caderno_mestre_id
        persona = (
            "Você é o showrunner operacional do canal Porquê BR neste caderno EFÊMERO. "
            "Siga o contrato editorial stickman; nunca invente estatística; cite fontes do caderno."
        )
        return BriefingEfemerico(
            tema=pedido.tema,
            codigo=pedido.codigo,
            slug=pedido.slug,
            n_cenas=pedido.n_cenas,
            caderno_mestre_id=mid,
            persona_efemero=persona,
            prompt_pesquisa=f"origem e explicação: {pedido.tema}",
            modo_pesquisa="fast",
            pesquisa_obrigatoria=True,
            urls_pesquisa=["https://pt.wikipedia.org/wiki/Lista_de_express%C3%B5es_idiom%C3%A1ticas_da_l%C3%ADngua_portuguesa"],
            fontes_mestre_a_copiar=["002-PERSONA-EFEMERO-BASE", "007-ESTILO-STICKMAN"],
            refs_catalogo_sugeridas=["PERS-menina-rosa", "AMB-cafe", "OBJ-caneca"],
            prompt_roteiro=f"Escreva o roteiro do Short sobre {pedido.tema} seguindo o contrato editorial.",
            prompt_seo="Gere título, descrição e hashtags pt-BR sem pedir comentário; categoria 27.",
            prompt_direcao_cenas="Monte a direção das cenas em JSON CenaIndividual 2.0.0 com rótulos PQBR-EP####-S##.",
            prompt_compliance="Confira tom, fontes e ausência de clickbait falso.",
            riscos_compliance=["verificar etimologia disputada"],
            modelo_sugerido="notebooklm-chat",
            rotulo_episodio_prefix=pedido.codigo,
            nota_salva=True,
        )


class AdaptadorNotebookLMBriefing:
    """Adaptador real: activities do workflows/notebooklm (mestre)."""
    nome = "notebooklm"

    def briefar(self, pedido: PedidoBriefingMestre) -> BriefingEfemerico:
        import asyncio
        return asyncio.run(self.abriefar(pedido))

    async def abriefar(self, pedido: PedidoBriefingMestre) -> BriefingEfemerico:
        from pqbr.workflows import notebooklm as n
        from pqbr.config_caderno_mestre import id_mestre  # briefing e texto, nao midia: a trava de midia fica nos caminhos de midia (nlm_gerar_short etc.)

        mid = pedido.caderno_mestre_id or id_mestre()
        if not mid or not _UUID.match(mid):
            raise RuntimeError("caderno_mestre_id não configurado")
        if not GASTO_BRIEFING_MESTRE.pode_gastar:
            raise RuntimeError("gasto briefing mestre negado")
        pergunta = montar_pergunta_briefing(pedido)
        txt = await n.nlm_mestre_perguntar(mid, pergunta, salvar_nota=pedido.salvar_nota)
        briefing = parse_briefing(txt, pedido, mid)
        if pedido.limpar_chat_apos:
            await n.nlm_mestre_limpar_chat(mid)
        return briefing.model_copy(update={"nota_salva": pedido.salvar_nota})


def briefador_mestre(nome: str | None = None) -> BriefadorMestre:
    nome = nome or "notebooklm"
    if nome == "falso":
        return AdaptadorFalsoBriefing()
    if nome == "notebooklm":
        return AdaptadorNotebookLMBriefing()
    raise KeyError(f"BriefadorMestre sem adaptador: {nome}")
