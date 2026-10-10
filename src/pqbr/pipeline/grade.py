"""Grade diária, 3 barreiras de repetição, R10, polêmica e bloqueio absoluto (F5-01; RF-01..RF-05).

Funções puras: o `GradeDiariaWorkflow` coleta, chama isto e grava no banco. As 3 barreiras:
  1. exata    — tema normalizado igual a um já publicado/em uso;
  2. variação — variação próxima (R10: "um tema, um vídeo, inclusive variações próximas");
  3. banco    — índice único `temas_r10_unico` (última trava, no INSERT).
Limiar da variação e pesos da polêmica: PROPOSTA, recalibrar em 2–4 semanas (REGRAS §4)."""
from __future__ import annotations
import re, unicodedata
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Literal
from ..contratos import (DecisaoRepeticao, GradeDiaria, ItemGrade, JANELAS, PontuacaoPolemica)

# Mistura configurável (t378: escopo pode virar ≥80% curiosidades/perenes; EM CONSTRUÇÃO — discutir com José)
FRACAO_PERENE_PADRAO = 0.3  # REGRAS §4 vigente: ~70% em alta / ~30% perenes
LIMIAR_VARIACAO = 0.55  # PROPOSTA (recalibrar com o histórico)
_STOP = set("""a o as os um uma uns umas de do da dos das no na nos nas em por porque porquê que qual quais
quando como pra para e é ser se sua seu suas seus ao aos à às com sem mais muito tão the gente nós brasileiro
brasileiros brasil brasileira br sempre nao tem ter quase faz fica vira usa chama chamam pedem só ja já ainda até ou isso esse essa este esta aquele tudo todo toda""".split())

# Bloqueio absoluto (REGRAS §4): política partidária, tragédias, religião, grupos protegidos,
# conselho de saúde/finanças/jurídico, incentivo a ato ilegal ou perigoso.
BLOQUEIO: dict[str, tuple[str, ...]] = {
    "politica_partidaria": ("lula", "bolsonaro", "pt ", "psdb", "partido", "eleição", "eleicao", "deputado", "senador", "presidente da república", "stf"),
    "tragedia": ("tragédia", "tragedia", "enchente", "desabamento", "massacre", "chacina", "acidente fatal", "morte de", "assassinato"),
    "religiao": ("igreja", "religião", "religiao", "evangélico", "evangelico", "católico", "catolico", "umbanda", "candomblé", "pastor", "padre"),
    "grupos_protegidos": ("negros", "gays", "lgbt", "trans ", "indígenas", "indigenas", "deficientes", "nordestinos são", "imigrantes"),
    "conselho_saude_financas_juridico": ("remédio para", "remedio para", "cura", "dieta para", "investir em", "como investir", "processar", "advogado", "imposto de renda"),
    "ilegal_perigoso": ("como roubar", "gato de luz", "gatonet", "dirigir bêbado", "dirigir bebado", "fogos dentro", "desafio perigoso"),
}

# Componentes da polêmica (0–100 cada) e pesos — PROPOSTA (t200: recalibrar com analista + compliance)
PESOS = {"divisao_opiniao": 0.35, "regionalismo": 0.20, "estereotipo": 0.25, "termos_sensiveis": 0.20}
_TERMOS_SENSIVEIS = ("mãe", "dinheiro", "futebol", "time", "nordeste", "sul", "paulista", "carioca", "baiano", "pobre", "rico")


