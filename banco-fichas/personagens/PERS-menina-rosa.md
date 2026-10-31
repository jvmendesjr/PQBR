# PERS-menina-rosa — Ficha Permanente

Estado: `permanente` — padrão definitivo do canal, selecionado pelo José em 28/10/2026 (t148u).
Origem: Drive da conta PQBR, pasta `Fontes/Imagens` (id `1ziYivEewPQIvlgt6Z7v7R8wXPerPLvLd`), entregue pelo José em 28/10/2026 (t148u); arquivos originais `Agent Image - *` renomeados para o padrão PQBR. É o nº 2 do catálogo do elenco (`ELENCO-catalogo.png`).

- **Imagem (folha multi-pose 16:9):** `banco-fichas/personagens/PERS-menina-rosa-folha.png` — 5 giros (frente, três quartos, perfil, três quartos de costas e costas), 9 expressões e 10 poses de corpo inteiro. O `indice.json` guarda um recorte normalizado de cada um (`giro-*`, `exp-*`, `pose-*`), para o Flow e o motion usarem uma pose sem a folha inteira.
- **Acento:** vestido rosa.
- **Protagonista feminino (José, t150u):** é a protagonista dos episódios de código ímpar (alternância do storyboard); o nº 2 do catálogo do elenco.

## Trava (frase-trava para o prompt e para o Agente do Flow)

Stickman 2D flat colorido do canal Porquê BR: mulher jovem adulta de cabelo preto preso em rabo de cavalo lateral com prendedor rosa, vestido rosa chapado sem mangas e sapatos brancos ovais de contorno preto. Cabeça redonda branca grande com contorno preto, dois olhos pretos sempre visíveis, boca de reação (nunca articula fala), corpo e membros em traço preto fino, fundo claro em tom creme, sem texto e sem marca na imagem.

## O que está fechado

- **Rosto e roupa:** os da folha. Não trocar roupa, cor de acento, cabelo nem acessório entre cenas.
- **Folha multi-pose:** serve como referência visual e de aprovação. O recorte individual do personagem (para anexar como `Elemento` no Flow) é gerado a partir desta folha quando a cena pedir; a folha inteira nunca vai como imagem única para animar vídeo (t146u).

## Proibido

Um olho só (ciclope / `grotesco`), pele humana, volume 3D, fotorrealismo, dedos realistas, boca aberta articulando fala (`boca_articula_fala`), corte da cabeça no topo (`corte_oculos_cabeca`), texto ou marca na imagem.

## Idade e proporção (aprendizado 30/10/2026, revisão do piloto EP1003 v3 — José)

- **Ela é adulta, não criança.** É uma mulher jovem adulta. O nome PERS-menina-rosa é só o ID do catálogo; nos prompts do Flow e do Agente, escrever sempre **"mulher jovem adulta"** e nunca "menina/girl" — a palavra "menina/girl" fez o modelo encolher a personagem e renderizar o cenário em escala adulta, deixando-a com cara de criança, sobretudo em tomadas abertas (S07 caminhando no café, S03/S04 observando).
- **Proporção adulta:** alta, corpo inteiro, em pé no chão, balcão e mesas na altura da cintura dela, cadeiras abaixo da cintura. Em tomada aberta, ela fica em primeiro plano, corpo inteiro, e o cenário vem em escala compatível com um adulto — nunca encolher a personagem para caber no cenário.
- **Nunca banquinho ou cadeira para subir, nunca mãos ou braços extras, nunca outra pessoa despejando ou agindo por ela.** Todos os braços e pernas são traços finos pretos de stickman. Caso registrado: na S05 v3 o modelo inventou dois braços realistas com manga xadrez despejando as chaleiras e pôs a personagem em pé num banquinho — nada disso estava no prompt. Erro de geração, não pedido: regenerar, não aceitar.
