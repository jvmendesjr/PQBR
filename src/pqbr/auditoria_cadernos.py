"""Cadernos de auditoria (t170u): mestre permanente + efêmero por episódio.

Puro, sem rede, sem Temporal: o worker continua sem reinício nesta
entrega, e a criação/consulta no Google passa pelo script
scripts/notebooklm/criar_mestre_auditoria.py e pelo CLI notebooklm-py
(perfil pqbr), nunca pela conta pessoal e nunca por título solto.

Regra central, herdada do fluxo mestre+efêmero criativo:
- Mestre de Auditoria = regra permanente. Nunca mídia, nunca episódio,
  nunca veredito de episódio específico.
- Efêmero de Auditoria = caso concreto. Um por episódio, registrado
  pelo ID, com cópia versionada (snapshot) das regras do mestre
  injetada como texto, porque um caderno não pode usar outro como
  fonte. Na auditoria que vale, a referência é UMA só: o efêmero.
  Mestre + efêmero juntos só em teste comparativo.
- Vídeo bruto não entra no caderno como vídeo assistido: entram
  stills/pranchas rotuladas, quadros-chave, descrição de movimento,
  roteiro, fichas e laudo textual. Transcrição sozinha não audita
  movimento, tempo nem mão segurando objeto.
"""
from __future__ import annotations
import re
from pydantic import BaseModel, ConfigDict, Field

CODIGO = re.compile(r"^PQBR-EP[0-9]{4,}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,60}$")
TITULO_MESTRE = "PQBR - Mestre de Auditoria"

# Campos do veredito atual (auditor_gemini.CenaAuditada, t108u/P7),
# reutilizados aqui como checklist textual do caderno de auditoria.
CHECKLIST_CENA = [
    "tem_personagem", "tem_texto_na_tela", "segue_estilo_declarado",
    "mesmo_personagem_do_bloco", "imagem_corresponde_a_fala",
    "legivel_no_celular", "ambiente_brasileiro", "legenda_com_erro",
    "parece_pessoa_real", "marca_real", "estereotipo_ofensivo",
    "texto_com_erro_de_sentido", "foco_unico_zona_segura",
    "corresponde_ao_titulo", "legenda_cobre_foco",
    "boca_articula_fala", "corte_oculos_cabeca", "grotesco",
]

REPROVA_SOZINHO = [
    "boca_articula_fala", "corte_oculos_cabeca", "grotesco",
    "tem_texto_na_tela", "parece_pessoa_real", "marca_real",
    "estereotipo_ofensivo", "texto_com_erro_de_sentido",
]

ERROS_RECORRENTES = [
    "PERS-menina-rosa lida como criança por proporção (deve ser mulher jovem adulta, em pé no chão)",
    "Personagem em banquinho/cadeira para parecer maior (proibido; balcão/mesa na altura da cintura)",
    "Braços realistas extras ou mãos extras sem corpo que as segure",
    "Objeto levantando/derramando sozinho, sem mão visível (ex.: chaleira sem mão, EP1003)",
    "Clipe gerado a partir de imagem já rejeitada (nunca reutilizar still reprovado)",
    "Texto dentro da imagem, letreiro, placa ou balão",
    "Movimento plano: só zoom lento, sem intenção cinematográfica",
]


def titulo_efemero_auditoria(codigo: str, slug: str) -> str:
    """Título do efêmero de auditoria. Identidade continua sendo o ID registrado, nunca o título."""
    if not CODIGO.match(codigo):
        raise ValueError("código de episódio inválido")
    if not SLUG.match(slug):
        raise ValueError("slug inválido")
    return f"Auditoria - {codigo} - {slug}"


def eh_titulo_auditoria(titulo: str) -> bool:
    return titulo.startswith("Auditoria - PQBR-EP")


def snapshot_regras_mestre(versao: str = "1.0.0") -> str:
    """Texto versionado a injetar no efêmero de auditoria (AUD-SNAP).

    É uma cópia, não um link: se o mestre mudar, o efêmero antigo
    continua com a versão que o auditou, e o novo efêmero recebe a nova.
    """
    linhas = [
        f"AUD-SNAP versao={versao} mestre={TITULO_MESTRE}",
        "Padrão visual: cartoon 2D flat colorido stickman, contorno preto, cabeça redonda branca,",
        "dois olhos sempre visíveis, traço preto fino, roupa chapada colorida fixa, fundo creme claro,",
        "sem texto dentro da imagem, sem pessoa realista, sem volume 3D, sem dedos realistas.",
        "PERS-menina-rosa: mulher jovem adulta, proporções adultas, em pé no chão. Nunca girl, nunca criança.",
        "Checklist por cena: " + ", ".join(CHECKLIST_CENA) + ".",
        "Reprovam sozinhos: " + ", ".join(REPROVA_SOZINHO) + ".",
        "Erros recorrentes a procurar primeiro:",
    ] + [f"- {e}" for e in ERROS_RECORRENTES] + [
        "Veredito estruturado por cena: aprova / aprova_com_ressalva / reprova + motivos com fonte citada + o que mudar.",
        "Vídeo: auditar por stills, quadros-chave e descrição de movimento. Transcrição sozinha não basta.",
        "Em dúvida: reprovar com ressalva e pedir o quadro que falta. Nunca inventar o que não foi visto.",
    ]
    return "\n".join(linhas)


class VereditoCenaAuditoria(BaseModel):
    """Veredito mínimo de uma cena auditada pelo caderno (texto, não decisão do worker)."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str = Field(pattern=r"^(S[0-9]{2,}|CAPA)$")
    veredito: str = Field(pattern=r"^(aprova|aprova_com_ressalva|reprova)$")
    motivos: list[str] = Field(default_factory=list)
    fontes_citadas: list[str] = Field(default_factory=list)
    o_que_mudar: str = ""
