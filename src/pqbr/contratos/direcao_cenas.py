"""Direção de cenas individuais pós-roteiro (t161u / José 30/10/2026; rótulo 2.0.0 em 31/10/2026).

O NotebookLM (pai intelectual) devolve a direção e os prompts por cena; o Temporal
valida fail-closed como lista de `CenaIndividual` 2.0.0 antes do adaptador Flow (passo 2, pendente).
Versão SemVer própria deste envelope (independente de CenaIndividual)."""
from __future__ import annotations
from typing import Literal
from pydantic import Field, model_validator
from . import Contrato
from .cena import CenaIndividual

VERSAO = "2.0.0"


class DirecaoCenas(Contrato):
    """Envelope versionado: saída validada da etapa direção (passo 1 pós-roteiro)."""
    versao: Literal["2.0.0"] = VERSAO
    codigo: str = Field(pattern=r"^PQBR-EP[0-9]{4,}$")
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,60}$")
    caderno: str = Field(min_length=8, max_length=80)
    estilo_aplicado: str = Field(min_length=20, max_length=900)
    cenas: list[CenaIndividual] = Field(min_length=2, max_length=60)
    briefing_id: str | None = Field(default=None, max_length=80)
    proximo: Literal["flow_cenas_individuais_pendente"] = "flow_cenas_individuais_pendente"

    @model_validator(mode="after")
    def _ordem_e_rotulos(self):
        nums = [c.numero for c in self.cenas]
        if nums != list(range(1, len(self.cenas) + 1)):
            raise ValueError("cenas devem ser 1..N sem buraco")
        for c in self.cenas:
            if not c.rotulo.startswith(self.codigo + "-S"):
                raise ValueError(f"rótulo {c.rotulo} fora do código {self.codigo}")
        return self
