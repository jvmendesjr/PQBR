# PESQUISA — extensões e scripts de geração em série (Flow / Meta Vibes) como referência de navegação

t529 · 24/10/2026 · aprovado por José. **Só estudo e registro.** Nenhuma extensão foi instalada, Flow, Vids e Vibes não foram abertos e a 9387 não foi tocada. As fontes foram lidas na web, nas páginas públicas: Chrome Web Store, GitHub e YouTube.

## 1. O que já existia registrado
- `docs/blueprints/modulo-producao-video/BLUEPRINT.md` §8, "Aprendizados do Darkplanner e das extensões":
  - Houve uma inspeção estática da extensão **DarkPlanner**, com os arquivos em `~/Workspace/extensoes/darkplanner/`.
  - O que aproveitar: fila e painel de produção com estados, progresso, tentativas e logs.
  - O que não copiar: o `manifest.json` com permissões amplas, os scripts no mundo `MAIN`, a interceptação de requests, os seletores remotos e as filas simultâneas.
  - As extensões ficaram registradas como "**referências conceituais**, não componentes".
- `BLUEPRINT.md` e `docs/blueprints/modulo-producao-video/ROADMAP.md`:
  - proíbem instalar ou executar extensões, reproduzir endpoints privados, interceptar requests ou contornar CAPTCHA e quotas;
  - preveem `FlowAdapter`/`PlatformProfile` "somente pela UI oficial via Camofox";
  - preveem um catálogo versionado de overlays, storyboard por cena com continuidade e os estados `PAUSED_QUOTA`, `PAUSED_AUTH`, `PAUSED_SITE_CHANGE` e `PAUSED_REVIEW`;
  - preveem o piloto de 1 cena antes de 5 a 7 cenas.
- **O que faltava:** nenhum documento cobria a **geração de storyboard em série** a partir de uma lista de prompts vinda do NotebookLM, com nomes e ordem determinísticos, nem um catálogo de ferramentas atuais da comunidade para Flow e Vibes. Também não havia nada sobre o Google Vids nesse sentido. Este documento preenche essa lacuna.
- Conversa YT-LLM: ver §1.1 (t530).

### 1.1 Conversa YT-LLM (agente do canal Porquê BR, 22/10/2026) — achados úteis
Fonte: conversa YT-LLM (transcript e arquivos de trabalho desse agente, 22/10/2026). Não houve discussão sobre **extensões** de Chrome para geração em série, nem sobre Whisk ou Meta Vibes. O que houve, e serve aqui:
- **GUÍA VOX — Motor de Producción** (fonte colada pelo José no caderno do YT-LLM): é um wizard que leva de roteiro a **beats** e daí a **um arquivo `.txt` de prompts de imagem**, depois a um **prompt de animação universal**, tudo no **Google Flow** (modelo de imagem, depois modelo de vídeo). As regras que interessam ao manifesto de série:
  - 1 beat = 2,5 a 3 s de narração (5 a 7 palavras a 2,2 palavras/s), com uma ideia visual por beat; todos os beats viram prompts, **em ordem**;
  - formato do arquivo: **um bloco por prompt, separados por uma linha em branco, SEM numeração nem rótulos** ("qualquer número solto vira prompt e gera imagem lixo"). É exatamente o formato de entrada das filas de extensão (seção 2);
  - cada bloco é **autossuficiente**: o bloco de estilo completo vai repetido em todo prompt, o que garante a consistência;
  - nome `[tema]-prompts.txt`, dividido em arquivos de no máximo 60 prompts;
  - animação: **o mesmo prompt universal para todas as imagens** (a imagem é o quadro final; câmera travada; 70 % montagem e 30 % "pôster vivo"; clipes de 5 ou 8 s).
