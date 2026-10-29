"""Banco de fichas, catálogo visual aberto (t150u, REGRAS §6): listar, buscar, registrar, anexar mídia, aprovar e descartar.

`banco-fichas/indice.json` (3.0.0) é a fonte para as máquinas; o `.md` de cada ficha é a leitura humana. A semente (t148u)
é do José; o agente acrescenta fichas novas para reaproveitar. Regras que este módulo faz cumprir:
- ficha nova nunca sobrescreve outra, nem repete o título de uma do mesmo tipo (reaproveitar vem antes de criar);
- ficha nova do agente nasce `aguardando_ok_jose` (usável desde já) ou `sugestao` (sem mídia); só o José aprova ou manda descartar;
- ficha `permanente` só muda por ordem do José (`por_jose=True`);
- imagem nova só entra no repositório até TAMANHO_MAX_IMAGEM; acima disso vai para o Drive (`imagem_drive_id`); vídeo é sempre do Drive.
Sem rede e sem LLM: gravar o arquivo no Drive é um passo à parte (integrations/drive.py)."""
from __future__ import annotations
import argparse, json, os, re, shutil, sys, unicodedata
from datetime import date
from pathlib import Path
from ..contratos.catalogo_visual import (EXT_IMAGEM, PASTA, PREFIXO, PROIBIDO_PADRAO, PROTAGONISTAS, SLUG, TAMANHO_MAX_IMAGEM,
                                         FichaCatalogo, VideoCatalogo)

RAIZ_PADRAO = Path(__file__).resolve().parents[3] / "banco-fichas"
VERSAO_INDICE = "3.0.0"
MARCA_MD = "<!-- gerado por pipeline/banco_fichas.py (t150u) -->"
_ORDEM_ESTADO = {"permanente": 0, "aguardando_ok_jose": 1, "sugestao": 2}
_MAGIA = {".png": (b"\x89PNG\r\n\x1a\n",), ".jpg": (b"\xff\xd8\xff",), ".jpeg": (b"\xff\xd8\xff",), ".webp": (b"RIFF",)}
_PARADAS = {"de", "do", "da", "dos", "das", "com", "para", "que", "uma", "um", "em", "no", "na", "nos", "nas", "os", "as", "ao", "por", "sem"}


def _raiz(raiz: Path | str | None = None) -> Path:
    return Path(raiz) if raiz else Path(os.environ.get("PQBR_BANCO_FICHAS") or RAIZ_PADRAO)


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def _json(dados: dict) -> str:
    texto = json.dumps(dados, ensure_ascii=False, indent=2)
    # retângulos de recorte [x0, y0, x1, y1] em uma linha só
    return re.sub(r"\[\s*([\d.eE+-]+),\s*([\d.eE+-]+),\s*([\d.eE+-]+),\s*([\d.eE+-]+)\s*\]", r"[\1, \2, \3, \4]", texto) + "\n"


def carregar(raiz: Path | str | None = None) -> dict:
    return json.loads((_raiz(raiz) / "indice.json").read_text(encoding="utf-8"))


def _gravar(dados: dict, raiz: Path | str | None = None) -> None:
    caminho = _raiz(raiz) / "indice.json"
    dados["atualizado"] = date.today().isoformat()
    tmp = caminho.with_suffix(".json.tmp")
    tmp.write_text(_json(dados), encoding="utf-8")
    os.replace(tmp, caminho)


def _dump(f: FichaCatalogo) -> dict:
    d = f.model_dump(mode="json", exclude_none=True, exclude={"versao"})
    if d.get("papel") == "item": d.pop("papel")
    return {k: v for k, v in d.items() if v not in ([], {}, "")}


def fichas(raiz: Path | str | None = None) -> list[FichaCatalogo]:
    return [FichaCatalogo.model_validate(d) for d in carregar(raiz).get("fichas", [])]


def listar(tipo: str | None = None, estado: str | None = None, raiz: Path | str | None = None) -> list[FichaCatalogo]:
    return [f for f in fichas(raiz) if (tipo is None or f.tipo == tipo) and (estado is None or f.estado == estado)]


