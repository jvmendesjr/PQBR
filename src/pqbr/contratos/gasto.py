"""Autorização de gasto por etapa (t130u). Determinístico: o código só gasta o que este contrato permite.
Agente primeiro: o modelo propõe o texto; não escolhe modelo, meio nem se pode gastar."""
from __future__ import annotations
from typing import Literal
from . import Contrato

VERSAO = "1.0.0"


class AutorizacaoGasto(Contrato):
    versao: Literal["1.0.0"] = VERSAO
    etapa: str
    modelo: str
    pode_gastar: bool
    meio: Literal["chat_caderno", "chat_9router", "imagem", "video", "nenhum"]
    deterministico: str
    agente: str


GASTO_SEO_NOTEBOOK = AutorizacaoGasto(
    etapa="seo",
    modelo="notebooklm-chat",
    pode_gastar=True,
    meio="chat_caderno",
    deterministico="JSON do SEO passa em validar_seo; senão tenta de novo e cai no fallback",
    agente="o ask devolve o JSON; não escolhe outro modelo",
)

GASTO_SEO_FALLBACK = AutorizacaoGasto(
    etapa="seo_fallback",
    modelo="9router:especialista-seo",
    pode_gastar=True,
    meio="chat_9router",
    deterministico="só depois de duas respostas inválidas do NotebookLM",
    agente="combo já definido em config/modelos_9router.json; o agente não troca o modelo",
)


GASTO_VIDEO_NLM = AutorizacaoGasto(
    etapa="notebooklm_video",
    modelo="notebooklm-video",
    pode_gastar=False,
    meio="video",
    deterministico="nlm_gerar_short recusa antes de chamar o CLI",
    agente="nenhum",
)

GASTO_IMAGEM_NLM = AutorizacaoGasto(
    etapa="notebooklm_infografico",
    modelo="notebooklm-infographic",
    pode_gastar=False,
    meio="imagem",
    deterministico="o episódio não chama nlm_gerar_capa nesta etapa",
    agente="nenhum",
)

GASTO_FLOW_IMAGEM = AutorizacaoGasto(
    etapa="flow_imagem",
    modelo="google-flow",
    pode_gastar=True,
    meio="imagem",
    deterministico="imagens do Flow são gratuitas (t131u). Em 27/10 a tela gerou com Nano Banana 2 Lite, 9:16, e a ficha não mostrou crédito (t132u). Sem teto para cenas individuais (board removido 29/10/2026)",
    agente="não troca para vídeo nem para 2K/4K Aprimorada; se sair pessoa em vez de stickman, não repete o mesmo texto",
)

GASTO_FLOW_VIDEO = AutorizacaoGasto(
    etapa="flow_video",
    modelo="google-flow",
    pode_gastar=True,
    meio="video",
    deterministico="gasta o saldo que houver no Flow; acabou, Google Vids; depois Meta Vibes",
    agente="lê a tela no Camofox e segue; não inventa seletor",
)
