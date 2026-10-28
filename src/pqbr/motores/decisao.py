"""Porta `decide()` do Jev (JEV-EF; REGRAS §7; RNF-02; t143u).

O código faz perguntas fechadas sobre um estado em texto: escolha entre opções (choice), nível em
uma escala (score) ou probabilidade de um fato (noul). O Jev responde só com decisão estruturada e
nunca redige texto. Cada resposta é checada contra a pergunta feita e o contrato Pydantic recebe os
dados. Se a confiança ficar abaixo do limiar do contrato, se o contrato não tiver limiar, se o contrato
recusar o resultado ou se o Jev falhar, a decisão volta com `escalar=True`. Quem chamou leva o caso a um
LLM ou ao José. Nenhuma falha vira ação.

Peças: `Pergunta` (pedido), `Provedor` (porta de transporte), `JevTypeSafe` e `JevOpenRouter`
(adaptadores; o OpenRouter manda o mesmo pedido e recebe as mesmas respostas), `DecisorJev` (núcleo:
tentativas, fallback, limiar e registro de consumo). `decide()` usa o decisor montado pelo bloco
`decisao` de `config/motores.json`. A chamada é síncrona: de dentro de um event loop, use `to_thread`.
A porta não verifica segredo nem PII do estado: quem chama anonimiza (REGRAS §17).
"""
from __future__ import annotations

import http.client
import json
import math
import os
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Generic, Literal, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel, ValidationError

from ..contratos import RegistroConsumo
from ..storage.consumo import gravar
from . import config

M = TypeVar("M", bound=BaseModel)
TIPOS = ("choice", "score", "noul")
RETRY = frozenset({"rate_limited", "overloaded", "network", "http_500", "http_502", "http_503", "http_504"})
MAX_RESPOSTA_BYTES = 1_000_000
MAX_ESTADO_CHARS = 60_000
USER_AGENT = "pqbr-decisao/0.18"
Transporte = Callable[[str, bytes, dict[str, str], float], bytes]


class FalhaDecisao(RuntimeError):
    """Resposta do Jev que não pode ser usada. `codigo` diz o motivo, sem trecho de resposta nem segredo."""

    def __init__(self, codigo: str) -> None:
        super().__init__(codigo)
        self.codigo = codigo


def codigo_http(status: int) -> str:
    return {401: "auth_failed", 403: "auth_failed", 402: "credits_exhausted", 429: "rate_limited",
            529: "overloaded"}.get(status, f"http_{status}")


@dataclass(frozen=True)
class Pergunta:
    """Pergunta fechada. `criterios`: opção → significado (choice); níveis do menor ao maior (score); nada (noul)."""

    nome: str
    tipo: Literal["choice", "score", "noul"]
    instrucoes: str
    criterios: Mapping[str, str] | Sequence[str] | None = None

    def __post_init__(self) -> None:
        if self.tipo not in TIPOS:
            raise ValueError(f"tipo de pergunta desconhecido: {self.tipo}")
        if not self.nome or not self.instrucoes.strip():
            raise ValueError("pergunta sem nome ou sem instrução")
        if self.tipo == "choice" and not (isinstance(self.criterios, Mapping) and len(self.criterios) >= 2):
            raise ValueError("choice precisa de pelo menos duas opções")
        if self.tipo == "score" and not (isinstance(self.criterios, (list, tuple)) and len(self.criterios) >= 2):
            raise ValueError("score precisa de pelo menos dois níveis, do menor para o maior")
        if self.tipo == "noul" and self.criterios is not None:
            raise ValueError("noul não recebe critérios")

    def como_jev(self) -> dict[str, Any]:
        if self.tipo == "noul":
            return {"type": "noul", "instructions": self.instrucoes}
        if self.tipo == "choice":
            return {"type": "choice", "instructions": self.instrucoes, "criteria": dict(self.criterios)}
        return {"type": "score", "instructions": self.instrucoes, "criteria": list(self.criterios)}


