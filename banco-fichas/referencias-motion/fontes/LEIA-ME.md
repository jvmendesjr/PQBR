# Banco de fontes do motion

Aqui ficam as fontes (letras) que o bloco explicativo em motion pode usar. É parte do banco de inspiração, a pasta `banco-fichas/referencias-motion/`.

Toda fonte nova entra como candidata (`aguardando_ok_jose`). Só o José aprova. A fonte do padrão do canal é a **Fredoka** (decisão do José em 28/10/2026); só muda por ordem dele.

## Como o José adiciona uma fonte

Caminho fácil: mande ao agente, no chat, o **link do Google Fonts** (ou só o nome da família). O agente baixa, confere e registra. Depois ele mostra o resultado para o José olhar.

Caminho técnico (na raiz do repositório):

```
PYTHONPATH=src .venv/bin/python -m pqbr.pos.motion.fontes verificar ARQUIVO.ttf
PYTHONPATH=src .venv/bin/python -m pqbr.pos.motion.fontes registrar ARQUIVO.ttf \
  --id minha-fonte \
  --origem-url https://github.com/google/fonts/tree/main/ofl/minhafonte \
  --licenca OFL-1.1 \
  --arquivo-licenca OFL.txt \
  --uso "títulos curtos" \
  --notas "o que foi conferido"
PYTHONPATH=src .venv/bin/python -m pqbr.pos.motion.fontes listar
PYTHONPATH=src .venv/bin/python -m pqbr.pos.motion.fontes aprovar minha-fonte --por Jose
```

## O que o agente confere sozinho

- Licença livre: OFL-1.1, Apache-2.0 ou UFL-1.0, com o arquivo da licença junto.
- Arquivo local `.ttf` ou `.otf`. WOFF, WOFF2 e coleções são recusados.
- Cobertura completa do português: todas as letras, acentos (á à â ã é ê í ó ô õ ú ü ç e vizinhos), números e pontuação (aspas, travessão, reticências, %, €, º, ª).
- Tamanho de até 3 MB.
- O endereço de origem começa com `https://`.
- O identificador (`id`) é único e só tem minúsculas, números e hífen.

Se algo falhar, nada é gravado e o agente explica o motivo.

## Estados

1. `aguardando_ok_jose`: candidata. Pode ser vista e testada.
2. `aprovada`: o José aceitou. Só ele aprova.

## Nome dos arquivos (padrão)

O agente guarda cada fonte como `<id>/<id>.ttf` e a licença como `<id>/LICENSE.txt`, só com letras minúsculas, números e hífen. Os nomes de origem do Google Fonts têm colchetes e vírgulas, que quebram em endereços e CSS. O nome original fica no índice, no campo `arquivo_original`.

## Como a fonte é usada

A fonte nunca vem da internet no render. O arquivo local é carregado direto da pasta. O plano de motion escolhe a fonte pelo `id` (campo `fonte` do `PlanoMotion` 1.1.0, padrão `fredoka`, só fonte aprovada). No CSS, o nome fica `PQBR-<id>`.

## Remover uma fonte recusada

Peça ao agente. Ele apaga a pasta da fonte e a linha do índice (`remover ID`). Fonte já aprovada só sai por ordem do José (`--por-jose`). O histórico fica no git.

## Fontes aprovadas

Todas vêm do repositório oficial do Google Fonts, com licença OFL-1.1. O José aprovou as quatro em 28/10/2026. A Patrick Hand ficou de fora: a licença dela traz um e-mail pessoal do autor.

| id | Família | Licença | Origem | Cara |
|---|---|---|---|---|
| `baloo-2` | Baloo 2 | OFL-1.1 | https://github.com/google/fonts/tree/main/ofl/baloo2 | Arredondada e amigável, de cartum. |
| `fredoka` | Fredoka | OFL-1.1 | https://github.com/google/fonts/tree/main/ofl/fredoka | Arredondada e gordinha, boa para títulos e números. |
| `short-stack` | Short Stack | OFL-1.1 | https://github.com/google/fonts/tree/main/ofl/shortstack | Manuscrita de marcador, traço grosso, parece feita à mão como o stickman. |
| `shantell-sans` | Shantell Sans | OFL-1.1 | https://github.com/google/fonts/tree/main/ofl/shantellsans | Escrita à mão informal, com ajustes de peso e de "balanço". |
