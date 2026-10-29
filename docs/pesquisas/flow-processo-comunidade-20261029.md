# Pesquisa: processo completo de criação no Google Flow (Agente) — comunidade 2026-10-29

**Pedido:** José t148u — validar/complementar o processo de 8 itens com pesquisa na comunidade (Agent-Reach), para consistência de personagens entre cenas, repetível em outras plataformas.

**Método:** Agent-Reach v1.5.0 (`agent-reach doctor --json` no `pc`).
- **Usado:** Exa (`mcporter exa.web_search_exa`), web/Jina Reader, YouTube/yt-dlp (metadados + legendas auto EN de 2 tutoriais).
- **Parcial/bloqueado:** Reddit API/rdt → 403/forbidden (trechos via índice de busca WebSearch, rotulados); Twitter/X search → 404 GraphQL (cookies presentes, endpoint quebrado); OpenCLI Reddit/X não conectado.
- **Fallback rotulado:** WebSearch (Cursor) para threads Reddit e síntese de guias.
- **Nota de versão:** Agent Reach tem update disponível v1.6.0 (não aplicado nesta tarefa).

**Escopo:** Google Flow (`labs.google` / `flow.google.com`) + Agente embutido + Ingredients / Characters / Storyboard Studio / Scenebuilder / Nano Banana / Veo-Omni. Nada foi gerado no Flow nesta pesquisa.

---

## 1. Processo do José (rascunho a validar)

1. Cada vídeo tem o seu projeto.
2. Abrir um projeto novo para cada produção.
3. Verificar no roteiro se já tem as imagens no banco e entregá-las.
4. Acessar o Flow e verificar se a função Agente está ativa.
5. Pedir para o Agente criar imagens que faltam para servir como referência.
6. Apontar todas as referências e pedir o storyboard.
7. Usar o storyboard como referência para o Agente produzir o que falta (tudo via Agente).
8. O prompt já detalha modelo, formato (9:16) e todos os detalhes.

---

## 2. Confirmações (o que a comunidade/oficial apoia)

