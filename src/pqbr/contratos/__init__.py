"""Contratos Pydantic v2 do domínio PQBR (ARQUITETURA §11, F3-01).

Todo dado que cruza a fronteira de um agente, do Jev ou de uma ferramenta passa por um destes
modelos: entrada tipada, saída validada, campos extras proibidos. Valores fixos vêm de REGRAS."""
from __future__ import annotations
import re
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PALAVRAS_POR_SEGUNDO = 2.3            # REGRAS §5 (t324–t326)
DURACAO_MIN_S, DURACAO_MAX_S, DURACAO_ALVO_S = 15, 180, 50
CTA = "Segue o Porquê BR"             # REGRAS §5 (t262)
JANELAS = ("11:40", "14:40", "18:35", "21:15")  # REGRAS §15
POLEMICA_TETO = 75                    # > 75 aguarda o José (REGRAS §4)
_ROTULO_NOME = re.compile(r"^\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]{1,20}\s*:")
_PEDE_COMENTARIO = re.compile(r"(?i)\b(comenta|comente|deixa (?:aqui )?(?:nos|no) coment|escreve nos coment)")


class Contrato(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


# CONTRATO §16.4 (t427) -------------------------------------------------------------------------
class CenaVisual(Contrato):
    fala: str = Field(min_length=1, max_length=400)
    acao: str = Field(min_length=3, max_length=400)          # ação visível
    enquadramento: str = Field(min_length=3, max_length=120)
    ambiente: str = Field(min_length=3, max_length=400)       # lugar, época, 3–5 objetos-âncora, luz/horário


class BlocoVisual(Contrato):
    estilo: str = Field(min_length=20, max_length=600)        # [ESTILO] 2D + meio/tom/paleta/referência
    personagem: str = Field(min_length=20, max_length=600)    # [PERSONAGEM] repetido palavra por palavra; sem nome
    personagem_2: str | None = Field(default=None, max_length=600)   # máx. 2 (§11.1)
    cenas: list[CenaVisual] = Field(min_length=2, max_length=60)     # [CENAS] ~3–5 s; cena 1 literal; última retoma a 1ª

    @model_validator(mode="after")
    def _regras(self):
        if "2d" not in self.estilo.lower() and "3d" not in self.estilo.lower():
            raise ValueError("[ESTILO] deve declarar 2D (ou 3D só se o roteiro pedir)")
        return self


# RF-07 ---------------------------------------------------------------------------------------
class RoteiroShort(Contrato):
    episodio_id: str = Field(pattern=r"^[a-z0-9-]{3,64}$")
    titulo: str = Field(min_length=5, max_length=100)
    falas: list[str] = Field(min_length=2, max_length=60)
    entidades_cena: list[str] = Field(min_length=1, max_length=40)
    bloco_visual: BlocoVisual                                  # obrigatório (CONTRATO §16.4, t427)

    @property
    def palavras(self) -> int:
        return sum(len(f.split()) for f in self.falas)

    @property
    def duracao_estimada_s(self) -> float:
        return round(self.palavras / PALAVRAS_POR_SEGUNDO, 1)

    @model_validator(mode="after")
    def _regras(self):
        if self.falas[-1].rstrip(" .!") != CTA:
            raise ValueError(f'a última fala deve ser apenas "{CTA}"')
        for f in self.falas:
            if _ROTULO_NOME.match(f):
                raise ValueError("fala com rótulo 'Nome:' (sem nomes, narrador único)")
            if _PEDE_COMENTARIO.search(f):
                raise ValueError("roteiro não pode pedir comentário (t263)")
        if not DURACAO_MIN_S <= self.duracao_estimada_s <= DURACAO_MAX_S:
            raise ValueError(f"duração estimada {self.duracao_estimada_s}s fora de 15–180 s")
        return self


# RF-02 ---------------------------------------------------------------------------------------
class DecisaoRepeticao(Contrato):
    repetido: bool
    barreira: Literal["exata", "variacao", "banco", "nenhuma"]
    tema_parecido: str | None = None
    confianca: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def _coerente(self):
        if self.repetido == (self.barreira == "nenhuma"):
            raise ValueError("repetido exige barreira; não repetido exige 'nenhuma'")
        return self


# RF-05 ---------------------------------------------------------------------------------------
class PontuacaoPolemica(Contrato):
    valor: int = Field(ge=0, le=100)
    componentes: dict[str, int] = Field(default_factory=dict)
    bloqueio_absoluto: bool = False
    categoria_bloqueio: str | None = None

    @property
    def aguarda_jose(self) -> bool:
        return self.valor > POLEMICA_TETO

    @property
    def entra_na_grade(self) -> bool:
        return not self.bloqueio_absoluto and not self.aguarda_jose


# RF-12..RF-14 --------------------------------------------------------------------------------
VEREDITOS = ("aprova", "aprova_com_ressalva", "terceira_rodada", "reprova")  # = auditor_visual.ORDEM (t403)
VereditoTipo = Literal["aprova", "aprova_com_ressalva", "terceira_rodada", "reprova"]
PUBLICAVEL = ("aprova", "aprova_com_ressalva")   # métrica nunca reprova (REGRAS §5); só segurança reprova (t435)


class VereditoAuditor(Contrato):
    veredito: VereditoTipo
    motivos: list[str] = Field(default_factory=list, max_length=20)
    id_cena: str | None = None
    rodadas: int = Field(ge=1, le=3)  # 3ª rodada só desempata (t357 b)

    @model_validator(mode="after")
    def _motivo(self):
        if self.veredito != "aprova" and not self.motivos:
            raise ValueError("veredito diferente de aprova exige motivo")
        return self


# RF-18 ---------------------------------------------------------------------------------------
class DecisaoPublicacao(Contrato):
    acao: Literal["refazer", "trocar", "chamar_jose"]
    confere_agendado: bool


# RF-23 ---------------------------------------------------------------------------------------
class ClassificacaoComentario(Contrato):
    rotulos: list[str] = Field(max_length=10)
    alvo: Literal["video", "canal", "pessoa", "grupo", "outro"]
    ironia_possivel: bool = False
    grave: bool = False
    pede_acao: bool = False


# RF-19, RF-21 --------------------------------------------------------------------------------
class SinalItem5(Contrato):
    origem: Literal["comentarios", "compliance", "metricas", "auditor"]
    motivo: str = Field(min_length=3, max_length=300)
    gravidade: Literal["informativo", "atencao", "critico"]
    video_id: str = Field(pattern=r"^[A-Za-z0-9_-]{11}$")


# RF-33 ---------------------------------------------------------------------------------------
class PropostaAgente(Contrato):
    agente: str = Field(pattern=r"^[a-z0-9-]{3,40}$")
    tipo: Literal["correcao", "melhoria", "manutencao", "parametro"]
    alvo: Literal["parametro", "regra", "tema", "script"]
    chave: str = Field(min_length=1, max_length=120)
    valor_atual: str | None = None
    valor_proposto: str = Field(min_length=1, max_length=500)
    justificativa: str = Field(min_length=5, max_length=500)
    evidencias: list[str] = Field(default_factory=list, max_length=10)
    risco: Literal["baixo", "medio", "alto"] = "medio"


# RF-35 ---------------------------------------------------------------------------------------
class Falha(Contrato):
    evidencia: str = Field(min_length=3, max_length=2000)
    horario: datetime
    episodio: str | None = None


class TicketManutencao(Contrato):
    localizacao: str = Field(min_length=3, max_length=300)   # arquivo/módulo/workflow
    falha: Falha
    correcoes_sugeridas: list[str] = Field(min_length=1, max_length=10)
    aprovacao_abertura: bool = False
    aprovacao_merge: bool = False

    @model_validator(mode="after")
    def _ordem(self):
        if self.aprovacao_merge and not self.aprovacao_abertura:
            raise ValueError("merge sem aprovação de abertura")
        return self


# RF-36 ---------------------------------------------------------------------------------------
class DeterminacaoRevisao(Contrato):
    item: str
    decisao: Literal["excluir", "corrigir", "reaproveitar", "arquivar"]
    observacao: str = ""


# RF-44..RF-46 (t355–t357) --------------------------------------------------------------------
class TriagemCorrecao(Contrato):
    classe: Literal["corrigivel", "sensivel", "fora_de_escopo"]
    motivo: str = Field(min_length=3, max_length=300)


class PassoCorrecao(Contrato):
    acao: Literal["navegar", "ler", "clicar", "digitar", "colar", "upload", "buscar_codigo"]
    alvo: str = Field(max_length=300)


class ResultadoIntervencao(Contrato):
    resolvido: bool
    passos: list[PassoCorrecao] = Field(default_factory=list, max_length=50)
    conta_confere: bool = True        # t357 d: sessão/conta certas antes de agir
    aprendizado: str = Field(default="", max_length=1000)
    proposta_script: str | None = Field(default=None, max_length=2000)


class VerificacaoCorrecao(Contrato):
    ok: bool
    motivo: str = ""


class ResultadoCorrecao(Contrato):
    resultado: Literal["corrigido", "esgotado", "sensivel"]
    tentativas: int = Field(ge=0, le=3)
    motivo: str = ""
    proposta_script: str | None = None
    chamar_jose: bool


# RF-47 ---------------------------------------------------------------------------------------
class RegistroConsumo(Contrato):
    provedor: str = Field(min_length=2, max_length=40)
    modelo: str = Field(min_length=1, max_length=120)
    tipo_acao: Literal['ideacao', 'roteiro', 'seo', 'pesquisa', 'ficha_visual', 'auditor_visual',
                       'auditor_texto', 'auditor_desempate', 'jev_triagem', 'jev_classificacao',
                       'jev_decisao', 'jev_verificacao', 'correcao_autonoma', 'comunidade',
                       'compliance', 'analista', 'assistente', 'publicacao', 'teste_resposta', 'outro']
    sucesso: bool
    ferramenta: str | None = None
    workflow_id: str | None = None
    activity: str | None = None
    tentativa: int = Field(default=1, ge=1)
    chamadas: int = Field(default=1, ge=1)
    tokens_entrada: int | None = Field(default=None, ge=0)
    tokens_saida: int | None = Field(default=None, ge=0)
    duracao_ms: int | None = Field(default=None, ge=0)
    erro_classe: str | None = Field(default=None, max_length=80)
    custo_estimado_micro_usd: int | None = Field(default=None, ge=0)


# RF-01 ---------------------------------------------------------------------------------------
class ItemGrade(Contrato):
    data: date
    janela: Literal["11:40", "14:40", "18:35", "21:15"]
    tema: str = Field(min_length=3, max_length=300)
    polemica: int = Field(ge=0, le=100)
    fonte: Literal["em_alta", "perene", "reserva"]
    status: Literal["planejado", "aguardando_jose"] = "planejado"


class GradeDiaria(Contrato):
    data: date
    itens: list[ItemGrade] = Field(max_length=4)

    @model_validator(mode="after")
    def _consistente(self):
        if any(i.data != self.data for i in self.itens):
            raise ValueError("item de outra data na grade (incidente de 08/10)")
        if len({i.janela for i in self.itens}) != len(self.itens):
            raise ValueError("janela repetida")
        return self


# CONTRATO §16.5 / migração 0012 (t427) ------------------------------------------------------------
_SLUG = r"^[a-z0-9][a-z0-9-]{1,60}$"
_CODIGO = r"^PQBR-EP[0-9]{4,}$"
CategoriaTema = Literal["expressao", "habito_mania", "curiosidade_cultura_pop", "sazonal"]


class TemaPendente(Contrato):
    slug: str = Field(pattern=_SLUG)
    tema: str = Field(min_length=3, max_length=300)
    tema_normalizado: str = Field(min_length=3, max_length=300)
    categoria: CategoriaTema
    janela_sazonal: tuple[date, date] | None = None
    data_prevista: date | None = None
    status: Literal["proposto", "aprovado", "em_producao", "auditado", "pronto_publicar", "falhou"] = "proposto"
    fontes: list[str] = Field(default_factory=list, max_length=20)   # ≥ 2 antes de aprovar (§16.5)
    bloco_visual: BlocoVisual | None = None
    metadados: dict = Field(default_factory=dict)
    caminhos: dict = Field(default_factory=dict)
    criado_por: str = "codigo"

    @model_validator(mode="after")
    def _regras(self):
        if self.categoria == "sazonal" and self.janela_sazonal is None:
            raise ValueError("tema sazonal exige janela_sazonal (Caçador, 30 dias antes)")
        if self.status != "proposto" and len(self.fontes) < 2:
            raise ValueError("tema fora de 'proposto' exige ≥ 2 fontes (§16.5)")
        return self


class TemaPublicado(Contrato):
    id: int = Field(ge=1)
    slug: str = Field(pattern=_SLUG)
    tema: str = Field(min_length=3, max_length=300)
    tema_normalizado: str = Field(min_length=3, max_length=300)
    categoria: CategoriaTema
    codigo: str = Field(pattern=_CODIGO)
    video_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{11}$")
    publicado_em: datetime
    privacidade: Literal["private", "public", "scheduled"] = "private"
    fontes: list[str] = Field(default_factory=list)
    bloco_visual: BlocoVisual | None = None
    metadados: dict = Field(default_factory=dict)
    caminhos: dict = Field(default_factory=dict)


# Migração 0013 (t435) ------------------------------------------------------------------------------
class ErroAceitavel(Contrato):
    episodio_codigo: str | None = Field(default=None, pattern=_CODIGO)
    tema_slug: str | None = Field(default=None, pattern=_SLUG)
    cena: str | None = Field(default=None, pattern=r"^S[0-9]{2,}$")
    categoria: Literal["legenda", "texto", "visual", "audio", "loop", "outro"]
    chave: str = Field(min_length=2, max_length=80)
    descricao: str = Field(min_length=3, max_length=500)
    gravidade: Literal["leve", "media"] = "leve"
    veredito_auditor: Literal["aprova", "aprova_com_ressalva", "terceira_rodada"]
    rodadas: int = Field(default=2, ge=1, le=3)
    evidencia: dict = Field(default_factory=dict)
    decisao: Literal["pendente", "aceito", "corrigir_prompt", "virar_seguranca"] = "pendente"
    revisado_por: str | None = None
    revisado_em: datetime | None = None

    @model_validator(mode="after")
    def _regras(self):
        if not (self.episodio_codigo or self.tema_slug):
            raise ValueError("episodio_codigo ou tema_slug obrigatório")
        if self.decisao != "pendente" and not (self.revisado_por and self.revisado_em):
            raise ValueError("decisão exige revisado_por e revisado_em")
        return self
