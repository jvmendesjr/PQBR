"""Vigia de atualizações das ferramentas sensíveis — atribuição do Dev (José t516).

Workflow semanal (Schedule a criar com OK do José): para cada ferramenta vigiada, lê a versão instalada e a última
publicada (PyPI / GitHub releases, só leitura), compara e gera RelatorioAtualizacoes curto com proposta.
NUNCA aplica atualização, não publica nada, não reinicia serviço. Esqueleto: activities e workflow prontos e testados;
ainda não registrados em worker nem agendados.
"""
from __future__ import annotations
import json, re, subprocess, urllib.request
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from ..contratos import FerramentaVigiada, ItemAtualizacao, RelatorioAtualizacoes

FILA = "pqbr-episodio"
VIGIADAS: list[dict] = [
    {"nome": "notebooklm-py", "fonte": "pypi", "alvo": "notebooklm-py", "python": "~/.pqbr/notebooklm/venv/bin/python",
     "notas": "https://github.com/teng-lin/notebooklm-py/releases"},
    {"nome": "camoufox", "fonte": "github", "alvo": "daijro/camoufox", "notas": "https://github.com/daijro/camoufox/releases"},
    {"nome": "temporalio (SDK)", "fonte": "pypi", "alvo": "temporalio", "python": "~/Workspace/PQBR/.venv/bin/python",
     "notas": "https://github.com/temporalio/sdk-python/releases"},
    {"nome": "temporal (servidor/CLI)", "fonte": "github", "alvo": "temporalio/cli", "notas": "https://github.com/temporalio/cli/releases"},
    {"nome": "pydantic-ai-slim", "fonte": "pypi", "alvo": "pydantic-ai-slim", "python": "~/Workspace/PQBR/.venv/bin/python",
     "notas": "https://github.com/pydantic/pydantic-ai/releases"},
    {"nome": "pydantic", "fonte": "pypi", "alvo": "pydantic", "python": "~/Workspace/PQBR/.venv/bin/python",
     "notas": "https://docs.pydantic.dev/latest/changelog/"},
    {"nome": "9router (modelos dos combos)", "fonte": "manual", "alvo": "config/modelos_9router.json",
     "notas": "conferir modelos mapeados por combo no painel do 9router"},
]


def _num(v: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", v or "")[:4])


def classificar(instalada: str, ultima: str) -> str:
    """Puro: 'em_dia' | 'patch' | 'minor' | 'major' | 'desconhecido'."""
    a, b = _num(instalada), _num(ultima)
    if not a or not b:
        return "desconhecido"
    if a >= b:
        return "em_dia"
    if a[0] != b[0]:
        return "major"
    if a[1:2] != b[1:2]:
        return "minor"
    return "patch"


PROPOSTA = {
    "em_dia": "nada a fazer",
    "patch": "atualizar após ler notas e rodar testes (risco baixo)",
    "minor": "ler notas; testar em canário antes; atualizar com OK do José",
    "major": "não atualizar sem plano: ler quebras, abrir proposta do Dev",
    "desconhecido": "conferir manualmente",
}


def montar_relatorio(itens: list[ItemAtualizacao], semana: str) -> RelatorioAtualizacoes:
    """Puro: resumo curto em uma linha por item fora do dia."""
    pend = [i for i in itens if i.situacao not in ("em_dia",)]
    linhas = [f"{i.nome}: {i.instalada or '?'} → {i.ultima or '?'} ({i.situacao}) — {i.proposta}" for i in pend]
    return RelatorioAtualizacoes(semana=semana, itens=itens,
                                 resumo="\n".join(linhas) or "Tudo em dia.", aplicado=False)


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "pqbr-vigia", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


@activity.defn
async def vigia_checar(f: dict) -> dict:
    """Só leitura: versão instalada (importlib.metadata no python indicado) e última publicada."""
    fv = FerramentaVigiada.model_validate(f)
    instalada = ultima = ""
    erro = None
    try:
        if fv.python and fv.fonte == "pypi":
            import os
            py = os.path.expanduser(fv.python)
            instalada = subprocess.run([py, "-c", f"import importlib.metadata as m;print(m.version({fv.alvo!r}))"],
                                       capture_output=True, text=True, timeout=30).stdout.strip()
        if fv.fonte == "pypi":
            ultima = _get_json(f"https://pypi.org/pypi/{fv.alvo}/json")["info"]["version"]
        elif fv.fonte == "github":
            ultima = _get_json(f"https://api.github.com/repos/{fv.alvo}/releases?per_page=1")[0]["tag_name"]
    except Exception as e:  # registra, não falha a semana inteira
        erro = type(e).__name__
    sit = classificar(instalada, ultima) if not erro else "desconhecido"
    return ItemAtualizacao(nome=fv.nome, instalada=instalada, ultima=ultima, situacao=sit,
                           proposta=PROPOSTA[sit] if not erro else f"falha na leitura ({erro}); conferir",
                           notas=fv.notas).model_dump()


@workflow.defn
class VigiaAtualizacoesWorkflow:
    @workflow.run
    async def run(self, semana: str) -> dict:
        itens = []
        for f in VIGIADAS:
            r = await workflow.execute_activity(vigia_checar, f, start_to_close_timeout=timedelta(minutes=2),
                                                retry_policy=RetryPolicy(maximum_attempts=2))
            itens.append(ItemAtualizacao.model_validate(r))
        return montar_relatorio(itens, semana).model_dump()


ATIVIDADES_VIGIA = [vigia_checar]
