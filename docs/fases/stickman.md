# Fases — stickman, fichas e Drive

José fechou o stickman em 27/10/2026 (t133u). As fases abaixo são o corte para não misturar decisão, texto, imagem e arquivo.

## Fase 0 — Decisão nos documentos vigentes

Feito nesta entrega.

- Identidade única: stickman. O bloco de cartum genérico sai do contrato que o roteiro copia.
- 3D não se pede. O campo antigo que liberava 3D passa a recusar.
- Logotipos e a silhueta do mapa: o José disse, na mesma noite, que estão certos. Não reabri os PNG nesta entrega.

## Fase 1 — Banco em texto

Feito nesta entrega. Pasta `banco-fichas/`.

Dois personagens, dois ambientes e quatro objetos. O elenco passou a `definido` na fase 3. Ambiente e objeto seguem `rascunho_texto`.

A pesquisa da estrutura está em `docs/pesquisas/fichas-stickman-estrutura-20261027.md`.

## Fase 2 — Espelho no Drive

Feito nesta entrega. Pasta `PQBR/00_Biblia_Visual/banco-fichas`, id `1JcDUFDEdiQmDtHX_4c57lgLFcM6-yoT4`, em `config/drive_pastas.json` na chave `banco_fichas`. Subiram os markdown e o `indice.json`. O envio conferiu md5 e tamanho. Nada foi apagado.

Antes desse envio, em 27/10, `00_Biblia_Visual` tinha cadernos, dois pacotes canônicos e pesquisas. Não tinha ficha de personagem. A pasta do sistema é `PQBR` (`1RKEE2kn2WDrH6SK__1SA5QkFkxwpqzya`), na mesma conta Google do Flow e do Studio.

Os pacotes `pacote-c913c002c9be` e `pacote-17b4cf4f727f` continuam como estavam: são hash antigo e ainda carregam o bloco visual de 12/10. Não reescrever o hash.

## Fase 3 — Imagem de referência

Tentativa 1 feita em 27/10, seguindo o fluxo (manifesto antes, bloco único sem número e sem fala, rótulo só no arquivo, Lite escolhido no menu, exemplos humanos da tela não usados). A imagem saiu pessoa com volume, 1376×768, mãos com dedos. Não é a frente. Não virou asset. O mesmo prompt não se repete. Detalhe no DECISOES-LOG t138u. A aba Personagens foi aberta; a imagem não foi concluída como personagem.

1. A frente não se pede de novo ao Flow enquanto a roupa não tiver cor. O desenho de t139u está recusado.
2. A aba Personagens foi aberta em 27/10 (t138u). A tentativa 1 e os PNG de t139u não servem.
3. A próxima folha só nasce depois que o José apontar a roupa. Aí sim: frente, lado e três expressões, e ele olha de novo.
4. Expressões e objetos vêm depois. Não gerar a folha inteira antes.

Leitura de canais grandes em 27/10: `docs/pesquisas/canais-que-repetem-o-desenho-20261027.md`. O que se copia é um corpo preso e um Short de uma situação. Não se copia tom adulto, choque, nem luta.

Recusado em 28/10 (t140u). José comparou com a busca e com tutoriais de stickman e não quis o tubo sem roupa. Os PNG ficam no disco e não são referência. Em t141u ele fechou: a arquitetura e o NotebookLM ficam; o material inspira o desenho e o prompt do storyboard que já existe. A próxima folha, depois da cor da roupa, é frente, lado e expressões. Análise em `docs/pesquisas/referencias-stickman-20261028.md`.

Atualizado em 28/10 (t146u — regra canônica do José + geração real no Google Flow com `🍌 Nano Banana Pro`):
- José enviou 5 recortes reais tirados de vídeos do próprio canal Porquê BR (`banco-fichas/referencias-canal/`) e reprovou os desenhos programáticos anteriores (inclusive um erro grotesco de um olho só na pose de perfil).
- **Regra canônica fixada (t146u):** para **personagens, objetos e locais permanentes** (`banco-fichas/`), usar **fichas permanentes geradas no Google Flow com o modelo mais potente de geração de imagens (atualmente `🍌 Nano Banana Pro`, 0 créditos)**, ancoradas nas 5 imagens reais do canal.
- **Histórico (descartado em t148u, ver o bloco abaixo): 12 fichas permanentes geradas no Google Flow com `🍌 Nano Banana Pro` e inspecionadas visualmente (`permanente_aguardando_ok_jose`). Os IDs `PERS-M`, `PERS-F` e `PERS-M-classico` abaixo não existem mais:**
  - `PERS-M.png` (`768×1376`, 9:16) e `PERS-M-folha.png` (`1376×768`, 16:9, 3 poses de corpo inteiro com 2 olhos sempre visíveis): stickman 2D em nanquim preto sobre papel creme (`#f5f0e4`) com hachura na bochecha, óculos redondos vermelhos (`#e23b2f`), luvas brancas e pés pretos ovais.
  - `PERS-F.png` (`768×1376`, 9:16) e `PERS-F-folha.png` (`1376×768`, 16:9, 3 poses de corpo inteiro com 2 olhos sempre visíveis): stickman feminina no mesmo traço, com coque preto no topo e argola amarela (`#e6b325`) à esquerda.
  - `PERS-M-classico.png` (`768×1376`, 9:16) e `PERS-M-classico-folha.png` (`1376×768`, 16:9): stickman clássico do canal sem óculos.
  - `AMB-cozinha.png` e `AMB-sala.png` (`768×1376`, 9:16): cozinha e sala brasileiras em nanquim + hachura sobre papel creme (`#f5f0e4`).
  - `OBJ-chaleira.png`, `OBJ-xicara.png`, `OBJ-filtro-pano.png` e `OBJ-controle-remoto.png` (`1024×1024`, 1:1): objetos permanentes em nanquim + hachura sobre papel creme (`#f5f0e4`).
