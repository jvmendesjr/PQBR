"""Cadernos efêmeros (t459, José 12/10/2026). Sem caderno mestre permanente no NotebookLM.
Pacote canônico = persona + comandos/prompts + contrato editorial + bloco visual §16.7, versionado por sha256 no
Postgres local (`pqbr.pacote_canonico`, fonte de verdade) e espelhado no Drive `00_Biblia_Visual/pacote-<hash12>/`.
Ciclo do caderno do episódio: criar ("Short - <código> - <slug>", registrado em `pqbr.cadernos_episodio`) → persona →
injetar pacote → fonte/roteiro → gerar → arquivar (fontes, respostas, vídeo → Drive + `pqbr.arquivo_caderno`) →
publicação → **D+2** → **verificar as cópias (regra permanente)** → apagar **pelo id registrado para o código do episódio** (nunca por título), com allowlist
(título `Short - <código> - …`, dono, UUID completo, registro arquivado) e `MESTRES_PROIBIDOS`.
Atividades de banco/Drive rodam na fila `episodio-pqbr`; as da CLI do NotebookLM na `notebooklm-pqbr`."""
from __future__ import annotations
import asyncio, hashlib, json, os, re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from temporalio import activity, workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from .notebooklm import FILA_NOTEBOOKLM, MESTRES_PROIBIDOS, UUID, CODIGO, titulo_caderno, _cli, _json, _ids

RAIZ = Path(os.environ.get("PQBR_RAIZ", "/home/pc/Workspace/PQBR"))
PACOTES = Path(os.environ.get("PQBR_PACOTE_DIR", "/home/pc/.pqbr/pacote"))
EXPORT = Path(os.environ.get("PQBR_CADERNO_EXPORT_DIR", "/home/pc/.pqbr/cadernos-arquivo"))
FILA_EPISODIO = "episodio-pqbr"
D_APAGAR = timedelta(hours=48)
FONTES_PACOTE = {   # nome do item → arquivo do repo (o bloco §16.7 é extraído do contrato)
    "persona": "templates/notebooklm/persona-pqbr.txt",
    "comandos_prompts": "templates/notebooklm/comandos-pqbr.md",
    "contrato_editorial": "docs/CONTRATO-EDITORIAL.md",
}


def bloco_visual_16_7(contrato: str) -> str:
    sec = contrato.split("### 16.7", 1)[1]
    m = re.search(r"```\n(.*?)```", sec, re.S)
    if not m or "[ESTILO]" not in m.group(1): raise ValueError("bloco §16.7 não encontrado no contrato")
    return m.group(1).strip()


