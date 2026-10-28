"""Plano de motion graphics do pós (REGRAS §26, t145u).

O papel `motion` devolve um PlanoMotion: peças do catálogo com tempos absolutos do vídeo final.
Texto na tela sai só do bloco de números travados; cores só do elenco e da marca; o bloco de
tela cheia nunca é a última cena e nunca cobre o gancho. Quem renderiza é pos/motion/render.py."""
from __future__ import annotations
import re
from typing import Literal
from pydantic import Field, model_validator
from . import Contrato, _PEDE_COMENTARIO
from ..pos.motion.catalogo import carregar_catalogo, PALETA

VERSAO = "1.0.0"
EPISODIO = re.compile(r"^PQBR-EP\d{4,}$")
# §26: nunca pedir clique, curtida, inscrição ou comentário na tela (t263).
_PEDE_ACAO = re.compile(r"(?i)\b(clica|clique|curte|curta|inscreva|inscreve|compartilha|segue a[íi])\b")
GANCHO_MIN_S = 4.0        # gancho e conflito ficam em vídeo (R1, R3)
CAUDA_MIN_S = 4.0         # reconhecimento, CTA e loop voltam ao vídeo (§11.2)
BLOCO_MIN_S, BLOCO_MAX_S = 6.0, 30.0   # alvo ~18–20 s
TRANSICAO_S = 0.4
Valor = str | int | float | bool | list[str]


class BlocoNumeros(Contrato):
    """Fatos do roteiro e das fontes do NotebookLM que podem aparecer na tela (ano, origem, números, frases curtas)."""
    itens: list[str] = Field(min_length=1, max_length=16)

    @model_validator(mode="after")
    def _regras(self):
        for it in self.itens:
            if not (1 <= len(it) <= 160): raise ValueError(f"item do bloco fora de 1–160 caracteres: {it!r}")
            if _PEDE_COMENTARIO.search(it) or _PEDE_ACAO.search(it): raise ValueError(f"bloco pede ação do espectador: {it!r}")
        if len(set(self.itens)) != len(self.itens): raise ValueError("item repetido no bloco de números")
        return self


class PecaMotion(Contrato):
    modelo: str = Field(pattern=r"^[a-z][a-z0-9-]{2,40}$")
    inicio: float = Field(ge=0)
    fim: float = Field(gt=0)
    parametros: dict[str, Valor] = Field(default_factory=dict)
    justificativa: str = Field(default="", max_length=300)

    @model_validator(mode="after")
    def _regras(self):
        if self.fim <= self.inicio: raise ValueError(f"peça {self.modelo}: fim deve ser maior que início")
        return self


class FaixaBloco(Contrato):
    inicio: float = Field(ge=0)
    fim: float = Field(gt=0)


