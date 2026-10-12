# Estilo 2D — referências (t430, 12/10/2026)

**Método:** fila `notebooklm-pqbr` (tipo `pesquisa`), caderno efêmero `Short - t430-estilo-2d` com persona canônica aplicada antes de tudo; 2 buscas web `add-research --mode fast` (global + BR) → 41 fontes importadas; 3 chats de conteúdo (+1 chat de teste "ok" para diagnosticar auth). Respostas do NotebookLM abaixo, sem edição; números de inscritos/views são os que as fontes citam (podem estar desatualizados) — conferir antes de usar em decisão.
**Incidente:** sessão NotebookLM expirada; reautenticado autonomamente com `login --browser-cookies chrome` (instalado `rookie-cookies` no venv). O `ask` dentro do worker voltou a falhar por auth 2× após a pesquisa web; os 3 chats rodaram pela CLI no mesmo caderno. Pendente: investigar a expiração no worker (playbook).

## Síntese PQBR
1. Estilos com mais tração em curiosidade/explicativo curto: flat vector (Kurzgesagt), stickman/line art, motion graphics/tipografia cinética, cutout/puppet, whiteboard/doodle. O nosso padrão (cartum 2D plano, 1 personagem) fica entre flat vector e cutout — **manter**.
2. Mudanças sugeridas pelas fontes: expressões faciais/corporais **exageradas**; personagem em cores quentes com **alto contraste sobre fundo frio/limpo**; fundo **minimalista** (evitar detalhes sedutores); trocar enquadramento a cada **2–4 s** (não 3–5); gancho visual nos **3 s** iniciais (50–60% da evasão ocorre aí, OpusClip).
3. Texto na tela: fontes apontam +15–25% de retenção com legendas embutidas (OpusClip). Como o NotebookLM erra texto em imagem, a proposta é **imagem sem texto** + **legenda queimada no pós** (post-short), não no prompt.
4. Canais de referência — BR: Minuto da Terra, Ciência Todo Dia, Any Malu (Combo Studio; recorde puxado por Shorts), Mundo Bita, Monica Toy, Gato Galáctico, Mundo Torajo, Mega Curioso, Nem Eu Sabia, O Curioso, Diário do Curioso; global: Kurzgesagt, TED-Ed, Alan Becker (Animator vs. Animation), Koranos, Animate Your Science, Andrea Terbea, Random42. Mais próximos do nosso formato (curiosidade + 2D curto): Minuto da Terra, Any Malu (Shorts), Kurzgesagt (paleta), Alan Becker (stickman).

## Chat 1
**Pergunta:** Com base nas fontes, quais estilos visuais 2D têm mais tração em Shorts/vídeos curtos de curiosidades e explicativos? Para cada um: descrição visual concreta (traço, paleta, fundo, personagem, ritmo de cortes), por que funciona e a fonte. Seja específico.

Com base no levantamento das fontes do caderno, os estilos visuais 2D com maior tração e eficiência de retenção em Shorts/vídeos curtos de curiosidades e explicativos dividem-se em 5 formatos principais:

---

### 1. Flat Vector / Vetorial Plano (ex: Kurzgesagt, Slack)
* **Descrição visual concreta:**
  * **Traço:** Formas geométricas vetoriais limpas, bordas nítidas e contornos bem definidos, sem fotorrealismo ou gradientes pesados [1-3].
  * **Paleta:** Cores altamente saturadas em blocos sólidos (*bold color blocking*), contrastando tons quentes e frios para alto impacto visual [2-4].
  * **Fundo:** Campos de cor plana ou fundos em azul-marinho profundo (*deep navy*) com sombras suaves e gradientes sutis, despoluídos de detalhes desnecessários [2, 4, 5].
  * **Personagem:** Figuras estilizadas compostas por formas geométricas básicas (membros retangulares ou ovais, expressões faciais minimalistas) [2, 5].
  * **Ritmo de cortes:** Animação ágil (*snappy*), com metamorfoses de formas (*morphing*), zooms suaves de câmera e cortes combinados (*match-cuts*) [2].
