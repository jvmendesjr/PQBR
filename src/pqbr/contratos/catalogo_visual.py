"""Catálogo visual aberto (t150u, REGRAS §6): ficha de personagem, figura, animal, objeto, ambiente ou situação.

O conjunto de t148u é a semente, escolhida pelo José. O agente acrescenta fichas novas para reaproveitar:
ficha nova já pode ser usada, nasce `aguardando_ok_jose` (ou `sugestao`, se ainda não tem mídia) e o José cura.
Imagem fica no repositório só até TAMANHO_MAX_IMAGEM; vídeo vai sempre para o Drive. Quem grava é
pipeline/banco_fichas.py; este módulo só diz o que é uma ficha válida."""
from __future__ import annotations
import re
from datetime import date
from typing import Literal
from pydantic import Field, model_validator
from . import Contrato

VERSAO = "1.0.0"
Tipo = Literal["personagem", "figura", "animal", "objeto", "ambiente", "situacao"]
Estado = Literal["sugestao", "aguardando_ok_jose", "permanente"]
Origem = Literal["jose", "mantenedor", "agente"]
Papel = Literal["item", "colecao"]       # colecao = grade com vários itens (ELENCO-catalogo, OBJ-catalogo, ANIM-catalogo)

PREFIXO: dict[str, str] = {"personagem": "PERS", "figura": "FIG", "animal": "ANIM", "objeto": "OBJ", "ambiente": "AMB", "situacao": "SIT"}
PASTA: dict[str, str] = {"personagem": "personagens", "figura": "figuras", "animal": "animais", "objeto": "objetos", "ambiente": "ambientes", "situacao": "situacoes"}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# `ELENCO-catalogo` é o id da grade dos 12 desde t148u (arquivo e docs já o citam); as demais grades seguem PREFIXO-slug.
ID_ELENCO = "ELENCO-catalogo"
ID = re.compile(rf"^(?:(?:PERS|FIG|ANIM|OBJ|AMB|SIT)-[a-z0-9]+(?:-[a-z0-9]+)*|{ID_ELENCO})$")
ID_PERSONAGEM = re.compile(r"^PERS-[a-z0-9]+(?:-[a-z0-9]+)*$")
ID_AMBIENTE = re.compile(r"^AMB-[a-z0-9]+(?:-[a-z0-9]+)*$")
ID_OBJETO = re.compile(r"^OBJ-[a-z0-9]+(?:-[a-z0-9]+)*$")
EXT_IMAGEM = (".png", ".jpg", ".jpeg", ".webp")
TAMANHO_MAX_IMAGEM = 2_000_000           # bytes; acima disso a imagem vai para o Drive (imagem_drive_id)

# José, t150u: protagonista masculino = nº 1 do catálogo, feminino = nº 2 (alternância par/ímpar do elenco).
PROTAGONISTAS: dict[str, str] = {"masculino": "PERS-menino-azul", "feminino": "PERS-menina-rosa"}

# Texto canônico que entra em toda ficha gerada (REGRAS §6, CONTRATO-EDITORIAL §19): vale para qualquer tipo.
PROIBIDO_PADRAO = ("texto escrito dentro da imagem, marca ou logo real, pessoa realista ou fotorrealismo, rosto realista identificável de pessoa real ou celebridade (um stickman que representa figura histórica não é rosto real), "
                   "volume 3D, um olho só (ciclope), cabeça cortada, nome de personagem escrito ou falado")

_NEGACAO = re.compile(r"proibid[oa]s?:?[^.]*|\b(?:sem|nada de|nunca|nem)\s+[^,.;]*", re.I)
_PEDE_REALISMO = re.compile(r"\b3d\b|fotorreal|realista|photoreal|hiper.?real", re.I)
_PEDE_TEXTO = re.compile(r"\b(escrito|escrita|letreiro|placa com|com o texto|com a frase|logotipo|logomarca)\b", re.I)
_DA_NOME = re.compile(r"\b(chama-se|se chama|de nome|nome:|apelido)\b", re.I)
_REAL = re.compile(r"\b(celebridade|famos[oa]|pessoa real)\b", re.I)


def afirmativo(texto: str) -> str:
    """O que o texto pede, sem as frases de proibição ('proibido: ...', 'sem ...')."""
    return _NEGACAO.sub(" ", texto or "")


class VideoCatalogo(Contrato):
    drive_id: str = Field(pattern=r"^[A-Za-z0-9_-]{10,80}$")      # vídeo nunca vai para o repositório (t150u)
    duracao_s: float = Field(gt=0, le=30)
    loop: bool = False
    legenda: str = Field(default="", max_length=200)


