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
CTA = "Segue o Porquê BR"             # REGRAS §5 (t467; fallback)
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


# CONTRATO-EDITORIAL §19 [ESTILO], José 27/10/2026 (t133u). Identidade única: stickman.
# O nome ESTILO_PADRAO_2D permanece só como apelido do texto vigente, para import antigo.
ESTILO_PADRAO_STICKMAN = (
    "Stickman de tubos grossos e arredondados, cabeça redonda grande, membros com ponta redonda, "
    "traço chapado, sem dedos desenhados e sem pessoa de cartum. Um acento de cor chapada por personagem, "
    "fundo limpo e claro, no máximo 3 a 5 objetos, humor de comédia leve. Personagem grande no quadro, "
    "cabeça inteira visível, agindo, expressão simples e exagerada, boca fechada. "
    "Proibido: pessoa desenhada, fotorrealismo, volume 3D, rosto de pessoa real ou celebridade, marca ou logo real, "
    "texto escrito dentro da imagem. Formato vertical 9:16, faixas de cima e de baixo livres."
)
ESTILO_PADRAO_2D = ESTILO_PADRAO_STICKMAN


class BlocoVisual(Contrato):
    estilo: str = Field(default=ESTILO_PADRAO_STICKMAN, min_length=20, max_length=900)
    personagem: str = Field(min_length=20, max_length=600)    # frase-trava do stickman; sem nome falado
    personagem_2: str | None = Field(default=None, max_length=600)   # máx. 2 (§11.1)
    cenas: list[CenaVisual] = Field(min_length=2, max_length=60)     # [CENAS] ~2–4 s; cena 1 literal; última retoma a 1ª
    pedido_3d_ou_realista: bool = False   # t133u: o campo fica, mas true é recusado (3D descartado)

    @model_validator(mode="after")
    def _regras(self):
        if self.pedido_3d_ou_realista:
            raise ValueError("[ESTILO] 3D e realismo foram descartados (t133u)")
        e = self.estilo.lower()
        afirm = re.sub(r"proibid[oa]s?:?[^.]*", " ", e)
        afirm = re.sub(r"\b(sem|nada de|nunca|nem)\s+[^,.;]*", " ", afirm)
        if re.search(r"\b3d\b|fotorreal|realista|photoreal|hiper.?real", afirm):
            raise ValueError("[ESTILO] pede 3D ou realismo; descartado (t133u)")
        if "stickman" not in e:
            raise ValueError("[ESTILO] a identidade é stickman (t133u)")
        return self


# RF-07 ---------------------------------------------------------------------------------------
class RoteiroShort(Contrato):
    episodio_id: str = Field(pattern=r"^[a-z0-9-]{3,64}$")
    titulo: str = Field(min_length=5, max_length=100)
    falas: list[str] = Field(min_length=2, max_length=60)
    tipo_cta: Literal["trocadilho_tema", "convite_seguir", "fallback"]
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
        cta_final = self.falas[-1].strip()
        if not cta_final:
            raise ValueError("a última fala deve conter uma CTA")
        if self.tipo_cta == "fallback":
            if cta_final.rstrip(" .!") != CTA:
                raise ValueError(f'CTA fallback deve ser apenas "{CTA}"')
        elif cta_final.rstrip(" .!") == CTA:
            raise ValueError('CTA literal deve declarar tipo_cta="fallback"')
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
    # 'ficha_visual' = só histórico (fichas pausadas, t400/t437): aceito para ler linhas antigas; código novo não usa.
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


# Jev: classificações estruturadas (RNF-02, REGRAS §7; t437) ------------------------------------
class ClassificacaoEmailYouTube(Contrato):
    """E-mail do YouTube/Google para a conta do canal. O Jev só classifica; o código age."""
    categoria: Literal["strike", "claim", "policy_warning", "monetization", "account_security",
                       "upload_status", "marketing", "other"]
    gravidade: Literal["informativo", "atencao", "critico"]
    acao: Literal["ignorar", "registrar", "abrir_ticket", "chamar_jose"]
    video_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{11}$")
    prazo: date | None = None                      # prazo de recurso/resposta citado no e-mail
    confianca: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def _regras(self):
        if self.categoria in ("strike", "account_security") and self.acao != "chamar_jose":
            raise ValueError("strike/segurança da conta sempre chama o José (recurso só com ele)")
        if self.categoria in ("strike", "claim", "policy_warning", "account_security") and self.gravidade == "informativo":
            raise ValueError("categoria de risco não pode ser informativa")
        return self