def normalizar(tema: str) -> str:
    t = unicodedata.normalize("NFKD", tema.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _radical(p: str) -> str:
    for suf in ("mente", "coes", "cao", "oes", "s", "a", "o", "e"):
        if len(p) > 4 and p.endswith(suf):
            return p[: -len(suf)]
    return p


def _nucleo(tema: str) -> set[str]:
    return {_radical(p) for p in normalizar(tema).split() if p not in _STOP and len(p) > 1}


def similaridade(a: str, b: str) -> float:
    """Núcleo de palavras (sem stopwords, por radical): Jaccard, ou sobreposição quando ≥ 2 termos
    em comum (pega "chuveiro elétrico" × "tomada do chuveiro elétrico"). Variação só semântica
    (sem palavra em comum) fica para o Jev na faixa de dúvida (PROPOSTA)."""
    na, nb = _nucleo(a), _nucleo(b)
    if not na or not nb:
        return 1.0 if normalizar(a) == normalizar(b) else 0.0  # sem núcleo: só a barreira exata decide
    comum = len(na & nb)
    jacc = comum / len(na | nb)
    sobre = comum / min(len(na), len(nb)) if comum >= 2 else 0.0
    return round(max(jacc, 0.85 * sobre), 3)


def checar_repeticao(tema: str, usados: Iterable[str]) -> DecisaoRepeticao:
    n = normalizar(tema)
    melhor, parecido = 0.0, None
    for u in usados:
        if normalizar(u) == n:
            return DecisaoRepeticao(repetido=True, barreira="exata", tema_parecido=u, confianca=1.0)
        s = similaridade(tema, u)
        if s > melhor:
            melhor, parecido = s, u
    if melhor >= LIMIAR_VARIACAO:
        return DecisaoRepeticao(repetido=True, barreira="variacao", tema_parecido=parecido, confianca=melhor)
    return DecisaoRepeticao(repetido=False, barreira="nenhuma", tema_parecido=parecido, confianca=round(1 - melhor, 3))


def bloqueio_absoluto(tema: str) -> str | None:
    t = f" {tema.lower()} "
    for cat, termos in BLOQUEIO.items():
        if any(x in t for x in termos):
            return cat
    return None


def pontuar_polemica(tema: str, componentes: dict[str, int] | None = None) -> PontuacaoPolemica:
    comp = dict(componentes or {})
    t = tema.lower()
    comp.setdefault("termos_sensiveis", min(100, 35 * sum(x in t for x in _TERMOS_SENSIVEIS)))
    for k in PESOS:
        comp.setdefault(k, 0)
        if not 0 <= comp[k] <= 100:
            raise ValueError(f"componente {k} fora de 0–100")
    valor = round(sum(PESOS[k] * comp[k] for k in PESOS))
    cat = bloqueio_absoluto(tema)
    return PontuacaoPolemica(valor=valor, componentes=comp, bloqueio_absoluto=cat is not None, categoria_bloqueio=cat)


@dataclass(frozen=True)
class Candidato:
    tema: str
    fonte: Literal["em_alta", "perene"]
    componentes: dict | None = None
    sugerido_por_jose: bool = False


@dataclass(frozen=True)
class Recusa:
    tema: str
    motivo: str          # r10_exata, r10_variacao, bloqueio:<cat>, duplicado_no_lote
    parecido: str | None = None


def montar_grade(dia: date, candidatos: list[Candidato], usados: Iterable[str],
                 janelas: tuple[str, ...] = JANELAS,
                 fracao_perene: float = FRACAO_PERENE_PADRAO) -> tuple[GradeDiaria, list[Recusa]]:
    """Grade do dia D só a partir de D (RF-01). ~70% em alta / ~30% perenes; última janela de preferência perene (RF-03).
    R10 vale mesmo para tema sugerido pelo José (recusa e avisa). Polêmica > 75 entra como `aguardando_jose`."""
    usados = list(usados)
    aceitos: list[tuple[Candidato, PontuacaoPolemica]] = []
    recusas: list[Recusa] = []
    for c in candidatos:
        d = checar_repeticao(c.tema, usados + [a.tema for a, _ in aceitos])
        if d.repetido:
            dentro_lote = d.tema_parecido in [a.tema for a, _ in aceitos]
            recusas.append(Recusa(c.tema, "duplicado_no_lote" if dentro_lote else f"r10_{d.barreira}", d.tema_parecido))
            continue
        p = pontuar_polemica(c.tema, c.componentes)
        if p.bloqueio_absoluto:
            recusas.append(Recusa(c.tema, f"bloqueio:{p.categoria_bloqueio}"))
            continue
        aceitos.append((c, p))
    n = min(len(janelas), len(aceitos))
    perenes = [x for x in aceitos if x[0].fonte == "perene"]
    alta = [x for x in aceitos if x[0].fonte == "em_alta"]
    n_perene = min(len(perenes), max(1, round(n * fracao_perene))) if n else 0
    if not 0 <= fracao_perene <= 1:
        raise ValueError("fracao_perene fora de 0–1")
    escolhidos_alta = alta[: n - n_perene]
    escolhidos_perene = perenes[: n - len(escolhidos_alta)]
    ordem = escolhidos_alta + escolhidos_perene  # perenes por último → última janela perene
    itens = [ItemGrade(data=dia, janela=j, tema=c.tema, polemica=p.valor, fonte=c.fonte,
                       status="aguardando_jose" if p.aguarda_jose else "planejado")
             for j, (c, p) in zip(janelas, ordem)]
    return GradeDiaria(data=dia, itens=itens), recusas


def grade_reaproveitada(grade: GradeDiaria, dia: date) -> bool:
    """Vigia do incidente de 08/10: a grade do dia D nunca é a de outro dia."""
    return grade.data != dia