class FichaCatalogo(Contrato):
    versao: Literal["1.0.0"] = VERSAO
    id: str = Field(pattern=ID.pattern)
    tipo: Tipo
    papel: Papel = "item"
    titulo: str = Field(min_length=3, max_length=80)
    trava: str = Field(min_length=20, max_length=700)             # frase repetida igual em todo prompt; sem nome, sem texto na imagem
    proibido: str = Field(default="", max_length=500)             # só o que é específico; PROIBIDO_PADRAO vale sempre
    estado: Estado
    origem: Origem
    criado_em: date
    autor: str | None = Field(default=None, max_length=40)        # cliente ou papel que registrou
    aprovado_por: str | None = Field(default=None, max_length=40)
    aprovado_em: date | None = None
    tags: list[str] = Field(default_factory=list, max_length=12)
    imagem: str | None = Field(default=None, max_length=160)      # caminho relativo a banco-fichas/, dentro da pasta do tipo
    imagem_drive_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{10,80}$")
    videos: list[VideoCatalogo] = Field(default_factory=list, max_length=6)
    recortes: dict[str, list[float]] = Field(default_factory=dict, max_length=24)   # nome → [x0, y0, x1, y1] normalizado dentro de `imagem`
    personagens: list[str] = Field(default_factory=list, max_length=4)
    ambiente: str | None = None
    objetos: list[str] = Field(default_factory=list, max_length=6)
    acao: str | None = Field(default=None, min_length=5, max_length=300)    # só situação: a pose ou o movimento corriqueiro
    acento: str | None = Field(default=None, max_length=60)                 # só personagem: peça ou cor que o identifica
    elenco_num: int | None = Field(default=None, ge=1, le=99)               # só personagem: número no catálogo do elenco
    folha_individual: bool | None = None                                    # só personagem: tem folha multi-pose própria?
    com_elenco: bool | None = None                                          # só ambiente: a imagem traz personagens do elenco em cena

    @model_validator(mode="after")
    def _regras(self):
        if self.id == ID_ELENCO:
            if self.tipo != "personagem" or self.papel != "colecao": raise ValueError(f"{ID_ELENCO} é a grade (papel colecao) de personagens")
        elif not self.id.startswith(PREFIXO[self.tipo] + "-"): raise ValueError(f"id {self.id} não é de {self.tipo} (prefixo {PREFIXO[self.tipo]}-)")
        if self.tipo == "situacao" and not self.acao: raise ValueError("situação exige `acao`: a pose ou o movimento corriqueiro")
        if self.tipo != "situacao" and self.acao: raise ValueError("`acao` é só de situação")
        if self.tipo != "personagem" and (self.acento or self.elenco_num is not None or self.folha_individual is not None):
            raise ValueError("acento, elenco_num e folha_individual são só de personagem")
        if self.tipo != "ambiente" and self.com_elenco is not None: raise ValueError("com_elenco é só de ambiente")
        if self.tipo == "personagem" and self.papel == "item":
            if not self.acento: raise ValueError("personagem exige `acento` (peça ou cor chapada que o identifica)")
            if "stickman" not in self.trava.lower(): raise ValueError("trava de personagem descreve o stickman do canal")
        if not all(SLUG.match(t) and len(t) <= 30 for t in self.tags): raise ValueError("tags: minúsculas, sem acento, separadas por hífen, até 30 caracteres")
        if len(set(self.tags)) != len(self.tags): raise ValueError("tag repetida")
        if self.imagem is not None:
            p = self.imagem
            if p.startswith("/") or ".." in p.split("/") or "\\" in p: raise ValueError("imagem: caminho relativo a banco-fichas/, sem '..'")
            if not p.startswith(PASTA[self.tipo] + "/"): raise ValueError(f"imagem de {self.tipo} fica em {PASTA[self.tipo]}/")
            if not p.lower().endswith(EXT_IMAGEM): raise ValueError(f"imagem: extensão fora de {EXT_IMAGEM}")
        if self.recortes and not self.imagem: raise ValueError("recortes exigem `imagem`")
        for nome, r in self.recortes.items():
            if not SLUG.match(nome): raise ValueError(f"recorte {nome!r}: nome em minúsculas, sem acento, com hífen")
            if len(r) != 4 or any(not 0.0 <= v <= 1.0 for v in r) or r[2] <= r[0] or r[3] <= r[1]:
                raise ValueError(f"recorte {nome!r}: esperava [x0, y0, x1, y1] normalizado (0 a 1), com x1>x0 e y1>y0")
        if any(not ID_PERSONAGEM.match(i) for i in self.personagens): raise ValueError("personagens: ids PERS-*")
        if self.ambiente is not None and not ID_AMBIENTE.match(self.ambiente): raise ValueError("ambiente: id AMB-*")
        if any(not ID_OBJETO.match(i) for i in self.objetos): raise ValueError("objetos: ids OBJ-*")
        if self.id in (*self.personagens, *self.objetos, self.ambiente): raise ValueError("ficha não referencia a si mesma")
        if self.estado != "sugestao" and not (self.imagem or self.imagem_drive_id or self.videos):
            raise ValueError("ficha sem mídia só existe como `sugestao`")
        if self.estado == "aguardando_ok_jose" and (self.aprovado_por or self.aprovado_em): raise ValueError("ficha aguardando OK não tem aprovação")
        if self.estado == "permanente" and self.origem != "jose" and not (self.aprovado_por and self.aprovado_em):
            raise ValueError("ficha permanente que não é do José precisa de aprovado_por e aprovado_em")
        for campo, texto in (("trava", self.trava), ("proibido", self.proibido), ("titulo", self.titulo)):
            a = afirmativo(texto)
            if campo == "trava" and _PEDE_REALISMO.search(a): raise ValueError("trava pede 3D ou realismo; o padrão é cartum 2D flat (t133u/t148u)")
            if campo == "trava" and _PEDE_TEXTO.search(a): raise ValueError("trava pede texto na imagem; a imagem nunca leva texto (§19)")
            if campo == "trava" and _REAL.search(a): raise ValueError("trava pede pessoa real ou celebridade")
            if _DA_NOME.search(a): raise ValueError(f"{campo}: elenco sem nome falado ou escrito (REGRAS §5)")
        return self
