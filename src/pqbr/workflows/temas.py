"""t465 (José 14:00): grade sempre com 7 dias de temas abertos em pqbr.temas_pendentes (≥ 80% curiosidade/cultura pop).
Quem propõe é o MotorIntelectual (NotebookLM hoje, porta src/pqbr/motores, t512/t513); o Líder Editorial (PydanticAI) monta o pedido e valida; o código só orquestra e valida
(bloqueio absoluto, anti-repetição, contrato TemaPendente). Tema usado na publicação → pqbr.temas_publicados e
reposição automática (ReposicaoTemasWorkflow). Agenda diária: Schedule pqbr-reposicao-temas (scripts/temporal/schedules.py)."""
from __future__ import annotations
import json, os, re
from datetime import date, timedelta as _td
from temporalio import activity, workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from datetime import timedelta

DIAS, POR_DIA = 7, 4                 # 4 janelas por dia (ItemGrade) × 7 dias
ALVO = DIAS * POR_DIA
FRACAO_MIN_CURIOSIDADE = 0.8         # CONTRATO §16.5
ABERTOS = ("proposto", "aprovado")
CATEGORIAS = ("expressao", "habito_mania", "curiosidade_cultura_pop", "sazonal")
SEP = "||"


def ler_proposta(valor: str) -> list[dict]:
    """'categoria: Por que …?' separados por '||' (PropostaAgente.valor_proposto ≤ 500). Puro; testado."""
    out = []
    for item in (valor or "").split(SEP):
        m = re.match(r"\s*([a-z_]+)\s*:\s*(.+?)\s*$", item)
        if m and m.group(1) in CATEGORIAS and 3 <= len(m.group(2)) <= 300:
            out.append({"categoria": m.group(1), "tema": m.group(2)})
    return out


def filtrar(propostas: list[dict], usados: list[str], abertos_cat: list[str]) -> tuple[list[dict], list[dict]]:
    """Bloqueio absoluto + anti-repetição (contra usados e entre si) + teto de 20% sazonal. Puro; testado."""
    from ..pipeline.grade import checar_repeticao, bloqueio_absoluto
    aceitos, recusas, vistos, cats = [], [], list(usados), list(abertos_cat)
    for p in propostas:
        motivo = bloqueio_absoluto(p["tema"])
        if not motivo and checar_repeticao(p["tema"], vistos).repetido: motivo = "repetido"
        if not motivo and p["categoria"] == "sazonal":
            motivo = "sazonal só pelo Caçador, com janela"   # o Líder Editorial repõe só perene (≥ 80%)
        if not motivo:
            novos = cats + [p["categoria"]]
            if sum(c != "sazonal" for c in novos) / len(novos) < FRACAO_MIN_CURIOSIDADE: motivo = "fração < 80%"
        if motivo: recusas.append({**p, "motivo": motivo}); continue
        aceitos.append(p); vistos.append(p["tema"]); cats.append(p["categoria"])
    return aceitos, recusas


def _banco():
    from .pacote import _banco as b
    return b()


@activity.defn
async def temas_situacao() -> dict:
    with _banco() as c:
        ab = c.execute("select categoria from pqbr.temas_pendentes where status = any(%s)", (list(ABERTOS),)).fetchall()
        usados = [r[0] for r in c.execute("select tema from pqbr.temas union select tema from pqbr.temas_pendentes "
                                          "union select tema from pqbr.temas_publicados").fetchall()]
    return {"abertos": len(ab), "faltam": max(0, ALVO - len(ab)), "categorias": [r[0] for r in ab], "usados": usados}


