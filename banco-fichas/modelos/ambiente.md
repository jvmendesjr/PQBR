# Modelo — ficha de ambiente

Id estável do lugar, reaproveitado entre episódios. Não é o storyboard da cena.

## Trava

Lugar, época (hoje, salvo quando o roteiro for ao passado), hora e luz, 3 a 5 objetos-âncora. Fundo limpo. Sem texto e sem marca.

## Folha

1. Plano geral 16:9, vazio de personagem ou com membros do elenco só para dar escala e prova de convivência.
2. A mesma luz em todo ângulo. Mudança grande de luz é outra ficha.

## Proibido

Multidão, letreiro, logo, objeto a mais "para enfeitar". Objeto que a cena usa de perto tem ficha em `objetos/`.

## Estado

`permanente` quando o José aprova (conjunto de t148u). Catálogo aberto (t150u): o agente pode inserir lugar novo (`registrar`), depois de buscar; a ficha nasce `aguardando_ok_jose` (com imagem) ou `sugestao` (sem imagem). Ambiente que traz personagens do elenco em cena guarda os ids em `personagens` e marca `com_elenco`.
