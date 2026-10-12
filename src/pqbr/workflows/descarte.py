"""Descarte de caderno de TESTE pelo fluxo (José 12/10 18:06; LACUNAS itens 4 e 5).
reclassificar (classe 'pesquisa', com motivo) → exportar tudo (CLI) → arquivar em 3 cópias (Drive Bíblia, repo, Postgres) + Hindsight
→ verificar as 3 → só então ApagarCadernoWorkflow(teste=True) apaga pelo id. Qualquer cópia falhou = não apaga (exceção, workflow para)."""
from __future__ import annotations
import hashlib, json, shutil
from datetime import timedelta
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field
from temporalio import activity, workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from .notebooklm import FILA_NOTEBOOKLM, UUID, MESTRES_PROIBIDOS
    from .pacote import (FILA_EPISODIO, RAIZ, ApagarCadernoWorkflow, nlm_exportar_caderno, _banco, _pasta_biblia)

REPO_ARQ = "docs/pesquisas/arquivo-cadernos"


class PedidoDescarteTeste(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    caderno: str = Field(pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    rotulo: str = Field(pattern=r"^[a-z0-9-]{3,60}$")
    motivo: str = Field(min_length=10)
    videos: list[str] = []   # caminhos locais extras (vídeo gerado), arquivados junto


class CopiasVerificadas(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    postgres: int
    drive: int
    repo: int
    hindsight: bool
    bytes: int

    @property
    def completas(self) -> bool:
        return self.postgres > 0 and self.postgres == self.drive == self.repo and self.hindsight


def tipo_arquivo(nome: str) -> str:
    """Puro; testado."""
    return ("video" if nome.endswith(".mp4") else "resposta" if nome.startswith("respostas") else
            "metadados" if nome.startswith("metadados") else "fonte")


@activity.defn
async def registro_reclassificar_teste(caderno: str, motivo: str) -> str:
    if caderno in MESTRES_PROIBIDOS: raise RuntimeError("caderno mestre proibido")
    with _banco() as c:
        r = c.execute("update pqbr.cadernos_episodio set classe = 'pesquisa' where caderno_id = %s and apagado_em is null"
                      " and publicado_em is null returning titulo", (caderno,)).fetchone()
        if not r: raise RuntimeError("caderno não registrado, já apagado ou publicado: recusado")
        c.commit(); return r[0]


@activity.defn
async def arquivar_teste_3copias(caderno: str, rotulo: str, arquivos: list[str], motivo: str) -> dict:
    from ..integrations import drive
    from ..storage.hindsight import reter
    arqs = [Path(a) for a in arquivos if Path(a).is_file()]
    if not arqs: raise RuntimeError("nada exportado")
    repo = Path(RAIZ) / REPO_ARQ / f"{caderno[:8]}_{rotulo}"; repo.mkdir(parents=True, exist_ok=True)
    pasta = drive.garantir_pasta(f"PQBR/00_Biblia_Visual/cadernos-teste/{caderno[:8]}_{rotulo}")
    with _banco() as c:
        for f in arqs:
            dados = f.read_bytes(); t = tipo_arquivo(f.name)
            shutil.copy2(f, repo / f.name)
            did = drive.enviar(str(f), pasta)["id"]
            c.execute("insert into pqbr.arquivo_caderno (caderno_id, tipo, nome, sha256, bytes, drive_id, conteudo) values (%s,%s,%s,%s,%s,%s,%s)"
                      " on conflict (caderno_id, tipo, nome) do update set sha256 = excluded.sha256, bytes = excluded.bytes, drive_id = excluded.drive_id",
                      (caderno, t, f.name, hashlib.sha256(dados).hexdigest(), len(dados), did, None if t == "video" else dados.decode("utf-8", "replace")))
        c.execute("update pqbr.cadernos_episodio set arquivado_em = now() where caderno_id = %s", (caderno,)); c.commit()
    resumo = "\n".join(f"- {f.name} ({f.stat().st_size} bytes)" for f in arqs)
    texto = f"Caderno de teste descartado {caderno} ({rotulo}). Motivo: {motivo}. Arquivado em Drive 00_Biblia_Visual/cadernos-teste, {REPO_ARQ} e pqbr.arquivo_caderno:\n{resumo}"
    for f in arqs:
        if f.suffix in (".md", ".json"): texto += f"\n\n## {f.name}\n" + f.read_text(errors="replace")[:1500]
    reter(texto[:3500], f"PQBR arquivo de caderno de teste — {rotulo}")
    (repo / "HINDSIGHT.ok").write_text(hashlib.sha256(texto[:3500].encode()).hexdigest())
    return {"repo": str(repo), "drive_pasta": pasta, "arquivos": [f.name for f in arqs]}


@activity.defn
async def verificar_teste_3copias(caderno: str, repo: str) -> CopiasVerificadas:
    with _banco() as c:
        rows = c.execute("select nome, bytes, drive_id from pqbr.arquivo_caderno where caderno_id = %s", (caderno,)).fetchall()
    d = Path(repo)
    n_repo = sum(1 for nome, b, _ in rows if (d / nome).is_file() and (d / nome).stat().st_size == int(b))
    cop = CopiasVerificadas(postgres=len(rows), drive=sum(1 for r in rows if r[2]), repo=n_repo,
                            hindsight=(d / "HINDSIGHT.ok").is_file(), bytes=sum(int(r[1]) for r in rows))
    if not cop.completas: raise RuntimeError(f"arquivo NÃO verificado — não apagar: {cop.model_dump()}")
    with _banco() as c:
        c.execute("update pqbr.cadernos_episodio set verificado_em = now(), copias = %s where caderno_id = %s",
                  (json.dumps(cop.model_dump()), caderno)); c.commit()
    return cop


@workflow.defn
class DescartarCadernoTesteWorkflow:
    @workflow.run
    async def run(self, p: PedidoDescarteTeste) -> dict:
        r = dict(start_to_close_timeout=timedelta(minutes=10), retry_policy=RetryPolicy(maximum_attempts=2))
        await workflow.execute_activity(registro_reclassificar_teste, args=[p.caderno, p.motivo], task_queue=FILA_EPISODIO, **r)
        exp = await workflow.execute_activity(nlm_exportar_caderno, args=[p.caderno, f"TESTE-{p.rotulo}"], task_queue=FILA_NOTEBOOKLM,
                                              start_to_close_timeout=timedelta(minutes=20), retry_policy=RetryPolicy(maximum_attempts=2))
        arq = await workflow.execute_activity(arquivar_teste_3copias, args=[p.caderno, p.rotulo, [*exp, *p.videos], p.motivo],
                                              task_queue=FILA_EPISODIO, start_to_close_timeout=timedelta(minutes=30), retry_policy=RetryPolicy(maximum_attempts=2))
        cop = await workflow.execute_activity(verificar_teste_3copias, args=[p.caderno, arq["repo"]], task_queue=FILA_EPISODIO, **r)
        res = await workflow.execute_child_workflow(ApagarCadernoWorkflow.run, args=[p.caderno, "", "", True],
                                                    id=f"apagar-teste-{p.caderno}", task_queue=FILA_EPISODIO)
        return {"copias": cop.model_dump(), "arquivo": arq, "apagar": res}


ATIVIDADES_DESCARTE = [registro_reclassificar_teste, arquivar_teste_3copias, verificar_teste_3copias]
