"""Pedido LOOP do juiz Gemini (F7-02, t540): TEXTO autorizado por José em 25/10/2026.
Três checagens, o código decide:
 1. imagem×fala  — pranchas S01… + falas do roteiro (auditor_gemini.auditar, transmitir_texto=True);
 2. capa×título  — CAPA + título do SEO no mesmo pedido (corresponde_ao_titulo);
 3. loop textual — 1ª e última fala, só texto (templates/auditor/LOOP.txt, pipeline.auditor_texto).
Camofox PQBR 127.0.0.1:9387, sessão já logada, ações humanizadas; nenhum login novo. 2 rodadas no loop
textual: divergência → terceira_rodada. Veredito final: reprova > terceira_rodada > aprova_com_ressalva > aprova."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from temporalio import activity

VERSAO = "1.1.0"   # t544: + modelo
Veredito = Literal["aprova", "aprova_com_ressalva", "terceira_rodada", "reprova"]
ORDEM = ("reprova", "terceira_rodada", "aprova_com_ressalva", "aprova")


class ResultadoLoopGemini(BaseModel):
    """Contrato do resultado LOOP (v1.0.0). `publicavel` é derivado só pelo código."""
    model_config = ConfigDict(extra="forbid")
    versao: Literal["1.0.0", "1.1.0"] = VERSAO
    modelo: str = ""   # modelo Gemini confirmado no seletor
    codigo: str = Field(pattern=r"^PQBR-EP[0-9]{4,}$")
    imagem_fala: Veredito
    capa_titulo: Veredito
    loop_texto: Veredito
    veredito: Veredito
    motivos: list[str] = Field(default_factory=list)
    conversas: list[str] = Field(default_factory=list)
    visual_bruto: dict = Field(default_factory=dict)

    @property
    def publicavel(self) -> bool:
        return self.veredito in ("aprova", "aprova_com_ressalva")


def pior(*vs: str) -> str:
    return min(vs, key=ORDEM.index)


def decidir_loop_texto(respostas: list[str]) -> tuple[str, list[str]]:
    from ..pipeline.auditor_texto import decidir
    rs = [decidir(t) for t in respostas]
    if not rs: return "terceira_rodada", ["loop:sem_resposta"]
    vs = {r.veredito for r in rs}
    mot = sorted({f"loop:{m}" for r in rs for m in r.motivos})
    if "terceira_rodada" in vs or len(vs) > 1:
        return "terceira_rodada", mot + (["loop:divergencia"] if len(vs) > 1 else [])
    return rs[0].veredito, mot


def separar_visual(res: dict) -> tuple[str, str, list[str]]:
    """Do resultado VISUAL+TEXTO: imagem×fala e capa×título viram ressalva (métrica nunca reprova, REGRAS §5);
    segurança/divergência herdam o veredito do VISUAL."""
    v = res["veredito"]; mot = res.get("motivos", [])
    base = v if v in ("reprova", "terceira_rodada") else "aprova"
    imf = "aprova_com_ressalva" if any(":imagem_corresponde_a_fala" in m for m in mot) else base
    cap = "aprova_com_ressalva" if any("CAPA:corresponde_ao_titulo" in m for m in mot) else base
    if (res.get("bruto", {}).get("metricas", {}) or {}).get("imagem_corresponde_a_fala") is None and base == "aprova":
        imf = "terceira_rodada"      # texto não avaliado → fail-closed
    if (res.get("bruto", {}).get("metricas", {}) or {}).get("corresponde_ao_titulo") is None and base == "aprova":
        cap = "terceira_rodada"
    return imf, cap, mot


def combinar(codigo: str, visual: dict, loop_respostas: list[str], conversas: list[str]) -> ResultadoLoopGemini:
    imf, cap, mot_v = separar_visual(visual)
    lt, mot_l = decidir_loop_texto(loop_respostas)
    final = pior(imf, cap, lt, visual["veredito"] if visual["veredito"] in ("reprova", "terceira_rodada") else "aprova")
    if final == "aprova" and visual["veredito"] == "aprova_com_ressalva": final = "aprova_com_ressalva"
    return ResultadoLoopGemini(codigo=codigo, imagem_fala=imf, capa_titulo=cap, loop_texto=lt, veredito=final,
                               motivos=(mot_v + mot_l)[:30], conversas=conversas + visual.get("conversas", []),
                               visual_bruto=visual.get("bruto", {}))


def auditar_loop(codigo: str, slug: str, quadros: list[str], falas: list[str], bloco_visual: str, capa: str,
                 titulo: str, rodadas_loop: int = 2, persistir: bool = True) -> ResultadoLoopGemini:
    from .auditor_gemini import auditar, perguntar_gemini
    from ..pipeline.auditor_texto import montar_prompt
    if not falas or not titulo: raise ValueError("falas e título obrigatórios no LOOP")
    visual = auditar(codigo, slug, quadros, falas, bloco_visual, capa, rodadas=2, persistir=persistir,
                     transmitir_texto=True, titulo=titulo).model_dump()
    prompt = montar_prompt(falas[0], falas[-1]); resp, urls = [], []
    from .auditor_gemini import RespostaRecusada, _cfg
    espera = int(_cfg().get("gemini_loop_espera_s", 480))
    for _ in range(rodadas_loop):
        txt, url = "", ""
        for _t in range(2):   # t547: recusa = tentativa falha; 2ª falha → texto vazio → terceira_rodada (falha fechada)
            try:
                txt, url = perguntar_gemini([], prompt, espera_s=espera, marcador='"ultima_continua_na_primeira"'); break
            except RespostaRecusada:
                txt, url = "", ""
        resp.append(txt); urls.append(url)
    from . import auditor_gemini as ag
    return combinar(codigo, visual, resp, urls).model_copy(update={"modelo": ag.ULTIMO_MODELO or visual.get("modelo", "")})


@activity.defn
async def auditor_loop_gemini(codigo: str, slug: str, quadros: list[str], falas: list[str], bloco_visual: str,
                              capa: str, titulo: str) -> dict:
    import asyncio
    return (await asyncio.to_thread(auditar_loop, codigo, slug, quadros, falas, bloco_visual, capa, titulo)).model_dump()
