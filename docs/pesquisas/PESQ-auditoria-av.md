> **t516 (José, 24/10/2026):** sem API Google (Gemini/Veo/Omni, inclusive free tier). Os trechos abaixo que dependem de API estão descartados.

> ⛔ **PESQUISA / REFERÊNCIA DE PRÉ-CONSTRUÇÃO: AGENTES NÃO CONSULTAM SEM APROVAÇÃO EXPLÍCITA DO JOSÉ (t287).** Pode conter premissas superadas que, mal interpretadas, iriam parar em produção. As regras válidas estão em `docs/REGRAS.md`.

> Nota: cita a premissa antiga de 60–80 s, SUPERADA por t271 (15 s a 3 min, alvo ~50 s).

# Pesquisa: como a comunidade e a indústria auditam vídeo gerado por IA antes de publicar

Data: 08/10/2026. Pesquisa feita só na web, sem compras, cadastros ou postagens.
Escopo: auditor pré-publicação do canal Porquê BR (Shorts 9:16, 60–80 s, bonecos palito brancos da bíblia visual, vídeos gerados pelo NotebookLM Video Overviews).

Legenda: **[verificado]** = li na fonte citada. **[relato]** = relato de usuário ou blog, não reproduzido por nós. **[estimativa]** = conta nossa. **[incerto]** = não consegui confirmar.

---

## 1. Resumo executivo

1. **Quem faz isso em produção** separa o trabalho em duas partes. Código barato roda primeiro (ffmpeg, silêncio, quadros pretos, formato). Depois um juiz multimodal recebe **quadros amostrados e o roteiro em texto** e aplica uma rubrica fechada, com limiar de aprovação. Exemplos: o blog Gurdharam (5 quadros e o roteiro para o Gemini Flash, corte em 85/100), o repo `video-factory` (8 a 12 quadros no gate final) e o `reelforge`. **[verificado nas páginas]**
2. **Os erros que vimos no Gemini têm causa documentada:**
   - No modo padrão, o vídeo é amostrado a **1 quadro por segundo**, o áudio é processado a **1 Kbps, mono**, e o carimbo de tempo é inserido **a cada segundo**. A própria documentação avisa que ação rápida pode perder detalhe. **[verificado, doc oficial]**
   - Isso explica o timestamp impreciso e boa parte do áudio "inventado".
   - O benchmark AVHBench (ICLR 2025) mostra que dar áudio e vídeo juntos **piora** a alucinação cruzada entre os dois, e que dar texto (legenda ou transcrição) melhora. **[verificado no resumo do paper]**
3. **Recomendação central:** não deixar o modelo "ouvir" nem "achar o timestamp".
   - O código entrega a transcrição do Whisper, já com tempos, mais os quadros-chave por cena, já com tempos.
   - O LLM responde perguntas fechadas de sim ou não, por cena.
   - O **código** calcula a gravidade a partir dessas respostas. O LLM nunca dá a gravidade direto.
   - Loop, CTA, nomes, corte de fala e end card ficam 100% fora do LLM.
4. **Contra a oscilação de gravidade:**
   - Rodar mais de uma vez e decidir por maioria. Divergência vira **REVISÃO** (José), e não aprovação.
   - Usar âncoras **mistas** nos exemplos. Com âncoras uniformes, o modelo junta todas as dimensões numa nota só (o "efeito halo", relatado no Reddit).
   - Opcional: um júri de modelos diferentes, Gemini mais Qwen (o paper PoLL mostra menos viés com um painel diverso).