class ClassificacaoPopupCamofox(Contrato):
    """Pop-up/tela inesperada no Camofox. Ações fora da allowlist (login, captcha) escalam."""
    categoria: Literal["cookie_consent", "login_required", "captcha", "permission", "promo", "error", "other"]
    acao: Literal["aceitar", "fechar", "recusar", "recarregar", "reautenticar", "chamar_jose", "ignorar"]
    seletor: str | None = Field(default=None, max_length=300)    # alvo do clique, se houver
    confianca: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def _regras(self):
        if self.categoria == "captcha" and self.acao != "chamar_jose":
            raise ValueError("captcha nunca é resolvido por agente: chamar_jose")
        if self.categoria == "login_required" and self.acao not in ("reautenticar", "chamar_jose"):
            raise ValueError("login exige reautenticar (playbook) ou chamar_jose")
        if self.acao == "aceitar" and self.categoria not in ("cookie_consent", "permission"):
            raise ValueError("aceitar só para consentimento de cookies/permissão")
        return self


# SEO (RF-06; YouTube Data API snippet/status; t437) --------------------------------------------
CATEGORIA_YOUTUBE = "27"   # Educação — única categoria do canal (José 12/10/2026; antes havia "24" no dry-run)
_HASHTAG = re.compile(r"^#[0-9A-Za-zÀ-ÿ_]{2,50}$")


MARCA_LINK_QUEBRADO = re.compile(r"\[?\s*(suspicious\s+link\s+removed|link\s+removed|link\s+removido)\s*\]?", re.I)


class PacoteSEO(Contrato):
    titulo: str = Field(min_length=5, max_length=100)
    descricao: str = Field(min_length=10, max_length=5000)
    tags: list[str] = Field(default_factory=list, max_length=30)
    hashtags: list[str] = Field(min_length=3, max_length=15)
    categoria_id: str = Field(default=CATEGORIA_YOUTUBE, pattern=r"^[0-9]{1,3}$")   # 27 = Educação (aprovado José 12/10)
    idioma: Literal["pt-BR"] = "pt-BR"
    contem_midia_sintetica: bool = False    # status.containsSyntheticMedia; cartum 2D não realista não exige o rótulo (José 12/10)

    @field_validator("hashtags")
    @classmethod
    def _hashtags(cls, v: list[str]) -> list[str]:
        for h in v:
            if not _HASHTAG.match(h):
                raise ValueError(f"hashtag inválida: {h!r} (precisa de #, sem espaço)")
        if len({h.lower() for h in v}) != len(v):
            raise ValueError("hashtag repetida")
        return v

    @model_validator(mode="after")
    def _regras(self):
        if any(MARCA_LINK_QUEBRADO.search(t) for t in (self.titulo, self.descricao, *self.tags)):
            raise ValueError("link quebrado pelo NotebookLM ('[suspicious link removed]'); montar fontes pelo registro (t466)")
        if any("<" in t or ">" in t for t in (self.titulo, self.descricao, *self.tags)):
            raise ValueError("YouTube recusa < e > em título/descrição/tags")
        # limite da API: 500 caracteres somando as tags (tag com espaço conta +2 pelas aspas)
        total = sum(len(t) + (2 if " " in t else 0) for t in self.tags) + max(len(self.tags) - 1, 0)
        if total > 500:
            raise ValueError(f"tags somam {total} caracteres (> 500)")
        return self

    def snippet_status(self) -> dict:
        return {"snippet": {"title": self.titulo, "description": self.descricao, "tags": list(self.tags),
                            "categoryId": self.categoria_id, "defaultLanguage": self.idioma,
                            "defaultAudioLanguage": self.idioma},
                "status": {"privacyStatus": "private", "containsSyntheticMedia": self.contem_midia_sintetica,
                           "selfDeclaredMadeForKids": False}}


# ADR-011 (t510): saída do agente Líder Editorial na reposição da grade ---------------------------
class TemaProposto(Contrato):
    categoria: Literal["expressao", "habito_mania", "curiosidade_cultura_pop"]   # sazonal só pelo Caçador
    tema: str = Field(min_length=8, max_length=300, pattern=r"(?i)^\s*por que\b")


class PropostaTemas(Contrato):
    temas: list[TemaProposto] = Field(min_length=1, max_length=10)
    justificativa: str = Field(default="", max_length=500)


