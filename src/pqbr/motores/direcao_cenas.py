"""Porta + adaptadores da direção de cenas (passo 1 pós-roteiro).

Porta: `DiretorCenas`. Adaptador real: NotebookLM via notebooklm-py (activities já existentes).
Adaptador falso: devolve lista validável sem chamada de rede (testes).
Workflows/activities chamam a PORTA, nunca o CLI direto."""
from __future__ import annotations
import json, re
from typing import Protocol, runtime_checkable
from pqbr.contratos import ESTILO_PADRAO_STICKMAN
from pqbr.contratos.cena import CenaIndividual, elenco_alternado, protagonista_ref
from pqbr.contratos.direcao_cenas import VERSAO, DirecaoCenas
from pqbr.contratos.gasto import GASTO_DIRECAO_CENAS
from pqbr.pipeline import banco_fichas as bf
from pqbr.pipeline.validar_direcao_cenas import validar_lista


LIPS = "lips closed, only blinking and breathing."
_CONTRATO_VISUAL = (
    "Contrato visual CenaIndividual 2.0.0: uma cena por item; fala e narração em off e NAO entra nos prompts; "
    "prompt_animacao em ingles com a frase exata 'lips closed, only blinking and breathing'; "
    "enquadramento so plano_geral|plano_medio|plano_medio_curto|close; refs = ids do catalogo (PERS/AMB/OBJ/ANIM/FIG/SIT); "
    "personagem stickman; PERS-menina-rosa = mulher jovem adulta (nunca girl nem menina como idade)."
)


def _obj(texto: str) -> dict:
    t = re.sub(r"```(?:json)?", "", texto or "")
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        raise ValueError("direção sem JSON")
    return json.loads(t[i:j + 1])


def montar_prompt(codigo: str, n_cenas: int, resumo_catalogo: str, estilo: str = ESTILO_PADRAO_STICKMAN) -> str:
    elenco = elenco_alternado(codigo)
    prot = protagonista_ref(elenco)
    return (
        f"Com base no roteiro deste caderno, monte a direção das cenas do episódio {codigo}. "
        f"Protagonista fixo: {elenco} ({prot}). Não troque o protagonista. "
        f"Responda SÓ um JSON, sem texto fora dele, com exatamente {n_cenas} cenas (numeros 1..{n_cenas}). "
        f"Estilo obrigatório (cole no prompt_imagem de cada cena): {estilo}\n"
        f"{_CONTRATO_VISUAL}\n"
        f"Catálogo (ids em refs):\n{resumo_catalogo}\n"
        "Formato: {\"cenas\":[{\"fala\":\"...\",\"norte\":\"...\",\"inicio\":\"...\",\"fim\":\"...\","
        "\"movimento\":\"...\",\"enquadramento\":\"plano_medio\",\"prompt_imagem\":\"... stickman ...\","
        "\"prompt_animacao\":\"... lips closed, only blinking and breathing.\",\"refs\":[\"" + prot + "\"],"
        "\"epoca\":\"presente\",\"papel_personagem\":\"observa\",\"figurino\":\"atual_variavel\","
        "\"expressao\":\"...\",\"cenario_encaixe\":\"...\"}]}"
    )


def parse_cenas(texto: str, codigo: str, n_cenas: int) -> list[CenaIndividual]:
    d = _obj(texto)
    brutas = list(d.get("cenas") or [])
    if len(brutas) != n_cenas:
        raise ValueError(f"esperava {n_cenas} cenas, veio {len(brutas)}")
    saida: list[CenaIndividual] = []
    for i, c in enumerate(brutas, start=1):
        if not isinstance(c, dict):
            raise ValueError(f"cena {i} inválida")
        c = dict(c)
        c["versao"] = "2.0.0"
        c["numero"] = i
        c["rotulo"] = f"{codigo}-S{i:02d}"
        anim = (c.get("prompt_animacao") or "").strip()
        if "lips closed" not in anim.lower():
            anim = f"{anim} {LIPS}".strip()
        c["prompt_animacao"] = anim[:1000]
        saida.append(CenaIndividual.model_validate(c))
    return saida


@runtime_checkable
class DiretorCenas(Protocol):
    nome: str

    def direcionar(
        self,
        *,
        codigo: str,
        slug: str,
        caderno: str,
        n_cenas: int,
        estilo: str = ESTILO_PADRAO_STICKMAN,
    ) -> DirecaoCenas: ...