@dataclass(frozen=True)
class Resposta:
    """Resposta já checada. `confianca` é a confiança do Jev na escolha (choice e score) ou, no noul, a certeza
    do lado que ele prefere, max(p, 1-p). `nivel` é o nível do score ou, no noul, a probabilidade de sim."""

    tipo: str
    confianca: float
    escolha: str | None = None
    nivel: float | None = None


@dataclass(frozen=True)
class Decisao(Generic[M]):
    """Resultado de `decide()`. Com `escalar=True`, `valor` é None e quem chamou decide o próximo passo."""

    valor: M | None
    escalar: bool
    motivo: str
    confianca: float | None = None
    provedor: str | None = None
    respostas: Mapping[str, Resposta] | None = None


@runtime_checkable
class Provedor(Protocol):
    """Porta de transporte: envia o pedido e devolve o JSON da resposta, ou levanta FalhaDecisao."""

    nome: str
    modelo: str

    def consultar(self, corpo: dict[str, Any], timeout: float) -> Any: ...


class _SemRedirecionamento(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        # Um redirecionamento levaria o token para outra origem.
        raise urllib.error.HTTPError(req.full_url, code, "redirecionamento recusado", headers, fp)


def _enviar_urllib(url: str, corpo: bytes, cabecalhos: dict[str, str], timeout: float) -> bytes:
    pedido = urllib.request.Request(url, data=corpo, headers=cabecalhos, method="POST")
    try:
        with urllib.request.build_opener(_SemRedirecionamento).open(pedido, timeout=timeout) as resposta:
            bruto = resposta.read(MAX_RESPOSTA_BYTES + 1)
    except urllib.error.HTTPError as erro:
        raise FalhaDecisao(codigo_http(erro.code)) from None
    except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException):
        raise FalhaDecisao("network") from None
    if len(bruto) > MAX_RESPOSTA_BYTES:
        raise FalhaDecisao("response_too_large")
    return bruto


class ProvedorHTTP:
    """Pedido HTTP com corpo JSON. A chave é lida do ambiente a cada chamada e nunca é gravada nem registrada."""

    nome = "http"

    def __init__(self, *, endpoint: str, modelo: str, chave_env: str, transporte: Transporte | None = None) -> None:
        self.endpoint = endpoint
        self.modelo = modelo
        self.chave_env = chave_env
        self._transporte = transporte or _enviar_urllib

    def consultar(self, corpo: dict[str, Any], timeout: float) -> Any:
        chave = (os.environ.get(self.chave_env) or "").strip()
        if not chave:
            raise FalhaDecisao("no_key")
        dados = json.dumps({**corpo, "model": self.modelo}, separators=(",", ":"), default=str).encode("utf-8")
        cabecalhos = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json",
                      "Accept": "application/json", "User-Agent": USER_AGENT}
        bruto = self._transporte(self.endpoint, dados, cabecalhos, timeout)
        try:
            return json.loads(bruto)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise FalhaDecisao("malformed") from None


class JevTypeSafe(ProvedorHTTP):
    """Jev direto na TypeSafe: POST /v1/systemone, modelo `jev-latest`."""

    nome = "typesafe"


class JevOpenRouter(ProvedorHTTP):
    """Mesmo Jev pelo OpenRouter (fallback, JEV-02). Muda o endpoint, o modelo e a chave; pedido e respostas são iguais."""

    nome = "openrouter"


def _unitario(valor: Any) -> float:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise FalhaDecisao("malformed")
    numero = float(valor)
    if not math.isfinite(numero) or not -1e-6 <= numero <= 1 + 1e-6:
        raise FalhaDecisao("malformed")
    return min(1.0, max(0.0, numero))


