"""Activity do storyboard (t130u). O NotebookLM só devolve JSON no chat. Esta activity valida e grava.
Não gera imagem nem vídeo. `imagens_revisadas` fica false, então `pode_gerar_video()` fica false.
Base: docs/pesquisas/flow-storyboard-por-cena.md e o contrato Storyboard 1.2.0."""
from __future__ import annotations
import json, os, re
from pathlib import Path
from temporalio import activity
from ..contratos import ESTILO_PADRAO_STICKMAN
from ..contratos.gasto import GASTO_STORYBOARD
from ..contratos.storyboard import Storyboard, elenco_alternado

TRAB = Path(os.environ.get("PQBR_TRABALHO", "/home/pc/.pqbr/episodios"))
LIPS = "lips closed, only blinking and breathing."
PROMPT_STORYBOARD = (
    "Monte o storyboard do episódio {codigo}. Elenco protagonista fixo: {elenco}. "
    "Não troque o elenco e não preencha elenco_excecao. "
    "Responda SÓ um JSON, sem texto fora dele. Mínimo 3 cenas, máximo 12, nesta ordem. "
    "A fala é narração em off e NÃO entra nos prompts. Sem aspas, sem says/speaks/fala/diz/narra nos prompts. "
    "prompt_animacao em inglês, com a frase exata 'lips closed, only blinking and breathing'. "
    "Uma ação e um movimento de câmera. Início e fim como foto parada, mesma câmera e mesma luz. "
    "Enquadramento só: plano_geral, plano_medio, plano_medio_curto ou close. Nunca 'from the chest up'. "
    "Quem participa do ambiente usa figurino epoca_local e caracterizacao. Quem só observa usa o visual cotidiano travado da ficha (figurino atual_variavel), sem inventar roupa nova. "
    "expressao é reação (caras e bocas), nunca articulação de fala. "
    "refs: uma lista com \"ASSET_personagem_{elenco}-v1\". "
    "Coadjuvante, se o roteiro pedir outra pessoa, é o outro do elenco ({outro}) e leva justificativa. "
    "Roteiro:\n{roteiro}\n"
    '{{"norte_geral":"...","bloco_estilo":"Stickman de tubos grossos, cabeça redonda grande, sem pessoa de cartum",'
    '"ficha_personagem":"...","cenas":[{{"fala":"...","norte":"...","inicio":"...","fim":"...",'
    '"movimento":"...","enquadramento":"plano_medio","prompt_imagem":"...","prompt_animacao":"... lips closed, only blinking and breathing.",'
    '"refs":["ASSET_personagem_{elenco}-v1"],"epoca":"presente","papel_personagem":"observa","figurino":"atual_variavel",'
    '"expressao":"...","cenario_encaixe":"..."}}]}}'
)


def _obj(texto: str) -> dict:
    t = re.sub(r"```(?:json)?", "", texto or "")
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        raise ValueError("storyboard sem JSON")
    return json.loads(t[i:j + 1])


def ref_elenco(elenco: str) -> str:
    return f"ASSET_personagem_{elenco}-v1"


def storyboard_de_texto(texto: str, codigo: str) -> Storyboard:
    """Puro. Força código, ordem, elenco alternado e imagens_revisadas=false. Não chama rede."""
    d = _obj(texto)
    elenco = elenco_alternado(codigo)
    d["codigo"] = codigo
    d["versao"] = "1.2.0"
    d["imagens_revisadas"] = False
    d.pop("elenco_excecao", None)
    d["elenco"] = elenco
    d["bloco_estilo"] = ESTILO_PADRAO_STICKMAN
    trava = "Stickman de tubos grossos e arredondados, cabeça redonda grande, sem pessoa de cartum. "
    cenas = list(d.get("cenas") or [])
    for i, c in enumerate(cenas, start=1):
        c["versao"] = "1.2.0"
        c["numero"] = i
        c["rotulo"] = f"{codigo}_c{i:02d}"
        anim = (c.get("prompt_animacao") or "").strip()
        if "lips closed" not in anim.lower():
            anim = f"{anim} {LIPS}".strip()
        c["prompt_animacao"] = anim[:1000]
        refs = [r for r in (c.get("refs") or []) if isinstance(r, str)]
        c["refs"] = refs or [ref_elenco(elenco)]
        img = c.get("prompt_imagem") or ""
        if "stickman" not in img.lower():
            c["prompt_imagem"] = (trava + img).strip()[:2000]
    return Storyboard.model_validate(d)


def _destino_ok(destino: str) -> Path:
    raiz = TRAB.resolve()
    dest = Path(destino).resolve()
    if dest != raiz and raiz not in dest.parents:
        raise ValueError("destino do storyboard fora do diretório de trabalho")
    return dest


@activity.defn
async def storyboard_criar(texto: str, codigo: str, destino: str) -> dict:
    """Valida o JSON do chat e grava a ficha. Não gera imagem nem vídeo."""
    if not GASTO_STORYBOARD.pode_gastar or GASTO_STORYBOARD.meio != "chat_caderno":
        raise RuntimeError("contrato de gasto do storyboard não autoriza esta etapa")
    sb = storyboard_de_texto(texto, codigo)
    if sb.pode_gerar_video() or sb.imagens_revisadas:
        raise RuntimeError("storyboard não pode liberar vídeo nesta etapa")
    dest = _destino_ok(destino)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(sb.model_dump_json(indent=1), encoding="utf-8")
    return {
        "arquivo": str(dest),
        "cenas": len(sb.cenas),
        "elenco": sb.elenco,
        "imagens_revisadas": False,
        "pode_gerar_video": False,
        "gasto": GASTO_STORYBOARD.model_dump(),
    }
