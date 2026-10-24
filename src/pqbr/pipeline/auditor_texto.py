"""Contrato local do LOOP textual F7-02; não chama Jev, Gemini ou outro provedor."""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

TEMPLATE = Path(__file__).resolve().parents[3] / "templates" / "auditor" / "LOOP.txt"
SimNao = Literal["sim", "nao"]


class RespostaLoop(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ultima_continua_na_primeira: SimNao
    fala_final_cortada_no_meio: SimNao


class ResultadoLoop(BaseModel):
    veredito: Literal["aprova", "reprova", "terceira_rodada"]
    motivos: list[str]
    resposta: RespostaLoop | None = None


def montar_prompt(primeira: str, ultima: str) -> str:
    """Monta pedido mínimo usando só as duas frases necessárias; não envia nada."""
    if not primeira.strip() or not ultima.strip():
        raise ValueError("primeira e última frases são obrigatórias")
    return (TEMPLATE.read_text(encoding="utf-8")
            .replace("__PRIMEIRA__", primeira.strip())
            .replace("__ULTIMA__", ultima.strip()))


def validar(texto: str) -> RespostaLoop:
    """Lê JSON estruturado de um adapter futuro; rejeita campos extras e valores inválidos."""
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip())
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j < i:
        raise ValueError("json_invalido")
    return RespostaLoop.model_validate_json(t[i:j + 1])


def decidir(texto: str) -> ResultadoLoop:
    """O código decide: loop ausente ou fala truncada reprova; saída inválida pede nova rodada."""
    try:
        r = validar(texto)
    except Exception as exc:  # noqa: BLE001
        return ResultadoLoop(veredito="terceira_rodada", motivos=[f"resposta_invalida:{type(exc).__name__}"])
    motivos = []
    if r.ultima_continua_na_primeira == "nao":
        motivos.append("ultima_fala_nao_emenda_na_primeira")
    if r.fala_final_cortada_no_meio == "sim":
        motivos.append("fala_final_cortada_no_meio")
    return ResultadoLoop(veredito="reprova" if motivos else "aprova", motivos=motivos or ["loop_textual_ok"], resposta=r)
