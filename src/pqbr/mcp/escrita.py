"""Escrita de memória pelo MCP (t95u/t96u): o agente externo registra o que mudou e fica memorizado no Hindsight.
Barreiras: ferramenta `memoria_registrar` na política do papel; tags ⊆ escrita do papel e ⊆ tags da regra única
(hindsight_tags/política); commit, quando dado, precisa existir no repo; conteúdo passa pela barreira de segredos (reter)."""
from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Callable

from ..contratos.memoria_mcp import RegistroAlteracaoEntrada, RegistroMemoriaEntrada, RegistroMemoriaSaida
from ..contratos.politica import AcessoNegado, carregar
from ..governanca.estado_atual import ESTADO, TIPOS_EXIGEM, proximo_passo
from ..storage.hindsight_tags import TAG_OBS, tags_conteudo

RAIZ = Path(__file__).resolve().parents[3]


def commit_existe(h: str) -> bool:
    r = subprocess.run(["git", "-C", str(RAIZ), "cat-file", "-e", f"{h}^{{commit}}"], capture_output=True)
    return r.returncode == 0


def arquivos_do_commit(h: str) -> list[str]:
    r = subprocess.run(["git", "-C", str(RAIZ), "show", "--name-only", "--pretty=format:", h], capture_output=True, text=True)
    return [l for l in r.stdout.splitlines() if l.strip()]


def _tags(papel: str, e: RegistroMemoriaEntrada) -> list[str]:
    pode = set(carregar().de(papel).escrita)
    if e.tags:
        fora = set(e.tags) - pode
        if fora or TAG_OBS in e.tags:
            raise AcessoNegado(f"{papel} não escreve tags {sorted(fora or {TAG_OBS})}")
        return sorted(set(e.tags))
    return sorted(tags_conteudo("PQBR registro MCP", e.conteudo, pode)) or (["licao"] if "licao" in pode else [])


def registrar(papel: str, cliente: str, args: dict, *, exige_commit: bool = False,
              reter: Callable | None = None, verificar_commit: Callable[[str], bool] = commit_existe,
              listar_arquivos: Callable[[str], list[str]] = arquivos_do_commit, estado_txt: str | None = None) -> RegistroMemoriaSaida:
    e = (RegistroAlteracaoEntrada if exige_commit else RegistroMemoriaEntrada).model_validate(args)
    tags = _tags(papel, e)
    if not tags:
        raise AcessoNegado(f"{papel} não escreve memória")
    ok_commit = bool(e.commit) and verificar_commit(e.commit)
    if e.commit and not ok_commit:
        raise ValueError("commit não existe no repositório")
    tipo = getattr(e, "tipo", None)
    if tipo in TIPOS_EXIGEM and ESTADO not in listar_arquivos(e.commit):
        raise ValueError(f"{tipo} exige {ESTADO} atualizado no commit {e.commit}")
    ref = []
    if e.commit: ref.append(f"commit {e.commit}")
    if e.arquivos: ref.append("arquivos: " + ", ".join(e.arquivos))
    texto = e.conteudo + (f"\n\nReferência: {'; '.join(ref)}." if ref else "")
    ctx = f"PQBR registro MCP — cliente {cliente} ({papel})" + (f" — commit {e.commit}" if e.commit else "")
    if reter is None:
        from ..storage.hindsight import reter as reter_real
        reter = reter_real
    reter(texto, ctx, papel=papel, tags=tags, autor=cliente)
    hand = False
    if exige_commit and "estado" in carregar().de(papel).escrita:  # handoff p/ o próximo agente, visível a todos
        resumo = " ".join((e.handoff or e.conteudo).split())[:1500]
        reter(f"Handoff ({tipo}) de {cliente}, commit {e.commit}: {resumo}\nPróximo passo vigente: {proximo_passo(estado_txt)}"
              f"\nContinue por {ESTADO}.", f"PQBR handoff — cliente {cliente} ({papel}) — commit {e.commit}",
              papel=papel, tags=["estado"], autor=cliente)
        hand = True
    return RegistroMemoriaSaida(ok=True, autor=cliente, papel=papel, tags=tuple(tags), commit=e.commit,
                                commit_verificado=ok_commit, handoff_registrado=hand)