* **Por que funciona:** Reduz drasticamente a carga cognitiva do espectador, permitindo que conceitos abstratos, científicos ou curiosidades sejam compreendidos instantaneamente na tela pequena do celular [5].
* **Fonte:** *"Flat vector animation explainer videos"* [6], *"2D Animation Styles: Flat Design, Frame-by-Frame, Cutout and More - Magic Motion Studio"* [7] e *"How to Create Kurzgesagt-Style Animation with Gemini NANO BANANA PRO - YouTube"* [8].

---

### 2. Stickman / Minimalist Line Art (Desenho de Palito)
* **Descrição visual concreta:**
  * **Traço:** Contornos e linhas finas pretas, traçados limpos e silhuetas despojadas navegando pelo espaço negativo [9, 10].
  * **Paleta:** Monocromática (preto e branco) ou com o uso pontual de uma única cor de destaque [9].
  * **Fundo:** Espaço negativo neutro e limpo (fundo branco ou claro), sem poluição cenográfica [9, 10].
  * **Personagem:** Figuras de palito (*stick figures*) ou esboços minimalistas focados em poses expressivas, ação corporal e metáforas visuais diretas sem complexidade facial [10, 11].
  * **Ritmo de cortes:** Cortes diretos, movimentação ágil e expressiva com enquadramentos focados no timing cômico e no ritmo da narração [10].
* **Por que funciona:** A simplicidade extrema permite leitura instantânea sem necessidade de contexto visual complexo [10, 11]. Elimina distrações visuais para direcionar o foco para a narrativa e o humor, além de viabilizar alta velocidade de produção e forte atração viral em Shorts [10, 11].
* **Fonte:** *"Animator vs. Animation — How a Simple Stickman Became an Internet Classic"* [12], *"Cartoon Stick Animations: Why they're popular, and HOW to make them (for BEGINERS) - YouTube"* [13] e *"Animation YouTube Channel Ideas That Actually Work - Shorts Generator AI"* [14].

---

### 3. Motion Graphics / Tipografia Cinética e Infográficos Animados
* **Descrição visual concreta:**
  * **Traço:** Elementos vetoriais geométricos de alta precisão, ícones, gráficos de dados, mapas e tipografia cinética sem uso de personagens [15, 16].
  * **Paleta:** Contraste elevado com paleta limpa e tipografia em negrito (*sans-serif*) para máxima legibilidade móvel [16, 17].
  * **Fundo:** Telas limpas, escuras ou abstratas que destacam a movimentação e a transformação dos dados [16].
  * **Personagem:** Ausente; o foco visual é o movimento de formas, textos, ícones e estatísticas [15, 16].
  * **Ritmo de cortes:** Transições rápidas e frequentes (a cada 1 a 3 segundos), acompanhando com precisão a locução e as batidas do áudio [16, 18].
* **Por que funciona:** É o formato mais direto e limpo para transmitir dados, números, fluxos e lógica de processos com clareza técnica [16, 18]. Funciona muito bem na navegação silenciosa (*silent scrolling*) das redes sociais pelo apoio direto da tipografia animada na tela [18].
* **Fonte:** *"2D Animation Styles: Flat Design, Frame-by-Frame, Cutout and More - Magic Motion Studio"* [7] e *"2D Animation Styles You Should Know About in 2026 - Levitate Media"* [19].

---

### 4. Cutout Animation / Recorte Digital (*Puppet Animation*)
* **Descrição visual concreta:**
  * **Traço:** Ilustrações vetoriais limpas com personagens pré-desenhados divididos em camadas (cabeça, tronco, membros superiores e inferiores) [20, 21].
  * **Paleta:** Cores chapadas e graficamente bem definidas [1, 20].
  * **Fundo:** Cenários 2D modulares construídos em camadas [20].
  * **Personagem:** Bonecos digitais articulados por esqueleto virtual (*rigs/puppets*), movimentados por rotação e escala de membros com juntas visíveis ou suavizadas [20, 21].
  * **Ritmo de cortes:** Trocas de cena e cortes a cada 2–4 segundos [20].
* **Por que funciona:** Permite a reutilização contínua de *assets* entre episódios, reduzindo o tempo de produção em 40% a 60% a partir do segundo vídeo [22-24]. É a estrutura mais eficiente para sustentar a frequência diária de publicação exigida em canais de Shorts [23, 24].
* **Fonte:** *"2D Animation Styles: Flat Design, Frame-by-Frame, Cutout and More - Magic Motion Studio"* [7].