class AdaptadorNotebookLMDirecao:
    """Adaptador real: injeta fontes (resumo, estilo, contrato) no caderno do episódio e pergunta."""
    nome = "notebooklm"

    def direcionar(
        self,
        *,
        codigo: str,
        slug: str,
        caderno: str,
        n_cenas: int,
        estilo: str = ESTILO_PADRAO_STICKMAN,
    ) -> DirecaoCenas:
        import asyncio
        return asyncio.run(self.adirecionar(codigo=codigo, slug=slug, caderno=caderno, n_cenas=n_cenas, estilo=estilo))

    async def adirecionar(
        self,
        *,
        codigo: str,
        slug: str,
        caderno: str,
        n_cenas: int,
        estilo: str = ESTILO_PADRAO_STICKMAN,
    ) -> DirecaoCenas:
        from pqbr.workflows import notebooklm as n
        if not GASTO_DIRECAO_CENAS.pode_gastar or GASTO_DIRECAO_CENAS.meio != "chat_caderno":
            raise RuntimeError("gasto direção cenas não autoriza esta etapa")
        resumo = bf.resumo_para_prompt()
        await n.nlm_fonte(caderno, f"{slug}-catalogo-resumo", resumo)
        await n.nlm_fonte(caderno, f"{slug}-estilo-stickman", estilo)
        await n.nlm_fonte(caderno, f"{slug}-contrato-visual", _CONTRATO_VISUAL)
        pergunta = montar_prompt(codigo, n_cenas, resumo, estilo)
        erro = ""
        ultima: Exception | None = None
        for _ in range(2):
            txt = await n.nlm_perguntar(caderno, pergunta + (f" A resposta anterior foi inválida: {erro}. Corrija." if erro else ""))
            try:
                cenas = parse_cenas(txt, codigo, n_cenas)
                validar_lista(cenas)
                return DirecaoCenas(
                    codigo=codigo, slug=slug, caderno=caderno,
                    estilo_aplicado=estilo, cenas=cenas,
                )
            except Exception as e:  # noqa: BLE001
                ultima = e
                erro = str(e)[:300]
        raise RuntimeError(f"direção de cenas inválida após retries: {ultima}")


class AdaptadorFalsoDirecao:
    """Adaptador de teste: sem rede, devolve cenas mínimas válidas (stickman + adulta quando preciso)."""
    nome = "falso"

    def __init__(self, cenas: list[dict] | None = None):
        self._cenas = cenas

    def direcionar(
        self,
        *,
        codigo: str,
        slug: str,
        caderno: str,
        n_cenas: int,
        estilo: str = ESTILO_PADRAO_STICKMAN,
    ) -> DirecaoCenas:
        if self._cenas is not None:
            cenas = [CenaIndividual.model_validate({**c, "versao": "2.0.0"}) for c in self._cenas]
        else:
            prot = protagonista_ref(elenco_alternado(codigo))
            adulta = prot == "PERS-menina-rosa"
            base_img = (
                "Cartoon 2D flat colorido stickman, cabeça redonda branca, contorno preto, "
                + ("mulher jovem adulta stickman " if adulta else "stickman ")
                + f"@{prot} holds a cup in a cafe kitchen, full body, 9:16."
            )
            cenas = []
            for i in range(1, n_cenas + 1):
                cenas.append(CenaIndividual(
                    numero=i, rotulo=f"{codigo}-S{i:02d}",
                    fala=f"Fala da cena {i} sobre o tema do café fraco no Brasil.",
                    norte=f"mostrar o ponto {i} do café fraco",
                    inicio="Personagem stickman em pé no café, xícara na mão, plano médio.",
                    fim="Mesma câmera e luz, personagem olha a xícara com expressão de surpresa.",
                    movimento="ergue a xícara; slow push-in",
                    enquadramento="plano_medio",
                    prompt_imagem=base_img,
                    prompt_animacao=f"Locked camera, slow push-in, {LIPS}",
                    refs=[prot, "AMB-cafe", "OBJ-caneca"],
                    papel_personagem="observa", figurino="atual_variavel",
                    expressao="sobrancelhas levantadas, boca de reação fechada",
                    cenario_encaixe="em pé no chão ao lado do balcão, café de bairro",
                ))
        validar_lista(cenas)
        return DirecaoCenas(
            codigo=codigo, slug=slug, caderno=caderno,
            estilo_aplicado=estilo, cenas=cenas,
        )


def diretor_cenas(nome: str | None = None) -> DiretorCenas:
    """Seleção simples; testes passam AdaptadorFalsoDirecao direto."""
    nome = nome or "notebooklm"
    if nome == "notebooklm":
        return AdaptadorNotebookLMDirecao()
    if nome == "falso":
        return AdaptadorFalsoDirecao()
    raise KeyError(f"DiretorCenas sem adaptador: {nome}")
