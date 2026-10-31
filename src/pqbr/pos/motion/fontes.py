"""Banco de fontes do motion graphics: leitor sfnt em Python puro, validação e índice.

Só fonte com licença livre, arquivo local TTF/OTF, cobertura completa do pt-BR.
Nasce `aguardando_ok_jose`; só o José aprova. Nunca carrega de CDN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

RAIZ_FONTES = Path(
    os.environ.get("PQBR_FONTES_DIR", Path(__file__).resolve().parents[4] / "banco-fichas" / "referencias-motion" / "fontes")
)

LICENCAS_LIVRES = frozenset({"OFL-1.1", "Apache-2.0", "UFL-1.0"})
TAMANHO_MAXIMO = 3 * 1024 * 1024
ESTADOS = ("aguardando_ok_jose", "aprovada")
VERSAO_INDICE = "1.0.0"
REGRA_INDICE = (
    "Só fonte com licença livre (OFL-1.1, Apache-2.0, UFL-1.0), arquivo local TTF/OTF, nunca CDN; cobertura completa do pt-BR; "
    "nasce aguardando_ok_jose e só o José aprova; a fonte do padrão do canal é decisão dele (MG-03)."
)

_ACENTOS = "áàâãäéèêëíìîïóòôõöúùûüçñ"
PTBR_CARACTERES: frozenset[str] = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    + _ACENTOS
    + _ACENTOS.upper()
    + "0123456789"
    + ".,;:!?-–—…()[]{}\"'“”‘’«»/\\%&@#$+=*°ºª€· "
)


@dataclass(frozen=True)
class InfoFonte:
    familia: str
    subfamilia: str
    nome_completo: str
    versao: str
    copyright: str
    licenca_texto: str
    licenca_url: str
    cmap: frozenset[int]
    formato: str
    variavel: bool
    eixos: dict[str, tuple[float, float, float]] = field(default_factory=dict)
    peso_classe: int = 400


def _u(fmt: str, dados: bytes, pos: int) -> tuple[Any, ...]:
    return struct.unpack_from(fmt, dados, pos)


def _tabelas(dados: bytes) -> tuple[str, dict[str, tuple[int, int]]]:
    if len(dados) < 12:
        raise ValueError("arquivo truncado: menor que o cabeçalho sfnt")
    tag = dados[:4]
    if tag == b"ttcf":
        raise ValueError("coleção de fontes (ttcf) não é aceita; extraia uma fonte TTF/OTF")
    if tag in (b"wOFF", b"wOF2"):
        raise ValueError("fonte WOFF/WOFF2 não é aceita: converta para TTF/OTF")
    if tag in (b"\x00\x01\x00\x00", b"true"):
        formato = "ttf"
    elif tag == b"OTTO":
        formato = "otf"
    else:
        raise ValueError("o arquivo não é uma fonte sfnt (TTF/OTF)")
    n = _u(">H", dados, 4)[0]
    tabelas: dict[str, tuple[int, int]] = {}
    for i in range(n):
        base = 12 + 16 * i
        if base + 16 > len(dados):
            raise ValueError("arquivo truncado: diretório de tabelas incompleto")
        t, _cs, off, ln = _u(">4sIII", dados, base)
        if off + ln > len(dados):
            raise ValueError(f"arquivo truncado: tabela {t.decode('latin-1')} passa do fim")
        tabelas[t.decode("latin-1")] = (off, ln)
    for obrigatoria in ("cmap", "name", "head"):
        if obrigatoria not in tabelas:
            raise ValueError(f"tabela obrigatória ausente: {obrigatoria}")
    return formato, tabelas


def _decodificar(plataforma: int, bruto: bytes) -> str:
    if plataforma in (0, 3):
        return bruto.decode("utf-16-be", errors="replace")
    if plataforma == 1:
        return bruto.decode("mac_roman", errors="replace")
    return bruto.decode("latin-1", errors="replace")


def _nomes(dados: bytes, off: int, ln: int) -> dict[int, str]:
    fim = off + ln
    _fmt, n, so = _u(">HHH", dados, off)
    escolhidos: dict[int, tuple[int, str]] = {}
    for i in range(n):
        plat, enc, lang, nid, tam, o = _u(">HHHHHH", dados, off + 6 + 12 * i)
        ini = off + so + o
        if ini + tam > fim:
            continue
        texto = _decodificar(plat, dados[ini : ini + tam]).strip("\x00")
        if not texto:
            continue
        # preferir Windows inglês (3/0x409), depois Unicode, depois Mac
        prio = 0 if (plat == 3 and lang == 0x409) else 1 if plat in (0, 3) else 2
        if nid not in escolhidos or prio < escolhidos[nid][0]:
            escolhidos[nid] = (prio, texto)
    return {k: v[1] for k, v in escolhidos.items()}


def _cmap(dados: bytes, off: int, ln: int) -> frozenset[int]:
    n = _u(">HH", dados, off)[1]
    candidatas: list[tuple[int, int]] = []
    for i in range(n):
        plat, enc, o = _u(">HHI", dados, off + 4 + 8 * i)
        if plat == 0 or (plat == 3 and enc in (1, 10)):
            prio = 0 if (plat == 3 and enc == 10) else 1
            candidatas.append((prio, off + o))
    if not candidatas:
        raise ValueError("a fonte não tem subtabela cmap Unicode")
    cps: set[int] = set()
    for _prio, ini in sorted(candidatas):
        cps |= _subtabela_cmap(dados, ini)
    return frozenset(cps)


def _subtabela_cmap(dados: bytes, ini: int) -> set[int]:
    formato = _u(">H", dados, ini)[0]
    cps: set[int] = set()
    if formato == 4:
        segx2 = _u(">H", dados, ini + 6)[0]
        seg = segx2 // 2
        fins = ini + 14
        inis = fins + segx2 + 2
        deltas = inis + segx2
        rangos = deltas + segx2
        for s in range(seg):
            fim = _u(">H", dados, fins + 2 * s)[0]
            comeco = _u(">H", dados, inis + 2 * s)[0]
            delta = _u(">h", dados, deltas + 2 * s)[0]
            ro = _u(">H", dados, rangos + 2 * s)[0]
            if comeco > fim or comeco == 0xFFFF:
                continue
            for c in range(comeco, fim + 1):
                if c == 0xFFFF:
                    continue
                if ro == 0:
                    gid = (c + delta) & 0xFFFF
                else:
                    pos = rangos + 2 * s + ro + 2 * (c - comeco)
                    gid = _u(">H", dados, pos)[0]
                    if gid:
                        gid = (gid + delta) & 0xFFFF
                if gid:
                    cps.add(c)
    elif formato == 12:
        ng = _u(">I", dados, ini + 12)[0]
        for g in range(ng):
            a, b, gid = _u(">III", dados, ini + 16 + 12 * g)
            if b - a > 0x110000:
                raise ValueError("cmap formato 12 inválido")
            cps.update(range(a, b + 1)) if gid else None
    elif formato == 0:
        for c in range(256):
            if dados[ini + 6 + c]:
                cps.add(c)
    elif formato == 6:
        primeiro, cont = _u(">HH", dados, ini + 6)
        for k in range(cont):
            if _u(">H", dados, ini + 10 + 2 * k)[0]:
                cps.add(primeiro + k)
    return cps


def _eixos(dados: bytes, off: int) -> dict[str, tuple[float, float, float]]:
    off_eixos, _res, n, tam = _u(">HHHH", dados, off + 4)
    eixos: dict[str, tuple[float, float, float]] = {}
    for i in range(n):
        base = off + off_eixos + tam * i
        tag = dados[base : base + 4].decode("latin-1")
        mn, pad, mx = (v / 65536 for v in _u(">iii", dados, base + 4))
        eixos[tag] = (mn, pad, mx)
    return eixos


def ler_fonte(caminho: str | Path) -> InfoFonte:
    """Lê os metadados e a cobertura de um TTF/OTF; erros viram ValueError."""
    dados = Path(caminho).read_bytes()
    try:
        formato, tab = _tabelas(dados)
        nomes = _nomes(dados, *tab["name"])
        cmap = _cmap(dados, *tab["cmap"])
        variavel = "fvar" in tab
        eixos = _eixos(dados, tab["fvar"][0]) if variavel else {}
        peso = 400
        if "OS/2" in tab and tab["OS/2"][1] >= 6:
            peso = _u(">H", dados, tab["OS/2"][0] + 4)[0]
    except (struct.error, IndexError) as e:
        raise ValueError(f"arquivo de fonte truncado ou corrompido: {e}") from e
    return InfoFonte(
        familia=nomes.get(16) or nomes.get(1, ""),
        subfamilia=nomes.get(17) or nomes.get(2, ""),
        nome_completo=nomes.get(4, ""),
        versao=nomes.get(5, ""),
        copyright=nomes.get(0, ""),
        licenca_texto=nomes.get(13, ""),
        licenca_url=nomes.get(14, ""),
        cmap=cmap,
        formato=formato,
        variavel=variavel,
        eixos=eixos,
        peso_classe=peso,
    )


def faltantes_ptbr(info: InfoFonte) -> list[str]:
    """Caracteres do pt-BR que a fonte não cobre, em ordem."""
    return sorted(c for c in PTBR_CARACTERES if ord(c) not in info.cmap)


def _pesos(info: InfoFonte) -> list[int]:
    if info.variavel and "wght" in info.eixos:
        mn, _p, mx = info.eixos["wght"]
        return [int(round(mn)), int(round(mx))]
    return [info.peso_classe, info.peso_classe]


def _raiz(raiz: Path | None) -> Path:
    return Path(raiz) if raiz is not None else Path(os.environ.get("PQBR_FONTES_DIR", RAIZ_FONTES))


def _ler_indice(raiz: Path) -> dict[str, Any]:
    p = raiz / "indice.json"
    if not p.exists():
        return {"versao": VERSAO_INDICE, "decisao": "t149u", "atualizado": date.today().isoformat(), "regra": REGRA_INDICE, "fontes": []}
    return json.loads(p.read_text(encoding="utf-8"))


def _gravar_indice(raiz: Path, indice: dict[str, Any]) -> None:
    indice["atualizado"] = date.today().isoformat()
    raiz.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=raiz, prefix=".indice-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(indice, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, raiz / "indice.json")
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def listar(estado: str | None = None, raiz: Path | None = None) -> list[dict[str, Any]]:
    fontes = _ler_indice(_raiz(raiz))["fontes"]
    return [f for f in fontes if estado is None or f["estado"] == estado]


def obter(id: str, raiz: Path | None = None) -> dict[str, Any]:  # noqa: A002
    for f in listar(raiz=raiz):
        if f["id"] == id:
            return f
    raise KeyError(id)


def verificar(arquivo: str | Path) -> dict[str, Any]:
    """Relatório de uma fonte sem gravar nada."""
    info = ler_fonte(arquivo)
    faltantes = faltantes_ptbr(info)
    return {
        "arquivo": str(arquivo),
        "familia": info.familia,
        "subfamilia": info.subfamilia,
        "versao": info.versao,
        "formato": info.formato,
        "variavel": info.variavel,
        "eixos": {k: [v[0], v[2]] for k, v in info.eixos.items()},
        "pesos": _pesos(info),
        "licenca_declarada": info.licenca_texto,
        "licenca_url_declarada": info.licenca_url,
        "copyright": info.copyright,
        "tamanho": Path(arquivo).stat().st_size,
        "cobertura_ptbr": not faltantes,
        "faltantes_ptbr": faltantes,
    }


_RE_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def registrar(
    arquivo: str | Path,
    *,
    id: str,  # noqa: A002
    origem_url: str,
    licenca: str,
    arquivo_licenca: str | Path,
    uso: str = "",
    notas: str = "",
    consulta: str | None = None,
    raiz: Path | None = None,
) -> dict[str, Any]:
    """Valida tudo antes de gravar; copia fonte e licença e entra como aguardando_ok_jose."""
    raiz_p = _raiz(raiz)
    arquivo = Path(arquivo)
    arquivo_licenca = Path(arquivo_licenca)
    if not (3 <= len(id) <= 40 and _RE_ID.match(id)):
        raise ValueError(f"id inválido {id!r}: use minúsculas, dígitos e hífens, de 3 a 40 caracteres")
    indice = _ler_indice(raiz_p)
    if any(f["id"] == id for f in indice["fontes"]) or (raiz_p / id).exists():
        raise ValueError(f"id já existe: {id}; fonte existente nunca é sobrescrita")
    if arquivo.suffix.lower() not in (".ttf", ".otf"):
        raise ValueError("só arquivo .ttf ou .otf; converta WOFF/WOFF2 antes")
    if not arquivo.is_file():
        raise ValueError(f"arquivo de fonte não encontrado: {arquivo}")
    tamanho = arquivo.stat().st_size
    if tamanho > TAMANHO_MAXIMO:
        raise ValueError(f"fonte com {tamanho} bytes passa do limite de {TAMANHO_MAXIMO} (3 MB)")
    if licenca not in LICENCAS_LIVRES:
        raise ValueError(f"licença {licenca!r} fora da lista livre: {sorted(LICENCAS_LIVRES)}")
    if not arquivo_licenca.is_file() or arquivo_licenca.stat().st_size == 0:
        raise ValueError(f"arquivo de licença ausente ou vazio: {arquivo_licenca}")
    if licenca == "OFL-1.1" and "SIL OPEN FONT LICENSE" not in arquivo_licenca.read_text(encoding="utf-8", errors="replace").upper():
        raise ValueError("o arquivo de licença não contém o texto da SIL Open Font License")
    if not origem_url.startswith("https://"):
        raise ValueError("origem_url precisa começar com https://")
    info = ler_fonte(arquivo)
    faltantes = faltantes_ptbr(info)
    if faltantes:
        raise ValueError(f"cobertura do pt-BR incompleta; faltam: {' '.join(faltantes)}")

    destino = raiz_p / id
    destino.mkdir(parents=True)
    try:
        # Nome canônico ASCII: o original do Google Fonts tem colchetes e vírgulas, que viram %5B/%2C na URL do CSS.
        nome_fonte = f"{id}{arquivo.suffix.lower()}"
        nome_licenca = "LICENSE.txt"
        shutil.copyfile(arquivo, destino / nome_fonte)
        shutil.copyfile(arquivo_licenca, destino / nome_licenca)
        sha = hashlib.sha256((destino / nome_fonte).read_bytes()).hexdigest()
        entrada: dict[str, Any] = {
            "id": id,
            "familia": info.familia,
            "arquivo": f"{id}/{nome_fonte}",
            "arquivo_original": arquivo.name,
            "arquivo_licenca": f"{id}/{nome_licenca}",
            "licenca": licenca,
            "origem_url": origem_url,
            "consulta": consulta or date.today().isoformat(),
            "variavel": info.variavel,
            "pesos": _pesos(info),
        }
        if info.variavel:
            entrada["eixos"] = {k: [v[0], v[2]] for k, v in info.eixos.items()}
        entrada.update(
            {
                "cobertura_ptbr": True,
                "sha256": sha,
                "tamanho": tamanho,
                "uso": uso,
                "notas": notas,
                "estado": "aguardando_ok_jose",
                "aprovada_por": None,
                "aprovada_em": None,
            }
        )
        indice["fontes"].append(entrada)
        _gravar_indice(raiz_p, indice)
    except BaseException:
        shutil.rmtree(destino, ignore_errors=True)
        raise
    return entrada


def aprovar(id: str, por: str = "Jose", raiz: Path | None = None) -> dict[str, Any]:  # noqa: A002
    raiz_p = _raiz(raiz)
    indice = _ler_indice(raiz_p)
    for f in indice["fontes"]:
        if f["id"] == id:
            if f["estado"] != "aguardando_ok_jose":
                raise ValueError(f"fonte {id} já está {f['estado']}")
            f["estado"] = "aprovada"
            f["aprovada_por"] = por
            f["aprovada_em"] = date.today().isoformat()
            _gravar_indice(raiz_p, indice)
            return f
    raise KeyError(id)


def remover(id: str, por_jose: bool = False, raiz: Path | None = None) -> dict[str, Any]:  # noqa: A002
    """Tira a fonte do banco (pasta e linha do índice; o histórico fica no git). Fonte aprovada só sai por ordem do José."""
    raiz_p = _raiz(raiz)
    indice = _ler_indice(raiz_p)
    for i, f in enumerate(indice["fontes"]):
        if f["id"] != id:
            continue
        if f["estado"] == "aprovada" and not por_jose:
            raise ValueError(f"fonte aprovada {id} só sai por ordem do José (por_jose=True)")
        del indice["fontes"][i]
        _gravar_indice(raiz_p, indice)
        shutil.rmtree(raiz_p / id, ignore_errors=True)
        return f
    raise KeyError(id)


def familia_css(id: str) -> str:  # noqa: A002
    return f"PQBR-{id}"


def fonte_css(id: str, raiz: Path | None = None) -> str:  # noqa: A002
    """Regra @font-face de uma linha apontando para o arquivo local (file://)."""
    raiz_p = _raiz(raiz)
    f = obter(id, raiz_p)
    caminho = (raiz_p / f["arquivo"]).resolve()
    formato = "opentype" if caminho.suffix.lower() == ".otf" else "truetype"
    mn, mx = f["pesos"]
    largura = f.get("eixos", {}).get("wdth")
    stretch = f"font-stretch:{largura[0]:g}% {largura[1]:g}%;" if largura else ""
    return (
        f'@font-face{{font-family:"{familia_css(id)}";src:url("{caminho.as_uri()}") format("{formato}");'
        f"font-weight:{mn} {mx};{stretch}font-style:normal;font-display:block;}}"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m pqbr.pos.motion.fontes", description="Banco de fontes do motion")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar")
    v = sub.add_parser("verificar")
    v.add_argument("arquivo")
    r = sub.add_parser("registrar")
    r.add_argument("arquivo")
    r.add_argument("--id", required=True)
    r.add_argument("--origem-url", required=True)
    r.add_argument("--licenca", required=True)
    r.add_argument("--arquivo-licenca", required=True)
    r.add_argument("--uso", default="")
    r.add_argument("--notas", default="")
    r.add_argument("--consulta", default=None, help="AAAA-MM-DD; padrão: hoje")
    a = sub.add_parser("aprovar")
    a.add_argument("id")
    a.add_argument("--por", default="Jose")
    d = sub.add_parser("remover")
    d.add_argument("id")
    d.add_argument("--por-jose", action="store_true")
    args = p.parse_args(argv)
    try:
        if args.cmd == "listar":
            saida: Any = listar()
        elif args.cmd == "verificar":
            saida = verificar(args.arquivo)
        elif args.cmd == "registrar":
            saida = registrar(
                args.arquivo,
                id=args.id,
                origem_url=args.origem_url,
                licenca=args.licenca,
                arquivo_licenca=args.arquivo_licenca,
                uso=args.uso,
                notas=args.notas,
                consulta=args.consulta,
            )
        elif args.cmd == "remover":
            saida = remover(args.id, args.por_jose)
        else:
            saida = aprovar(args.id, args.por)
    except (ValueError, KeyError) as e:
        print(str(e), file=sys.stderr)
        return 1
    print(json.dumps(saida, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