def montar_pacote(raiz: Path = RAIZ) -> dict:
    """Itens + hash sha256 do JSON canônico (ordem de chaves fixa). Determinístico."""
    itens = {k: (raiz / v).read_text(encoding="utf-8") for k, v in FONTES_PACOTE.items()}
    itens["bloco_visual_16_7"] = bloco_visual_16_7(itens["contrato_editorial"])
    h = hashlib.sha256(json.dumps(itens, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return {"hash": h, "itens": itens, "origem": {**FONTES_PACOTE, "bloco_visual_16_7": "docs/CONTRATO-EDITORIAL.md §16.7"}}


def texto_fonte_pacote(p: dict) -> str:
    """Uma única fonte para o caderno (menos fontes = menos ruído no NotebookLM)."""
    partes = [f"# PQBR — pacote canônico {p['hash'][:12]}\n"]
    for k in ("persona", "comandos_prompts", "bloco_visual_16_7", "contrato_editorial"):
        partes.append(f"\n\n## {k}\n\n{p['itens'][k]}")
    return "".join(partes)


def escrever_pacote(p: dict) -> Path:
    d = PACOTES / p["hash"][:12]; d.mkdir(parents=True, exist_ok=True)
    for k, v in p["itens"].items(): (d / f"{k}.md").write_text(v, encoding="utf-8")
    (d / "PQBR-pacote.md").write_text(texto_fonte_pacote(p), encoding="utf-8")
    (d / "manifesto.json").write_text(json.dumps({"hash": p["hash"], "origem": p["origem"]}, ensure_ascii=False, indent=1))
    return d


def _pasta_biblia() -> str:
    return json.loads((RAIZ / "config/drive_pastas.json").read_text())["00_Biblia_Visual"]


def _banco():
    from ..storage.banco import conectar
    return conectar("pqbr_app")


# ---------------- fila episodio-pqbr: banco + Drive ----------------
@activity.defn
async def pacote_garantir() -> dict:
    """Registra a versão atual (se nova), marca como ativa e espelha no Drive. Idempotente por hash."""
    p = montar_pacote(); d = escrever_pacote(p)
    with _banco() as c:
        c.execute("insert into pqbr.pacote_canonico (hash, itens, origem) values (%s, %s, %s) on conflict (hash) do nothing",
                  (p["hash"], json.dumps(p["itens"], ensure_ascii=False), json.dumps(p["origem"])))
        c.execute("update pqbr.pacote_canonico set ativo = (hash = %s) where canal_id = 'pqbr' and (ativo or hash = %s)",
                  (p["hash"], p["hash"]))
        ids = c.execute("select drive_ids from pqbr.pacote_canonico where hash = %s", (p["hash"],)).fetchone()[0] or {}
        if not ids:
            from ..integrations import drive
            if drive.ARQ_CRED.is_file():
                pasta = drive.buscar(f"pacote-{p['hash'][:12]}", _pasta_biblia())
                if not pasta:
                    _, j = drive._req("POST", f"{drive.API}/files?fields=id", json.dumps(
                        {"name": f"pacote-{p['hash'][:12]}", "mimeType": drive.PASTA, "parents": [_pasta_biblia()]}).encode())
                    pasta = j["id"]
                ids = {"_pasta": pasta, **{f.name: drive.enviar(str(f), pasta)["id"] for f in sorted(d.iterdir()) if f.is_file()}}
                c.execute("update pqbr.pacote_canonico set drive_ids = %s where hash = %s", (json.dumps(ids), p["hash"]))
        c.commit()
    return {"hash": p["hash"], "fonte": str(d / "PQBR-pacote.md"), "drive": ids}


@activity.defn
async def registro_buscar_caderno(codigo: str) -> str | None:
    with _banco() as c:
        r = c.execute("select caderno_id from pqbr.cadernos_episodio where episodio_codigo = %s and apagado_em is null",
                      (codigo,)).fetchone()
    return r[0] if r else None


@activity.defn
async def registro_caderno(caderno: str, codigo: str, slug: str, pacote_hash: str | None) -> None:
    if not UUID.match(caderno) or caderno in MESTRES_PROIBIDOS: raise RuntimeError("caderno inválido ou mestre")
    with _banco() as c:
        c.execute("insert into pqbr.cadernos_episodio (caderno_id, episodio_codigo, slug, titulo, pacote_hash)"
                  " values (%s, %s, %s, %s, %s) on conflict (caderno_id) do update set pacote_hash = excluded.pacote_hash",
                  (caderno, codigo, slug, titulo_caderno(codigo, slug), pacote_hash))
        c.commit()


@activity.defn
async def arquivar_caderno(caderno: str, codigo: str, slug: str, exportados: list[str], video: str | None) -> dict:
    """Fontes, respostas e vídeo → Drive (02_Episodios/AAAA-MM/<código>_<slug>/caderno) + pqbr.arquivo_caderno."""
    from ..integrations import drive
    arqs = [Path(a) for a in exportados] + ([Path(video)] if video else [])
    pasta = drive.garantir_pasta(f"PQBR/02_Episodios/{datetime.now():%Y-%m}/{codigo}_{slug}/caderno") if drive.ARQ_CRED.is_file() else None
    with _banco() as c:
        for f in arqs:
            dados = f.read_bytes(); tipo = "video" if f.suffix == ".mp4" else ("resposta" if f.name.startswith("respostas") else
                                                                              "metadados" if f.name.startswith("metadados") else "fonte")
            did = drive.enviar(str(f), pasta)["id"] if pasta else None
            c.execute("insert into pqbr.arquivo_caderno (caderno_id, tipo, nome, sha256, bytes, drive_id, conteudo)"
                      " values (%s, %s, %s, %s, %s, %s, %s) on conflict (caderno_id, tipo, nome) do update"
                      " set sha256 = excluded.sha256, bytes = excluded.bytes, drive_id = excluded.drive_id, conteudo = excluded.conteudo",
                      (caderno, tipo, f.name, hashlib.sha256(dados).hexdigest(), len(dados), did,
                       None if tipo == "video" else dados.decode("utf-8", "replace")))
        n = c.execute("update pqbr.cadernos_episodio set arquivado_em = now() where caderno_id = %s and episodio_codigo = %s",
                      (caderno, codigo)).rowcount
        if n != 1: raise RuntimeError("caderno não registrado para este episódio")
        c.commit()
    return {"arquivos": len(arqs), "drive_pasta": pasta}


@activity.defn
async def registro_publicado(caderno: str, codigo: str, quando_iso: str) -> str:
    q = datetime.fromisoformat(quando_iso)
    with _banco() as c:
        n = c.execute("update pqbr.cadernos_episodio set publicado_em = %s, apagar_apos = %s"
                      " where caderno_id = %s and episodio_codigo = %s and apagado_em is null",
                      (q, q + D_APAGAR, caderno, codigo)).rowcount
        if n != 1: raise RuntimeError("caderno não registrado para este episódio")
        c.commit()
    return (q + D_APAGAR).isoformat()


@activity.defn
async def verificar_arquivo(caderno: str, esperados: dict) -> dict:
    """REGRA PERMANENTE (José 12/10): arquivar e VERIFICAR vêm antes de apagar. Confere as 3 cópias:
    Postgres (linhas de arquivo_caderno com sha256/bytes), Drive (todo item com drive_id, md5/tamanho conferidos no upload)
    e repo/disco local (`esperados["repo"]`: caminho → bytes). `esperados["n"]` = nº mínimo de itens. Marca verificado_em."""
    from pathlib import Path as _P
    with _banco() as c:
        rows = c.execute("select nome, bytes, drive_id from pqbr.arquivo_caderno where caderno_id = %s", (caderno,)).fetchall()
        faltas = []
        if len(rows) < int(esperados.get("n", 1)): faltas.append(f"postgres {len(rows)} < {esperados.get('n')}")
        if any(r[2] is None for r in rows): faltas.append("item sem cópia no Drive")
        for cam, b in (esperados.get("repo") or {}).items():
            f = _P(cam)
            if not f.is_file() or f.stat().st_size != int(b): faltas.append(f"repo: {cam}")
        if faltas: raise RuntimeError("arquivo NÃO verificado — não apagar: " + "; ".join(faltas[:5]))
        copias = {"postgres": len(rows), "drive": sum(r[2] is not None for r in rows), "repo": len(esperados.get("repo") or {}),
                  "bytes": sum(int(r[1]) for r in rows)}
        c.execute("update pqbr.cadernos_episodio set verificado_em = now(), copias = %s where caderno_id = %s",
                  (json.dumps(copias), caderno)); c.commit()
    return copias


@activity.defn
async def registro_autorizar_apagar(caderno: str, codigo: str) -> str:
    """Allowlist do banco: o id tem de ser O caderno registrado para o código, arquivado E verificado, publicado há ≥ 48 h."""
    with _banco() as c:
        r = c.execute("select titulo, arquivado_em, apagar_apos, verificado_em from pqbr.cadernos_episodio"
                      " where caderno_id = %s and episodio_codigo = %s and apagado_em is null", (caderno, codigo)).fetchone()
    if not r: raise RuntimeError("caderno fora da allowlist (não registrado para o episódio)")
    if r[1] is None or r[3] is None: raise RuntimeError("caderno não arquivado/verificado: arquivar e verificar antes de apagar")
    if r[2] is None or r[2] > datetime.now(timezone.utc): raise RuntimeError("antes de D+2 da publicação")
    return r[0]


@activity.defn
async def registro_apagado(caderno: str, codigo: str) -> None:
    with _banco() as c:
        c.execute("update pqbr.cadernos_episodio set apagado_em = now() where caderno_id = %s and episodio_codigo = %s",
                  (caderno, codigo)); c.commit()


@activity.defn
async def registro_fonte(caderno: str, fonte_id: str, tipo: str, titulo: str | None = None) -> None:
    """Isolamento (t459c): toda fonte injetada no caderno do episódio é registrada por id."""
    with _banco() as c:
        c.execute("insert into pqbr.fontes_caderno (caderno_id, fonte_id, tipo, titulo) values (%s, %s, %s, %s)"
                  " on conflict (caderno_id, fonte_id) do nothing", (caderno, fonte_id, tipo, titulo)); c.commit()


@activity.defn
async def registro_fontes_listar(caderno: str) -> list[str]:
    with _banco() as c:
        return [r[0] for r in c.execute("select fonte_id from pqbr.fontes_caderno where caderno_id = %s", (caderno,)).fetchall()]


class ContaminacaoCaderno(Exception):
    pass


def fontes_estranhas(lista: dict | list, permitidas: list[str]) -> list[dict]:
    """Fontes do caderno que NÃO estão registradas para o episódio (puro; testado)."""
    ok = set(permitidas)
    return [{"id": f["id"], "title": f.get("title")} for f in _ids(lista) if f["id"] not in ok]


# ---------------- fila notebooklm-pqbr: CLI ----------------
@activity.defn
async def nlm_conferir_fontes(caderno: str, permitidas: list[str]) -> int:
    """Antes de gerar: bloqueia se o caderno tiver fonte não registrada para o episódio (contaminação cruzada)."""
    if caderno in MESTRES_PROIBIDOS: raise RuntimeError("caderno mestre proibido")
    lst = _json(await asyncio.to_thread(_cli, "source", "list", "-n", caderno, "--json", timeout=120))
    if isinstance(lst, dict): lst = lst.get("sources", [])
    estranhas = fontes_estranhas(lst, permitidas)
    if estranhas: raise ContaminacaoCaderno(f"caderno {caderno} tem {len(estranhas)} fonte(s) fora do registro: {estranhas[:5]}")
    if not lst: raise ContaminacaoCaderno("caderno sem fontes")
    return len(lst)
@activity.defn
async def nlm_injetar_pacote(caderno: str, fonte_pacote: str, pacote_hash: str) -> str:
    """Adiciona o pacote canônico como fonte (idempotente pelo título com o hash)."""
    if caderno in MESTRES_PROIBIDOS: raise RuntimeError("caderno mestre proibido")
    titulo = f"PQBR pacote {pacote_hash[:12]}"
    for s in _ids(_json(await asyncio.to_thread(_cli, "source", "list", "-n", caderno, "--json", timeout=120))):
        if s.get("title") == titulo: return s["id"]
    out = await asyncio.to_thread(_cli, "source", "add", "-n", caderno, "--type", "file", fonte_pacote,
                                  "--title", titulo, "--json", timeout=300)
    src = next(_ids(_json(out)))["id"]
    await asyncio.to_thread(_cli, "source", "wait", "-n", caderno, src, "--timeout", "300", timeout=330)
    return src


@activity.defn
async def nlm_exportar_caderno(caderno: str, codigo: str) -> list[str]:
    """Texto integral de cada fonte + histórico de respostas + metadados → arquivos locais (para arquivar)."""
    if caderno in MESTRES_PROIBIDOS: raise RuntimeError("caderno mestre proibido")
    d = EXPORT / f"{codigo}_{caderno[:8]}"; d.mkdir(parents=True, exist_ok=True); out = []
    meta = await asyncio.to_thread(_cli, "metadata", "-n", caderno, "--json", timeout=120)
    (d / "metadados.json").write_text(meta); out.append(str(d / "metadados.json"))
    for i, s in enumerate(_ids(_json(await asyncio.to_thread(_cli, "source", "list", "-n", caderno, "--json", timeout=120)))):
        t = await asyncio.to_thread(_cli, "source", "fulltext", "-n", caderno, s["id"], timeout=180)
        f = d / f"fonte_{i + 1:02d}_{s['id'][:8]}.md"; f.write_text(f"# {s.get('title', '')}\n{s.get('url') or ''}\n\n{t}"); out.append(str(f))
    h = await asyncio.to_thread(_cli, "history", "-n", caderno, "--json", "--show-all", timeout=120)
    (d / "respostas.json").write_text(h); out.append(str(d / "respostas.json"))
    return out


@activity.defn
async def nlm_apagar_caderno(caderno: str, codigo: str, titulo_registrado: str) -> dict:
    """Apaga UM caderno pelo id completo (a CLI aceita id parcial → exigimos UUID inteiro). Nunca por título."""
    if not UUID.match(caderno): raise RuntimeError("id incompleto/ inválido: recusado")
    if caderno in MESTRES_PROIBIDOS or caderno[:8] in MESTRES_PROIBIDOS: raise RuntimeError("caderno mestre proibido")
    if not CODIGO.match(codigo) or not titulo_registrado.startswith(f"Short - {codigo} - "):
        raise RuntimeError("fora da allowlist de título")
    alvo = next((n for n in _ids(_json(await asyncio.to_thread(_cli, "list", "--json", timeout=120))) if n["id"] == caderno), None)
    if alvo is None: return {"apagado": False, "motivo": "já não existe"}
    if alvo.get("title") != titulo_registrado or alvo.get("is_owner") is False:
        raise RuntimeError("título/dono no NotebookLM não confere com o registro: recusado")
    await asyncio.to_thread(_cli, "delete", "-n", caderno, "-y", timeout=120)
    return {"apagado": True, "caderno": caderno}


@workflow.defn
class ApagarCadernoWorkflow:
    """Inicia na publicação real; dorme até D+2 (+ jitter); confere allowlist no banco; apaga pelo id; registra."""
    @workflow.run
    async def run(self, caderno: str, codigo: str, publicado_iso: str) -> dict:
        r = dict(start_to_close_timeout=timedelta(minutes=5), retry_policy=RetryPolicy(maximum_attempts=3))
        apos = await workflow.execute_activity(registro_publicado, args=[caderno, codigo, publicado_iso], task_queue=FILA_EPISODIO, **r)
        espera = datetime.fromisoformat(apos) - workflow.now() + timedelta(minutes=workflow.random().randint(5, 90))
        if espera.total_seconds() > 0: await workflow.sleep(espera)
        await workflow.execute_activity(verificar_arquivo, args=[caderno, {"n": 2}], task_queue=FILA_EPISODIO, **r)
        titulo = await workflow.execute_activity(registro_autorizar_apagar, args=[caderno, codigo], task_queue=FILA_EPISODIO, **r)
        res = await workflow.execute_activity(nlm_apagar_caderno, args=[caderno, codigo, titulo], task_queue=FILA_NOTEBOOKLM,
                                              start_to_close_timeout=timedelta(minutes=5), retry_policy=RetryPolicy(maximum_attempts=2))
        await workflow.execute_activity(registro_apagado, args=[caderno, codigo], task_queue=FILA_EPISODIO, **r)
        return res


ATIVIDADES_REGISTRO = [registro_fonte, registro_fontes_listar, pacote_garantir, registro_buscar_caderno, registro_caderno, arquivar_caderno, registro_publicado,
                       verificar_arquivo, registro_autorizar_apagar, registro_apagado]
ATIVIDADES_NLM_CICLO = [nlm_conferir_fontes, nlm_injetar_pacote, nlm_exportar_caderno, nlm_apagar_caderno]