@activity.defn
async def temas_inserir(propostas: list[dict]) -> dict:
    from ..contratos import TemaPendente
    from ..pipeline.grade import normalizar
    s = await temas_situacao()
    aceitos, recusas = filtrar(propostas, s["usados"], s["categorias"])
    aceitos = aceitos[:s["faltam"]]
    with _banco() as c:
        dia0 = c.execute("select coalesce(max(data_prevista), current_date) from pqbr.temas_pendentes where status = any(%s)",
                         (list(ABERTOS),)).fetchone()[0]
        n0 = s["abertos"]
        for i, p in enumerate(aceitos):
            slug = re.sub(r"[^a-z0-9]+", "-", normalizar(p["tema"]).replace("por que ", ""))[:55].strip("-")
            prev = date.today() + _td(days=(n0 + i) // POR_DIA)
            tp = TemaPendente(slug=slug, tema=p["tema"], tema_normalizado=normalizar(p["tema"]), categoria=p["categoria"],
                              data_prevista=prev, criado_por="lider-editorial")
            c.execute("insert into pqbr.temas_pendentes (canal_id, slug, tema, tema_normalizado, categoria, status, data_prevista, criado_por, metadados) "
                      "values ('pqbr', %s, %s, %s, %s, 'proposto', %s, %s, %s) on conflict (slug) do nothing",
                      (tp.slug, tp.tema, tp.tema_normalizado, tp.categoria, tp.data_prevista, tp.criado_por, json.dumps({"origem": "t465"})))
        c.commit()
    return {"inseridos": len(aceitos), "recusas": recusas}


@activity.defn
async def tema_publicado(tema_id: int, codigo: str, video_id: str | None, privacidade: str) -> None:
    """Publicação real: move o tema de temas_pendentes para temas_publicados (dispara a reposição no workflow)."""
    with _banco() as c:
        c.execute("insert into pqbr.temas_publicados (canal_id, slug, tema, tema_normalizado, categoria, codigo, video_id, publicado_em, "
                  "privacidade, fontes, bloco_visual, metadados, caminhos) select canal_id, slug, tema, tema_normalizado, categoria, %s, %s, now(), %s, "
                  "fontes, bloco_visual, metadados, caminhos from pqbr.temas_pendentes where id = %s", (codigo, video_id, privacidade, tema_id))
        c.execute("delete from pqbr.temas_pendentes where id = %s", (tema_id,)); c.commit()


PEDIDO = (
    "Reposição da grade (t465): faltam {faltam} temas para manter 7 dias abertos (alvo {alvo}). Proponha até 5 temas NOVOS e curtos "
    "de curiosidade/cultura popular brasileira (origem de expressões, hábitos e manias, curiosidades que prendem a atenção), "
    "cada um como pergunta 'Por que …?', categoria ∈ expressao, habito_mania, curiosidade_cultura_pop. "
    "Sem política atual ou partidária, religião como alvo, tragédia, marca real ou pessoa real viva; personagem histórico do passado e história política do passado são permitidos, com ironia e hipótese com linguagem de incerteza; sem repetir os já usados (fonte 'temas-usados'). "
    "Responda SÓ com JSON: {{\"temas\": [{{\"categoria\": \"...\", \"tema\": \"Por que ...?\"}}], \"justificativa\": \"...\"}}")


def pedido_temas(faltam: int, usados: list[str], hoje: str) -> dict:
    """Líder Editorial monta o pedido ao MotorIntelectual (t512: NotebookLM propõe). Sessão efêmera semanal. Puro; testado."""
    sem = date.fromisoformat(hoje).isocalendar()   # dict puro (sandbox do workflow); a atividade valida em PedidoMotor
    return dict(tarefa="temas", sessao=f"grade-temas-{sem[0]}w{sem[1]:02d}",
                       pergunta=PEDIDO.format(faltam=faltam, alvo=ALVO),
                       contexto="# temas-usados (não repetir)\n" + "\n".join(f"- {u}" for u in usados))


def propostas_de(saida) -> list[dict]:
    """PropostaTemas → lista de dicts para filtrar/temas_inserir. Puro; testado."""
    return [{"categoria": t.categoria, "tema": t.tema} for t in saida.temas]


def parse_direto(texto: str):
    """JSON do motor → PropostaTemas sem LLM; itens inválidos descartados. None se não houver JSON utilizável. Puro; testado."""
    from ..contratos import PropostaTemas, TemaProposto
    a, b = texto.find("{"), texto.rfind("}")
    if a < 0 or b <= a: return None
    try: bruto = json.loads(texto[a:b + 1])
    except ValueError: return None
    ok = []
    for t in (bruto.get("temas") or [])[:10]:
        try: ok.append(TemaProposto.model_validate(t))
        except Exception: continue   # noqa: BLE001
    return PropostaTemas(temas=ok, justificativa=str(bruto.get("justificativa", ""))[:500]) if ok else None


@activity.defn
async def temas_validar_agente(texto: str) -> dict:
    """ADR-011/t512: o Líder Editorial (PydanticAI) só interpreta e valida a resposta do motor em PropostaTemas.
    Primeiro parse determinístico; LLM só se a resposta não vier em JSON válido. Sem escrita aqui."""
    saida = parse_direto(texto)
    meta = {"parse": "direto"}
    if saida is None:
        from ..agents import rodar
        from ..contratos import PropostaTemas
        saida, meta = await rodar("lider-editorial", PropostaTemas,
                                  "Extraia os temas propostos pelo motor intelectual abaixo, sem inventar nem completar:\n\n" + texto[:15000])
        meta = {**meta, "parse": "agente"}
    return {"propostas": propostas_de(saida), "meta": meta}


@workflow.defn
class ReposicaoTemasWorkflow:
    @workflow.run
    async def run(self, rodadas: int = 3) -> dict:
        cur = dict(start_to_close_timeout=timedelta(minutes=3), retry_policy=RetryPolicy(maximum_attempts=3))
        ag = dict(start_to_close_timeout=timedelta(minutes=6), retry_policy=RetryPolicy(maximum_attempts=3))
        mot = dict(start_to_close_timeout=timedelta(minutes=25), retry_policy=RetryPolicy(maximum_attempts=2))
        total, recusas, metas = 0, [], []
        for _ in range(rodadas):
            s = await workflow.execute_activity(temas_situacao, **cur)
            if not s["faltam"]: break
            ped = pedido_temas(s["faltam"], s["usados"], workflow.now().date().isoformat())
            resp = await workflow.execute_activity("motor_consultar", ped, task_queue="notebooklm-pqbr", **mot)
            await workflow.execute_activity(temas_registrar_caderno, args=[resp["sessao_id"], ped["sessao"]], **cur)
            v = await workflow.execute_activity(temas_validar_agente, resp["texto"], **ag)
            metas.append({"motor": resp["motor"], "sessao": resp["sessao_id"], **v["meta"]})
            res = await workflow.execute_activity(temas_inserir, v["propostas"], **cur)
            total += res["inseridos"]; recusas += res["recusas"]
        return {"inseridos": total, "recusas": recusas[:20], "motor": metas}


@activity.defn
async def temas_registrar_caderno(caderno: str, sessao: str) -> None:
    """t517: o caderno semanal de temas entra em pqbr.cadernos_episodio (classe 'pesquisa') na criação, para o
    fluxo de descarte (DescartarCadernoTesteWorkflow) cobri-lo. Idempotente."""
    from .notebooklm import UUID, MESTRES_PROIBIDOS
    if not UUID.match(caderno) or caderno in MESTRES_PROIBIDOS: raise RuntimeError("caderno inválido ou mestre")
    with _banco() as c:
        c.execute("insert into pqbr.cadernos_episodio (caderno_id, episodio_codigo, slug, titulo, classe)"
                  " values (%s, null, %s, %s, 'pesquisa') on conflict (caderno_id) do nothing",
                  (caderno, sessao, f"Short - {sessao}"))
        c.commit()


ATIVIDADES_TEMAS = [temas_situacao, temas_inserir, tema_publicado, temas_validar_agente, temas_registrar_caderno]
