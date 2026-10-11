"""Auditor VISUAL 2D sem fichas (F7-02, t399–t403).

O Gemini web responde só sim/nao/na por cena (templates/auditor/VISUAL_2D.txt).
O código decide. Regras: CONTRATO §16.6, REGRAS §5.
- SEGURANCA (reprova): parece_pessoa_real, marca_real, estereotipo_ofensivo,
  texto_com_erro_de_sentido = "sim".
- METRICAS (nunca reprovam; "nao" vira ressalva): segue_estilo_declarado,
  mesmo_personagem_do_bloco, imagem_corresponde_a_fala, legivel_no_celular,
  ambiente_brasileiro.
- 2 rodadas: falha só se as duas concordam; divergência → terceira_rodada
  (o agente Auditor desempata). 1 rodada: a falha vale, com aviso.
- Resposta inválida/incompleta → terceira_rodada.
Veredito: reprova > terceira_rodada > aprova_com_ressalva > aprova.
"""
from __future__ import annotations
import json, re
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[3] / "templates" / "auditor" / "VISUAL_2D.txt"
SEGURANCA = ("parece_pessoa_real", "marca_real", "estereotipo_ofensivo", "texto_com_erro_de_sentido")
METRICAS = ("segue_estilo_declarado", "mesmo_personagem_do_bloco", "imagem_corresponde_a_fala",
            "legivel_no_celular", "ambiente_brasileiro")
CHAVES = ("tem_personagem", "tem_texto_na_tela") + METRICAS + SEGURANCA
PODE_NA = {"mesmo_personagem_do_bloco", "texto_com_erro_de_sentido"}
ORDEM = ("reprova", "terceira_rodada", "aprova_com_ressalva", "aprova")


def montar_prompt(bloco_visual: str, cenas: list[tuple[str, str]], rodada: int) -> str:
    t = TEMPLATE.read_text(encoding="utf-8")
    linhas = "\n".join(f"- {i}: {fala}" for i, fala in cenas)
    return t.replace("__RODADA__", str(rodada)).replace("__BLOCO_VISUAL__", bloco_visual.strip()).replace("__CENAS__", linhas)


def _norm(x) -> str | None:
    s = str(x).strip().lower().replace("ã", "a")
    return s if s in ("sim", "nao", "na") else None


def ler_resposta(texto: str, ids: list[str]) -> tuple[dict, list[str]]:
    """-> ({id: {chave: sim|nao|na}}, problemas). Tira cerca ```json."""
    probs: list[str] = []
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip())
    try:
        d = json.loads(t)
    except ValueError:
        return {}, ["json_invalido"]
    cenas = {}
    for c in d.get("cenas", []) if isinstance(d, dict) else []:
        cid = str(c.get("id", "")).strip().upper()
        if cid not in ids:
            continue
        r = {}
        for k in CHAVES:
            v = _norm(c.get(k))
            if v is None or (v == "na" and k not in PODE_NA):
                probs.append(f"{cid}:{k}")
                continue
            r[k] = v
        cenas[cid] = r
    for i in ids:
        if i not in cenas:
            probs.append(f"{i}:ausente")
    return cenas, probs


def decidir(respostas: list[str], ids: list[str]) -> dict:
    """respostas = texto bruto de cada rodada (1 ou 2)."""
    rodadas, problemas = [], []
    for n, txt in enumerate(respostas, 1):
        c, p = ler_resposta(txt, ids)
        rodadas.append(c)
        problemas += [f"r{n}:{x}" for x in p]
    falhas, divergencias, ressalvas = [], [], []
    metricas = {m: [0, 0] for m in METRICAS}  # [sim, total]
    for i in ids:
        for k in SEGURANCA:
            votos = [r[i][k] for r in rodadas if i in r and k in r[i]]
            sims = votos.count("sim")
            if sims and sims == len(votos) and len(votos) == len(rodadas):
                falhas.append((i, k))
            elif sims:
                divergencias.append((i, k))
        for k in METRICAS:
            votos = [r[i][k] for r in rodadas if i in r and k in r[i] and r[i][k] != "na"]
            metricas[k][0] += votos.count("sim")
            metricas[k][1] += len(votos)
            if votos and votos.count("nao") == len(votos):
                ressalvas.append((i, k))
    if falhas:
        v = "reprova"
    elif divergencias or problemas:
        v = "terceira_rodada"
    elif ressalvas:
        v = "aprova_com_ressalva"
    else:
        v = "aprova"
    return {
        "veredito": v,
        "falhas": falhas,
        "divergencias": divergencias,
        "problemas": problemas,
        "ressalvas": ressalvas,
        "metricas": {k: (s / t if t else None) for k, (s, t) in metricas.items()},
        "rodada_unica": len(rodadas) == 1,
    }
