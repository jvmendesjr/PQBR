# ELENCO-catalogo — Ficha Permanente

Estado: `permanente` — padrão definitivo do canal, selecionado pelo José em 28/10/2026 (t148u). Em t150u o José definiu os protagonistas, aceitou o `PERS-bob-oculos` como 13º do catálogo e abriu o catálogo (o elenco é referência, não lista fechada).
Origem: Drive da conta PQBR, pasta `Fontes/Imagens` (id `1ziYivEewPQIvlgt6Z7v7R8wXPerPLvLd`), entregue pelo José em 28/10/2026 (t148u); arquivos originais `Agent Image - *` renomeados para o padrão PQBR.

- **Imagem (grade 4×3, 16:9):** `banco-fichas/personagens/ELENCO-catalogo.png` — os 12 personagens numerados do canal (recortes `num-01` a `num-12` no `indice.json`).
- **Estilo:** cartoon 2D, flat, colorido, com personagens stickman: cabeça redonda branca grande com contorno preto, dois olhos pretos sempre visíveis, boca simples de reação, corpo e membros em traço preto fino, roupa chapada colorida fixa por personagem, fundo claro em tom creme, paleta suave, sombra leve chapada no chão; sem texto, sem marca, sem volume 3D, sem fotorrealismo.

## Os 13 do catálogo

| nº | descrição curta | ficha |
|---|---|---|
| 1 | menino de cabelo espetado preto e camiseta azul — **protagonista masculino** | `PERS-menino-azul` |
| 2 | menina de rabo de cavalo e vestido rosa — **protagonista feminina** | `PERS-menina-rosa` (folha) |
| 3 | senhor de poucos fios de cabelo, óculos quadrados, cachecol cinza e colete verde | `PERS-senhor-cachecol` |
| 4 | punk de moicano azul e camiseta preta de caveira | `PERS-punk-azul` |
| 5 | menina cacheada de camiseta amarela | `PERS-cacheada` (folha) |
| 6 | careca sonolento de pijama azul | `PERS-pijama-sono` |
| 7 | rapaz de moletom vermelho com fones de ouvido grandes | `PERS-fones-vermelho` |
| 8 | menino de boné verde e mochila preta | `PERS-bone-verde` (folha) |
| 9 | stickman clássico de camisa branca e gravata azul | `PERS-gravata-azul` (folha) |
| 10 | nerd de óculos redondos, laço vermelho e suspensório | `PERS-nerd-laco` |
| 11 | rei de coroa dourada e capa vermelha | `PERS-rei-coroa` |
| 12 | rapaz ansioso de moletom roxo | `PERS-roxo-ansioso` (folha) |
| 13 | moça de cabelo bob e óculos redondos (fora da grade) | `PERS-bob-oculos` (folha) |

## Regras

- Elenco sem nomes falados ou escritos (REGRAS §5). O número do catálogo não entra no vídeo.
- **Protagonistas (José, t150u):** o nº 1 é o `masculino` e o nº 2 é o `feminino` da alternância par/ímpar do storyboard (par = masculino, ímpar = feminino).
- **Catálogo aberto (José, t150u):** o agente pode inserir personagens novos e deve variar o elenco; os ids acima são a base. Antes de criar, buscar (`pipeline/banco_fichas.py`).
- Personagem sem folha individual usa o recorte do catálogo (`num-NN`) até ganhar a própria folha, gerada com o modelo mais potente e ancorada neste conjunto.
- As fichas dos nº 3, 4, 6, 7, 10 e 11 foram escritas pelo mantenedor a partir da grade do José e esperam o OK dele (`aguardando_ok_jose`). O nº 3 tem cachecol cinza (a descrição antiga dizia verde e careca; a grade mostra poucos fios de cabelo).
- O nº 1 tem a boca aberta sorrindo na grade: é reação breve. Ao animar, boca fechada (sem articular fala).