5. **Identidade do personagem:** CLIP e DINOv2 contra a referência **correlacionam mal** com o julgamento humano em personagem de desenho. Na tabela do paper CHARIS, a correlação com humanos em estilo cartoon fica entre 0,07 e 0,20 para CLIP e entre 0,14 e 0,34 para DINOv2, contra 0,39 a 0,50 do método por atributos. O que funcionou melhor foi um VLM respondendo **atributo por atributo** (tipo, estilo, atributos, transformação). Isso casa com a nossa bíblia: cabeça branca, sem roupa, olhos de ponto, acessórios.
6. **Custo:**
   - Toda a camada determinística roda em CPU, de graça.
   - A camada LLM cabe no **free tier da Gemini API**. A página de preços lista o Gemini 3.8 Flash com input e output "Free of charge". Os limites de RPM e RPD não são publicados como número fixo; aparecem no AI Studio.
   - No free tier, **o conteúdo é usado para melhorar os produtos do Google**. É um ponto de decisão para vídeos ainda não publicados.
   - O Qwen Chat web serve como 2º juiz gratuito, mas sem API gratuita confirmada.
   - Modelos locais que veem áudio e vídeo juntos (Qwen3-Omni) **não cabem** num servidor modesto: o model card pede ~108 GB de GPU para 60 s de vídeo.

---

## 2. Arquitetura recomendada para o nosso caso

### 2.1 Fluxo

```
master.mp4
  │
  ├─ Camada 0 (CPU, grátis, determinística)
  │    ffprobe (9:16, duração) · silencedetect · EOF dBFS · freezedetect
  │    faster-whisper (pt, word_timestamps) → transcrição com tempos
  │    PySceneDetect (AdaptiveDetector) → cenas + 1 quadro-chave no meio de cada cena
  │    OCR (RapidOCR/Tesseract) nos quadros-chave e na faixa do end card
  │
  ├─ Camada 1 (CPU, grátis, texto puro)
  │    CTA / nomes / loop: regex + similaridade (rapidfuzz/jiwer) contra o roteiro/contrato
  │    loop semântico: LLM SÓ-TEXTO (1ª frase × última frase da transcrição), 2 rodadas
  │
  ├─ Camada 2 (LLM multimodal, free tier)
  │    por CENA: quadro-chave + imagem de referência do elenco + trecho da transcrição daquela cena
  │    perguntas fechadas (JSON): cabeça branca? roupa? pele colorida? olhos de ponto? acessório X?
  │                               3D/realista? nº de personagens? imagem ilustra a fala? texto legível?
  │    2 rodadas (3ª se divergir) · opcional 2º juiz (Qwen) nas cenas em dúvida
  │
  └─ Decisão (código)
       tabela atributo→gravidade (LEVE/GRAVE) definida pelo José na t222
       qualquer FAIL determinístico → FAIL
       GRAVE confirmado em 2 de 2 rodadas → reprova
       divergência entre rodadas ou entre juízes → REVISÃO (José)
       só LEVE → aprova_com_ressalva
```

A ideia de **PASS / REVIEW / FAIL** com a etapa barata primeiro aparece pronta no `ComfyUI-QualityGate`. Lá a etapa VLM é deliberadamente desligada até provar ganho num conjunto rotulado (20 a 30 PASS e 20 a 30 FAIL). **[verificado no README; repo com 0 estrelas, usar só como padrão de projeto]**

### 2.2 Cada checagem e o método mais barato que é confiável

