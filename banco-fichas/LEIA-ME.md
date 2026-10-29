# Banco de fichas — stickman

Padrão visual definitivo do canal (t148u): o conjunto entregue pelo José no Drive (`Fontes/Imagens`, id `1ziYivEewPQIvlgt6Z7v7R8wXPerPLvLd`) em 28/10/2026. As fichas em nanquim geradas no Flow em t146u foram descartadas a pedido dele e saíram do diretório (preservadas no histórico do git, commit `ad1b689`).

Identidade: stickman flat colorido — cartum 2D de contorno preto, cores chapadas suaves, fundo claro em tom creme. Não é pessoa realista, não é 3D e não é o nanquim de t146u.

## O que entra

| Tipo | Pasta | O que é |
|---|---|---|
| Elenco | `personagens/ELENCO-catalogo.png` | grade 4×3 com os 12 personagens numerados |
| Personagem | `personagens/PERS-*-folha.png` | folha individual multi-pose (turnarounds, 9 expressões, ~13 poses); 6 personagens têm folha própria |
| Ambiente | `ambientes/AMB-*.png` | 11 lugares em 16:9; 3 fichas incluem 3 personagens do elenco em cena (prova de escala) |
| Objeto | `objetos/OBJ-catalogo.png` | grade 4×3 com os 12 objetos permanentes |
| Animal | `animais/ANIM-catalogo.png` | grade 4×3 com os 12 animais domésticos |

Modelos de ficha em `modelos/`. Índice legível por máquina: `indice.json`.

## Como o Flow usa

A folha do personagem entra como referência (`Elemento`), citada pelo id curto. O recorte individual para a cena é gerado a partir da folha quando a produção pedir; a folha inteira nunca vai como imagem única para animar vídeo (t146u). O prompt da cena muda pose, expressão, objeto e lugar; não redesenha cabeça nem roupa.

## O que não volta

- As fichas em nanquim de t146u (descartadas pelo José em t148u).
- A bíblia de 08/10 (Zé, Lia, Valdemar, Sandra) fica histórica. Nome não entra no vídeo.
- Os frames antigos do canal (`referencias-canal/`) foram descartados em t149u por ordem do José; a âncora vigente é este conjunto.

## Protagonistas

A alternância do storyboard segue por gênero (par = masculino, ímpar = feminino). Quem do elenco novo assume cada gênero: **EM CONSTRUÇÃO — aguardando o José**.