| Item José | Veredito | Evidência |
|---|---|---|
| 1–2 Projeto por vídeo / projeto novo | **Confirmado** | Oficial: mídia do Agente salva no projeto aberto ([Help Agent](https://support.google.com/labs/answer/17093911)). Tutoriais abrem projeto novo por filme ([Klever Nuts](https://www.youtube.com/watch?v=IaOekALLe4U), [More Tutorials](https://www.youtube.com/watch?v=_0ZRdM1GCRQ)). Misturar episódios no mesmo projeto gera deriva visual (caso EP1003 PQBR t141u–t145u). |
| 3 Banco → entregar fichas existentes | **Confirmado** | Google Blog: criar *ingredients* (personagem/objeto/estilo) **antes** da cena ([5 tips](https://blog.google/innovation-and-ai/products/flow-video-tips/)). DreamDrive 15/10/2026: gastar tempo em referências limpas antes de gastar crédito ([DreamDrive](https://www.dreamdrive.ai/learn/google-labs/flow-ingredients-and-scenebuilder-consistency/)). Reddit r/VEO3: “reference materials for every person, place and thing” ([thread](https://www.reddit.com/r/VEO3/comments/1qjaaaj/struggling_with_google_flow_consistency_guardrail/)). |
| 4 Agente ativo + settings | **Confirmado** | Oficial: ligar Agente no prompt box; defaults de imagem/vídeo; **Confirm before generating** ([Help](https://support.google.com/labs/answer/17093911)). Tutoriais: **Always** para não queimar crédito ao só brainstormar (More Tutorials). |
| 5 Agente cria refs que faltam | **Confirmado** | Agente gera imagens/vídeos e pode escolher modelo; anexar refs no chat ([Help](https://support.google.com/labs/answer/17093911)). Nano Banana / Pro para stills de consistência antes de Veo (Reddit r/VEO3 xPitPat; guia Nano Banana Cloud [2026-03](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana)). |
| 6 Refs + storyboard via Agente | **Confirmado com ressalvas** | Agente outline storyboards ([Help](https://support.google.com/labs/answer/17093911)). Comunidade: personagem tem de ser **entidade/Character pinado** (`@Nome` ou Character nativo), não só nome no texto — senão Nano Banana inventa rosto (More Tutorials). Grade 3×3 serve de cheat sheet; **não** alimentar a grade inteira como input de vídeo ([r/VEO3](https://www.reddit.com/r/VEO3/comments/1ui6suc/help_best_storyboardshotlist_to_video_prompt/)). |
| 7 Produção toda via Agente a partir do storyboard | **Confirmado com ressalvas** | Fluxo comunitário dominante: stills por painel → revisão → Frames/Ingredients-to-Video **1 cena por geração** → Scenebuilder. Pedir “um vídeo com todas as cenas da grade” costuma falhar (cortes/duplicatas) — alinhado à regra PQBR t146u. |
| 8 Prompt detalha modelo + formato + detalhes | **Parcial** | Defaults do Agente (ratio, modelo, xN) são o travamento confiável ([Help](https://support.google.com/labs/answer/17093911)). Sugerir modelo no pedido é ok (José t147u). **Não** redescrever cabelo/roupa já presentes na ficha — causa drift ([DreamDrive](https://www.dreamdrive.ai/learn/google-labs/flow-ingredients-and-scenebuilder-consistency/), [Versely](https://www.versely.studio/blog/versely-ai-movie-maker-multi-scene-storyboard-workflow-2026)). Detalhar: ação, câmera, luz, restrições (lips closed), formato. |

---

## 3. Lacunas / passos que faltam no rascunho do José

1. **Instruções para o Agente (constituição do projeto)** — estilo flat, elenco, “lips closed”, sem texto na imagem, 9:16, o que evitar. Oficial + Reddit “Ultimate Guide” (r/ThinkingDeeplyAI / r/promptingmagic).
2. **Characters nativos do Flow** (`@Nome`) além de Element/Ingredient — entidade reutilizável com voz/imagem ([Help Characters](https://support.google.com/flow/answer/16935308)).
3. **Confirmar antes de gerar = Sempre** (já no PQBR; reforçar no checklist).
4. **Ordem estrita: fichas → storyboard de stills → revisão humana → vídeo.** Não pular revisão (`imagens_revisadas`).
5. **1 painel / 1 ação / 1 clipe** — nunca grade multi-painel como input de vídeo; nunca 3 ações no mesmo prompt de 8 s ([r/GoogleFlow](https://www.reddit.com/r/GoogleFlow/comments/1u1ayrs/things_i_wish_i_knew_before_wasting_50/), DreamDrive).
6. **Ingredients limpos** — fundo neutro, 2–3 refs por shot (personagem + objeto + estilo), descritor curto fixo (“a menina de camiseta rosa”), sem redescrever aparência.
7. **Collections + naming** — `S01_…`, pastas References / Storyboard / Finals; Agente pode renomear/agrupar ([Help](https://support.google.com/flow/answer/16935308)).
8. **Scene matrix** — tabela cena × propósito × personagem × local × câmera × status (Reddit Ultimate Guide).
9. **2 variantes nas stills de personagem**, escolher a melhor antes de animar (DreamDrive).
10. **Frames-to-Video** para start frame aprovado; Ingredients-to-Video para âncora de identidade; Scenebuilder só depois dos clipes bons.
11. **Limites de crédito / quota do Agente** — queries do Agente têm limite diário (não cobram crédito); mídia gerada pelo Agente **cobra** crédito de Flow ([Help Agent](https://support.google.com/labs/answer/17093911)).
12. **Estilo constante** — mesma frase de estilo / mesma ficha de estilo em todo o episódio.

---

## 4. Contradições / nuances

| Tensão | Resolução recomendada PQBR |
|---|---|
| “Prompt com todos os detalhes” vs “não redescrever a ficha” | Detalhar **ação + câmera + luz + restrições + formato/modelo sugerido**; aparência vem da ficha pinada. |
| Agente escolhe o modelo vs prompt força o modelo | Defaults do projeto = Nano Banana Pro (imagem) / Omni Flash (vídeo); o pedido **sugere** e o Agente resolve (padrão José t147u). Se o Agente propor modelo que gasta crédito sem necessidade → parar e avisar José. |
| Storyboard grade vs painéis individuais | Grade ok para planejamento/cheat sheet; produção = painéis 9:16 separados. |
| Ingredients Veo 2 vs Veo 3 / Omni | UI muda; método (refs limpas + 1 ação) permanece. Omni/Gemini Flash citado na comunidade para melhor preservação de identidade/voz — validar na UI atual antes do piloto. |
| “Tudo via Agente” vs controle fino | Agente orquestra; se o Character não for pinado automaticamente, **repedir com Character anexado** (More Tutorials). |

---

## 5. Processo recomendado (numerado) — proposta PQBR

1. **Projeto novo** `PQBR-EPxxxx-slug` (nunca misturar episódios).
2. **Ligar Agente** → Settings: Confirm=**Sempre**; imagem `9:16` + `🍌 Nano Banana Pro` + x1; vídeo `9:16` + modelo barato padrão (Omni Flash) + x1.
3. **Gravar Instruções do Agente** (estilo flat stickman, lips closed, sem texto/marca, elenco do episódio, naming S0N).
4. **Cruzar roteiro × `banco-fichas/`** → listar PERS/AMB/OBJ/ANIM/SIT presentes e faltantes.
5. **Entregar fichas existentes** ao projeto (upload Element / Character / Ingredients; fundo limpo; recorte individual, não grade de catálogo).
6. **Pedir ao Agente as fichas que faltam** (só stills Nano Banana Pro) → entram no catálogo PQBR (`aguardando_ok_jose` / permanente conforme regra).
7. **Pedir storyboard** ao Agente com: fichas pinadas + prompts das cenas (JSON NotebookLM / slots SUBJECT/ACTION/CAMERA/ATMOSPHERE) + formato 9:16 + sugestão de modelo de still.
8. **Separar painéis** S01..S0N em 9:16; Collections `Referencias` / `Storyboard` / `Cenas`.
9. **Revisão humana** (`imagens_revisadas`) — José ou portão automatizado; sem OK, sem vídeo.
10. **Produzir clipes via Agente**, 1 cena por vez: Ingredients/Character + start frame; prompt só de movimento; lips closed; sem grade.
11. **Scenebuilder** só para montar clipes aprovados (Extend/Jump com parcimônia).
12. **Baixar** stills/clipes para o repo/Drive com nomes canônicos; seguir para motion (MG-05).

---

## 6. Template de prompt (best practice)

### 6.1 Pedido ao Agente — fichas faltantes
```
Projeto: PQBR-EP1003-cafe-fraco. Formato 9:16. Modelo sugerido: Nano Banana Pro.
Estilo: cartoon 2D flat colorido stickman (Instruções do projeto).
Crie ficha de referência limpa (fundo creme, corpo inteiro, 2 olhos, sem texto) para:
- [ID catálogo] [descrição mínima do que a ficha NÃO mostra ainda]
Anexe/use as refs já no projeto: @PERS-menina-rosa, AMB-cafe, OBJ-caneca.
Confirme antes de gerar. Não gere vídeo.
```

### 6.2 Pedido ao Agente — storyboard
```
Com as referências pinadas (@PERS-…, @AMB-…, @OBJ-…), monte storyboard de N cenas 9:16.
Para cada cena use exactamente:
SUBJECT: [nome curto fixo da ficha, sem redescrever roupa/cabelo]
ACTION: [uma ação só]
CAMERA: [plano + movimento]
ATMOSPHERE: [luz/fundo já alinhado ao AMB]
CONSTRAINTS: lips closed; single continuous shot later; no text; no cuts in still
Entregue grade de planejamento + lista S01..S0N. Modelo still: Nano Banana Pro. Não anime ainda.
```

### 6.3 Pedido ao Agente — cena (após revisão)
```
Anime S0N. Referências: Character @… + start frame S0N + ingredients objeto/local.
MODELO sugerido: Omni 1.1 Flash (ou o barato padrão do projeto).
Formato 9:16, x1.
MOTION: [uma ação]. CAMERA: […]. lips closed, only blinking/breathing.
Single continuous shot, no cuts, no on-screen text, no subtitles.
```

Estruturas equivalentes na comunidade: SCAM (Subject/Composition/Action/Mood) [r/GoogleFlow]; SUBJECT/ACTION/CAMERA/ATMOSPHERE [Versely]; Cinematography+Subject+Action+Context+Style [Veo 3.1 Cloud].

---

## 7. O que generaliza para outras plataformas

- Projeto (ou pasta) **por episódio**.
- Bíblia visual / character sheet **antes** de gerar.
- Storyboard still barato → revisão → vídeo caro.
- Refs pinadas > texto repetido de aparência.
- 1 shot = 1 ação = 1 geração.
- Travas de estilo no “system/instructions” do projeto.
- Naming e collections/pastas.
- Modelo/aspecto nos defaults + prompt operacional enxuto.

Aplicável a Runway, Kling, Sora storyboard, Higgsfield (descartado no PQBR), etc., mudando só o nome da ferramenta de referência.

---

## 8. Fontes (top + complemento)

### Top 5 (usar no resumo)
1. Google Labs Help — Use the Google Flow Agent: https://support.google.com/labs/answer/17093911
2. Google Blog — 5 tips for using Flow: https://blog.google/innovation-and-ai/products/flow-video-tips/
3. DreamDrive — Flow Ingredients and Scenebuilder (2026-10-15): https://www.dreamdrive.ai/learn/google-labs/flow-ingredients-and-scenebuilder-consistency/
4. YouTube — I let the Google Flow AGENT Storyboard… (More Tutorials): https://www.youtube.com/watch?v=_0ZRdM1GCRQ
5. Reddit — Ultimate Guide to Google Flow Agent (r/ThinkingDeeplyAI): https://www.reddit.com/r/ThinkingDeeplyAI/comments/1tt25so/the_ultimate_guide_to_google_flow_agent_for_ai/

### Complemento
- Help Create videos / Ingredients / Characters: https://support.google.com/flow/answer/16353334 · https://support.google.com/flow/answer/16935308
- Nano Banana prompting (Cloud, 2026-03): https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana
- Veo 3.1 prompting: https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1
- Versely multi-scene storyboard 2026: https://www.versely.studio/blog/versely-ai-movie-maker-multi-scene-storyboard-workflow-2026
- Skywork storyboard→Veo in Flow: https://skywork.ai/blog/ai-video/how-to-convert-storyboard-images-to-veo-3-1-videos-in-flow
- YouTube Klever Nuts Agent→movie: https://www.youtube.com/watch?v=IaOekALLe4U
- Reddit r/GoogleFlow prompt mistakes: https://www.reddit.com/r/GoogleFlow/comments/1u1ayrs/things_i_wish_i_knew_before_wasting_50/
- Reddit r/VEO3 consistency: https://www.reddit.com/r/VEO3/comments/1qjaaaj/ · storyboard grid: https://www.reddit.com/r/VEO3/comments/1ui6suc/
- Pesquisas PQBR anteriores: `docs/pesquisas/flow-agente-e-nano-banana-pro-20261028.md`, `docs/pesquisas/flow-storyboard-por-cena.md`

---

## 9. Limites desta pesquisa

- Reddit corpo completo 403 via Jina/API; síntese via WebSearch.
- Twitter search 404 (GraphQL); sem posts X citados.
- Legendagens YT parciais (429 em alguns idiomas); EN ok para 2 vídeos.
- Features Ingredients/Extend/Jump variam por modelo na UI — revalidar no Camofox no piloto EP1003.