| Checagem | Método recomendado | Custo | Por que assim |
|---|---|---|---|
| **Identidade** (bíblia visual) | Quadro-chave por cena (PySceneDetect) mais a referência do elenco. O VLM responde um checklist de **atributos** (sim/não/incerto), e o **código** mapeia cada atributo para LEVE ou GRAVE. 2 rodadas; divergência vira REVISÃO. Indício extra só para triagem: saturação de cor na região do boneco, para pegar pele ou roupa colorida **[hipótese nossa, não testada]** | Grátis (free tier) | O CHARIS mostra que decompor em atributos supera CLIP/DINOv2 em desenho. Com o código decidindo a gravidade, a oscilação "leve na A, grave na D" para de mudar o veredito |
| **Texto–imagem** | Por cena: o trecho da transcrição do Whisper que cai naquela cena mais o quadro-chave. Pergunta: "a imagem ilustra esta fala? sim/não/parcial". Cena sem personagem é válida se ilustra a fala (regra da t222) | Grátis | Damos o texto em vez do áudio, o que evita a alucinação cruzada (AVHBench) |
| **Dinamismo / "só slide"** | `ffmpeg freezedetect` + número de cortes do PySceneDetect + diferença média entre quadros. O LLM não entra | Grátis | A diferença de quadros e o score de cena já mediram isso no nosso teste. Falta calibrar o limiar |
| **Legibilidade** | OCR nos quadros-chave (texto cortado ou ilegível = baixa confiança ou texto truncado na borda). O VLM só confirma os casos marcados, com resolução de mídia alta | Grátis | O OCR é determinístico. O VLM com resolução alta só entra no caso duvidoso |
| **Nome na legenda** | OCR mais a lista de nomes e aliases | Grátis | Separa "nome escrito no quadro" de "nome falado". No vídeo B, o "Seu Valdemar" que o Gemini disse ser falado pode ter vindo do quadro **[a confirmar com OCR]** |
| **CTA** | Regex com a lista fechada nos últimos 8 s da transcrição (já existe) | Grátis | 8/8 no nosso teste |
| **Loop** | (a) similaridade lexical entre a última frase e a ponte do roteiro (`rapidfuzz`/`jiwer`); (b) LLM **só texto**: "a última frase completa a primeira?", 2 rodadas | Grátis | O Gemini com vídeo errou o loop e citou a frase removida. Com texto puro do Whisper, ele não tem como "ouvir" o que não existe |
| **End card** | Ler o texto da faixa por OCR e/ou hash perceptual (`imagehash`) numa região fixa, em vez do diff global | Grátis | O template por diff falhou (faixa 5,36, nenhuma detecção) |
| **Corte de fala** | Fim da última palavra (Whisper word timestamps) vs. duração, mais EOF dBFS, mais VAD (`silero-vad`) no último segundo | Grátis | Combina 3 sinais. Nenhum deles sozinho reprova (o checklist v2 já diz isso) |
| **Tom** | LLM **só texto** sobre a transcrição contra o contrato editorial, com âncoras mistas, 2 rodadas. Opcional: Qwen como 2º juiz | Grátis | Tom é texto. Mandar vídeo só aumenta o risco de alucinação |

### 2.3 Onde rodar a camada LLM

| Opção | Custo | Prós | Contras |
|---|---|---|---|
| **Gemini API, free tier (chave do AI Studio)** | Grátis. Limites visíveis no AI Studio, não publicados como número fixo | Controla `fps` (por exemplo 2–3), `media_resolution`, `thinking_level` e recorte de trecho, e devolve JSON. Aceita 10 vídeos por requisição. É o caminho oficial, sem automação de navegador | **Free tier: os dados são usados para melhorar os produtos do Google** (página de preços). Criar a chave é decisão do José **[não feito]** |
| Gemini API paga | **[estimativa]** Gemini 3.8 Flash a US$0,75/M tokens de input até 31/12/2026. Um vídeo de 70 s em resolução alta dá ~300 tok/s, perto de 21 mil tokens, ou ~US$0,016 por chamada, mais o output. Com 4 vídeos/dia × 3 chamadas, fica em centavos de dólar por dia | Sem uso dos dados para treino. Limites maiores | Exige billing. A partir de 23/03/2026, contas novas podem cair em pré-pago |
| **AI Studio Playground com o plano Pro do José** | Já pago | Cota maior que o free tier. Tem os mesmos controles (nível de pensamento, resolução de mídia) | Só a interface web; o plano não vale para chamadas de API. Automatizar exige navegador |
| **Gemini web (app)** | Já pago (Pro) | Pro permite até 1 hora de vídeo somado por prompt (free: 5 min). Tem o toggle "Extended thinking / Complex problem solving", que está virando níveis low/medium/high em outubro de 2026 (9to5Google) | Não dá para fixar fps, resolução nem JSON. A amostragem padrão continua a 1 fps. Automatizar a interface é frágil |
| **Qwen Chat web (chat.qwen.ai)** | Grátis (rate-limited) **[limites exatos incertos]** | 2º juiz de família diferente. A doc da QwenCloud diz que Qwen3.6-Plus aceita vídeo de até 2 h/2 GB e tem modo "thinking" controlável. Há relatos de um toggle Thinking na interface web **[confirmar na UI]** | Sem API gratuita confirmada. Política de dados do chat não revisada **[incerto]** |
| Local: Qwen3-VL 2B/4B (GGUF, llama.cpp, CPU) | Grátis | Sem envio de dados. Serve para perguntas sim/não **por quadro** | O llama.cpp padrão não lê vídeo nativo; é preciso mandar quadros como imagens (relato r/LocalLLaMA). Velocidade em CPU **[incerta]**. Qualidade abaixo do Gemini |
| Local: Qwen3-Omni-30B-A3B (áudio + vídeo) | Hardware inviável | Aceita áudio e vídeo juntos e entende português | O model card pede ~108 GB de GPU (BF16) para 60 s de vídeo |

