# Estrutura de ficha para o stickman

Leitura de 27/10/2026. Nada foi gerado no Flow nesta pesquisa. O banco que aplica isto está em `banco-fichas/`. As fichas de lá são texto, sem imagem.

## O que foi lido

1. Wikipedia, "Model sheet" (página lida em 27/10/2026): https://en.wikipedia.org/wiki/Model_sheet
   - A ficha existe para o desenho não sair "off-model" quando mais de uma cena, ou mais de uma geração, precisa parecer o mesmo personagem.
   - O habitual de estúdio: cabeça e corpo em vários ângulos, mãos e pés, expressões, proporção, roupa e gesto.
   - Várias folhas quando o personagem tem atitude fina. Desvio só se a direção permitir.

2. DreamDrive, "Flow Ingredients and Scenebuilder", atualizado em 15/10/2026 (página lida em 27/10/2026): https://www.dreamdrive.ai/learn/google-labs/flow-ingredients-and-scenebuilder-consistency/
   - No Flow, a consistência vem de imagem de referência (Ingredients to Video), não de redescrever o personagem.
   - Personagem: frente, bem iluminada, fundo liso, roupa inteira visível; 3/4 se couber. Evitar sombra forte e acessório que não seja do personagem.
   - Objeto: sozinho, fundo neutro, sem reflexo de outra coisa; dois ângulos ajudam.
   - Estilo: um quadro de paleta e luz, sem um assunto forte que vaze para a cena.
   - Duas ou três referências por tomada. Mais que isso, o modelo escolhe sozinho.
   - A mesma descrição em todo prompt. Estender o clipe em vez de gerar de novo, quando a cena continua.

3. Já no repositório, `docs/pesquisas/flow-storyboard-por-cena.md` (26/10): citar a ficha pelo nome curto e não redescrever roupa nem cabelo, porque isso causa deriva.

Não achei, nesta leitura, um padrão brasileiro de ficha de stickman para Shorts. O recorte abaixo é o model sheet de animação, enxugado pelo que o Flow pede e pelo que o canal é: comédia de poucos detalhes.

## O que a PQBR guarda, e o que deixa para depois

Guarda agora, em texto:

- Personagem: uma frase-trava, frente obrigatória, 3/4 só depois da frente aceita, folha curta de expressões, um acessório, uma cor de acento.
- Ambiente: lugar, luz, 3 a 5 objetos, o que não entra.
- Objeto: sozinho, dois ângulos, sem marca, escala só quando o stickman já tiver imagem.

Deixa para depois, de propósito:

- Giro completo (frente, lado, costas, 3/4 dos dois lados). O stickman tem pouca informação; a frente travada resolve mais do que oito vistas geradas sem aprovação.
- Mãos e pés detalhados. O contrato do stickman é sem dedos desenhados.
- Catálogo no Postgres (`visual_assets`) e resolvedor. Continuam por fazer. Esta pasta não os substitui.

## Por que as duas imagens de 27/10 não servem de ficha

O pedido descreveu o elenco feminino em texto (coque, argola, pinta, camiseta, calça) e pediu stickman. As duas saíram pessoa de cartum. Sem uma imagem de referência aprovada, repetir descrição não trava o personagem.