---

### 5. Whiteboard / Doodle Animation (Lousa Explicativa)
* **Descrição visual concreta:**
  * **Traço:** Desenho contínuo em estilo rascunho (*doodle*) simulando traço à mão livre [25, 26].
  * **Paleta:** Traço preto dominante sobre fundo claro, com adição pontual de uma cor primária para destacar termos-chave [25, 27].
  * **Fundo:** Fundo branco limpo simulando um quadro ou folha de papel [25, 26].
  * **Personagem:** Ilustrações didáticas e esquemas visuais traçados passo a passo na tela [25, 28].
  * **Ritmo de cortes:** Poucos cortes bruscos; as transições ocorrem por revelação progressiva (*dynamic drawing*), *panning* ou zooms contínuos em tempo real [28, 29].
* **Por que funciona:** O surgimento progressivo das ilustrações atua como sinalizador visual (*signalling effect*), capturando a atenção, guiando o olhar do espectador e aumentando a retenção e a compreensão do conteúdo [29-32].
* **Fonte:** *"Comparison of dynamic visuals to other presentation formats when learning social science topics in an online setting - Australasian Journal of Educational Technology"* [33], *"A comparison of the effectiveness of Whiteboard Animation Videos versus PowerPoint Videos"* [34] e *"How To Implement Video Learning And Animation: A Guide For Training Managers On A Tight Budget"* [26].

---


## Chat 2
**Pergunta:** Liste os canais 2D de referência (Shorts ou explicativos de curiosidade), separando Brasil e global: nome, estilo visual em 1 linha, porte aproximado (inscritos/views se a fonte disser) e a fonte. Não invente números; se a fonte não disser, escreva 'sem dado'.

### 🇧🇷 Canais Brasileiros

* **Minuto da Terra**
  * **Estilo visual:** Animação 2D e ilustrações didáticas em estilo rascunho com dinamismo visual para explicar conceitos científicos [1, 2].
  * **Porte aproximado:** 1,26 milhão de inscritos (compilado citado acumula 46 mil visualizações) [2].
  * **Fonte:** *"Compilado de Curiosidades Explicadas com Desenho Animado | Minuto da Terra"* [1, 2].

* **Ciência Todo Dia** (Pedro Loos)
  * **Estilo visual:** Apresentação em vlog combinada com animações 2D divertidas, intuitivas e esquemas gráficos explicativos [3-5].
  * **Porte aproximado:** Mais de 324 mil inscritos e 9 milhões de visualizações (na época do estudo) [3]; atingiu mais de 2,3 milhões de inscritos [6].
  * **Fonte:** *"UM CASO DE APROPRIAÇÃO DE DIVULGAÇÃO CIENTÍFICA PELO CANAL CIÊNCIA TODO DIA NO YOUTUBE - Univates"* [3, 6, 7].

* **O (sur)real Mundo de Any Malu** (Combo Studio)
  * **Estilo visual:** Animação 2D cartoon de personagem (*puppet/rigging*) em formato de vlogger/influenciadora digital em Shorts e podcast animado [8, 9].
  * **Porte aproximado:** Mais de 3,5 milhões de inscritos (alcançou mais de 30 milhões de views em um único mês impulsionado por Shorts) [8, 10].
  * **Fonte:** *"Com sucesso de podcast e aposta em 'shorts', YouTube da Any Malu bate recorde de visualizações - Cebola Verde"* [8, 10, 11] e *"História da animação no Brasil – Wikipédia, a enciclopédia livre"* [9].

* **Mundo Bita**
  * **Estilo visual:** Animação 2D vetorial plana (*Flat Design*) altamente colorida e educativa [12].
  * **Porte aproximado:** 14,5 milhões de inscritos e 22,9 bilhões de visualizações [13].
  * **Fonte:** *"20 canais brasileiros que mais engajam crianças no YouTube - Meio e Mensagem"* [13, 14].