def obter(id: str, raiz: Path | str | None = None) -> FichaCatalogo:
    for f in fichas(raiz):
        if f.id == id: return f
    raise KeyError(f"ficha inexistente: {id}")


def existe(id: str, raiz: Path | str | None = None) -> bool:
    return any(d.get("id") == id for d in carregar(raiz).get("fichas", []))


def protagonista(elenco: str, raiz: Path | str | None = None) -> FichaCatalogo:
    """Ficha do protagonista do episódio (`masculino` ou `feminino`); o índice manda, a constante é o padrão."""
    mapa = carregar(raiz).get("protagonistas") or PROTAGONISTAS
    return obter(mapa[elenco], raiz)


def _tokens(texto: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", _sem_acento(texto)) if len(t) >= 3 and t not in _PARADAS]


def buscar(consulta: str, tipo: str | None = None, limite: int = 8, raiz: Path | str | None = None) -> list[FichaCatalogo]:
    """Busca simples e determinística por palavra (id, título, tags, ação, acento e trava). Mais perto do tema primeiro; permanente antes."""
    palavras = _tokens(consulta)
    achados: list[tuple[int, FichaCatalogo]] = []
    for f in fichas(raiz):
        if tipo and f.tipo != tipo: continue
        campos = ((f.id.replace("-", " "), 3), (f.titulo, 3), (" ".join(f.tags), 3), (f.acao or "", 2), (f.acento or "", 2), (f.trava, 1))
        pontos = 0
        for texto, peso in campos:
            base = _sem_acento(texto)
            pontos += peso * sum(1 for p in palavras if p in base)
        if pontos: achados.append((pontos, f))
    achados.sort(key=lambda x: (-x[0], _ORDEM_ESTADO[x[1].estado], x[1].id))
    return [f for _, f in achados[:limite]]


def _checar_imagem(origem: Path) -> str:
    ext = origem.suffix.lower()
    if ext not in EXT_IMAGEM: raise ValueError(f"imagem: extensão {ext or '(nenhuma)'} fora de {EXT_IMAGEM}")
    if not origem.is_file(): raise FileNotFoundError(f"imagem não encontrada: {origem}")
    if origem.stat().st_size > TAMANHO_MAX_IMAGEM:
        raise ValueError(f"imagem com {origem.stat().st_size} bytes passa de {TAMANHO_MAX_IMAGEM}: envie ao Drive (integrations/drive.py) e passe imagem_drive_id")
    cab = origem.read_bytes()[:12]
    if not any(cab.startswith(m) for m in _MAGIA[ext]) or (ext == ".webp" and cab[8:12] != b"WEBP"):
        raise ValueError(f"imagem: o conteúdo não é {ext[1:]} de verdade")
    return ext


def _estado_frase(estado: str) -> str:
    return {"sugestao": "ideia sem mídia ainda; o agente pode produzir a imagem ou o vídeo da cena e anexar (`anexar_midia`)",
            "aguardando_ok_jose": "inserida pelo agente e já usável; o José aprova (`aprovar`) ou manda descartar",
            "permanente": "aprovada pelo José"}[estado]


def _origem_frase(f: FichaCatalogo) -> str:
    base = {"jose": "entregue ou selecionada pelo José", "mantenedor": "escrita pelo mantenedor", "agente": "inserida pelo agente"}[f.origem]
    return f"{base}; criada em {f.criado_em.isoformat()}" + (f" por {f.autor}" if f.autor else "")


_REUSO = {
    "personagem": "Anexe a imagem como `Elemento` no Flow e cite o id curto. Roupa, cor de acento e cabelo não mudam entre cenas. Sem nome falado nem escrito. Boca de reação, nunca de fala.",
    "ambiente": "Mesma luz e mesmos objetos-âncora entre cenas do mesmo lugar. Objeto que a cena usa de perto tem ficha em `objetos/`.",
    "objeto": "Mesma cor e mesma luz entre cenas; escala medida pelo stickman do elenco ao lado.",
    "figura": "Mesma forma e mesma cor entre cenas; escala medida pelo stickman do elenco ao lado.",
    "animal": "Mesma forma e mesma cor entre cenas; escala medida pelo stickman do elenco ao lado.",
    "situacao": "Descreve a pose ou o movimento; o personagem é escolhido do catálogo na hora, sem trocar roupa nem acento. Vídeo fica no Drive; aqui só a ficha. Boca de reação, nunca de fala.",
}


def renderizar_md(f: FichaCatalogo) -> str:
    linhas = [MARCA_MD, f"# {f.id} — {f.titulo}", "", f"Estado: `{f.estado}` — {_estado_frase(f.estado)}.", f"Origem: {_origem_frase(f)}.", ""]
    if f.aprovado_por: linhas += [f"Aprovada por {f.aprovado_por} em {f.aprovado_em.isoformat() if f.aprovado_em else '—'}.", ""]
    if f.imagem: linhas.append(f"- **Imagem:** `banco-fichas/{f.imagem}`" + (f" (recortes: {', '.join(sorted(f.recortes))})" if f.recortes else ""))
    if f.imagem_drive_id: linhas.append(f"- **Imagem no Drive:** `{f.imagem_drive_id}`")
    for v in f.videos: linhas.append(f"- **Vídeo (Drive):** `{v.drive_id}`, {v.duracao_s:g} s{', em loop' if v.loop else ''}" + (f" — {v.legenda}" if v.legenda else ""))
    if not (f.imagem or f.imagem_drive_id or f.videos): linhas.append("- **Mídia:** pendente.")
    if f.acao: linhas.append(f"- **Ação:** {f.acao}")
    if f.acento: linhas.append(f"- **Acento:** {f.acento}")
    if f.personagens: linhas.append("- **Personagens:** " + ", ".join(f"`{i}`" for i in f.personagens))
    if f.ambiente: linhas.append(f"- **Ambiente:** `{f.ambiente}`")
    if f.objetos: linhas.append("- **Objetos:** " + ", ".join(f"`{i}`" for i in f.objetos))
    if f.tags: linhas.append("- **Tags:** " + ", ".join(f.tags))
    extra = f"; {f.proibido.rstrip('.')}" if f.proibido else ""
    linhas += ["", "## Trava (frase-trava para o prompt e para o Agente do Flow)", "", f.trava, "",
               "## Como reaproveitar", "", _REUSO[f.tipo], "",
               "## Proibido", "", f"{PROIBIDO_PADRAO}{extra}.", ""]
    return "\n".join(linhas)


def caminho_md(f: FichaCatalogo, raiz: Path | str | None = None) -> Path:
    return _raiz(raiz) / PASTA[f.tipo] / f"{f.id}.md"


def caminho_imagem(f: FichaCatalogo, raiz: Path | str | None = None) -> Path | None:
    """Arquivo da imagem no repositório; None quando a ficha só tem imagem no Drive ou ainda não tem mídia."""
    return _raiz(raiz) / f.imagem if f.imagem else None


def _gerado(md: Path) -> bool:
    return md.is_file() and md.read_text(encoding="utf-8").startswith(MARCA_MD)


def _atualizar_md(antes: FichaCatalogo, depois: FichaCatalogo, raiz: Path | str | None, nota: str = "") -> None:
    """Ficha gerada é reescrita inteira; ficha escrita à mão só troca a linha `Estado:` e ganha a nota ao fim."""
    md = caminho_md(depois, raiz)
    if _gerado(md) or not md.is_file():
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(renderizar_md(depois), encoding="utf-8")
        return
    texto = md.read_text(encoding="utf-8")
    if antes.estado != depois.estado:
        texto = re.sub(r"(?m)^Estado: .*$", f"Estado: `{depois.estado}` — {_estado_frase(depois.estado)}.", texto, count=1)
    if nota: texto = texto.rstrip("\n") + f"\n\n- {nota}\n"
    md.write_text(texto, encoding="utf-8")


def registrar(*, tipo: str, slug: str, titulo: str, trava: str, acento: str | None = None, acao: str | None = None, tags: tuple[str, ...] | list[str] = (),
              proibido: str = "", personagens: list[str] | tuple[str, ...] = (), ambiente: str | None = None, objetos: list[str] | tuple[str, ...] = (),
              imagem_origem: Path | str | None = None, imagem_existente: str | None = None, imagem_drive_id: str | None = None,
              videos: list[dict] | tuple[dict, ...] = (), recortes: dict[str, list[float]] | None = None, elenco_num: int | None = None,
              folha_individual: bool | None = None, com_elenco: bool | None = None, papel: str = "item", origem: str = "agente",
              autor: str | None = None, por_jose: bool = False, raiz: Path | str | None = None) -> dict:
    """Insere uma ficha nova. Devolve {id, estado, arquivo, imagem, similares}. Nada é gravado se alguma regra falhar."""
    if tipo not in PREFIXO: raise ValueError(f"tipo inválido: {tipo}")
    if not (SLUG.match(slug) and 2 <= len(slug) <= 40): raise ValueError("slug: minúsculas, sem acento, com hífen, de 2 a 40 caracteres")
    if origem == "jose" and not por_jose: raise ValueError("origem `jose` só por ordem dele (por_jose=True)")
    if imagem_origem and imagem_existente: raise ValueError("passe imagem_origem (arquivo novo) ou imagem_existente (já no banco), não os dois")
    r = _raiz(raiz)
    dados = carregar(r)
    id_ = f"{PREFIXO[tipo]}-{slug}"
    if any(d.get("id") == id_ for d in dados.get("fichas", [])): raise ValueError(f"ficha já existe: {id_}; reaproveite ou escolha outro slug")
    norm = _sem_acento(titulo).strip()
    for d in dados.get("fichas", []):
        if d.get("tipo") == tipo and _sem_acento(d.get("titulo", "")).strip() == norm:
            raise ValueError(f"já existe {tipo} com o mesmo título: {d['id']}; reaproveite")
    similares = [f.id for f in buscar(f"{titulo} {' '.join(tags)}", tipo=tipo, limite=3, raiz=r)]
    ext, imagem = None, None
    if imagem_origem:
        origem_p = Path(imagem_origem)
        ext = _checar_imagem(origem_p)
        imagem = f"{PASTA[tipo]}/{id_}{ext}"
    elif imagem_existente:
        imagem = imagem_existente
        if not (r / imagem).is_file(): raise FileNotFoundError(f"imagem_existente não está no banco: {imagem}")
    tem_midia = bool(imagem or imagem_drive_id or videos)
    estado = "permanente" if (por_jose and origem == "jose") else ("aguardando_ok_jose" if tem_midia else "sugestao")
    corpo = dict(id=id_, tipo=tipo, papel=papel, titulo=titulo, trava=trava, proibido=proibido, estado=estado, origem=origem, criado_em=date.today(),
                 autor=autor, tags=list(tags), imagem=imagem, imagem_drive_id=imagem_drive_id, videos=[VideoCatalogo(**v) for v in videos],
                 recortes=dict(recortes or {}), personagens=list(personagens), ambiente=ambiente, objetos=list(objetos), acao=acao, acento=acento,
                 elenco_num=elenco_num, folha_individual=folha_individual, com_elenco=com_elenco)
    if estado == "permanente": corpo.update(aprovado_por="Jose", aprovado_em=date.today())
    ficha = FichaCatalogo.model_validate(corpo)
    for ref in [*ficha.personagens, *ficha.objetos, *([ficha.ambiente] if ficha.ambiente else [])]:
        if not any(d.get("id") == ref for d in dados.get("fichas", [])): raise ValueError(f"referência fora do catálogo: {ref}")
    criados: list[Path] = []
    try:
        if imagem_origem and ext:
            destino = r / imagem
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(origem_p, destino); criados.append(destino)
        md = caminho_md(ficha, r)
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(renderizar_md(ficha), encoding="utf-8"); criados.append(md)
        dados.setdefault("fichas", []).append(_dump(ficha))
        _gravar(dados, r)
    except Exception:
        for p in criados: p.unlink(missing_ok=True)
        raise
    return {"id": id_, "estado": estado, "arquivo": str(md.relative_to(r)), "imagem": imagem, "similares": similares}


def _atualizar(id: str, mudar, raiz: Path | str | None, nota: str = "") -> FichaCatalogo:
    r = _raiz(raiz)
    dados = carregar(r)
    for i, d in enumerate(dados.get("fichas", [])):
        if d.get("id") != id: continue
        antes = FichaCatalogo.model_validate(d)
        depois = FichaCatalogo.model_validate({**antes.model_dump(mode="json"), **mudar(antes)})
        dados["fichas"][i] = _dump(depois)
        _atualizar_md(antes, depois, r, nota)
        _gravar(dados, r)
        return depois
    raise KeyError(f"ficha inexistente: {id}")


def anexar_midia(id: str, *, imagem_origem: Path | str | None = None, imagem_drive_id: str | None = None, video: dict | None = None,
                 por_jose: bool = False, raiz: Path | str | None = None) -> FichaCatalogo:
    """Acrescenta imagem (arquivo novo ou Drive) e/ou um vídeo (Drive) a uma ficha. `sugestao` vira `aguardando_ok_jose`."""
    atual = obter(id, raiz)
    if atual.estado == "permanente" and not por_jose: raise ValueError("ficha permanente só muda por ordem do José (por_jose=True)")
    if (imagem_origem or imagem_drive_id) and (atual.imagem or atual.imagem_drive_id): raise ValueError("a ficha já tem imagem; registre outra ficha em vez de trocar")
    if not (imagem_origem or imagem_drive_id or video): raise ValueError("nada para anexar")
    r = _raiz(raiz)
    destino: Path | None = None
    imagem = atual.imagem
    if imagem_origem:
        ext = _checar_imagem(Path(imagem_origem))
        imagem = f"{PASTA[atual.tipo]}/{id}{ext}"
        destino = r / imagem
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(imagem_origem, destino)

    def mudar(f: FichaCatalogo) -> dict:
        m: dict = {}
        if imagem: m["imagem"] = imagem
        if imagem_drive_id: m["imagem_drive_id"] = imagem_drive_id
        if video: m["videos"] = [*(v.model_dump() for v in f.videos), VideoCatalogo(**video).model_dump()]
        if f.estado == "sugestao": m["estado"] = "aguardando_ok_jose"
        return m
    try:
        return _atualizar(id, mudar, r, nota=f"Mídia anexada em {date.today().isoformat()}.")
    except Exception:
        if destino: destino.unlink(missing_ok=True)
        raise


def adicionar_recorte(id: str, nome: str, retangulo: list[float] | tuple[float, ...], raiz: Path | str | None = None) -> FichaCatalogo:
    """Registra um recorte nomeado [x0, y0, x1, y1] (0 a 1) da imagem da ficha, por exemplo uma pose da folha. Só metadado: vale em qualquer estado."""
    return _atualizar(id, lambda f: {"recortes": {**f.recortes, nome: list(retangulo)}}, raiz)


def aprovar(id: str, por: str = "Jose", raiz: Path | str | None = None) -> FichaCatalogo:
    """O José aprova: `aguardando_ok_jose` vira `permanente`."""
    atual = obter(id, raiz)
    if atual.estado != "aguardando_ok_jose": raise ValueError(f"só ficha aguardando OK é aprovada (estado atual: {atual.estado})")
    return _atualizar(id, lambda f: {"estado": "permanente", "aprovado_por": por, "aprovado_em": date.today().isoformat()}, raiz)


def descartar(id: str, motivo: str, *, por: str = "agente", por_jose: bool = False, raiz: Path | str | None = None) -> dict:
    """Tira a ficha do diretório (o histórico fica no git). Permanente só por ordem do José. Imagem compartilhada com outra ficha não é apagada."""
    if len(motivo.strip()) < 5: raise ValueError("descartar exige motivo")
    r = _raiz(raiz)
    dados = carregar(r)
    alvo = obter(id, r)
    if alvo.estado == "permanente" and not por_jose: raise ValueError("ficha permanente só sai por ordem do José (por_jose=True)")
    outras = [FichaCatalogo.model_validate(d) for d in dados["fichas"] if d.get("id") != id]
    if any(id in (*o.personagens, *o.objetos, o.ambiente) for o in outras): raise ValueError(f"{id} é referenciada por outra ficha")
    apagados: list[str] = []
    md = caminho_md(alvo, r)
    if md.is_file(): md.unlink(); apagados.append(str(md.relative_to(r)))
    if alvo.imagem and not any(o.imagem == alvo.imagem for o in outras) and (r / alvo.imagem).is_file():
        (r / alvo.imagem).unlink(); apagados.append(alvo.imagem)
    dados["fichas"] = [d for d in dados["fichas"] if d.get("id") != id]
    dados.setdefault("descartadas", []).append({"id": id, "tipo": alvo.tipo, "titulo": alvo.titulo, "motivo": motivo.strip(), "data": date.today().isoformat(), "por": por})
    _gravar(dados, r)
    return {"id": id, "apagados": apagados}


def resumo_para_prompt(raiz: Path | str | None = None, limite: int = 4500) -> str:
    """Lista curta do catálogo para o prompt do storyboard: um item por linha, com o id que vai em `refs`."""
    fs = fichas(raiz)
    prot = {v: k for k, v in (carregar(raiz).get("protagonistas") or PROTAGONISTAS).items()}
    nomes = {"personagem": "Personagens", "ambiente": "Ambientes", "objeto": "Objetos", "animal": "Animais", "figura": "Figuras", "situacao": "Situações (pose ou movimento corriqueiro)"}
    saida: list[str] = ["Catálogo aberto: o id vai em `refs`. [sem mídia] = ideia sem imagem ainda (descreva a ação no prompt). O que a cena pedir e não estiver aqui, descreva no prompt."]
    for tipo in ("personagem", "ambiente", "objeto", "animal", "figura", "situacao"):
        itens = [f for f in fs if f.tipo == tipo and f.papel == "item"]
        if tipo == "personagem": itens.sort(key=lambda f: f.id not in prot)
        if not itens: continue
        saida.append(f"{nomes[tipo]}:")
        for f in itens:
            marca = f" [protagonista {prot[f.id]}]" if f.id in prot else ""
            sem = " [sem mídia]" if f.estado == "sugestao" else ""
            saida.append(f"- {f.id}{marca}: {f.titulo}{sem}")
    texto = "\n".join(saida)
    return texto if len(texto) <= limite else texto[:limite].rsplit("\n", 1)[0] + "\n- …"


def _cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m pqbr.pipeline.banco_fichas", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("listar"); s.add_argument("--tipo"); s.add_argument("--estado")
    s = sub.add_parser("obter"); s.add_argument("id")
    s = sub.add_parser("buscar"); s.add_argument("consulta"); s.add_argument("--tipo")
    s = sub.add_parser("registrar"); s.add_argument("arquivo_json", help="JSON com os argumentos de registrar()")
    s = sub.add_parser("aprovar"); s.add_argument("id"); s.add_argument("--por", default="Jose")
    s = sub.add_parser("descartar"); s.add_argument("id"); s.add_argument("--motivo", required=True); s.add_argument("--por-jose", action="store_true")
    sub.add_parser("resumo")
    a = p.parse_args(argv)
    try:
        if a.cmd == "listar": out = [{"id": f.id, "tipo": f.tipo, "estado": f.estado, "titulo": f.titulo} for f in listar(a.tipo, a.estado)]
        elif a.cmd == "obter": out = obter(a.id).model_dump(mode="json", exclude_none=True)
        elif a.cmd == "buscar": out = [{"id": f.id, "estado": f.estado, "titulo": f.titulo} for f in buscar(a.consulta, a.tipo)]
        elif a.cmd == "registrar": out = registrar(**json.loads(Path(a.arquivo_json).read_text(encoding="utf-8")))
        elif a.cmd == "aprovar": out = aprovar(a.id, a.por).model_dump(mode="json", exclude_none=True)
        elif a.cmd == "descartar": out = descartar(a.id, a.motivo, por="cli", por_jose=a.por_jose)
        else:
            print(resumo_para_prompt()); return 0
    except (ValueError, KeyError, FileNotFoundError) as e:
        print(f"erro: {e}", file=sys.stderr); return 1
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
