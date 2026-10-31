"""Adaptador codebase-memory-mcp por papel (migração para codebase-memory-mcp, 2026-10-29).

Ressalva (ordem do José, 29/10/2026): se `GitNexus` for chamado acidentalmente nesta aplicação, leia-se codebase-memory-mcp.

O CBM é local no servidor (~/.local/opt/codebase-memory-mcp/codebase-memory-mcp,
fora do repo; a PQBR só registra o índice dela, projeto "PQBR"). Toda resposta é
filtrada pelos caminhos que o papel pode ver; papel desconhecido ou sem a
ferramenta `codigo_consultar` => negado. Só CLI/stdio local; nada de --http,
nada de Lens (ui_enabled=false).

Mapeamento (interface externa do `codigo` não muda: query|context|impact):
- query   -> search_graph, com as linhas convertidas em definitions e filtradas
- context -> get_code_snippet em modo outline (resolve e desambigua, sem source) + trace_path both depth 3
- impact  -> get_code_snippet em modo outline (resolve e desambigua, sem source) + trace_path inbound depth 3
O context do backend anterior também não devolvia source, só metadados do símbolo e
vizinhos. Devolver source pelo MCP tripa a barreira de segredos (falso
positivo do regex de e-mail sobre decoradores como `@activity.defn`) e pode
vazar segredo embutido no código; quem precisa do source lê o arquivo nas
linhas indicadas, fora do `codigo`.
Ambiguidade é sempre explícita: nome com vários candidatos devolve
status "ambiguous" com sugestões (filtradas pelo papel), nunca o primeiro
candidato em silêncio. Processos e classificação de risco
do backend anterior não têm equivalente no CBM e não são emulados: impact devolve
risco "sem_equivalente" com nota, em vez de um escore inventado.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Callable

from ..contratos.politica import carregar

BIN = os.environ.get(
    "PQBR_CBM_BIN",
    str(Path.home() / ".local/opt/codebase-memory-mcp/codebase-memory-mcp"),
)
PROJECT = os.environ.get("PQBR_CBM_PROJECT", "PQBR")
REPO = str(Path(__file__).resolve().parents[3])
COMANDOS = {"query", "context", "impact"}


def _relativizar(caminho: str) -> str:
    if not caminho:
        return caminho
    p = Path(caminho)
    if p.is_absolute():
        try:
            return str(p.relative_to(REPO))
        except ValueError:
            return caminho
    return caminho.lstrip("./")


def _tool(nome: str, flags: list[str]) -> Any:
    r = subprocess.run(
        [BIN, "cli", nome, "--project", PROJECT, *flags, "--format", "json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if r.returncode != 0:
        detalhe = "\n".join(
            ln for ln in (r.stderr or "").splitlines() if "level=warn" not in ln
        )[-500:]
        if "symbol not found" in detalhe:
            return {"status": "nao_encontrado_cli", "texto": detalhe}
        raise RuntimeError(f"codebase-memory-mcp {nome} falhou (exit {r.returncode}): {detalhe}")
    saida = r.stdout or ""
    inicio = saida.find("{")
    if inicio >= 0:
        try:
            return json.loads(saida[inicio:])
        except json.JSONDecodeError:
            pass
    return {"texto": saida.strip()}


def _filtrar(no: Any, ve: Callable[[str], bool]) -> Any:
    if isinstance(no, dict):
        fp = None
        for chave in ("filePath", "file", "file_path"):
            if chave in no:
                fp = no[chave]
                break
        if fp is not None:
            rel = _relativizar(fp)
            if not ve(rel):
                return None
        qn_prefix = no.get("qn_prefix")
        if qn_prefix is not None:
            segmentos = qn_prefix.split(".")
            if segmentos and segmentos[0] == "PQBR":
                segmentos = segmentos[1:]
            derivado = "/".join(segmentos)
            if not derivado or not ve(derivado):
                return None
        filtrado = {k: v for k, v in ((k, _filtrar(v, ve)) for k, v in no.items()) if v is not None}
        if fp is not None:
            rel = _relativizar(fp)
            filtrado["filePath"] = rel
            if "file" in filtrado:
                filtrado["file"] = rel
            if "file_path" in filtrado:
                filtrado["file_path"] = rel
        return filtrado
    if isinstance(no, list):
        return [x for x in (_filtrar(i, ve) for i in no) if x is not None]
    return no


def _query(alvo: str) -> Any:
    r = _tool("search_graph", ["--query", alvo])
    if isinstance(r, dict) and "cols" in r and "rows" in r:
        cols = r["cols"]
        definitions = []
        for linha in r["rows"]:
            d = dict(zip(cols, linha))
            definitions.append(
                {
                    "qn": d.get("qn"),
                    "label": d.get("label"),
                    "filePath": d.get("file"),
                    "lines": d.get("lines"),
                    "rank": d.get("rank"),
                }
            )
        return {
            "definitions": definitions,
            "total": r.get("total"),
            "search_mode": r.get("search_mode"),
        }
    return r


def _resolver(alvo: str) -> Any:
    r = _tool("get_code_snippet", ["--qualified-name", alvo, "--source-mode", "outline"])
    if isinstance(r, dict):
        r.pop("source", None)
    if isinstance(r, dict) and r.get("status") in ("ambiguous", "nao_encontrado_cli"):
        if r.get("status") == "nao_encontrado_cli":
            return {"status": "nao_encontrado", "alvo": alvo, "detalhe": r.get("texto", "")[:200]}
        return r
    if isinstance(r, dict) and "qualified_name" in r:
        return r
    detalhe = r.get("texto", "")[:200] if isinstance(r, dict) else ""
    return {"status": "nao_encontrado", "alvo": alvo, "detalhe": detalhe}


def _contexto(alvo: str) -> Any:
    s = _resolver(alvo)
    if s.get("status") in ("ambiguous", "nao_encontrado"):
        return s
    trace = _tool(
        "trace_path",
        ["--function-name", s["qualified_name"], "--direction", "both", "--depth", "3"],
    )
    if isinstance(trace, dict) and trace.get("status") == "ambiguous":
        return {"symbol": s, "trace": trace, "epistemic": "exact"}
    return {
        "symbol": s,
        "trace": trace,
        "epistemic": "exact",
        "nota": "processos do backend anterior não têm equivalente no CBM e não são emulados",
    }


def _impacto(alvo: str) -> Any:
    s = _resolver(alvo)
    if s.get("status") in ("ambiguous", "nao_encontrado"):
        return s
    trace = _tool(
        "trace_path",
        ["--function-name", s["qualified_name"], "--direction", "inbound", "--depth", "3"],
    )
    if isinstance(trace, dict) and trace.get("status") == "ambiguous":
        return {"symbol": s, "trace": trace, "epistemic": "exact"}
    callers = trace.get("callers", {}) if isinstance(trace, dict) else {}
    return {
        "target": s,
        "direction": "upstream",
        "impactedCount": callers.get("callers_total", 0) if isinstance(callers, dict) else 0,
        "risk": "sem_equivalente",
        "riskNote": (
            "O CBM não classifica risco como o backend anterior; nenhum escore é emulado. "
            "Ausência de chamadores não prova que o símbolo não é usado: chamadas "
            "por nome em string (ex.: atividades Temporal) não geram aresta no grafo. "
            "Confirme com busca de texto antes de tratar a mudança como segura."
        ),
        "epistemic": "exact",
        "trace": trace,
    }


def _cli(args: list[str]) -> Any:
    comando, alvo = args[0], args[1]
    if comando == "query":
        return _query(alvo)
    if comando == "context":
        return _contexto(alvo)
    if comando == "impact":
        return _impacto(alvo)
    raise ValueError(f"comando não permitido: {comando}")


def consultar(papel: str, comando: str, alvo: str, executor: Callable[[list[str]], Any] = _cli) -> Any:
    pol = carregar()
    pol.exigir_ferramenta(papel, "codigo_consultar")
    if comando not in COMANDOS:
        raise ValueError(f"comando não permitido: {comando}")
    resultado = _filtrar(executor([comando, alvo]), lambda c: pol.ve_caminho(papel, c)) or {}
    if (
        isinstance(resultado, dict)
        and resultado.get("status") == "ambiguous"
        and not resultado.get("suggestions")
    ):
        return {"status": "negado", "motivo": "nenhum candidato visível para o papel"}
    return resultado