---

## 3. Ferramentas e abordagens

| Nome | Link | Custo | O que resolve | Maturidade / manutenção | Risco |
|---|---|---|---|---|---|
| Gemini API, video understanding | https://ai.google.dev/gemini-api/docs/video-understanding | Free tier, ou pago | Juiz multimodal com fps, recorte e resolução configuráveis; modo "agentic" no 3.8 Flash | Oficial, atualizado em 06/10/2026 | 1 fps por padrão; áudio a 1 Kbps; dados usados para treino no free tier |
| Gemini API, preços | https://ai.google.dev/gemini-api/docs/pricing | — | Confirma que 3.8 Flash e 3.5 Flash-Lite têm free tier | Oficial | Preço dobra em 01/01/2027 (3.8 Flash) |
| Gemini API, rate limits | https://ai.google.dev/gemini-api/docs/rate-limits | — | Onde ver a cota (no AI Studio) | Oficial | Limites não publicados como número fixo |
| Planos Google AI no AI Studio | https://ai.google.dev/gemini-api/docs/google-ai-plans | Plano Pro já existente | Cota maior no Playground | Oficial | Só vale na interface do AI Studio |
| Gemini Apps, upload de arquivos | https://support.google.com/gemini/answer/14903178 | — | Limites de vídeo no app (Pro: 1 h; free: 5 min; 10 arquivos/prompt) | Oficial | — |
| Mudança de modelos no app Gemini | https://9to5google.com/2026/10/03/gemini-model-limits-oct-26/ | — | Toggle "Extended thinking" migrando para low/medium/high; Deep Think no AI Pro | Imprensa, 03/10/2026 | Interface muda de nome (como José avisou) |
| Qwen: entendimento de áudio e vídeo | https://docs.qwencloud.com/developer-guides/speech/multimodal-speech | API paga **[cota grátis incerta]** | Omni aceita vídeo com áudio; recomenda ≤2–4 min para análise fina | Oficial | O Omni-Flash tem teto de 150 s por vídeo |
| Qwen: modelos de visão | https://docs.qwencloud.com/developer-guides/getting-started/vision-models | idem | Vídeo de até 2 h no Qwen3.6-Plus | Oficial | — |
| Qwen3-VL (open source) | https://github.com/QwenLM/Qwen3-VL | Grátis | VLM local, aceita vídeo por fps ou número de quadros | Ativo | Pede GPU para vídeo inteiro; em CPU, só quadros |
| Qwen3-Omni-30B-A3B | https://huggingface.co/Qwen/Qwen3-Omni-30B-A3B-Instruct | Grátis (pesos), GPU cara | Áudio e vídeo nativos | Ativo, Apache 2.0 | ~108 GB de GPU para 60 s |
| VideoScore2 | https://github.com/TIGER-AI-Lab/VideoScore2 · https://huggingface.co/TIGER-Lab/VideoScore2 | Grátis, precisa de GPU (base Qwen2.5-VL-7B) | Nota de qualidade visual, alinhamento texto–vídeo e física | Acadêmico, 49★ | Treinado para T2V realista, não para o nosso estilo; acurácia de 44% no próprio benchmark |
| VBench | https://github.com/Vchitect/VBench | Grátis, GPU recomendada | Métricas: subject_consistency (DINO), dynamic_degree (RAFT), aesthetic | 1,6k★, acadêmico | Mede consistência quadro a quadro, não contra a nossa referência |
| EvalCrafter | https://github.com/evalcrafter/EvalCrafter | Grátis | 17 métricas T2V | Acadêmico (CVPR 2024) | Pesado; pouco útil para palito 2D |
| T2V-CompBench | https://github.com/kaiyuesun98/t2v-compbench | Grátis | Composição (objetos, ações, contagem) | Acadêmico (CVPR 2025) | Idem |
| CHARIS / "Beyond the Pixels" | https://arxiv.org/html/2511.08087v1 | — | Método: identidade por atributos e transformações via VLM; mostra CLIP/DINOv2 fracos em desenho | Paper de nov/2025 | Os próprios autores dizem que detalhes sutis ainda escapam |
| AVHBench | https://arxiv.org/html/2410.18325v2 · https://github.com/kaist-ami/AVHBench | — | Evidência de alucinação cruzada entre áudio e vídeo | ICLR 2025 | — |
| PoLL, "Replacing Judges with Juries" | https://arxiv.org/abs/2404.18796 | — | Júri de modelos diversos: menos viés, mais barato que 1 juiz grande | Paper 2024 | Testado em texto, não em vídeo |
| "The Coin Flip Judge?" | https://arxiv.org/abs/2606.13685 | — | Mede a instabilidade de juízes LLM; recomenda várias rodadas e voto (segundo o resumo, ~11 rodadas para 95% de concordância com o veredito de 50 rodadas) | Paper 2026 | Testado em pares de texto; o número não se transfere direto para o nosso caso |
| faster-whisper | https://github.com/SYSTRAN/faster-whisper | Grátis, CPU int8 | Transcrição pt com word timestamps (já em uso) | Ativo | — |
| WhisperX | https://github.com/m-bain/whisperX | Grátis | Alinhamento forçado por palavra; tem modelo de alinhamento pt (wav2vec2 XLSR pt) | Ativo | Mais pesado que o faster-whisper |
| aeneas | https://github.com/readbeyond/aeneas | Grátis | Alinhar texto conhecido com áudio | **Parado** (v1.7.3, 2017) | Instalação antiga |
| dido (port de aeneas em Go) | https://github.com/digitalbiblesociety/dido | Grátis | Mesmo uso, mantido | Pequeno | Pouco usado |
| Montreal Forced Aligner (pt) | https://github.com/MontrealCorpusTools/mfa-models/releases/tag/dictionary-portuguese%5Fmfa-v2.0.0a | Grátis | Alinhamento forçado pt | Ativo | Exagero para o nosso uso |
| PySceneDetect | https://www.scenedetect.com/docs/latest/api/detectors.html | Grátis, CPU | Cortes de cena e quadro-chave por cena (AdaptiveDetector) | Ativo (0.7.x) | Animação pode gerar cortes demais; calibrar `min_scene_len` |
| ComfyUI-QualityGate | https://github.com/git-geeky/ComfyUI-QualityGate | Grátis | Padrão PASS/REVIEW/FAIL, etapa barata primeiro, protocolo de calibração com conjunto rotulado | 0★, último push em 06/2026 | Copiar a ideia, não o código |
| video-factory | https://github.com/NesDevr/video-factory | Grátis (usa Gemini) | 4 gates de revisão Gemini; gate final com 8 a 12 quadros e regeneração | Projeto pessoal | — |
| reelforge | https://github.com/akira231097/reelforge | Grátis (usa Gemini) | Nota em 6 dimensões e gate de aprovação; caminho REGENERATE/USE_FALLBACK | Projeto pessoal | — |
| Gurdharam, "Multimodal Judge" | https://www.gurdharam.com/blog/multimodal-judge-ai-video-quality-gate | — | Pipeline de 3 camadas para 5 canais de Shorts: ffmpeg antes, juiz Gemini em 5 quadros mais o roteiro, corte em 85 | Blog | Sem dados de falso positivo ou negativo |

