# Fases — stickman, fichas e Drive

José fechou o stickman em 27/10/2026 (t133u). As fases abaixo são o corte para não misturar decisão, texto, imagem e arquivo.

## Fase 0 — Decisão nos documentos vigentes

Feito nesta entrega.

- Identidade única: stickman. O bloco de cartum genérico sai do contrato que o roteiro copia.
- 3D não se pede. O campo antigo que liberava 3D passa a recusar.
- Logotipos e a silhueta do mapa: o José disse, na mesma noite, que estão certos. Não reabri os PNG nesta entrega.

## Fase 1 — Banco em texto

Feito nesta entrega. Pasta `banco-fichas/`.

Dois personagens, dois ambientes e quatro objetos. Estado `rascunho_texto`. Sem imagem. A cor da roupa não foi escolhida.

A pesquisa da estrutura está em `docs/pesquisas/fichas-stickman-estrutura-20261027.md`.

## Fase 2 — Espelho no Drive

Feito nesta entrega. Pasta `PQBR/00_Biblia_Visual/banco-fichas`, id `1JcDUFDEdiQmDtHX_4c57lgLFcM6-yoT4`, em `config/drive_pastas.json` na chave `banco_fichas`. Subiram os markdown e o `indice.json`. O envio conferiu md5 e tamanho. Nada foi apagado.

Antes desse envio, em 27/10, `00_Biblia_Visual` tinha cadernos, dois pacotes canônicos e pesquisas. Não tinha ficha de personagem. A pasta do sistema é `PQBR` (`1RKEE2kn2WDrH6SK__1SA5QkFkxwpqzya`), na mesma conta Google do Flow e do Studio.

Os pacotes `pacote-c913c002c9be` e `pacote-17b4cf4f727f` continuam como estavam: são hash antigo e ainda carregam o bloco visual de 12/10. Não reescrever o hash.

## Fase 3 — Imagem de referência

Ainda não. É o próximo trabalho de produção.

1. Gerar no Flow, imagem, Nano Banana 2 Lite, 9:16, só 1K. Imagem está autorizada (t131u). Não repetir o prompt de 27/10 que saiu pessoa.
2. Abrir a aba Personagens, ou Ingredients, e prender a frente aprovada. Essa aba foi vista na barra em 27/10 e não foi aberta.
3. O José olha a frente. Se servir, grava como `ASSET_personagem_masculino-v1` ou `feminino-v1` e a ficha muda de estado. Se não servir, a ficha continua rascunho.
4. Expressões e objetos vêm depois da frente. Não gerar a folha inteira antes.

## Fase 4 — Vídeos que já existem no Drive

Lidos em 27/10, só nomes e pastas. Nada foi movido nem apagado.

- `PQBR/02_Episodios/2026-10/`: EP1002 a EP1010, com mp4 e json. São os vídeos do lote, não um arquivo de experiência 3D.
- `PQBR/estilos-teste-20261012/`: `A.mp4`, `B.mp4`, `C.mp4` e as pastas `caderno-A`, `B`, `C`. Essa pasta não está em `config/drive_pastas.json`. Continua lá.
- `PQBR/99_Arquivo/`: vazia.
- Pasta antiga `Porquê BR` (`1Qt79b1VoiH9nLY23X-bhcqCUfy7QEMSM`): ainda existe, com `01-masters-shorts` e os mp4 stickman. A cópia para `99_Arquivo/rede-stickman` segue aberta no ROADMAP. Não foi feita.
- Busca por nome "3d" na conta não achou um vídeo do canal com esse nome. Achou arquivo pessoal fora das pastas PQBR; não abri e não movi. No disco do servidor, nenhum mp4 com "3d" no nome em `~/.pqbr` nem no repositório.

Se aparecer a pasta dos testes 3D, a ação é copiar para `PQBR/99_Arquivo/desenvolvimento-3d`, sem apagar o original, e tirar o 3D do fluxo. Não está feito porque o arquivo não foi encontrado.

## Fase 5 — O que o fluxo ainda não faz

Continua de pé, e não é esta entrega:

- O episódio para no storyboard e não chama o Flow.
- O auditor não entra no episódio.
- LOOP por cena, adiado.
- Publicação com `YOUTUBE_DRY_RUN=true`. Nada enviado.
- Catálogo `visual_assets` e o resolvedor sem LLM: previstos desde 08/10, não implantados. O banco de texto não liga isso sozinho.
