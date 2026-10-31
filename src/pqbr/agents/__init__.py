"""Fábrica de agentes PydanticAI (ADR-011, t510).

O agente só GERA e VALIDA (saída = contrato Pydantic v2). Efeito colateral (Postgres, Telegram, Drive)
fica em atividades Temporal separadas. Persona: company/agents/<papel>/AGENTS.md. Combo: config/modelos_9router.json.
Chave só por env (NINEROUTER_API_KEY, arquivo 600 do worker); nunca logada."""
from __future__ import annotations
import logging, os, re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..kit import router9

log = logging.getLogger("pqbr.agents")
RAIZ = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Papel:
    slug: str
    fallback: tuple[str, ...] = ()          # combos extras, em ordem (só combos core / simples)
    max_tokens: int = 1500
    temperatura: float = 0.4
    extras: dict = field(default_factory=dict)


# t512: 8 papéis. Roteirista, SEO e Caçador viraram etapas de workflow que chamam o MotorIntelectual; Comunidade adiada.
# t145u: 9º papel, motion (monta o bloco de motion graphics a partir do catálogo; não julga).
REGISTRO: dict[str, Papel] = {
    "diretor": Papel("diretor"),
    "lider-editorial": Papel("lider-editorial", fallback=("core-baixo",)),   # monta pedidos ao motor e valida respostas
    "pesquisador-origem": Papel("pesquisador-origem"),
    "auditor": Papel("auditor", fallback=("core-revisao",)),
    "lider-compliance": Papel("lider-compliance"),
    "guardiao-seguranca": Papel("guardiao-seguranca"),
    "observador": Papel("observador"),
    "dev": Papel("dev", fallback=("core-revisao",), temperatura=0.1),        # só diagnostica e propõe; nunca aplica
    "motion": Papel("motion", fallback=("core-medio",), temperatura=0.2),    # preso ao catálogo; texto só do bloco de números travados
}


def persona(papel: str) -> str:
    """Corpo do AGENTS.md sem o frontmatter YAML."""
    txt = (RAIZ / "company" / "agents" / papel / "AGENTS.md").read_text(encoding="utf-8")
    return re.sub(r"\A---\n.*?\n---\n", "", txt, flags=re.S).strip()


def modelo_9router(combo: str):
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider
    chave = os.environ["NINEROUTER_API_KEY"]
    return OpenAIChatModel(combo, provider=OpenAIProvider(base_url=router9.URL, api_key=chave))


def criar_agente(papel: str, output_type: Any, instrucoes_extra: str = "", model: Any = None):
    """Agent tipado para o papel. `model` permite injetar TestModel nos testes."""
    from pydantic_ai import Agent
    from pydantic_ai.models.fallback import FallbackModel
    p = REGISTRO[papel]
    combos = (router9.combo(papel), *p.fallback)
    if model is None:
        ms = [modelo_9router(c) for c in combos]
        model = ms[0] if len(ms) == 1 else FallbackModel(*ms)
    mt = p.max_tokens
    instr = persona(papel) + ("\n\n" + instrucoes_extra if instrucoes_extra else "")
    ag = Agent(model, output_type=output_type, instructions=instr, name=papel, retries=2,
               model_settings={"max_tokens": mt, "temperature": p.temperatura})
    # F1-05: ferramentas de leitura anexadas por padrão, filtradas pela política.
    # Papéis sem ferramenta nativa (ex.: lider-editorial, só memoria_buscar) não mudam.
    from .ferramentas import anexar_ferramentas_leitura
    anexar_ferramentas_leitura(ag, papel)
    return ag, combos


def _tokens(r) -> int | None:
    u = getattr(r, "usage", None)
    u = u() if callable(u) else u
    return getattr(u, "total_tokens", None) or ((getattr(u, "input_tokens", 0) or 0) + (getattr(u, "output_tokens", 0) or 0)) or None


async def rodar(papel: str, output_type: Any, pedido: str, instrucoes_extra: str = "", model: Any = None) -> tuple[Any, dict]:
    """Roda o agente e devolve (saída validada, meta). meta registra combo pedido, modelo que respondeu e fallback."""
    ag, combos = criar_agente(papel, output_type, instrucoes_extra, model)
    r = await ag.run(pedido)
    tk = _tokens(r)
    respondeu = getattr(r.response, "model_name", None) or "?"
    meta = {"papel": papel, "combo": combos[0], "combos": list(combos), "modelo": respondeu,
            "fallback": bool(len(combos) > 1 and respondeu in combos[1:]),   # 9router devolve o modelo real, não o combo: fallback do 9router fica invisível aqui
            "tokens": tk}
    log.info("agente %s combo=%s modelo=%s fallback=%s", papel, meta["combo"], respondeu, meta["fallback"])
    return r.output, meta