def _checar(pergunta: Pergunta, resposta: Any) -> Resposta:
    if not isinstance(resposta, dict) or resposta.get("type") != pergunta.tipo:
        raise FalhaDecisao("malformed")
    if pergunta.tipo == "noul":
        p = _unitario(resposta.get("noul"))
        return Resposta("noul", max(p, 1.0 - p), nivel=p)
    if pergunta.tipo == "choice":
        opcoes = set(pergunta.criterios)
        escolha = resposta.get("choice")
        probabilidades = resposta.get("probabilities")
        if not isinstance(escolha, str) or escolha not in opcoes:
            raise FalhaDecisao("malformed")
        if not isinstance(probabilidades, dict) or not set(probabilidades) <= opcoes:
            raise FalhaDecisao("malformed")
        for valor in probabilidades.values():
            _unitario(valor)
        return Resposta("choice", _unitario(resposta.get("confidence")), escolha=escolha)
    nivel = resposta.get("score")
    if isinstance(nivel, bool) or not isinstance(nivel, (int, float)) or not math.isfinite(float(nivel)):
        raise FalhaDecisao("malformed")
    if not -0.5 <= float(nivel) <= len(pergunta.criterios) - 0.5:
        raise FalhaDecisao("malformed")
    return Resposta("score", _unitario(resposta.get("confidence")), nivel=float(nivel))


def _validar_respostas(perguntas: Sequence[Pergunta], bruto: Any) -> dict[str, Resposta]:
    respostas = bruto.get("answers") if isinstance(bruto, dict) else None
    if not isinstance(respostas, dict):
        raise FalhaDecisao("malformed")
    return {p.nome: _checar(p, respostas.get(p.nome)) for p in perguntas}


def _contagem(uso: Any, *chaves: str) -> int | None:
    if not isinstance(uso, dict):
        return None
    for chave in chaves:
        valor = uso.get(chave)
        if isinstance(valor, int) and not isinstance(valor, bool) and valor >= 0:
            return valor
    return None


class DecisorJev:
    """Núcleo da porta: tenta cada provedor da cadeia, valida, fecha pelo limiar e registra cada chamada enviada."""

    def __init__(self, cadeia: Sequence[Provedor], *, limiares: Mapping[str, float],
                 registrar: Callable[[RegistroConsumo], None], timeout_s: float = 15.0,
                 tentativas: int = 2, pausa_s: float = 0.25) -> None:
        if not cadeia:
            raise ValueError("cadeia de provedores vazia")
        self.cadeia = tuple(cadeia)
        self.limiares = dict(limiares)
        self.registrar = registrar
        self.timeout_s = timeout_s
        self.tentativas = max(1, tentativas)
        self.pausa_s = pausa_s

    def decidir(self, contrato: type[M], estado: str, perguntas: Sequence[Pergunta],
                montar: Callable[[Mapping[str, Resposta]], Mapping[str, Any]], *,
                tipo_acao: str = "jev_decisao", workflow_id: str | None = None,
                activity: str | None = None) -> Decisao[M]:
        if not perguntas:
            raise ValueError("decide() precisa de pelo menos uma pergunta")
        nomes = [p.nome for p in perguntas]
        if len(set(nomes)) != len(nomes):
            raise ValueError("nomes de pergunta repetidos")
        if len(estado) > MAX_ESTADO_CHARS:
            return Decisao(None, True, "estado_grande_demais")
        corpo = {"state": estado, "questions": {p.nome: p.como_jev() for p in perguntas}}
        falhas: list[str] = []
        n = 0
        for provedor in self.cadeia:
            tentativa = 0
            while True:
                tentativa += 1
                n += 1
                inicio = time.monotonic()
                bruto = None
                try:
                    bruto = provedor.consultar(corpo, self.timeout_s)
                    respostas = _validar_respostas(perguntas, bruto)
                except FalhaDecisao as falha:
                    falhas.append(f"{provedor.nome}:{falha.codigo}")
                    if falha.codigo != "no_key":
                        self._registrar(provedor, n, False, falha.codigo, inicio, bruto,
                                        tipo_acao, workflow_id, activity)
                    if falha.codigo in RETRY and tentativa < self.tentativas:
                        time.sleep(self.pausa_s * tentativa)
                        continue
                    break
                self._registrar(provedor, n, True, None, inicio, bruto, tipo_acao, workflow_id, activity)
                return self._fechar(contrato, provedor, respostas, montar)
        return Decisao(None, True, "jev_indisponivel: " + ", ".join(falhas))

    def _registrar(self, provedor: Provedor, n: int, sucesso: bool, erro: str | None, inicio: float,
                   bruto: Any, tipo_acao: str, workflow_id: str | None, activity: str | None) -> None:
        uso = bruto.get("usage") if isinstance(bruto, dict) else None
        self.registrar(RegistroConsumo(
            provedor=provedor.nome, modelo=provedor.modelo, tipo_acao=tipo_acao, sucesso=sucesso,
            ferramenta="jev", workflow_id=workflow_id, activity=activity, tentativa=n,
            tokens_entrada=_contagem(uso, "input_tokens", "prompt_tokens"),
            tokens_saida=_contagem(uso, "output_tokens", "completion_tokens"),
            duracao_ms=int((time.monotonic() - inicio) * 1000), erro_classe=erro))

    def _fechar(self, contrato: type[M], provedor: Provedor, respostas: Mapping[str, Resposta],
                montar: Callable[[Mapping[str, Resposta]], Mapping[str, Any]]) -> Decisao[M]:
        confianca = min(r.confianca for r in respostas.values())
        limiar = self.limiares.get(contrato.__name__)
        if limiar is None:
            return Decisao(None, True, "sem_limiar_para_o_contrato", confianca, provedor.nome, respostas)
        if confianca < limiar:
            return Decisao(None, True, "confianca_abaixo_do_limiar", confianca, provedor.nome, respostas)
        dados = dict(montar(respostas))
        if "confianca" in contrato.model_fields:
            dados["confianca"] = confianca
        try:
            valor = contrato.model_validate(dados)
        except ValidationError:
            return Decisao(None, True, "contrato_recusou_a_resposta", confianca, provedor.nome, respostas)
        return Decisao(valor, False, "ok", confianca, provedor.nome, respostas)