Ferramentas citadas sem página aberta por mim (existência conhecida, verificar versão antes de usar): `silero-vad` (https://github.com/snakers4/silero-vad), `rapidfuzz` (https://github.com/rapidfuzz/RapidFuzz), `jiwer` (https://github.com/jitsi/jiwer), `imagehash` (https://github.com/JohannesBuchner/imagehash), RapidOCR (https://github.com/RapidAI/RapidOCR), filtro `freezedetect` do ffmpeg (https://ffmpeg.org/ffmpeg-filters.html#freezedetect).

---

## 4. Alertas da comunidade

1. **O juiz "inventa" quando não consegue ver ou ouvir.**
   - r/GeminiAI: um usuário relata que o Gemini 3.6 Flash criou conteúdo e timestamps **depois do fim** de um vídeo (https://www.reddit.com/r/GeminiAI/comments/1vn4a5b/gemini_invented_content_past_the_end_of_the_video/).
   - Outro usuário relata que o 3.1 Pro inventou a transcrição de um áudio sem nenhum aviso (https://www.reddit.com/r/GeminiAI/comments/1utka8p/gemini_31_pro_making_up_completely_unrelated/).
   - Um blog conta que o Gemini fabricou o resumo de um vídeo do YouTube (https://georgesaoulidis.com/when-llms-fake-it-gemini-hallucinated-a-whole-youtube-summary/).
   - O conselho que se repete: transcrição por STT dedicado e checagem das citações contra o original. **[relato]** Bate com o que vimos: frase removida citada como presente e nome "falado" inventado.
2. **Efeito halo.** O autor de um avaliador gratuito de Shorts com 3 juízes Gemini viu as 6 dimensões correlacionadas entre 0,72 e 0,83. A causa eram exemplos de referência uniformes (tudo bom ou tudo ruim). A correção é usar exemplos **mistos**, como "gancho bom, final ruim" (https://www.reddit.com/r/ArtificialInteligence/comments/1smkt0e/built_a_free_ai_grader_for_youtube_shorts_then/). **[relato]** Para nós: os exemplos da rubrica não podem ser só "tudo ok" e "tudo grave".
3. **O VLM serve para detectar, não para medir.** Em r/LLMDevs, um comentário diz que o modelo foi "confiável para sinalizar e inútil para convergir": acerta que está errado e erra por quanto (https://www.reddit.com/r/LLMDevs/comments/1w0xmju/i_built_a_validated_pipeline_for_generating_short/). **[relato]** Para nós: tempo, contagem e gravidade numérica ficam com o código.
4. **CLIP/DINOv2 contra referência não serve como gate de identidade em desenho.** Isso vem do paper CHARIS, não de relato. Serve no máximo como indício.
5. **Calibrar antes de confiar.** O QualityGate pede 20 a 30 exemplos rotulados por classe, sem os casos de fronteira, e só liga a etapa VLM se ela ganhar mais de 3 pontos de F1. Nosso gabarito hoje tem 4 a 8 vídeos, pouco para fixar limiar.
6. **Um juiz único oscila.** O "Coin Flip Judge" mede viradas de veredito entre rodadas e recomenda várias rodadas, voto e relatar a incerteza. O PoLL recomenda juízes de famílias diferentes.
7. **Canais faceless:** não publicar só para bater a cota de vídeos; manter revisão humana documentada; variar elementos de produção para não cair em "conteúdo inautêntico" (r/FacelessVideos: https://www.reddit.com/r/FacelessVideos/comments/1sq9478/how_to_avoid_demonetisation_with_faceless_ai/). **[relato]** Isso coincide com a regra que já temos: qualidade antes de 4 por dia.
8. **Modo agentic do Gemini.** Ele carrega "transcrição sob demanda" e economiza tokens em vídeo longo. Para clipe curto, a doc recomenda o modo estático quando cada quadro importa. Para nós: modo estático, com fps maior.

---

## 5. Próximos testes baratos (todos com as contas e a máquina que já temos)

| # | Teste | Custo | Critério de sucesso |
|---|---|---|---|
| 1 | **Variância:** rodar A (toalha) e D (loop quebrado) 5× cada no mesmo modelo e prompt, e contar quantas vezes a gravidade vira | Grátis (conta jvmendesjr) | Medir a taxa de virada. Se passar de 1 em 5, adotar 3 rodadas com voto |
| 2 | **Transcrição no lugar do áudio:** mandar ao Gemini os quadros-chave e a transcrição do Whisper, sem o vídeo, para B e D | Grátis | O "Seu Valdemar falado" e o "loop ok" desaparecem |
| 3 | **Identidade por atributos por cena:** PySceneDetect → quadro-chave → checklist JSON (cabeça branca, roupa, pele, olhos, acessório, 3D, nº de personagens) → código aplica a tabela LEVE/GRAVE da t222. Rodar em A, B, C, D | Grátis | A = ressalva, B/C = reprova, com o mesmo resultado em 2 rodadas |
| 4 | **Loop só texto:** última frase × ponte do roteiro (rapidfuzz/jiwer) mais um LLM só-texto em v1 e syn_f2 | Grátis | Separa v1 de syn_f2 nas 2 rodadas |
| 5 | **OCR** (RapidOCR) nos quadros-chave e na faixa do end card | Grátis, CPU | Detectar os 5 cards reais e o nome escrito no quadro do B |
| 6 | **2º juiz Qwen Chat** com o mesmo prompt dos testes 3 e 4, com Thinking ligado e desligado | Grátis | Concordância com o Gemini; registrar onde divergem |
| 7 | **Gemini API, free tier**, se o José autorizar criar a chave: `fps` 2–3, `media_resolution` alta, `thinking_level` alto, modo estático, saída JSON. Comparar com a interface web | Grátis (dados usados para treino) | Timestamps e gravidade mais estáveis que na web |
| 8 | **Heurística de cor** (saturação na região do personagem) em A vs. C | Grátis, CPU | Separar "pele/roupa colorida" de "palito branco" sem LLM |
| 9 | **`freezedetect` + número de cortes** para "só slide" | Grátis | Separar o explainer estático dos vídeos normais |
| 10 | **Aumentar o gabarito** para ≥20 aprovados e ≥20 reprovados (sintéticos mais reais), antes de fixar limiares | Tempo | Medir falso aprova e falso reprova com amostra decente |

Ordem sugerida: 2 → 3 → 4 → 1 → 5 → 6. Os testes 2 a 4 atacam exatamente as três falhas vistas: áudio inventado, gravidade instável e loop.

---

## Fontes consultadas, além das da tabela

- Reddit, r/LLMDevs: https://www.reddit.com/r/LLMDevs/comments/1w0xmju/i_built_a_validated_pipeline_for_generating_short/
- Reddit, r/ArtificialInteligence (efeito halo): https://www.reddit.com/r/ArtificialInteligence/comments/1smkt0e/built_a_free_ai_grader_for_youtube_shorts_then/
- Reddit, r/GeminiAI (alucinação depois do fim do vídeo): https://www.reddit.com/r/GeminiAI/comments/1vn4a5b/gemini_invented_content_past_the_end_of_the_video/
- Reddit, r/GeminiAI (transcrição inventada): https://www.reddit.com/r/GeminiAI/comments/1utka8p/gemini_31_pro_making_up_completely_unrelated/
- Reddit, r/LocalLLaMA (Qwen3-VL no llama.cpp com quadros): https://www.reddit.com/r/LocalLLaMA/comments/1ow0ss8/qwenqwen3vl4b_lmstudio_server_llamacpp_submitting/
- Reddit, r/comfyui ("filtrar em vez de forçar consistência"): https://www.reddit.com/r/comfyui/comments/1rylceb/instead_of_forcing_consistency_what_if_we_filter/ (só o título e o resumo da busca; a página não abriu)
- Reddit, r/StableDiffusion (SFace + DINOv2 como referência de personagem): https://www.reddit.com/r/StableDiffusion/comments/1vp0xct/character_consistency_via_cached_reference/ (só o título; o SFace é para rosto humano e não se aplica ao palito)
- Gemini, resolução de mídia: https://ai.google.dev/gemini-api/docs/media-resolution
- Gemini, thinking: https://ai.google.dev/gemini-api/docs/thinking

Limites desta pesquisa:
- As páginas do Reddit não abriram direto (bloqueio). Os trechos citados vêm do índice de busca.
- Não achei relato específico em r/aivideo, r/NewTubers ou r/PartneredYoutube sobre auditoria automática. Lá o padrão relatado é revisão humana.
- A cota gratuita exata do Qwen Chat e do free tier do Gemini **não foi confirmada**.
