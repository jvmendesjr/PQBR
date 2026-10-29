# Modelo — ficha de objeto

O objeto sozinho, ou em grade de catálogo. Serve para a caneca de um episódio ser a mesma caneca no outro.

## Trava

Nome comum do objeto, cor chapada, material visto de longe (pano, metal, plástico). Sem marca e sem texto na superfície.

## Folha

1. Grade 4×3 (`OBJ-catalogo.png`) ou fundo neutro, objeto inteiro.
2. Mesma cor e mesma luz entre cenas. Escala: o stickman do elenco ao lado, quando houver ficha individual.

## Estado

`permanente` quando o José aprova (conjunto de t148u). Catálogo aberto (t150u): o agente pode inserir objeto novo (`registrar`), depois de buscar; a ficha nasce `aguardando_ok_jose` (com imagem) ou `sugestao` (sem imagem). Objeto que não voltou em outro roteiro não ganha ficha individual.
