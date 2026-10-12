"""t464 (José 14:00): o NotebookLM faz o máximo do criativo dentro do caderno efêmero do episódio
(roteiro, SEO, capa); agentes/modelos só orquestram e validam (contratos Pydantic). O que o NotebookLM
não fizer cai no 9router com o combo do papel (config/modelos_9router.json)."""
from __future__ import annotations
import asyncio, json, re
from pathlib import Path
from temporalio import activity
from temporalio.exceptions import ApplicationError
from ..contratos import RoteiroShort, PacoteSEO, ESTILO_PADRAO_2D, CTA

PROMPT_ROTEIRO = (
    "Escreva o roteiro do Short sobre \"{tema}\" seguindo o contrato editorial e o bloco visual §16.7 do pacote PQBR: "
    "gancho até 3 s com a imagem literal da expressão, versão mais aceita + 'mas tem quem diga', ≥ 2 fontes deste caderno, "
    "loop na última cena. Narrador único, sem nomes, ~50 s (cerca de 115 palavras), última fala exatamente \"" + CTA + "\". "
    "Um personagem 2D sem nome descrito numa frase-ficha detalhada (idade, cabelo, roupa, traço marcante), repetida igual. "
    "Uma cena por fala. Responda SÓ um JSON, sem texto fora dele, neste formato: "
    '{{"episodio_id":"{slug}","titulo":"...","falas":["..."],"entidades_cena":["..."],'
    '"bloco_visual":{{"personagem":"...","cenas":[{{"fala":"...","acao":"...","enquadramento":"...","ambiente":"..."}}]}},'
    '"fontes":["URL ou título da fonte do caderno", "..."]}}')
PROMPT_SEO = (
    "Com base no roteiro deste caderno, gere o SEO do Short do canal Porquê BR (pt-BR): titulo (≤ 70 caracteres, pergunta curiosa, "
    "sem clickbait enganoso), descricao (2–3 frases + as fontes + hashtags), tags (≤ 12), hashtags (3–5, inclua #shorts). "
    'Responda SÓ um JSON: {"titulo":"...","descricao":"...","tags":["..."],"hashtags":["#..."]}')
PROMPT_CAPA = ("Capa de YouTube Short 9:16: UMA única ilustração 2D de cartum da CENA 1, personagem grande no centro, sem texto, "
               "sem títulos, sem gráficos, sem ícones; siga [ESTILO] e [PERSONAGEM] da fonte do roteiro.")


def _obj(texto: str) -> dict:
    t = re.sub(r"```(?:json)?", "", texto or "")
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i: raise ValueError("resposta sem JSON")
    return json.loads(t[i:j + 1])


def roteiro_de_texto(texto: str, slug: str) -> tuple[dict, list[str]]:
    """Valida o roteiro do NotebookLM no contrato RoteiroShort (estilo §16.7 forçado). Puro; testado."""
    d = _obj(texto)
    d["episodio_id"] = slug
    d.setdefault("bloco_visual", {})["estilo"] = ESTILO_PADRAO_2D
    fontes = [str(f) for f in d.get("fontes", []) if str(f).strip()]
    r = RoteiroShort.model_validate({k: d.get(k) for k in ("episodio_id", "titulo", "falas", "entidades_cena", "bloco_visual")})
    if len(fontes) < 2: raise ValueError("roteiro precisa de ≥ 2 fontes (§16.5)")
    if len(r.bloco_visual.cenas) < 4: raise ValueError("poucas cenas (mín. 4)")
    return r.model_dump(), fontes


def roteiro_markdown(r: dict, fontes: list[str]) -> str:
    bv = r["bloco_visual"]
    return (f"# {r['titulo']}\n\n## Falas (narrador único)\n" + "\n".join(f"{i+1}. {f}" for i, f in enumerate(r["falas"])) +
            f"\n\n## Bloco visual\n[ESTILO] {bv['estilo']}\n[PERSONAGEM] {bv['personagem']}\n[CENAS]\n" +
            "\n".join(f"S{i+1:02d} — fala: {c['fala']} | ação: {c['acao']} | enquadramento: {c['enquadramento']} | ambiente: {c['ambiente']}"
                      for i, c in enumerate(bv["cenas"])) + "\n\n## Fontes\n" + "\n".join(fontes))


def steering_de_roteiro(r: dict) -> str:
    bv = r["bloco_visual"]
    return f"[ESTILO] {bv['estilo']} [PERSONAGEM] {bv['personagem']}"


@activity.defn
async def validar_roteiro(texto: str, slug: str) -> dict:
    try:
        r, f = roteiro_de_texto(texto, slug)
    except Exception as e:  # noqa: BLE001
        raise ApplicationError(f"roteiro inválido: {str(e)[:400]}", type="SaidaInvalida", non_retryable=True) from None
    return {"roteiro": r, "fontes": f, "markdown": roteiro_markdown(r, f), "steering": steering_de_roteiro(r)}


@activity.defn
async def validar_seo(texto: str) -> dict:
    try:
        return PacoteSEO.model_validate(_obj(texto)).model_dump()
    except Exception as e:  # noqa: BLE001
        raise ApplicationError(f"SEO inválido: {str(e)[:400]}", type="SaidaInvalida", non_retryable=True) from None


@activity.defn
async def seo_9router(roteiro_md: str) -> dict:
    """Reserva: o NotebookLM não entregou SEO válido → Especialista de SEO no 9router (combo do papel)."""
    from ..kit.router9 import chat_papel
    erro = ""
    for _ in range(2):
        t = await asyncio.to_thread(chat_papel, "especialista-seo", "Você é o Especialista de SEO do Porquê BR. Responda só JSON.",
                                    PROMPT_SEO + "\n\nRoteiro:\n" + roteiro_md[:6000] + (f"\nCorrija: {erro}" if erro else ""), 1200)
        try: return PacoteSEO.model_validate(_obj(t)).model_dump() | {"_origem": "9router"}
        except Exception as e: erro = str(e)[:300]  # noqa: BLE001
    raise ApplicationError("SEO 9router inválido: " + erro, type="SaidaInvalida", non_retryable=True)


@activity.defn
async def compliance_roteiro(roteiro_md: str) -> dict:
    """Líder de Compliance + Guardião (combos do papel). Reprova só por segurança (CONTRATO §16.6)."""
    from ..kit.router9 import chat_papel
    from ..seguranca.barreira import exigir_limpo
    exigir_limpo(roteiro_md, "roteiro")   # Guardião: sem segredo/injeção no que vai ao NotebookLM
    pedido = ("Confira o roteiro contra o contrato editorial do Porquê BR. Reprove só por: pessoa real/celebridade, marca real, "
              "estereótipo ofensivo, política/religião/tragédia, afirmação falsa apresentada como certa, pedido de comentário, "
              "conselho especializado. Responda só JSON: {\"aprovado\":true|false,\"motivos\":[...],\"ressalvas\":[...]}\n\n" + roteiro_md[:8000])
    d = _obj(await asyncio.to_thread(chat_papel, "lider-compliance", "Você é o Líder de Compliance do Porquê BR.", pedido, 800))
    if not isinstance(d.get("aprovado"), bool): raise ValueError("compliance sem campo aprovado")
    if not d["aprovado"]:   # segunda opinião antes de bloquear (t421)
        s = _obj(await asyncio.to_thread(chat_papel, "revisao", "Você revisa decisões de compliance. Responda só JSON.", pedido, 800))
        d["segunda_opiniao"] = s
        if s.get("aprovado") is True: d["aprovado"] = None   # divergência → escala (não gera)
    return d