* **Monica Toy** (Mauricio de Sousa Produções)
  * **Estilo visual:** Animação 2D minimalista em estilo de recorte digital plano (*chibi*) sem diálogos [13].
  * **Porte aproximado:** 16,0 milhões de inscritos e 13,7 bilhões de visualizações [13].
  * **Fonte:** *"20 canais brasileiros que mais engajam crianças no YouTube - Meio e Mensagem"* [13, 14].

* **Gato Galáctico** (Ronaldo de Azevedo / criador de "Cueio")
  * **Estilo visual:** Animação 2D de cartum com personagens estilizados (marcado historicamente pela série animada 'Cueio') [13, 15].
  * **Porte aproximado:** 20,6 milhões de inscritos e 4,2 bilhões de visualizações [13].
  * **Fonte:** *"20 canais brasileiros que mais engajam crianças no YouTube - Meio e Mensagem"* [13, 14] e *"Quem se lembra desses canais de animação brasileiros? : r/perguntas - Reddit"* [15, 16].

* **Mundo Torajo**
  * **Estilo visual:** Animação 2D de personagens estilizados em formato de avatar e vlogger animado [17, 18].
  * **Porte aproximado:** 5,1 milhões de inscritos [18].
  * **Fonte:** *"Evolução dos canais de animação no Brasil - YouTube"* [18, 19].

* **Mega Curioso**
  * **Estilo visual:** Ilustrações animadas no estilo "Draw My Life" acompanhando a narração [20].
  * **Porte aproximado:** sem dado.
  * **Fonte:** *"7 CANAIS DO YOUTUBE DE CURIOSIDADES GERAIS - SEM QUASES"* [20, 21].

* **Nem Eu Sabia**
  * **Estilo visual:** Curiosidades explicadas com ilustrações dinâmicas e comentários narrados [22].
  * **Porte aproximado:** sem dado.
  * **Fonte:** *"7 CANAIS DO YOUTUBE DE CURIOSIDADES GERAIS - SEM QUASES"* [21, 22].

* **O Curioso**
  * **Estilo visual:** Listas de curiosidades e mistérios apresentadas com imagens e animações acompanhadas por narração [22].
  * **Porte aproximado:** sem dado.
  * **Fonte:** *"7 CANAIS DO YOUTUBE DE CURIOSIDADES GERAIS - SEM QUASES"* [21, 22].

* **Diário do Curioso**
  * **Estilo visual:** Listas explicativas com apoio visual de imagens e animações com voz guia de tom jornalístico [23].
  * **Porte aproximado:** sem dado.
  * **Fonte:** *"7 CANAIS DO YOUTUBE DE CURIOSIDADES GERAIS - SEM QUASES"* [21, 23].

---

### 🌐 Canais Globais

* **Kurzgesagt – In a Nutshell**
  * **Estilo visual:** Animação vetorial plana (*Flat Vector Design*) com formas geométricas, cores vibrantes/saturadas e mascotes de pássaros [24].
  * **Porte aproximado:** sem dado nas fontes de texto para total de inscritos (vídeos individuais citados acumulam 9 milhões de views em *"How to Make a Kurzgesagt Video in 1200 Hours"* e 1 milhão de views em *"O maior buraco negro do Universo"*) [25, 26].
  * **Fonte:** *"5 science animation YouTube channels you need to follow"* [24, 27, 28] e *"How to Create Kurzgesagt-Style Animation with Gemini NANO BANANA PRO - YouTube"* [26, 29].

* **TED-Ed**
  * **Estilo visual:** Diversidade de estilos de animação 2D (doodle, recorte digital e abordagens autorais por animadores convidados) [30, 31].
  * **Porte aproximado:** sem dado.
  * **Fonte:** *"5 science animation YouTube channels you need to follow"* [27, 30, 31] e *"35 Iconic 2D Animation Examples to Spark Your Creativity! - Animaker"* [32, 33].

* **Alan Becker** (série *Animator vs. Animation*)
  * **Estilo visual:** Minimalista de bonecos de palito (*Stickman*) interagindo de forma cômica com ferramentas de software [34].
  * **Porte aproximado:** Ultrapassou 100 mil inscritos via campanha de financiamento (episódios virais com 25 milhões a 30 milhões de views, como *"Animation vs. Geometry"* e *"Animation vs. Coding"*) [35-37].
  * **Fonte:** *"Animator vs. Animation — How a Simple Stickman Became an Internet Classic"* [34, 35, 38] e *"Cartoon Stick Animations: Why they're popular, and HOW to make them (for BEGINERS) - YouTube"* [36, 37, 39].