class PlanoMotion(Contrato):
    versao: Literal["1.0.0"] = VERSAO
    episodio: str = Field(pattern=EPISODIO.pattern)
    duracao_video_s: float = Field(gt=0, le=180)
    fps: int = Field(default=30, ge=24, le=60)
    elenco: Literal["PERS-M", "PERS-F"]   # IDs aposentados em t148u; o conjunto novo de banco-fichas/ entra no re-base do MG-03
    bloco_numeros: BlocoNumeros
    bloco: FaixaBloco | None = None              # trecho cortado para tela cheia (o porquê)
    pecas: list[PecaMotion] = Field(min_length=1, max_length=40)
    recursos: dict[str, str] = Field(default_factory=dict)   # chave → caminho de imagem (recortes, quadros)
    peca_nova: str | None = Field(default=None, max_length=600)   # quando nenhum modelo serve; vai para a biblioteca antes de usar

    @model_validator(mode="after")
    def _regras(self):
        cat = carregar_catalogo()
        itens = set(self.bloco_numeros.itens)
        for p in self.pecas:
            m = cat.get(p.modelo)
            if m is None: raise ValueError(f"modelo fora do catálogo: {p.modelo}")
            if p.fim > self.duracao_video_s + 1e-6: raise ValueError(f"peça {p.modelo} passa do fim do vídeo")
            for nome, spec in m.parametros.items():
                if spec.get("obrigatorio") and nome not in p.parametros: raise ValueError(f"{p.modelo}: falta parâmetro {nome}")
            for nome, val in p.parametros.items():
                spec = m.parametros.get(nome)
                if spec is None: raise ValueError(f"{p.modelo}: parâmetro desconhecido {nome}")
                tipo = spec["tipo"]
                if tipo == "texto":
                    if not isinstance(val, str) or (spec.get("travado") and val not in itens):
                        raise ValueError(f"{p.modelo}.{nome}: texto fora do bloco de números travados: {val!r}")
                elif tipo == "textos":
                    if not isinstance(val, list) or not all(isinstance(v, str) for v in val): raise ValueError(f"{p.modelo}.{nome}: esperava lista de textos")
                    if spec.get("travado") and any(v not in itens for v in val): raise ValueError(f"{p.modelo}.{nome}: texto fora do bloco de números travados")
                    if not (spec.get("min", 1) <= len(val) <= spec.get("max", 16)): raise ValueError(f"{p.modelo}.{nome}: quantidade fora de {spec.get('min', 1)}–{spec.get('max', 16)}")
                elif tipo == "cor":
                    if val not in PALETA: raise ValueError(f"{p.modelo}.{nome}: cor fora do elenco e da marca: {val!r}")
                elif tipo == "opcao":
                    if val not in spec["opcoes"]: raise ValueError(f"{p.modelo}.{nome}: opção inválida {val!r}")
                elif tipo == "imagem":
                    if not isinstance(val, str) or val not in self.recursos: raise ValueError(f"{p.modelo}.{nome}: imagem sem recurso declarado: {val!r}")
                elif tipo == "numero":
                    if isinstance(val, bool) or not isinstance(val, (int, float)): raise ValueError(f"{p.modelo}.{nome}: esperava número")
            if m.camada == "tela_cheia":
                if self.bloco is None: raise ValueError(f"peça de tela cheia ({p.modelo}) sem bloco definido")
                if p.inicio < self.bloco.inicio - 1e-6 or p.fim > self.bloco.fim + 1e-6: raise ValueError(f"peça {p.modelo} fora do bloco de tela cheia")
        if self.bloco is not None:
            b = self.bloco
            if b.fim <= b.inicio: raise ValueError("bloco: fim deve ser maior que início")
            if b.inicio < GANCHO_MIN_S: raise ValueError(f"bloco começa antes de {GANCHO_MIN_S:g} s: gancho e conflito ficam em vídeo (R1)")
            if b.fim > self.duracao_video_s - CAUDA_MIN_S: raise ValueError("bloco não pode ser a última cena: o loop volta ao vídeo (§11.2)")
            if not (BLOCO_MIN_S <= b.fim - b.inicio <= BLOCO_MAX_S): raise ValueError(f"bloco fora de {BLOCO_MIN_S:g}–{BLOCO_MAX_S:g} s")
            if not any(p.modelo == "transicao-cortina" and p.parametros.get("fase") == "cobre" and abs(p.fim - b.inicio) < 1e-6 for p in self.pecas) \
               or not any(p.modelo == "transicao-cortina" and p.parametros.get("fase") == "revela" and abs(p.inicio - b.inicio) < 1e-6 for p in self.pecas) \
               or not any(p.modelo == "transicao-cortina" and p.parametros.get("fase") == "cobre" and abs(p.fim - b.fim) < 1e-6 for p in self.pecas) \
               or not any(p.modelo == "transicao-cortina" and p.parametros.get("fase") == "revela" and abs(p.inicio - b.fim) < 1e-6 for p in self.pecas):
                raise ValueError("bloco exige a transição padrão (cortina cobre/revela) na entrada e na saída")
            for p in self.pecas:
                if p.modelo == "transicao-cortina" and not (0.2 <= p.fim - p.inicio <= 0.8): raise ValueError("transição padrão dura de 0,2 a 0,8 s")
        return self

    def clipes_substituidos(self, cortes: list[float]) -> list[int]:
        """Índices (1-based) dos clipes cuja faixa cai inteira dentro do bloco, dado o vetor de durações dos cortes."""
        if self.bloco is None: return []
        acc, saida = 0.0, []
        for i, d in enumerate(cortes, start=1):
            a, b = acc, acc + d
            if a >= self.bloco.inicio - 1e-6 and b <= self.bloco.fim + 1e-6: saida.append(i)
            acc = b
        return saida


def transicao_padrao(bloco: FaixaBloco, dur: float = TRANSICAO_S) -> list[PecaMotion]:
    """As quatro peças da transição padrão: cobre/revela na entrada e na saída do bloco."""
    return [
        PecaMotion(modelo="transicao-cortina", inicio=bloco.inicio - dur, fim=bloco.inicio, parametros={"fase": "cobre"}),
        PecaMotion(modelo="transicao-cortina", inicio=bloco.inicio, fim=bloco.inicio + dur, parametros={"fase": "revela"}),
        PecaMotion(modelo="transicao-cortina", inicio=bloco.fim - dur, fim=bloco.fim, parametros={"fase": "cobre"}),
        PecaMotion(modelo="transicao-cortina", inicio=bloco.fim, fim=bloco.fim + dur, parametros={"fase": "revela"}),
    ]
