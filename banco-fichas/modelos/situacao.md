# Modelo — ficha de situação

Pose ou movimento corriqueiro de um personagem: acenar, pensar, digitar, correr com pressa, esperar. Imagem ou vídeo curto que serve de referência de ação para o storyboard e, no motion, para o personagem que aparece explicando ou participando. Catálogo aberto (t150u): o agente pode inserir situações novas.

Id estável (`SIT-<slug>`). A situação não tem dono: o personagem sai do catálogo na hora da cena, sem trocar roupa nem acento.

## Ação

Uma frase: o corpo inteiro, o gesto, a direção do olhar e a expressão de reação. Sem objeto de marca e sem texto.

## Trava

A pose escrita para o prompt: de frente ou de lado, onde ficam as mãos, a cabeça e os pés. Não cita nome nem roupa de personagem.

## Mídia

- **Imagem:** opcional, até 2 MB no repositório.
- **Vídeo:** só no Drive (`videos[].drive_id`, até 30 s, no máximo 6 por ficha). Marcar `loop` quando o gesto repete (digitar, esperar).
- Ficha sem mídia é `sugestao`: ideia pronta para o agente produzir a imagem ou o vídeo. Ao anexar (`anexar_midia`), ela vira `aguardando_ok_jose`.

## Proibido

Boca articulando fala, texto na imagem, marca, pessoa realista, volume 3D, um olho só (ciclope), cabeça cortada.

## Estado

`sugestao`, `aguardando_ok_jose` (usável desde já) ou `permanente` (o José aprovou).