- **Fábrica de Shorts en Gemini Notebook** (canal IATOP, https://www.youtube.com/@Inteligencia-Artificial-IATOP): etapa 4.2, que pede ao NotebookLM um prompt para o Flow/Nano Banana gerar **1 imagem com 6 vinhetas 9:16** para pré-visualizar o estilo antes da série. Serve como "canário de estilo" barato antes do storyboard completo.
- **Lições do YT-LLM que valem aqui**:
  - o estilo papercut foi **abortado** no NotebookLM por falta de zoom e movimento nos recortes;
  - "storyboard" **não** funciona como motor visual *dentro* do NotebookLM (o Video Overview ignora o storyboard). Isso reforça que o storyboard em série deve ser feito no Flow, e não no NotebookLM;
  - assets nomeados `ASSET_<tipo>_<nome>-v<N>` (ex.: `prop-plugue-3pinos-v1`), personagem stickman travado, descrever 2 a 4 movimentos críticos por beat;
  - cotas do NotebookLM por capacidade (planejar o lote);
  - nenhuma extensão instalada.
- **Cobertura da busca**:
  - lidas as posições ~502 a 3099 da conversa (amostragem com lacunas pequenas). As posições 0 a 501 não foram lidas;
  - lidos os arquivos de trabalho do agente em `/workspace/yt-llm-bot/` no box: `notebooklm-video-short-briefing.md`, `sources/guia-vox.md`, `sources/fabrica-shorts.md`, `ops/*.md`.

**Impacto no §5:**
- `ManifestoSerie` ganha os campos `bloco_estilo` (repetido em todo prompt), `segundos_por_beat` e `prompt_animacao_universal`;
- ao exportar o `.txt` para revisão humana, usar o formato de blocos separados por linha em branco, sem números;
- a ordem e o nome ficam só no manifesto e no nome do arquivo (`<ep>_c<NN>_...`).

## 2. Ferramentas encontradas (fontes reais)
| Ferramenta | Alvo | Lógica relevante | Fonte |
|---|---|---|---|
| VEO Automation Free | Flow | Fila de prompts (linha em branco, TXT ou CSV); estados Queued → Reviewing → Generating % → Completed; renomeia arquivos com **índice do prompt + texto**; pausa/retoma; cooldown ao detectar "unusual activity"; pausa "humana" proporcional ao tamanho do prompt; delay aleatório; frame-to-video e ingredients 1–6 | https://chromewebstore.google.com/detail/free-veo-automation-bulk/lnadnaegfljibehcgclljdefggflfpkn |
| VEO Automation (Queue, Batch & Auto-Download) | Flow | Cria o projeto, ajusta as opções, digita cada prompt, espera, baixa e renomeia numa pasta nomeada | https://chromewebstore.google.com/detail/google-flow-automation-%E2%80%94/inmkimakahiennggieafocbmfjlmfbhn |
| Flow Queue | Flow | Importa TXT, CSV, TSV ou JSON; imagem de referência por prompt; controla pasta e nome do arquivo | https://chromewebstore.google.com/detail/flow-queue-auto-veo-nano/jgfmgcoonfeifpbaciimdjeldpmjgoli |
| Google Flow Automator | Flow | CSV ou Sheets, **planejamento de storyboard**, imagens de referência, auto-download | https://chromewebstore.google.com/detail/google-flow-automator-nan/jincmbkbdocdfgljlmoididhodhenbgm |
| VeoLab | Flow | Fila Veo 3.1 Lite, Fast e Quality, mais Omni Flash | https://chromewebstore.google.com/detail/veolab-auto-veo-nano-bana/ndhmfcpphkhjbkmlbpoajddagggdheck |
| AutoFlow | Flow | Queue Manager com retries; "Studio" que mantém personagens entre shots e **encadeia o último frame** | https://www.auto-flow.studio/ |
| gflow-cli (open source) | Flow | Playwright headed com perfil persistente; `character create`; `video chain` por **manifesto JSONL** (I2V do último frame); `run --config batch.json` com `"ref": "batch:N"`; grava o item **antes** de submeter; falha rápido em **drift de seletor (exit 23)** sem reenviar; seletores por cascata de rótulos acessíveis | https://github.com/ffroliva/gflow-cli · https://github.com/ffroliva/gflow-cli/blob/develop/docs/DEBUGGING.md |
| google-flow-browser-mcp | Flow | `selectors.map.json` populado por `discover-ui`; `safe-actions`; `account-check`; fila de um job por vez; `grid-architect` para shots em lote | https://github.com/TMSSS05/google-flow-browser-mcp/tree/main |
| browser2api | Flow | `selectors.py` e `enums.py` por plataforma (modelos, orientação); fluxo login → configurar → preencher → enviar → poll do DOM → baixar | https://github.com/Rabornkraken/browser2api |
| Auto Vibes × G-Labs (Auto-MetaAI) | Meta Vibes | Uma linha por prompt; referências por papel (Character, Scene, Style; Start/End frame); distribuição **Chain 1:2→2:3**; biblioteca que casa imagens por nome (`shot1_start`); **subpasta por tarefa** e presets de nome; sufixo `_720p`; "Retry failed" | https://github.com/duckmartians/Auto-MetaAI · https://duckspace.net/en/auto-vibes/ · https://chromewebstore.google.com/detail/auto-vibes-x-g-labs-autom/bchhcfjoloinebjpbfklckgohpjehdmf |
| Vibes AutoFlow | Meta Vibes | Setup único "Pick" do campo de prompt, do botão Generate e do Extend; auto-extend para 10, 15 ou 20 s; retry de 1 a 3; delay aleatório; 9:16; avisa que mudança de layout exige refazer o setup e que pode violar os ToS | https://chromewebstore.google.com/detail/vibes-autoflow/lgehciilaipbbncpdjljkahknfeefdhf |
| Vibes Automation | Meta Vibes | Modo **Concat** (encadeia prompts numa sequência mais longa); pastas por projeto | https://chromewebstore.google.com/detail/vibes-automation-auto-met/mikmoieklgpbgikeemkfffncmcmnhhab |

**Tutoriais**
- Storyboard Studio nativo do Flow: Tools → Prompting → Storyboard Studio. Cola-se o roteiro e o "Autofill" gera personagens, locações, props e cenas, que depois viram start frames. https://www.youtube.com/watch?v=Urxl_ivCei8
- Travar rosto e voz com Flow Characters: https://www.youtube.com/watch?v=x7aqsAtwAVE
- Automação e retry ("reuse prompt"): https://www.youtube.com/watch?v=3kOLDkWXRk4
- Usar a tag do personagem em todo shot para manter a consistência: https://medium.com/@4vibe.group/how-to-make-a-full-cartoon-in-google-flow-storyboard-studio-pro-workflow-b1b3d964dde1

**Google Vids:** não achei extensão de série. Ele fica como rota manual-assistida, a mapear do zero.

## 3. Lógica que vale copiar (no Camofox, sem extensão)
1. **Manifesto de série como fonte da verdade**: JSONL ordenado (`cena`, `ordem`, `prompt`, `refs`, `modelo`, `proporcao`), gravado **antes** de cada submissão, para nunca reenviar sem saber.
2. **Duas fases**:
   - (a) storyboard de imagens, uma por cena, com personagem e estilo fixos (Character/Style, tag do personagem em todo prompt);
   - (b) vídeo por cena usando a imagem como start frame, com a opção "chain", em que o último frame vira o início da próxima.
3. **Nome determinístico**: `<episodio>_c<NN>_<tipo>_<modelo>_<v>.ext`, com índice zero-padded e hash do prompt no manifesto, nunca o texto livre no nome.
4. **Mapa de UI versionado por plataforma** (`selectors`/`PlatformProfile`):
   - cascata de rótulos acessíveis em vez de CSS frágil;
   - catálogo de modais conhecidos (privacidade, cota, "unusual activity");
   - uma regra por modelo (durações, proporções, refs aceitas).
5. **Máquina de estados por item**: `fila → revisando → gerando → baixado → validado | falhou`. O retry é limitado e o drift de seletor vira `PAUSED_SITE_CHANGE` sem reenviar.
6. **Ritmo humano**:
   - um item por vez (concorrência 1, como a fila notebooklm);
   - pausa proporcional ao prompt mais um delay aleatório;
   - cooldown ao ver aviso de atividade incomum, e ele vira `PAUSED_QUOTA`/HOLD, nunca insistência.
7. **Agrupamento por episódio**: uma pasta por episódio e uma linha por cena, com "rerodar só as que falharam".

**Não copiar:**
- chamadas a APIs privadas (o gflow-cli usa `aisandbox`/`batchexecute`);
- interceptação de rede;
- seletores baixados de servidor remoto;
- concorrência maior que 1;
- spoofing de fingerprint;
- contorno de CAPTCHA.

## 4. Riscos
- **Termos de uso**: as próprias ferramentas avisam que automatizar pode violar os ToS do Google e da Meta. O risco é da conta (juniormoedavirtual) e só se mitiga com volume baixo, ritmo humano e parada em qualquer aviso.
- **Detecção**: a ação humanizada reduz o risco mas não o elimina. Não falsificar fingerprint nem usar proxy.
- **Mudança de UI**: todas as ferramentas quebram quando a UI muda. Por isso o mapa de UI é versionado, há um canário de um item e a regra "falhar rápido".
- **Custo**: cota paga só é gasta no vídeo; o storyboard de imagens costuma ser barato ou grátis (informação do gflow-cli, a confirmar na conta).
- **Direitos e uso**: baixar só o que a UI oficial permite.

## 5. Encaixe no PQBR
- **Contratos novos** (Pydantic, `VERSOES` 1.0.0, a criar no passo R2 do roadmap):
  - `CenaStoryboard` (ordem, prompt, refs, hash);
  - `ManifestoSerie` (episódio, plataforma, modelo, cenas ordenadas, regra de nome);
  - `ResultadoCena` (estado, arquivo, sha256);
  - `PedidoDecisaoVideo` (HOLD).
- **Origem**: o NotebookLM gera os prompts por cena a partir do `RoteiroShort`, e o Diretor de Arte fixa o personagem e o estilo (`config/estilo_visual.json`).
- **Porta**: `GeradorVideo.gerar(manifesto) -> list[ResultadoCena]`, com os adaptadores `FlowCamofox`, `VidsCamofox` e `VibesCamofox` sobre `NavegadorIdentidade` (ADR-012). Cada um tem um `PlatformProfile` versionado e é executado por uma activity no worker `camofox-pqbr`, com concorrência 1.
- **Cadeia**: Flow → Vids → Meta Vibes (t517). Se as 3 falharem → **HOLD** (decisão t529): o episódio é suspenso e o José recebe um pedido de decisão (Telegram), que ele responde por sinal do Temporal.
- O `EpisodioWorkflow` deixa de chamar `nlm_baixar_video`, que fica só como alternativa explícita.