ADAPTADORES: dict[str, type[ProvedorHTTP]] = {"typesafe": JevTypeSafe, "openrouter": JevOpenRouter}


def _adaptador(bloco: Mapping[str, Any]) -> ProvedorHTTP:
    classe = ADAPTADORES.get(bloco["adaptador"])
    if classe is None:
        raise KeyError(f"Jev sem adaptador: {bloco['adaptador']}")
    return classe(endpoint=bloco["endpoint"], modelo=bloco["modelo"], chave_env=bloco["chave_env"])


def decisor_padrao(registrar: Callable[[RegistroConsumo], None] | None = None) -> DecisorJev:
    """Decisor montado pelo bloco `decisao` de config/motores.json. O fallback entra só com `ativo: true`."""
    bloco = config()["decisao"]
    cadeia: list[Provedor] = [_adaptador(bloco["principal"])]
    fallback = bloco.get("fallback") or {}
    if fallback.get("ativo"):
        cadeia.append(_adaptador(fallback))
    return DecisorJev(cadeia, limiares=bloco["limiares"], registrar=registrar or gravar,
                      timeout_s=float(bloco["timeout_s"]), tentativas=int(bloco["tentativas"]))


def decide(contrato: type[M], estado: str, perguntas: Sequence[Pergunta],
           montar: Callable[[Mapping[str, Resposta]], Mapping[str, Any]], *, tipo_acao: str = "jev_decisao",
           workflow_id: str | None = None, activity: str | None = None) -> Decisao[M]:
    """Interface única do Jev (REGRAS §7). Usa o decisor da config; ver `DecisorJev.decidir`."""
    return decisor_padrao().decidir(contrato, estado, perguntas, montar, tipo_acao=tipo_acao,
                                    workflow_id=workflow_id, activity=activity)
