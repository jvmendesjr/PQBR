"""t467 (José 16:07): Auditor visual pelo Gemini Web no Camofox PQBR (conta já logada), humanizado.
Pranchas rotuladas (S01…, CAPA) → upload pelo menu "Enviar arquivos" → template VISUAL_2D colado → resposta
validada (RespostaAuditorGemini + auditor_visual.decidir). Erros não de segurança → pqbr.erros_aceitaveis.
Ações: só clique/tecla/upload humanos; leitura da resposta por evaluate SOMENTE leitura (innerText)."""
from __future__ import annotations
import json, re, subprocess, time, urllib.request
from collections import Counter
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from temporalio import activity

UPLOADS = Path("/home/pc/.pqbr/camofox/uploads")
FONTE = "DejaVu Sans:bold"
SN = Literal["sim", "nao", "na"]


class CenaAuditada(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(pattern=r"^(S[0-9]{2,}|CAPA)$")
    tem_personagem: SN; tem_texto_na_tela: SN; segue_estilo_declarado: SN; mesmo_personagem_do_bloco: SN
    imagem_corresponde_a_fala: SN; legivel_no_celular: SN; ambiente_brasileiro: SN; legenda_com_erro: SN
    parece_pessoa_real: SN; marca_real: SN; estereotipo_ofensivo: SN; texto_com_erro_de_sentido: SN
    foco_unico_zona_segura: SN; corresponde_ao_titulo: SN; legenda_cobre_foco: SN


class RespostaAuditorGemini(BaseModel):
    model_config = ConfigDict(extra="ignore")
    rodada: int = Field(ge=1, le=3)
    cenas: list[CenaAuditada] = Field(min_length=1, max_length=60)


class ResultadoAuditorGemini(BaseModel):
    veredito: Literal["aprova", "aprova_com_ressalva", "terceira_rodada", "reprova"]
    motivos: list[str] = Field(default_factory=list)
    rodadas: int
    erros_aceitaveis: int = 0
    persistido: bool = False
    texto_enviado: bool = False
    conversas: list[str] = Field(default_factory=list)
    bruto: dict = Field(default_factory=dict)


def _api(metodo: str, path: str, corpo: dict | None = None, t: int = 90) -> dict:
    from .camofox import BASE, _chave
    r = urllib.request.Request(BASE + path, data=json.dumps(corpo).encode() if corpo is not None else None, method=metodo,
                               headers={"Authorization": "Bearer " + _chave(), "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=t) as x:
        return json.load(x)


ESTAVEL_POLLS = 3        # ~24 s sem mudança e sem "Parar" → resposta terminada
PRAZO_UPLOAD_S = 90


class RespostaRecusada(RuntimeError):
    """Gemini respondeu, mas não com o JSON pedido (ex.: "Sou uma IA com base em texto…"). Falha fechada."""


def _anexos_prontos(tab: str, n: int) -> bool:
    s = _snap(tab)
    return s.count('img "attachment"') >= n   # t543: previews no composer


def _log(*a) -> None:
    import sys
    print(time.strftime("%H:%M:%S"), "[gemini]", *a, file=sys.stderr, flush=True)


def _snap(tab: str) -> str:
    return _api("GET", f"/tabs/{tab}/snapshot?userId=pqbr").get("snapshot", "")


def _ref(tab: str, rotulo: str, tentativas: int = 10) -> str:
    for _ in range(tentativas):
        m = re.search(rotulo + r'[^\n]*?\[(e\d+)\]', _snap(tab))
        if m: return m.group(1)
        time.sleep(1.5)
    raise RuntimeError(f"elemento não encontrado: {rotulo}")


def preparar_pranchas(quadros: list[str], capa: str | None, destino: Path) -> list[str]:
    """Rotula cada quadro com o id da cena embaixo (o template pede), no diretório de upload do Camofox."""
    destino.mkdir(parents=True, exist_ok=True); fonte = subprocess.run(["fc-match", "-f", "%{file}", FONTE], capture_output=True, text=True).stdout
    itens = [(f"S{i + 1:02d}", q) for i, q in enumerate(quadros)] + ([("CAPA", capa)] if capa else [])
    out = []
    for rid, q in itens:
        f = destino / f"{rid}.png"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", q, "-vf",
                        f"scale=540:-2,pad=iw:ih+90:0:0:white,drawtext=fontfile={fonte}:text={rid}:fontsize=60:fontcolor=black:x=(w-tw)/2:y=h-75",
                        str(f)], check=True)
        out.append(str(f))
    return out


def ler_texto_resposta(tab: str) -> str:
    js = ("(() => { const r = document.querySelectorAll('model-response, .model-response-text, message-content');"
          " return r.length ? r[r.length - 1].innerText : ''; })()")
    return str(_api("POST", f"/tabs/{tab}/evaluate", {"userId": "pqbr", "expression": js}).get("result") or "")


def perguntar_gemini(arquivos: list[str], prompt: str, espera_s: int = 420, marcador: str = '"cenas"') -> tuple[str, str]:
    """Nova conversa → anexa arquivos → cola prompt → envia → espera terminar. Devolve (texto, url da conversa)."""
    from .camofox_humano import clicar, escrever, pausa_humana
    tab = _api("POST", "/tabs", {"userId": "pqbr", "sessionKey": "gemini-auditor", "url": "https://gemini.google.com/app"})["tabId"]
    _log("aba aberta", tab)
    try:
        pausa_humana(2, 4)
        try: clicar(tab, ref=_ref(tab, r'button "Entendi"', 2))
        except RuntimeError: pass
        if arquivos:   # t540: LOOP textual vai sem anexos
            clicar(tab, ref=_ref(tab, r'button "Envio e ferramentas"'))
            pausa_humana(0.8, 1.8)
            _api("POST", f"/tabs/{tab}/upload", {"userId": "pqbr", "ref": _ref(tab, r'menuitem "Enviar arquivos'), "path": arquivos, "timeout": 20000}, t=120)
            pausa_humana(3, 6)   # previews das imagens
            t_up = time.time()
            while not _anexos_prontos(tab, len(arquivos)):   # t543: não envia sem os anexos (senão o Gemini recusa)
                if time.time() - t_up > PRAZO_UPLOAD_S:
                    _log("snapshot do campo:", "\n".join(l[:140] for l in _snap(tab).split("\n") if "Insira" in l or "img" in l or "image" in l.lower() or "arquivo" in l.lower())[:1500])
                    raise TimeoutError(f"anexos não apareceram em {PRAZO_UPLOAD_S}s")
                time.sleep(3)
            _log(f"{len(arquivos)} anexos prontos")
        clicar(tab, ref=_ref(tab, r'textbox "Insira um comando'))   # mouse humano no campo
        pausa_humana(0.6, 1.4)
        _api("POST", f"/tabs/{tab}/type", {"userId": "pqbr", "ref": _ref(tab, r'textbox "Insira um comando'), "text": prompt,
                                           "mode": "fill"})   # "colar" (texto longo); ref resolvido de novo após o upload
        pausa_humana(1.5, 3.5)
        for _ in range(20):   # o botão de enviar só habilita depois de terminar o upload
            m = re.search(r'button "Enviar mensagem"[^\n]*?\[(e\d+)\](?![^\n]*disabled)', _snap(tab))
            if m: break
            time.sleep(3)
        else: raise RuntimeError("botão Enviar mensagem não habilitou")
        clicar(tab, ref=m.group(1)); _log("enviado; esperando resposta")
        t0, txt, ant, estavel = time.time(), "", None, 0
        while True:
            if time.time() - t0 > espera_s:
                raise TimeoutError(f"Gemini sem resposta completa em {espera_s}s (len={len(txt)})")   # falha fechada
            time.sleep(8)
            s = _snap(tab)
            gerando = "Parar resposta" in s or 'button "Parar' in s
            txt = ler_texto_resposta(tab)
            _log(f"t={time.time()-t0:.0f}s gerando={gerando} len={len(txt)} fim={txt.rstrip()[-60:]!r}")
            if gerando: estavel = 0; ant = txt; continue
            if marcador in txt and txt.rstrip().endswith(("}", "```")): break
            estavel = estavel + 1 if (txt and txt == ant) else 0; ant = txt
            if estavel >= ESTAVEL_POLLS:   # terminou sem o JSON esperado: recusa/erro → não espera o prazo todo
                raise RespostaRecusada(f"Gemini terminou sem o JSON esperado: {txt.strip()[:160]!r}")
        url = _api("GET", f"/tabs?userId=pqbr")
        url = next((x["url"] for x in url.get("tabs", []) if x["tabId"] == tab), "")
        return txt, url
    finally:
        try: _api("DELETE", f"/tabs/{tab}?userId=pqbr")
        except Exception: pass


def validar(texto: str, ids: list[str]) -> str:
    t = re.sub(r"```(?:json)?", "", texto); i, j = t.find("{"), t.rfind("}")
    r = RespostaAuditorGemini.model_validate_json(t[i:j + 1])
    if len(ids) != len(set(ids)):
        raise ValueError("ids esperados duplicados")
    recebidos = [c.id for c in r.cenas]
    duplicados = sorted(k for k, n in Counter(recebidos).items() if n > 1)
    if duplicados:
        raise ValueError(f"cenas duplicadas: {duplicados}")
    inesperados = sorted(set(recebidos) - set(ids))
    if inesperados:
        raise ValueError(f"cenas inesperadas: {inesperados}")
    falt = sorted(set(ids) - set(recebidos))
    if falt:
        raise ValueError(f"cenas ausentes: {falt}")
    return json.dumps(r.model_dump(), ensure_ascii=False)


def _persistir_erros_aceitaveis(linhas: list[dict], sql: str) -> None:
    from .pacote import _banco
    with _banco() as c:
        for linha in linhas:
            c.execute(sql, linha)
        c.commit()


def auditar(codigo: str, slug: str, quadros: list[str], falas: list[str], bloco_visual: str, capa: str | None = None,
            rodadas: int = 2, persistir: bool = True, transmitir_texto: bool = False,
            titulo: str | None = None) -> ResultadoAuditorGemini:
    from ..pipeline.auditor_visual import montar_prompt, decidir, linhas_erros_aceitaveis, SQL_ERROS
    arqs = preparar_pranchas(quadros, capa, UPLOADS / f"auditor-{codigo}")
    ids = [Path(a).stem for a in arqs]
    cenas = [(f"S{i + 1:02d}", falas[i] if i < len(falas) else "") for i in range(len(quadros))] + ([("CAPA", "capa do vídeo (sem fala)")] if capa else [])
    brutos, urls = [], []
    for n in range(1, rodadas + 1):
        ok = None
        for _ in range(2):
            prompt = montar_prompt(bloco_visual if transmitir_texto else "",
                                   cenas if transmitir_texto else [], n,
                                   titulo=titulo if transmitir_texto else None,
                                   transmitir_texto=transmitir_texto)
            txt, url = perguntar_gemini(arqs, prompt); urls.append(url)
            try:
                ok = validar(txt, ids)
                # Nunca aceite avaliação de imagem×fala/título quando esses dados não foram enviados.
                if not transmitir_texto or not titulo or not bloco_visual.strip():
                    dados = json.loads(ok)
                    for item in dados["cenas"]:
                        if not transmitir_texto:
                            item["imagem_corresponde_a_fala"] = "na"
                        if item["id"] == "CAPA" and (not transmitir_texto or not titulo):
                            item["corresponde_ao_titulo"] = "na"
                        if not transmitir_texto or not bloco_visual.strip():
                            item["segue_estilo_declarado"] = "na"
                            item["mesmo_personagem_do_bloco"] = "na"
                    ok = json.dumps(dados, ensure_ascii=False)
                break
            except Exception as e: txt = ""; err = str(e)[:200]  # noqa: BLE001
        brutos.append(ok or "{}")
    res = decidir(brutos, ids)
    linhas = linhas_erros_aceitaveis(res, episodio_codigo=codigo)
    if persistir and linhas:
        _persistir_erros_aceitaveis(linhas, SQL_ERROS)
    mot = [f"{i}:{k}" for i, k in res["falhas"] + res["divergencias"] + res["ressalvas"]][:20] + res["problemas"][:5]
    veredito = res["veredito"]
    if not transmitir_texto:
        mot.append("texto não enviado; imagem×fala/loop não avaliados")
        if veredito == "aprova":
            veredito = "aprova_com_ressalva"
    if capa and not titulo:
        mot.append("título não enviado; correspondência da capa não avaliada")
        if veredito == "aprova":
            veredito = "aprova_com_ressalva"
    return ResultadoAuditorGemini(veredito=veredito, motivos=mot or ["sem ressalvas"], rodadas=rodadas,
                                  erros_aceitaveis=len(linhas), persistido=bool(persistir and linhas),
                                  texto_enviado=bool(transmitir_texto and (falas or bloco_visual or titulo)),
                                  conversas=urls, bruto={k: res[k] for k in ("metricas", "rodada_unica")})


@activity.defn
async def auditor_gemini(codigo: str, slug: str, quadros: list[str], falas: list[str], bloco_visual: str,
                         capa: str | None = None, persistir: bool = True, transmitir_texto: bool = False,
                         titulo: str | None = None) -> dict:
    import asyncio
    return (await asyncio.to_thread(auditar, codigo, slug, quadros, falas, bloco_visual, capa,
                                    persistir=persistir, transmitir_texto=transmitir_texto,
                                    titulo=titulo)).model_dump()