- **Agente do Google Flow calibrado no projeto (`e2dacb70-b9d0-4dc7-8b93-e6ac1688a454`):** `Confirmar antes de gerar = Sempre`, imagem padrão `9:16` + `x1` + `🍌 Nano Banana Pro`, vídeo padrão `9:16` + `x1` + `Omni 1.1 Flash` e `Instruções para o agente` gravadas com a diretriz canônica do canal. Pesquisa completa e receita técnica do upload Angular (`.sidebar-upload-btn`) em `docs/pesquisas/flow-agente-e-nano-banana-pro-20261028.md`.

Atualizado em 28/10 (t148u — o conjunto definitivo veio pronto do José):
- José reprovou as 12 fichas nanquim de t146u ("não estavam num bom nível"), mandou descartá-las e tirá-las do diretório, e entregou no Drive (`Fontes/Imagens`) 20 imagens no estilo que quer, declarado **o padrão definitivo do canal**. Elas viraram o `banco-fichas/` novo: catálogo dos 12 personagens + 6 folhas individuais multi-pose, 11 ambientes, catálogos de 12 objetos e de 12 animais (`indice.json` 2.0.0).
- O gerador programático de t144u foi aposentado (`scripts/aposentado/frente_stickman.py`) e os IDs `PERS-M`/`PERS-F`/`PERS-M-classico` morreram com as fichas antigas.
- Pendiam: apontar os protagonistas (resolvido em t150u, abaixo), regravar as `Instruções para o agente` no Flow com o traço t148u e espelhar o banco novo em `00_Biblia_Visual/banco-fichas` (P17).

Atualizado em 28/10 (t150u — catálogo aberto, protagonistas e situações):
- **Estilo nas palavras do José:** cartoon 2D, flat, colorido, com personagens stickman (REGRAS §5/§6, `config/estilo_visual.json`, `ESTILO_PADRAO_STICKMAN`).
- **Protagonistas definidos:** o nº 1 do catálogo (`PERS-menino-azul`: cabelo espetado preto, camiseta azul, boca aberta sorrindo) é o masculino; o nº 2 (`PERS-menina-rosa`) é a feminina. A alternância par/ímpar do storyboard segue. `PERS-bob-oculos` entra como nº 13 (13 personagens).
- **Catálogo aberto (`indice.json` 3.1.0, 62 fichas):** tudo em `banco-fichas/` é referência. O agente insere personagens, figuras, animais, objetos, lugares e **situações** (categoria nova, `situacoes/`) pelo mecanismo `pipeline/banco_fichas.py` (contrato `FichaCatalogo`, modelos em `banco-fichas/modelos/`, testes). Ficha do agente nasce `aguardando_ok_jose` (usável) ou `sugestao` (ideia sem mídia); só o José aprova ou descarta. **t155u:** 30 fichas (6 PERS derivadas, 12 OBJ, 12 ANIM) → `permanente`; 11 `SIT-*` seguem `sugestao`.
- **Fichas (t155u):** `PERS-menino-azul` (permanente, derivada do nº 1); as seis derivadas do elenco (`PERS-senhor-cachecol` nº 3, `PERS-punk-azul`, `PERS-pijama-sono`, `PERS-fones-vermelho`, `PERS-nerd-laco`, `PERS-rei-coroa`) e as 12 OBJ + 12 ANIM passaram a `permanente`; 11 situações em `sugestao`, sem mídia.
- **Peso no repositório:** as imagens da semente têm 2,5–6 MB (`banco-fichas` ≈ 93 MB). Imagem nova entra com até 2 MB; acima disso e todo vídeo ficam no Drive, citados por `imagem_drive_id`/`drive_id` (`TAMANHO_MAX_IMAGEM`).
- **Storyboard 1.3.0 e pacote:** a cena cita o catálogo em `refs` e o pacote canônico do NotebookLM leva o resumo do catálogo (`catalogo_visual`); ficha nova muda o hash do pacote sozinha.
- **P17 (t155u, parcial):** `Instruções para o agente` no Flow regravadas no flat; espelho Drive com 111 arquivos; 30 fichas aprovadas. **Ainda pendem:** folha individual do nº 1, mídia das 11 `SIT-*`, e OK do José para reiniciar o worker com o storyboard 1.3.0.

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