* **Koranos**
  * **Estilo visual:** Animação 2D/3D focada na ilustração de teorias científicas, mistérios e cenários hipotéticos [40, 41].
  * **Porte aproximado:** sem dado.
  * **Fonte:** *"5 science animation YouTube channels you need to follow"* [27, 40, 41].

* **Animate Your Science**
  * **Estilo visual:** Animações 2D vetoriais explicativas e resumos visuais (*video abstracts*) para pesquisas acadêmicas [42].
  * **Porte aproximado:** sem dado.
  * **Fonte:** *"5 science animation YouTube channels you need to follow"* [27, 42].

* **Andrea Terbea**
  * **Estilo visual:** Animação 2D expressiva focada em histórias da internet, comentários e metáforas visuais [33].
  * **Porte aproximado:** sem dado.
  * **Fonte:** *"35 Iconic 2D Animation Examples to Spark Your Creativity! - Animaker"* [32, 33].

* **Random42 Scientific Communication**
  * **Estilo visual:** Animação 3D hiper-realista e médica focada no corpo humano e nível celular [43, 44].
  * **Porte aproximado:** sem dado.
  * **Fonte:** *"5 science animation YouTube channels you need to follow"* [27, 43, 44].

---

🎬 Quer que eu detalhe o plano de roteiro para o próximo episódio do "Porquê BR" aplicando referências de retenção de um desses canais?

## Chat 3
**Pergunta:** Compare com este bloco padrão nosso: 'ilustração 2D plana de cartum, traço preto grosso, cores chapadas quentes, humor carinhoso, cenário brasileiro do dia a dia; 1 personagem grande no quadro; cena 1 = expressão ao pé da letra; troca a cada 3–5 s; sem texto nas imagens'. O que as fontes sugerem mudar ou manter (traço, paleta, expressões faciais exageradas, texto na tela, fundo, ritmo)? Responda em tópicos com fonte.

Comparando o seu bloco padrão atual com as evidências trazidas pelas fontes do caderno, identificamos **pontos fortes a manter** e **ajustes estratégicos de alta retenção** para o formato de Shorts de animação 2D:

---

### 1. Traço e Estética Visual
* **Recomendação:** **MANTER (com opção de refinamento).**
* **O que as fontes dizem:** O estilo de cartum 2D com contornos bem definidos e linhas pretas é altamente legível em telas pequenas de smartphones [1, 2]. A ilustração plana reduz a carga cognitiva, permitindo que o público compreenda a piada ou o conceito instantaneamente [1, 3].
* **Fontes:** *"2D Animation Styles: Flat Design, Frame-by-Frame, Cutout and More - Magic Motion Studio"* [1], *"Animation YouTube Channel Ideas That Actually Work - Shorts Generator AI"* [2] e *"Motion Graphics Trends: How Visual Storytelling is Evolving in 2026 - Critica"* [3].

---

### 2. Paleta de Cores
* **Recomendação:** **AJUSTAR / EXPANDIR CONTRASITE.**
* **O que as fontes dizem:** Embora o uso de cores quentes chapadas para o personagem e elementos principais funcione bem para passar o tom caloroso e brasileiro, os estudos de direção visual e IA de animação ressaltam a importância de aplicar **alto contraste entre tons quentes (foco) e tons frios ou escuros no fundo (ex: azul-marinho ou neutros)** [4-6]. Isso gera tensão visual e impede que o personagem se "funda" com o cenário em telas de celular [6].
* **Fontes:** *"Flat vector animation explainer videos"* [4, 5], *"How to Create Kurzgesagt-Style Animation with Gemini NANO BANANA PRO - YouTube"* [6] e *"Viralização de Vídeos Curtos: Estratégias Eficazes no TikTok, Reels e YouTube Shorts - Mackenzie"* [7].

---

