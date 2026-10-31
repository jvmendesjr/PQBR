# PERS-gravata-azul — Ficha Permanente

Estado: `permanente` — padrão definitivo do canal, selecionado pelo José em 28/10/2026 (t148u).
Origem: Drive da conta PQBR, pasta `Fontes/Imagens` (id `1ziYivEewPQIvlgt6Z7v7R8wXPerPLvLd`), entregue pelo José em 28/10/2026 (t148u); arquivos originais `Agent Image - *` renomeados para o padrão PQBR. É o nº 9 do catálogo do elenco (`ELENCO-catalogo.png`).

- **Imagem (folha multi-pose 16:9):** `banco-fichas/personagens/PERS-gravata-azul-folha.png` — 5 giros (frente, três quartos, perfil, três quartos de costas e costas), 9 expressões e 10 poses de corpo inteiro. O `indice.json` guarda um recorte normalizado de cada um (`giro-*`, `exp-*`, `pose-*`), para o Flow e o motion usarem uma pose sem a folha inteira.
- **Acento:** gravata azul.

## Trava (frase-trava para o prompt e para o Agente do Flow)

Stickman 2D flat colorido do canal Porquê BR: stickman clássico de poucos fios de cabelo, camisa social branca de manga comprida e gravata azul chapada. Cabeça redonda branca grande com contorno preto, dois olhos pretos sempre visíveis, boca de reação (nunca articula fala), corpo e membros em traço preto fino, fundo claro em tom creme, sem texto e sem marca na imagem.

## O que está fechado

- **Rosto e roupa:** os da folha. Não trocar roupa, cor de acento, cabelo nem acessório entre cenas.
- **Folha multi-pose:** serve como referência visual e de aprovação. O recorte individual do personagem (para anexar como `Elemento` no Flow) é gerado a partir desta folha quando a cena pedir; a folha inteira nunca vai como imagem única para animar vídeo (t146u).

## Proibido

Um olho só (ciclope / `grotesco`), pele humana, volume 3D, fotorrealismo, dedos realistas, boca aberta articulando fala (`boca_articula_fala`), corte da cabeça no topo (`corte_oculos_cabeca`), texto ou marca na imagem.
