"""Activity do storyboard (t130u). O NotebookLM só devolve JSON no chat. Esta activity valida e grava.
Não gera imagem nem vídeo. `imagens_revisadas` fica false, então `pode_gerar_video()` fica false.
Base: docs/pesquisas/flow-storyboard-por-cena.md e o contrato Storyboard 1.3.0.
Os `refs` são ids do catálogo visual aberto (`banco-fichas/`, t150u); o que não existe no catálogo sai da ficha e é devolvido em `refs_descartadas`."""
from __future__ import annotations
import json, os, re
from pathlib import Path
from temporalio import activity
from ..contratos import ESTILO_PADRAO_STICKMAN
from ..contratos.gasto import GASTO_STORYBOARD
from ..contratos.storyboard import REF_CATALOGO, VERSAO, Storyboard, elenco_alternado, protagonista_ref

TRAB = Path(os.environ.get("PQBR_TRABALHO", "/home/pc/.pqbr/episodios"))
LIPS = "lips closed, only blinking and breathing."
MAX_REFS = 6
_CATALOGO = re.compile(rf"^{REF_CATALOGO}$")
_LEGADO = re.compile(r"^ASSET_personagem_(masculino|feminino)-v\d+$")
PROMPT_STORYBOARD = (
    "Monte o storyboard do episódio {codigo}. Elenco protagonista fixo: {elenco} ({protagonista}). "
    "Não troque o protagonista e não preencha elenco_excecao. "
    "Responda SÓ um JSON, sem texto fora dele. Mínimo 3 cenas, máximo 12, nesta ordem. "
    "A fala é narração em off e NÃO entra nos prompts. Sem aspas, sem says/speaks/fala/diz/narra nos prompts. "
    "prompt_animacao em inglês, com a frase exata 'lips closed, only blinking and breathing'. "
    "Uma ação e um movimento de câmera. Início e fim como foto parada, mesma câmera e mesma luz. "
    "Enquadramento só: plano_geral, plano_medio, plano_medio_curto ou close. Nunca 'from the chest up'. "
    "Quem participa do ambiente usa figurino epoca_local e caracterizacao. Quem só observa usa o visual cotidiano travado da ficha (figurino atual_variavel), sem inventar roupa nova. "
    "expressao é reação (caras e bocas), nunca articulação de fala. "
    "refs: de 1 a 6 ids do item catalogo_visual do pacote, por cena: o protagonista {protagonista} quando ele aparece, mais o ambiente (AMB-), os objetos (OBJ-), "
    "os animais (ANIM-), as figuras (FIG-) e a situação (SIT-) que a cena usa. Só ids que estão na lista; o que a cena pedir e não estiver nela, descreva no prompt_imagem e não invente id. "
    "Coadjuvante, se o roteiro pedir outra pessoa, é outro personagem do catálogo (PERS-, diferente do protagonista; varie entre episódios) e leva justificativa. "
    "Roteiro:\n{roteiro}\n"
    '{{"norte_geral":"...","bloco_estilo":"Cartoon 2D flat colorido com personagens stickman, cabeça redonda grande",'
    '"ficha_personagem":"...","cenas":[{{"fala":"...","norte":"...","inicio":"...","fim":"...",'
    '"movimento":"...","enquadramento":"plano_medio","prompt_imagem":"...","prompt_animacao":"... lips closed, only blinking and breathing.",'
    '"refs":["{protagonista}"],"epoca":"presente","papel_personagem":"observa","figurino":"atual_variavel",'
    '"expressao":"...","cenario_encaixe":"..."}}]}}'
)


def _obj(texto: str) -> dict:
    t = re.sub(r"```(?:json)?", "", texto or "")
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        raise ValueError("storyboard sem JSON")
    return json.loads(t[i:j + 1])


def ref_elenco(elenco: str) -> str:
    """Ref do protagonista do episódio no catálogo visual (t150u): masculino = PERS-menino-azul, feminino = PERS-menina-rosa."""
    return protagonista_ref(elenco)


