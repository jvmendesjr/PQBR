# Banco de fichas — stickman

Texto de produção. O elenco tem frente desenhada aqui (t139u): tubo preto, cabeça branca, sem roupa. Ambiente e objeto ainda não têm imagem.

Identidade: stickman. Não é pessoa de cartum e não é volume 3D. Decisão: t133u, corpo fechado em t139u (27/10/2026).

## O que entra

| Tipo | Para que serve | O que a ficha pede | O que ainda não existe |
|---|---|---|---|
| Personagem | o mesmo boneco em toda cena | frente sem letra, um acento, sem roupa | `personagens/PERS-M.png` e `PERS-F.png` |
| Ambiente | o lugar, com poucos objetos | plano geral limpo, luz, 3 a 5 âncoras, o que não entra | a imagem |
| Objeto | a coisa sozinha, para não mudar de cena | fundo neutro, dois ângulos, escala ao lado do stickman, sem marca | a imagem |

Modelos em `modelos/`. Rascunhos preenchidos em `personagens/`, `ambientes/` e `objetos/`. Índice: `indice.json`.

## Como o Flow usa

A frente entra como referência (Ingredients), citada pelo id curto. O prompt da cena não redescreve cabeça, óculos nem roupa. Redescrição foi o que derrubou as imagens de 27/10: o pedido dizia stickman e saiu pessoa de cartum.

`ELENCO-frente.png` só compara a altura. Não vai para o Flow. A aba Personagens do Flow não recebeu estes arquivos.

## O que não volta

A bíblia de 08/10 (Zé, Lia, Valdemar, Sandra) fica histórica. Nome não entra no vídeo. O elenco ativo é `PERS-M` e `PERS-F`.

Não há roupa no cotidiano. Figurino de época só quando o personagem participa de outra época, e isso é outra ficha, não um retoque da base.
