# Pesquisa: storyboard por cena para o Google Flow ("fábrica em série")

t77u, 26/10/2026. Pesquisa web curta e **só estudo**: nada foi gerado no Flow. Complementa `PESQUISA-extensoes-geracao-em-serie.md` (t529), onde estão as extensões VEO Automation, Flow Queue, Flow Automator e AutoFlow, os tutoriais Storyboard Studio e Characters e a GUÍA VOX.

## Fontes
1. Versely, template de storyboard cena a cena (SUBJECT/ACTION/CAMERA/ATMOSPHERE, ficha de personagem, encadear o último frame): https://www.versely.studio/blog/versely-ai-movie-maker-multi-scene-storyboard-workflow-2026
2. DreamDrive, Flow Ingredients + Scenebuilder (referência por descrição fixa, sem redescrever o que a imagem mostra; início e fim com a mesma câmera e a mesma luz): https://www.dreamdrive.ai/learn/google-labs/flow-ingredients-and-scenebuilder-consistency/
3. J. Vertrees, Flow + Veo 3.1 Frames to Video (o fim da cena N é o início da N+1): https://jvertrees.hashnode.dev/what-we-learned-making-ai-video-with-google-flow-and-veo-3-1
4. Miraflow, 18 prompts início→fim (estrutura em 3 partes: Start Frame, End Frame, Motion): https://miraflow.ai/blog/google-flow-start-end-frame-ai-video-prompts-2026
5. Skywork, storyboard de imagens → Veo 3.1 no Flow (schema subject/setting/camera/motion/constraints repetido): https://skywork.ai/blog/ai-video/how-to-convert-storyboard-images-to-veo-3-1-videos-in-flow
6. Gist "prompt enhancement" (enquadramento pelo nome do plano; "from the chest up" corta a cabeça; texto entre aspas = fala com lip-sync): https://gist.github.com/cicalooo/45de8616c99d5707e92a925e9f9a4f87
7. FastAccess, guia do Veo 3 (aspas e verbos "says/speaks" disparam o lip-sync): https://fastgptplus.com/en/posts/veo3-prompt-guide
8. Google Cloud, guia de prompts do Veo 3.1 (negativo descrito em positivo): https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1

## Padrão comum
- **Ficha por cena, numerada e com rótulo fixo** (cena N, rótulo `<ep>_cNN`), com os slots sempre iguais: sujeito (descritor fixo), ação (uma só), câmera (plano + movimento), atmosfera e restrições. No `.txt` que vai para a fila da extensão, os blocos ficam sem número, e a ordem e o rótulo moram no manifesto e no nome do arquivo (GUÍA VOX, t529).
- **Referência identificada**: ficha de personagem e de estilo travadas como imagem (Ingredients/Characters), citadas pelo mesmo nome curto em toda cena, sem redescrever roupa ou cabelo (isso causa drift) [1][2].
- **Início e fim**: cada um descrito como foto parada, com a mesma câmera e a mesma luz. Mudança grande vira corte e dois clipes. Para continuidade, o fim da cena N vira o início da N+1 [2][3][4].
- **Movimento**: uma frase, com uma ação e um movimento de câmera, mais o que excluir (warping, flicker) [4][6].
- **Boca**: o lip-sync é disparado por texto entre aspas e por verbos de fala [6][7]. Para evitar: nunca pôr a narração no prompt, descrever "lips closed, only blinking and breathing" (negativo em positivo [8]) e, se preciso, preferir plano mais aberto ou o personagem de lado.
- **Cortes**: usar o nome do plano (close, plano médio, médio curto), nunca "do peito para cima", e pedir "full head visible with space above" [6].
- **Revisão antes do vídeo**: storyboard de imagens primeiro (barato), revisado, e só depois o vídeo por cena (t529 §3.2; DreamDrive gera 2 saídas e escolhe).

## Aplicação no PQBR
- O contrato `src/pqbr/contratos/storyboard.py` (`FichaCena`/`Storyboard` 1.0.0) cobre: número + rótulo, fala fora do prompt, norte/início/fim/movimento, plano, prompt de imagem e de animação, refs `ASSET_*`, época e papel do personagem. Ele valida "lips closed", proíbe framing descritivo e verbo de fala, exige que o personagem não protagonize cenas do passado (observador escondido ou caracterizado da época) e só libera vídeo com `imagens_revisadas`.
