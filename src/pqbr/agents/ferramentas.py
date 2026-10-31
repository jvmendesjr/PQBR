"""Ferramentas só leitura para os agentes PydanticAI (F1-05, P13).

Aceite do ROADMAP: módulo src/pqbr/agents/ferramentas.py, filtrado por
config/politica_papeis.json, ferramenta nativa do PydanticAI, sem escrita,
limite de chamadas, testes com TestModel. Sem MCP interno: este módulo
não cria nem chama um servidor MCP; as ferramentas nativas aqui são
leitura de arquivo local (ESTADO-ATUAL e código visível ao papel).

memoria_buscar é permitida pela política para vários papéis, mas não
ganha ferramenta nativa neste módulo: a busca de memória continua pelo
caminho existente (pqbr.storage.hindsight), sem servidor MCP interno.
Anexar uma ferramenta de memória aqui seria recriar esse caminho.

Papel desconhecido ou sem ferramenta de leitura => negado (fail-closed),
na mesma regra de pqbr.contratos.politica.
"""
from __future__ import annotations
from pathlib import Path

from ..contratos.politica import AcessoNegado, PoliticaPapeis, carregar

RAIZ = Path(__file__).resolve().parents[3]
LEITURA: tuple[str, ...] = ("memoria_buscar", "codigo_consultar", "estado_ler")
LIMITE_PADRAO = 20
_MAX_TEXTO = 4000


class LimiteChamadas(ValueError):
    """Chamada além do limite por execução do agente."""


class ContadorChamadas:
    """Contador simples por ferramenta, sem estado global."""

    def __init__(self, limite: int = LIMITE_PADRAO) -> None:
        self.limite = limite
        self.por_nome: dict[str, int] = {}

    @property
    def total(self) -> int:
        return sum(self.por_nome.values())

    def contar(self, nome: str) -> int:
        if self.total >= self.limite:
            raise LimiteChamadas(f"limite de {self.limite} chamadas de ferramenta atingido")
        self.por_nome[nome] = self.por_nome.get(nome, 0) + 1
        return self.por_nome[nome]


def ferramentas_para_papel(papel: str, politica: PoliticaPapeis | None = None) -> tuple[str, ...]:
    """Ferramentas de leitura do papel, na ordem da política. Papel desconhecido => AcessoNegado."""
    pol = politica or carregar()
    return tuple(n for n in pol.de(papel).ferramentas if n in LEITURA)


def exigir_leitura(papel: str, nome: str, politica: PoliticaPapeis | None = None) -> None:
    """Fail-closed: só aceita ferramenta de leitura que a política dá ao papel."""
    if nome not in ferramentas_para_papel(papel, politica):
        raise AcessoNegado(f"{papel} não usa a ferramenta de leitura {nome}")


def ler_estado(raiz: Path | None = None) -> str:
    """Só leitura: texto de docs/ESTADO-ATUAL.md, truncado. Nunca escreve."""
    return (Path(raiz or RAIZ) / "docs" / "ESTADO-ATUAL.md").read_text(encoding="utf-8")[:_MAX_TEXTO]


def ler_arquivo_visivel(papel: str, caminho: str, politica: PoliticaPapeis | None = None,
                        raiz: Path | None = None) -> str:
    """Só leitura: lê um arquivo do repo só se o papel o vê (ve_caminho). Sem execução, sem escrita."""
    pol = politica or carregar()
    exigir_leitura(papel, "codigo_consultar", pol)
    if not pol.ve_caminho(papel, caminho):
        raise AcessoNegado(f"{papel} não vê o caminho {caminho!r}")
    base = Path(raiz or RAIZ).resolve()
    alvo = (base / caminho).resolve()
    if base not in alvo.parents and alvo != base:
        raise AcessoNegado(f"caminho fora do repo: {caminho!r}")
    return alvo.read_text(encoding="utf-8")[:_MAX_TEXTO]


def anexar_ferramentas_leitura(agente, papel: str, politica: PoliticaPapeis | None = None,
                               limite: int = LIMITE_PADRAO):
    """Anexa as ferramentas nativas de leitura ao agente (tool_plain) e devolve (agente, contador).

    Só anexa o que a política permite: estado_ler vira a ferramenta
    ler_estado e codigo_consultar vira consultar_codigo.
    memoria_buscar não é anexada aqui (ver docstring do módulo).
    """
    pol = politica or carregar()
    nomes = ferramentas_para_papel(papel, pol)
    contador = ContadorChamadas(limite)
    if "estado_ler" in nomes:
        @agente.tool_plain
        def ler_estado() -> str:  # noqa: F811 - ferramenta nativa, nome intencional
            contador.contar("estado_ler")
            try:
                return (RAIZ / "docs" / "ESTADO-ATUAL.md").read_text(encoding="utf-8")[:_MAX_TEXTO]
            except OSError:
                return "negado: ESTADO-ATUAL indisponível"
    if "codigo_consultar" in nomes:
        @agente.tool_plain
        def consultar_codigo(caminho: str) -> str:
            contador.contar("codigo_consultar")
            # Ferramenta nativa não pode derrubar o run com exceção: caminho negado
            # vira mensagem segura, sem detalhe do que existe fora do permitido.
            try:
                return ler_arquivo_visivel(papel, caminho, pol)
            except (AcessoNegado, OSError):
                return "negado: caminho fora do permitido para o papel" 
    return agente, contador