def _ids_do_catalogo() -> set[str] | None:
    """Ids das fichas usáveis do catálogo (`banco-fichas/indice.json`, sem as grades). None se o índice não existe: então só vale a forma do id."""
    from ..pipeline import banco_fichas
    try:
        return {d["id"] for d in banco_fichas.carregar().get("fichas", []) if d.get("papel", "item") == "item"}
    except FileNotFoundError:
        return None


def _refs(brutas: object, existentes: set[str] | None) -> tuple[list[str], list[str]]:
    """(refs aceitas, refs descartadas). `ASSET_personagem_<gênero>-v1` do legado vira o protagonista do catálogo; id fora do catálogo é descartado."""
    boas: list[str] = []
    fora: list[str] = []
    for r in brutas if isinstance(brutas, list) else []:
        if not isinstance(r, str):
            continue
        r = r.strip()
        legado = _LEGADO.match(r)
        if legado:
            r = protagonista_ref(legado.group(1))
        if _CATALOGO.match(r) and (existentes is None or r in existentes):
            if r not in boas:
                boas.append(r)
        else:
            fora.append(r)
    return boas[:MAX_REFS], fora + boas[MAX_REFS:]


def _montar(texto: str, codigo: str) -> tuple[Storyboard, list[str]]:
    d = _obj(texto)
    elenco = elenco_alternado(codigo)
    existentes = _ids_do_catalogo()
    d["codigo"] = codigo
    d["versao"] = VERSAO
    d["imagens_revisadas"] = False
    d.pop("elenco_excecao", None)
    d["elenco"] = elenco
    d["bloco_estilo"] = ESTILO_PADRAO_STICKMAN
    trava = "Cartoon 2D flat colorido, stickman de cabeça redonda branca grande com contorno preto. "
    descartadas: list[str] = []
    cenas = list(d.get("cenas") or [])
    for i, c in enumerate(cenas, start=1):
        c["versao"] = VERSAO
        c["numero"] = i
        c["rotulo"] = f"{codigo}_c{i:02d}"
        anim = (c.get("prompt_animacao") or "").strip()
        if "lips closed" not in anim.lower():
            anim = f"{anim} {LIPS}".strip()
        c["prompt_animacao"] = anim[:1000]
        refs, fora = _refs(c.get("refs"), existentes)
        c["refs"] = refs or [ref_elenco(elenco)]
        descartadas += [f"c{i:02d}:{r}" for r in fora]
        cj = c.get("coadjuvante")
        if isinstance(cj, str) and cj.startswith("PERS-") and existentes is not None and cj not in existentes:
            raise ValueError(f"cena {i}: coadjuvante {cj} fora do catálogo; escolha um id PERS- da lista")
        img = c.get("prompt_imagem") or ""
        if "stickman" not in img.lower():
            c["prompt_imagem"] = (trava + img).strip()[:2000]
    return Storyboard.model_validate(d), descartadas


def storyboard_de_texto(texto: str, codigo: str) -> Storyboard:
    """Força código, ordem, elenco alternado e imagens_revisadas=false. Não chama rede; lê só o índice local do catálogo."""
    return _montar(texto, codigo)[0]


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
    sb, descartadas = _montar(texto, codigo)
    if sb.pode_gerar_video() or sb.imagens_revisadas:
        raise RuntimeError("storyboard não pode liberar vídeo nesta etapa")
    dest = _destino_ok(destino)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(sb.model_dump_json(indent=1), encoding="utf-8")
    return {
        "arquivo": str(dest),
        "cenas": len(sb.cenas),
        "elenco": sb.elenco,
        "refs_descartadas": descartadas,
        "imagens_revisadas": False,
        "pode_gerar_video": False,
        "gasto": GASTO_STORYBOARD.model_dump(),
    }
