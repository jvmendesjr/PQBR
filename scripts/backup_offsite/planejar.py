#!/usr/bin/env python3
"""F3-04: inventário offline; não instala, copia, envia ou remove arquivos."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat

ORIGENS = {"pqbr-db": "pqbr", "hindsight": "hindsight"}
DESTINO = "PQBR/backups-db"


def privado(st, diretorio=False):
    tipo = stat.S_ISDIR if diretorio else stat.S_ISREG
    if not tipo(st.st_mode) or st.st_uid != os.getuid() or st.st_mode & 0o077:
        raise ValueError("Origem deve ser própria, privada e do tipo esperado")


def pasta_segura(pasta):
    pasta = Path(os.path.abspath(pasta))
    for parte in (pasta, *pasta.parents):
        if parte.is_symlink():
            raise ValueError("Links simbólicos não são aceitos")
    privado(pasta.lstat(), diretorio=True)
    return pasta


def assinatura(st):
    return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)


def resumir(arquivo):
    antes = arquivo.lstat()
    privado(antes)
    if antes.st_size == 0:
        raise ValueError("Dump vazio")
    fd = os.open(arquivo, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as entrada:
        aberto = os.fstat(entrada.fileno())
        privado(aberto)
        if assinatura(antes) != assinatura(aberto):
            raise ValueError("Dump mudou antes da leitura")
        digest = hashlib.sha256()
        while bloco := entrada.read(1024 * 1024):
            digest.update(bloco)
        if assinatura(aberto) != assinatura(os.fstat(entrada.fileno())):
            raise ValueError("Dump mudou durante a leitura")
    if assinatura(antes) != assinatura(arquivo.lstat()):
        raise ValueError("Dump mudou após a leitura")
    return antes.st_size, digest.hexdigest()


def planejar(backup_root):
    raiz = pasta_segura(backup_root)
    itens = []
    for origem, prefixo in ORIGENS.items():
        pasta = pasta_segura(raiz / origem)
        encontrados = []
        for arquivo in sorted(pasta.iterdir()):
            nome = arquivo.name
            # Temporários, logs e outros arquivos nunca entram no plano.
            if not nome.endswith(".dump"):
                continue
            padrao = re.fullmatch(rf"{prefixo}-(\d{{8}}-\d{{4}})\.dump", nome)
            if not padrao:
                raise ValueError("Nome de dump fora da convenção da origem")
            datetime.strptime(padrao.group(1), "%Y%m%d-%H%M")
            tamanho, sha = resumir(arquivo)
            encontrados.append({"origem": origem, "nome": nome,
                                "bytes": tamanho, "sha256": sha,
                                "destino_logico": f"{DESTINO}/{origem}/{nome}"})
        if not encontrados:
            raise ValueError(f"Nenhum dump final em {origem}")
        itens.extend(encontrados)
    return {"versao": 1, "estado": "PLANO_OFFLINE_NAO_AUTORIZA_ENVIO",
            "gerado_em": datetime.now(timezone.utc).isoformat(),
            "retencao_remota": "PENDENTE_JOSE_SEM_EXCLUSAO",
            "destino": "PROPOSTA_LOGICA_NAO_VERIFICADA_NO_DRIVE",
            "itens": itens}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup-root", required=True, type=Path,
                        help="Pasta privada contendo pqbr-db/ e hindsight/; usar fixtures nesta etapa")
    args = parser.parse_args()
    try:
        plano = planejar(args.backup_root)
    except (OSError, ValueError):
        # Não ecoar paths, conteúdo de dumps ou detalhes de exceções em logs.
        parser.exit(2, "Plano recusado: origem ausente, insegura, inválida ou alterada.\n")
    print(json.dumps(plano, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
