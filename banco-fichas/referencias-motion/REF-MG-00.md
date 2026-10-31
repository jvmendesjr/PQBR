# REF-MG-00 — Padrão flat colorido do canal

- **Origem:** interna. Âncora da coletânea: a identidade visual do próprio canal, o conjunto definitivo de `banco-fichas/` (t148u; estilo nas palavras do José em t150u: "cartoon 2D, flat, colorido, com personagens stickman").
- **Estado:** `aprovada` (29/10/2026, t131u — José aprovou a regra e as fichas).
- **Histórico:** a ficha nasceu em t147u no nanquim de t146u (papel creme `#f5f0e4`, hachura, cores de `PERS-M`/`PERS-F`), que o José reprovou e mandou descartar (t148u). Em t150u foi reescrita no padrão flat colorido. O OK que ela espera é sobre esta versão.
- **Prova renderizada:** `provas/mg10-pecas.png` (12 quadros com a paleta flat, a Fredoka e o layout do bloco, sem violação de zona segura). O desenho do cartão v2 está em `runtime/piloto-motion/mg03/folha-cartoes-v2.png`, aprovado pelo José em 28/10 (t152u).

## Gramática (o que o motion copia daqui)

- **Fundo:** creme claro, chapado (`#f6f1e7` na tela e `#f7f7f2` no cartão, na paleta do motor); nunca branco puro como fundo da tela nem gradiente.
- **Traço:** contorno preto fino, cor chapada, sem hachura, sem brilho, sem sombra projetada de software.
- **Cor de acento:** só a paleta do motor (`pqbr.pos.motion.catalogo.PALETA`), que vem do elenco e da marca: protagonista masculino em azul-aço (`#4b83ba`, escuro `#2c5f93`, acento `#e03837`), feminina em rosa (`#ee7e91`, escuro `#b83a5d`, acento `#826caf`), apoio amarelo `#f6c956`, verde da marca `#0f766e`, tinta `#1f2328`, cinza `#6b7280`. Letra colorida sobre fundo claro usa o tom escuro (o rosa chapado dá só 2,3:1 no creme).
- **Tipografia:** uma fonte só, a Fredoka (OFL, definida pelo José em t149u, por arquivo local). Nada de fonte de interface.
- **Personagem:** quando aparece, vem de uma ficha `PERS-*` do catálogo, num quadradinho num canto da zona segura (peça `personagem-moldura`), com recorte estático e boca de reação.
- **Ritmo:** molas fechadas (o elemento assenta com um leve excesso e volta), entrada por idioma (surgir, riscar, datilografar), nunca fade puro.
- **Texto:** só o bloco de números travados do roteiro.

## Por que ela existe

O tutorial de t145u (passo "name a look, feed a frame") e a regra das fichas permanentes (t146u) apontam a mesma coisa: a referência que ninguém copia é a própria biblioteca do canal. Toda variação da coletânea mede distância daqui; toda referência externa nova precisa dizer o que acrescenta **a esta ficha**, e nunca a substitui.