# t513/t515: contratos das portas de motor (src/pqbr/motores) -------------------------------------
# ---- MotorIntelectual -------------------------------------------------------------------------
class PedidoMotor(Contrato):
    tarefa: Literal["temas", "roteiro", "seo", "pesquisa", "direcao"]
    pergunta: str = Field(min_length=10, max_length=20000)
    contexto: str = Field(default="", max_length=200000)     # vira fonte do caderno/sessão (ex.: temas já usados)
    sessao: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,60}$")  # rótulo da sessão efêmera (no NotebookLM: título "Short - <sessao>")
    pesquisa_web: str | None = Field(default=None, max_length=1500)


class RespostaMotor(Contrato):
    motor: str
    sessao_id: str
    texto: str = Field(max_length=20000)
    meta: dict = Field(default_factory=dict)


class PedidoVideo(Contrato):
    codigo: str
    roteiro: str = Field(min_length=10)
    bloco_visual: dict = Field(default_factory=dict)
    destino: str
    vertical: bool = True


class ResultadoVideo(Contrato):
    gerador: str
    arquivo: str
    meta: dict = Field(default_factory=dict)


# t515: versão SemVer de cada contrato. MAJOR = quebra (campo removido/renomeado/regra mais estrita);
# MINOR = campo opcional novo/regra mais frouxa; PATCH = doc. Todo contrato novo entra aqui (teste obriga).
# Vigia de atualizações — Dev (t516) -----------------------------------------------------------
class FerramentaVigiada(Contrato):
    nome: str = Field(min_length=2, max_length=80)
    fonte: Literal["pypi", "github", "manual"]
    alvo: str = Field(min_length=2, max_length=200)
    python: str | None = None
    notas: str = ""


class ItemAtualizacao(Contrato):
    nome: str
    instalada: str = ""
    ultima: str = ""
    situacao: Literal["em_dia", "patch", "minor", "major", "desconhecido"]
    proposta: str = Field(min_length=3, max_length=300)
    notas: str = ""


class RelatorioAtualizacoes(Contrato):
    semana: str = Field(pattern=r"^\d{4}w\d{2}$")
    itens: list[ItemAtualizacao]
    resumo: str = Field(min_length=3, max_length=3000)
    aplicado: Literal[False] = False   # o Dev nunca aplica


# Navegador/identidade — ADR-012 (t526) -------------------------------------------------------
class InstanciaNavegador(Contrato):
    conta: str = Field(pattern=r"^[a-z0-9-]{2,30}$")
    porta: int = Field(ge=9000, le=9999)
    estado: Literal["individual", "ativa", "reservada"]
    unit: str = Field(min_length=3, max_length=80)
    nota: str = ""


class SaudeNavegador(Contrato):
    conta: str
    porta: int
    ok: bool
    navegador: bool = False
    motivo: str = ""


VERSOES: dict[str, str] = {
    "InstanciaNavegador": "1.0.0",
    "SaudeNavegador": "1.0.0",
    "FerramentaVigiada": "1.0.0",
    "ItemAtualizacao": "1.0.0",
    "RelatorioAtualizacoes": "1.0.0",
    "CenaVisual": "1.0.0",
    "BlocoVisual": "2.0.0",
    "RoteiroShort": "1.0.0",
    "DecisaoRepeticao": "1.0.0",
    "PontuacaoPolemica": "1.0.0",
    "VereditoAuditor": "1.0.0",
    "DecisaoPublicacao": "1.0.0",
    "ClassificacaoComentario": "1.0.0",
    "SinalItem5": "1.0.0",
    "PropostaAgente": "1.0.0",
    "Falha": "1.0.0",
    "TicketManutencao": "1.0.0",
    "DeterminacaoRevisao": "1.0.0",
    "TriagemCorrecao": "1.0.0",
    "PassoCorrecao": "1.0.0",
    "ResultadoIntervencao": "1.0.0",
    "VerificacaoCorrecao": "1.0.0",
    "ResultadoCorrecao": "1.0.0",
    "RegistroConsumo": "1.0.0",
    "ItemGrade": "1.0.0",
    "GradeDiaria": "1.0.0",
    "TemaPendente": "1.0.0",
    "TemaPublicado": "1.0.0",
    "ErroAceitavel": "1.0.0",
    "ClassificacaoEmailYouTube": "1.0.0",
    "ClassificacaoPopupCamofox": "1.0.0",
    "PacoteSEO": "1.0.0",
    "TemaProposto": "1.0.0",
    "PropostaTemas": "1.0.0",
    "PedidoMotor": "1.0.0",
    "RespostaMotor": "1.0.0",
    "PedidoVideo": "1.0.0",
    "ResultadoVideo": "1.0.0",
}
