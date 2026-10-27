"""Plano e ensaio do fallback pelo Studio (t124u, t125u).

A API segue sendo o caminho. Quando o refresh volta invalid_grant, a publicação inteira
daquele envio fica para o Camofox. O ensaio percorre, em memória, as mesmas funções da API
(subida privada, agenda, privacidade) sobre o corpo que a API usaria. A base pode estar
desatualizada. Não abre o navegador e não envia.
"""
from __future__ import annotations
import json
from ..contratos.studio_fallback import BASE_PASSOS, AVISO, EnsaioCliques, PassoEnsaio


def _dir():
    from . import youtube as yt
    return yt.SIM_DIR


def _ler(dados: dict, caminho: str):
    if caminho == "_arquivo":
        return dados.get("_arquivo"), "_arquivo" in dados
    cur = dados
    for p in caminho.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return None, False
        cur = cur[p]
    return cur, True


def _texto(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    return "" if v is None else str(v)


def _confere(funcao: str, campo: str, valor, presente: bool) -> tuple[bool, str]:
    if not presente:
        return False, "campo ausente na base da API"
    if funcao == "subir_privado" and campo == "status.privacyStatus" and valor != "private":
        return False, "subida tem de ser privada"
    if campo == "status.containsSyntheticMedia" and valor is not True:
        return False, "mídia sintética tem de estar marcada"
    if campo == "status.selfDeclaredMadeForKids" and valor is not False:
        return False, "marcado como feito para crianças"
    if funcao == "agendar" and not valor:
        return False, "agenda sem publishAt"
    if funcao == "tornar_publico" and valor != "public":
        return False, "visibilidade diferente de pública"
    if funcao == "tornar_privado" and valor != "private":
        return False, "visibilidade diferente de privada"
    if campo == "snippet.description" and "PQBR-EP" not in str(valor):
        return False, "descrição sem o código"
    if campo == "snippet.tags" and not any(str(t).startswith("PQBR-EP") for t in (valor or [])):
        return False, "etiqueta sem o código"
    if campo in ("snippet.title", "_arquivo") and not valor:
        return False, "valor vazio"
    return True, "valor copiado da API"


def ensaiar(corpo: dict, funcoes: tuple[str, ...], arquivo: str | None = None) -> EnsaioCliques:
    """Simula os cliques das funções pedidas. Lê a base da API. Não fala com o navegador."""
    dados = {**corpo, **({"_arquivo": arquivo} if arquivo else {})}
    passos = []
    for p in BASE_PASSOS:
        if p.funcao not in funcoes:
            continue
        valor, presente = _ler(dados, p.campo_api)
        ok, motivo = _confere(p.funcao, p.campo_api, valor, presente)
        clicavel = p.seletor is not None and p.observado_em is not None
        if clicavel:
            motivo = f"{motivo}; seletor observado em {p.observado_em}"
        passos.append(PassoEnsaio(funcao=p.funcao, ordem=p.ordem, acao=p.acao, alvo=p.alvo,
                                  campo_api=p.campo_api, valor=_texto(valor)[:5000], clicavel=clicavel,
                                  base_ok=ok, motivo=motivo))
    if not passos:
        raise ValueError("ensaio sem passos")
    return EnsaioCliques(funcoes=funcoes, ok=all(s.base_ok for s in passos),
                         clicavel=all(s.clicavel for s in passos), passos=tuple(passos), aviso=AVISO)


def ensaiar_envio(corpo: dict, arquivo: str) -> EnsaioCliques:
    return ensaiar(corpo, ("subir_privado", "agendar"), arquivo)


def ensaiar_privacidade(privacidade: str) -> EnsaioCliques:
    if privacidade not in ("public", "private"):
        raise ValueError("privacidade inválida")
    funcao = "tornar_publico" if privacidade == "public" else "tornar_privado"
    corpo = {"status": {"privacyStatus": privacidade, "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}}
    return ensaiar(corpo, (funcao,))


def planejar(arquivo: str, corpo: dict, codigo: str, motivo: str = "renovacao_oauth") -> dict:
    if corpo["status"]["privacyStatus"] != "private" or corpo["status"]["containsSyntheticMedia"] is not True:
        raise ValueError("plano do Studio fora da regra (privado + mídia sintética)")
    ensaio = ensaiar_envio(corpo, arquivo)
    d = _dir(); d.mkdir(parents=True, exist_ok=True)
    plano = {**corpo, "_arquivo": arquivo, "_caminho": "camofox", "_motivo": motivo, "_executado": False,
             "_ensaio": ensaio.model_dump(mode="json")}
    f = d / f"{codigo}-camofox.json"
    f.write_text(json.dumps(plano, ensure_ascii=False, indent=1))
    return {"caminho": "camofox", "simulado": True, "executado": False, "video_id": None,
            "payload": str(f), "motivo": motivo, "privacidade": "private", "ensaio_ok": ensaio.ok,
            "clicavel": ensaio.clicavel}


def planejar_privacidade(codigo: str, video_id: str | None, privacidade: str, motivo: str = "renovacao_oauth") -> dict:
    ensaio = ensaiar_privacidade(privacidade)
    d = _dir(); d.mkdir(parents=True, exist_ok=True)
    plano = {"codigo": codigo, "video_id": video_id, "privacidade": privacidade,
             "_caminho": "camofox", "_motivo": motivo, "_executado": False,
             "_ensaio": ensaio.model_dump(mode="json")}
    f = d / f"{codigo}-camofox-privacidade.json"
    f.write_text(json.dumps(plano, ensure_ascii=False, indent=1))
    return {"caminho": "camofox", "executado": False, "payload": str(f), "ensaio_ok": ensaio.ok,
            "clicavel": ensaio.clicavel, **{k: plano[k] for k in ("codigo", "video_id", "privacidade")}}