### 3. Personagem e Expressões Faciais
* **Recomendação:** **MANTER E EXPLICITAR EXPRESSÕES EXAGERADAS.**
* **O que as fontes dizem:** Manter 1 personagem grande e centralizado no terço médio do enquadramento vertical (9:16) é essencial para navegação móvel [8, 9]. As fontes sugerem reforçar a diretriz de **expressões faciais e gestos corporais exagerados**, pois eles atuam como gatilho de conexão emocional imediata e potencializam os picos de humor [10-12].
* **Fontes:** *"35 Iconic 2D Animation Examples to Spark Your Creativity! - Animaker"* [10], *"Animation YouTube Channel Ideas That Actually Work - Shorts Generator AI"* [11], *"The Ideal YouTube Shorts Length & Format for Retention (Data-Backed) - OpusClip Blog"* [8, 9] e *"Viralização de Vídeos Curtos: Estratégias Eficazes no TikTok, Reels e YouTube Shorts - Mackenzie"* [12].

---

### 4. Texto na Tela e Legendas
* **Recomendação:** **MUDAR (Ponto Crítico de Retenção).**
* **O que as fontes dizem:** A orientação atual "sem texto nas imagens" vai na contramão dos dados de retenção. Vídeos curtos com **legendas embutidas (*burned-in captions*) ou palavras-chave animadas na tela apresentam uma retenção de 15% a 25% maior** [13, 14]. Como grande parte do consumo de Shorts ocorre no mudo em locais públicos, o texto animado retém a atenção do olhar e reforça a narrativa sonora [7, 13, 15].
* **Fontes:** *"The Ideal YouTube Shorts Length & Format for Retention (Data-Backed) - OpusClip Blog"* [13, 14] e *"Viralização de Vídeos Curtos: Estratégias Eficazes no TikTok, Reels e YouTube Shorts - Mackenzie"* [7, 15].

---

### 5. Cenário e Fundo
* **Recomendação:** **MANTER (com foco em minimalismo).**
* **O que as fontes dizem:** O cenário do dia a dia brasileiro reforça o gatilho de **autenticidade**, fator apontado como um dos pilares mais fortes para o sucesso e engajamento no YouTube Shorts [16, 17]. No entanto, o fundo deve ser despoluído (*minimalist background*), evitando detalhes secundários que causem ruído ou distraiam o espectador do conceito central (*seductive details effect*) [1, 3, 18].
* **Fontes:** *"A comparison of the effectiveness of Whiteboard Animation Videos versus PowerPoint Videos - UTwente"* [18], *"Motion Graphics Trends: How Visual Storytelling is Evolving in 2026 - Critica"* [3] e *"Viralização de Vídeos Curtos: Estratégias Eficazes no TikTok, Reels e YouTube Shorts - Mackenzie"* [16, 17].

---

### 6. Ritmo de Cortes e Gancho Inicial
* **Recomendação:** **LIGEIRAMENTE ACELERAR (2–4 s) + GANCHO RIGOROSO DE 3s.**
* **O que as fontes dizem:** O intervalo de 3–5 segundos por cena está no limite aceitável, mas as pesquisas em Shorts indicam que os vídeos de maior desempenho renovam o interesse visual com um corte, variação de ângulo ou zoom a cada **2–4 segundos** [5, 14, 19]. Além disso, **50% a 60% da evasão ocorre nos primeiros 3 segundos**, tornando indispensável que a Cena 1 apresente o gancho visual/expressão absurda imediatamente sem preâmbulos [20-22].
* **Fontes:** *"Flat vector animation explainer videos"* [5], *"The Ideal YouTube Shorts Length & Format for Retention (Data-Backed) - OpusClip Blog"* [14, 19-21] e *"Viralização de Vídeos Curtos: Estratégias Eficazes no TikTok, Reels e YouTube Shorts - Mackenzie"* [22].

---

### 💡 Proposta de Bloco Padrão Refinado:

> **[ESTILO]:** ilustração 2D plana de cartum, traço preto nítido, cores quentes chapadas no personagem com alto contraste em fundo frio/despoluído, humor carinhoso.
> **[PERSONAGEM]:** 1 personagem grande e centralizado no quadro, com expressões faciais e corporais exageradas.
> **[AMBIENTE]:** cenário brasileiro do dia a dia minimalista.
> **[CENAS]:** gancho visual/literal nos primeiros 3 s; variação visual/troca de enquadramento a cada 2–4 s; legendas dinâmicas e palavras-chave em destaque.

