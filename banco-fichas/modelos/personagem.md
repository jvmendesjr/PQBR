# Modelo — ficha de personagem

Id estável (`PERS-<slug>`). Sem nome falado ou escrito no vídeo.

Catálogo aberto (t150u): o elenco é referência, não lista fechada. O agente pode inserir personagem novo quando o tema pedir variedade (`pipeline/banco_fichas.py`, `registrar`), depois de buscar se já não existe um parecido. Estilo: cartoon 2D, flat, colorido, stickman.

Preencher só o que estiver decidido. A roupa do cotidiano é a da folha individual aprovada; não trocar roupa nem acento entre cenas.

## Trava

Uma frase curta, repetida igual. Cabeça, corpo, um acessório, uma cor de acento. Sem idade de pessoa real, sem pele, sem dedos.

## Imagem

- **Folha individual:** multi-pose 16:9 (contact sheet) com turnarounds (frente, três quartos, perfil, costas), ~9 expressões no mesmo rosto e ~10 poses de corpo inteiro. Os recortes nomeados (`giro-*`, `exp-*`, `pose-*`) ficam no `indice.json` como retângulos normalizados `[x0, y0, x1, y1]` (no máximo 24).
- **Sem folha:** a ficha aponta o recorte do catálogo (`num-NN`, em `ELENCO-catalogo.png`) até ganhar a folha própria.
- **Imagem nova:** até 2 MB no repositório (png, jpg ou webp); acima disso, no Drive (`imagem_drive_id`).
- Boca de reação, não boca de fala.

## Proibido na imagem

Pessoa realista, dedos desenhados, volume 3D, marca, texto, um olho só (ciclope), cabeça cortada.

## Estado

`permanente` quando o José aprova (conjunto de t148u). Ficha nova do agente nasce `aguardando_ok_jose` (com imagem) ou `sugestao` (sem imagem). Descartar: `descartar` (permanente só por ordem do José).