Quer que eu aplique essa estrutura atualizada na criação de um roteiro de teste para o "Porquê BR"?

## Fontes do caderno (41)
- 20 canais brasileiros que mais engajam crianças no YouTube - Meio e Mensagem | https://www.meioemensagem.com.br/midia/30-canais-brasileiros-engajam-criancas-youtube
- 2D Animation Styles You Should Know About in 2026 - Levitate Media | https://levitatemedia.com/learn/2d-animation-styles-you-should-know-about
- 2D Animation Styles: Flat Design, Frame-by-Frame, Cutout and More - Magic Motion Studio | https://magicmotionstudio.com/2d-animation-styles/
- 35 Iconic 2D Animation Examples to Spark Your Creativity! - Animaker | https://www.animaker.com/hub/2d-animation-examples/
- 5 science animation YouTube channels you need to follow | https://www.animateyour.science/post/5-science-animation-youtube-channels-you-need-to-follow
- 7 CANAIS DO YOUTUBE DE CURIOSIDADES GERAIS - SEM QUASES | http://www.semquases.com/2015/12/7-canais-do-youtube-de-curiosidades.html
- A comparison of the effectiveness of Whiteboard Animation Videos versus PowerPoint Videos - at www.essay.utwente.nl. | https://essay.utwente.nl/80865/1/Draijer_MA_Behavioural%2C%20Management%20and%20Social%20sciences.pdf
- Animation YouTube Channel Ideas That Actually Work - Shorts Generator AI | https://shortsgenerator.ai/blog/animation-youtube-channel-ideas/
- Animator vs. Animation — How a Simple Stickman Became an Internet Classic | https://animationclub.school/blog/animator-vs-animation-how-a-simple-stickman-became-an-internet-classic/
- COMO FAZER SHORTS DARK DE CURIOSIDADE QUE VIRALIZAM - YouTube | https://www.youtube.com/watch?v=topqf5sc6qY
- CONTENT ANALYSIS OF SHORT VIDEOS AS THE DOMINANT FORMAT FOR AUDIENCE ENGAGEMENT ON TIKTOK, IG REELS, AND YOUTUBE SHORTS: A LITERATURE REVIEW | https://sociohum.net/index.php/INJOLE/article/download/259/260
- Cartoon Stick Animations: Why they're popular, and HOW to make them (for BEGINERS) - YouTube | https://www.youtube.com/watch?v=mj-lFyMsLUw
- Choosing the Right Animation Style for Your 2D Explainer Video - ExplainPitch | https://explainpitch.com/en/die-wahl-des-richtigen-animationsstils-fuer-ihr-2d-erklaervideo/
- Com sucesso de podcast e aposta em 'shorts', YouTube da Any Malu bate recorde de visualizações - Cebola Verde | https://cebolaverde.com.br/com-sucesso-de-podcast-e-aposta-em-shorts-youtube-da-any-malu-bate-recorde-de-visualizacoes/
- Como CRIAR o seu PRIMEIRO SHORTS ANIMADO COM IA para MONETIZAR no YOUTUBE | https://www.youtube.com/watch?v=1ec3vZsrHTY
- Comparison of dynamic visuals to other presentation formats when learning social science topics in an online setting - Australasian Journal of Educational Technology | https://ajet.org.au/index.php/AJET/article/download/7639/1955/27989
- Compilado de Curiosidades Explicadas com Desenho Animado | Minuto da Terra | https://www.youtube.com/watch?v=1bKKsIIYjys
- Evolução dos canais de animação no Brasil - YouTube | https://www.youtube.com/watch?v=jwFfQGSN9rk
- Flat vector animation explainer videos | https://explain.film/explainer-video-styles/flat-vector
- História da animação no Brasil – Wikipédia, a enciclopédia livre | https://pt.wikipedia.org/wiki/Hist%C3%B3ria_da_anima%C3%A7%C3%A3o_no_Brasil
- How To Implement Video Learning And Animation: A Guide For Training Managers On A Tight Budget - Vendor Directory | https://vendordirectory.td.org/documents/19098
- How to Create Kurzgesagt-Style Animation with Gemini NANO BANANA PRO - YouTube | https://www.youtube.com/watch?v=ne90oYvwcF0
- How to Make Stickman Animations and Go VIRAL in 1 Week (FREE AI Tools) - YouTube | https://www.youtube.com/watch?v=JI8xeuCg7I0
- Motion Graphics Trends: How Visual Storytelling is Evolving in 2026 - Critica | https://www.criticatv.com/motion-graphics-trends-how-visual-storytelling-is-evolving-in-2026/
- Novo relatório do YouTube mostra como os animadores online estão remodelando a indústria do entretenimento - Animation Magazine | https://www.animationmagazine.net/pt/2026/04/new-youtube-report-shows-how-online-animators-are-reshaping-the-entertainment-industry/
- O poder da Animação 2D para explicar projetos e ideias complexas - Panóptica Multimídia | https://www.panoptica.com.br/post/o-poder-da-anima%C3%A7%C3%A3o-2d-para-explicar-projetos-e-ideias-complexas
- Quem se lembra desses canais de animação brasileiros? : r/perguntas - Reddit | https://www.reddit.com/r/perguntas/comments/1umvqq1/quem_se_lembra_desses_canais_de_anima%C3%A7%C3%A3o/
- Social Media 2025: Vídeos curtos Educativos e Interativos Engajam - Agência UGAH! | https://agenciaugah.com.br/videos-curtos-educativos-e-interativos-engajam-e-vendem-mais/
- The Ideal YouTube Shorts Length & Format for Retention (Data-Backed) - OpusClip Blog | https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention
- The biggest animation channel in Brazil, @imaginago | Meliense Podcast #120 - YouTube | https://www.youtube.com/watch?v=eUgrvf97Ddw
- The top 5 animation trends that will dominate 2026 | Lummi | https://www.lummi.ai/blog/animation-trends-2026
- Top 12 2D Animation Trends to Follow in 2026 | MonkyVision | https://monkyvision.com/blog/2d-animations-trends/
- UM CASO DE APROPRIAÇÃO DE DIVULGAÇÃO CIENTÍFICA PELO CANAL CIÊNCIA TODO DIA NO YOUTUBE - Univates | https://www.univates.br/revistas/index.php/signos/article/download/3245/2035
- Viralização de Vídeos Curtos: Estratégias Eficazes no TikTok, Reels e YouTube Shorts - Mackenzie | https://dspace.mackenzie.br/bitstreams/b24c19b8-9ac7-41af-8621-8a7bc7d42017/download
- Why Stick Figure YouTube Videos Keep Breaking Out in 2026 - Satura AI | https://saturaai.com/blog/why-stick-figure-youtube-videos-keep-breaking-out-in-2026-jpkuyd
- https://abral.org.br/20-canais-brasileiros-que-mais-engajam-criancas-no-youtube/ | https://abral.org.br/20-canais-brasileiros-que-mais-engajam-criancas-no-youtube/
- https://blog.saga.com.br/8-canais-de-animacao-para-conhecer/ | https://blog.saga.com.br/8-canais-de-animacao-para-conhecer/
- https://core.ac.uk/download/588677290.pdf | https://core.ac.uk/download/588677290.pdf
- https://m.youtube.com/@ilustradamente.oficial/videos?view=0&sort=dd&shelf_id=4 | https://m.youtube.com/@ilustradamente.oficial/videos?view=0&sort=dd&shelf_id=4
- https://www.proceedings.blucher.com.br/download-pdf/animao-2d-como-recurso-de-apoio-didtico-para-o-ensino-de-desenho-tcnico-38058 | https://www.proceedings.blucher.com.br/download-pdf/animao-2d-como-recurso-de-apoio-didtico-para-o-ensino-de-desenho-tcnico-38058


## Superado (12/10/2026)
Uma rotina periódica gerou no caderno "PQBR - pesquisa bloco visual 2D" um bloco divergente (fundo creme, cortes de 3–5 s). **Superado, não adotar:** vale o §16.7 aprovado pelo José (personagem quente sobre fundo limpo frio/neutro, 3–5 objetos, cortes de 2–4 s, imagem absurda no 1º segundo).
