> ⛔ **PESQUISA / REFERÊNCIA DE PRÉ-CONSTRUÇÃO: AGENTES NÃO CONSULTAM SEM APROVAÇÃO EXPLÍCITA DO JOSÉ (t287).** Pode conter premissas superadas que, mal interpretadas, iriam parar em produção. As regras válidas estão em `docs/REGRAS.md`.

> Nota: gabarito dos 4 vídeos (TV, sinal amarelo, controle remoto, tomada do chuveiro). O CTA gravado nestes roteiros é o antigo; o válido é só "Segue o Porquê BR" (t262/t263).

Relatório com o material real extraído dos 4 episódios em `/workspace/yt-llm-bot/episodios`.

---

### 1. Episódio TV (Dormir com a TV Ligada)

- **Título publicado, data e ID/link:**
  - Título: "Por Que Dormir com a TV Ligada Destrói Seu Sono Sem Você Perceber? 📺💤 #shorts"
  - Data: 2026-10-06T20:41:27Z
  - ID/Link: https://youtube.com/shorts/5i78fV-V6lI (extraído de `06-publicacao.json` e dumps do canal)
- **Roteiro usado (texto integral):**
```markdown
# Partitura Técnica de Roteiro - Porquê BR
## Episódio: stickman-dormir-com-tv-ligada-v1
## Título Conceitual: Por que dormir com a TV ligada destrói seu sono?
## Duração Estimada: 52.0s | Palavras: 115

<!-- INICIO_ROTEIRO -->
### [00.00 - 03.00] VOCÊ ACORDA CANSADO?
- **Tempo:** 00.00 - 03.00 (safe zones 9:16 respeitadas)
- **Visual:** Stickman dormindo todo torto na cama com luz azul da TV piscando forte na cara dele; olhos abrem assustados.
- **Narração:** ...por que você acorda destruído mesmo dormindo a noite inteira de TV ligada?
- **Texto na tela / Legenda:** ACORDOU MOÍDO?
- **SFX:** Zumbido de TV estática e bipe agudo

### [03.00 - 45.00] O GOLPE DA LUZ AZUL
- **Tempo:** 03.00 - 45.00 (safe zones 9:16 respeitadas)
- **Visual:** Cérebro do Stickman com capacete de operário confuso; luz azul entra pela pálpebra fechada como raios laser; fábrica de melatonina fecha as portas; gráfico do sono REM caindo em abismo; Stickman zumbi tropeçando de manhã com xícara de café furada.
- **Narração:** O problema não é o barulhinho de fundo que você jura que ajuda a relaxar. A luz azul da tela atravessa suas pálpebras fechadas e dá um golpe baixo no cérebro: ela bloqueia a produção de melatonina, o hormônio do sono profundo. Seu corpo até apaga, mas seu cérebro fica em alerta máximo, como se ainda fosse dia claro. Você não atinge o descanso reparador, passa a noite em sono superficial e acorda parecendo que foi atropelado por um caminhão de cansaço.
- **Texto na tela / Legenda:** GOLPE DA LUZ AZUL
- **SFX:** Sirene de fábrica, alarme abafado e som de vidro trincando

### [45.00 - 52.00] SEGUE O @PORQUEBR
- **Tempo:** 45.00 - 52.00 (safe zones 9:16 respeitadas)
- **Visual:** Stickman desliga a TV no controle, coloca máscara de dormir estilosa e aponta sorrindo para o ícone do Porquê BR.
- **Narração:** Pra salvar seu sono e sua saúde, desliga essa tela agora e segue o Porquê BR pra descobrir...
- **Texto na tela / Legenda:** SEGUE O @PORQUEBR
- **SFX:** Clique de botão, 'click' de interruptor e sino suave

### [Loop-CTA Conector Obrigatório]
- **CTA:** Segue o Porquê BR pra não perder nenhuma novidade e curiosidade todo dia!
<!-- FIM_ROTEIRO -->
```
- **Transcrição da narração:** Não gerado arquivo dedicado de transcrição/whisper (`não encontrado`). A narração segue as marcações `Narração:` do roteiro acima.
- **Prompts usados:**
  - **Steering / Instruções:**
```text
<!-- INICIO_STEERING -->
Animação 2D limpa Stickman minimalista. Fundo plano cream #FDFBF7 sem textura de papel. PROIBIDO papercut, PROIBIDO bordas brancas die-cut, PROIBIDO sombras drop shadow de papel recortado.
Idioma oficial: Português do Brasil (pt-br).
ESTRUTURA DE FECHAMENTO (LOOP-CTA CONECTOR OBRIGATÓRIO):
Nos 4 segundos finais, a locução DEVE falar textualmente a chamada conectada ao início: "Segue o Porquê BR pra não perder nenhuma novidade e curiosidade todo dia!".
Na tela, exibir grafismo/legenda "Segue @porquebr" com o Stickman apontando.
Sem despedidas estanques, conectando a última palavra diretamente na frase inicial do vídeo para reprodução contínua em loop infinito.
<!-- FIM_STEERING -->
```
  - **Fábrica / SOP base:** `/workspace/yt-llm-bot/ops/sop-short-stickman-completo.md` e `/workspace/yt-llm-bot/sources/fabrica-shorts.md`.
  - **SEO:**
    - Título: `Por Que Dormir com a TV Ligada Destrói Seu Sono Sem Você Perceber? 📺💤 #shorts`
    - Descrição: `Dormir de TV ligada sabota melatonina e sono reparador. Entenda a ciência da luz azul no cérebro. Inscreva-se no @porquebr-t4c!`
    - Tags: `Shorts, Porquê BR, Curiosidades BR, dormir com tv ligada, luz azul sono, melatonina, sono ruim, acordar cansado, saude do sono, higiene do sono, curiosidades ciencia, porque br`
- **Caminhos dos arquivos:**
  - `06-publicacao.json`: `/workspace/yt-llm-bot/episodios/stickman-dormir-com-tv-ligada-v1/06-publicacao.json`
  - `02-roteiro`: `/workspace/yt-llm-bot/episodios/stickman-dormir-com-tv-ligada-v1/02-roteiro-stickman-dormir-com-tv-ligada-v1.md`
  - `02-steering`: `/workspace/yt-llm-bot/episodios/stickman-dormir-com-tv-ligada-v1/02-steering-stickman-dormir-com-tv-ligada-v1.txt`
  - `05-seo-pack`: `/workspace/yt-llm-bot/episodios/stickman-dormir-com-tv-ligada-v1/05-seo-pack-stickman-dormir-com-tv-ligada-v1.md`

---

### 2. Episódio Sinal Amarelo (Acelera que dá tempo)

- **Título publicado, data e ID/link:**
  - Título: "Por que o sinal amarelo no Brasil significa 'acelera que dá tempo'? #Shorts"
  - Data: 2026-10-05 (marcado como já publicado/duplicado em `06-publicacao.json`)
  - ID/Link: `não encontrado` em `06-publicacao.json`
- **Roteiro usado (texto integral):**
```markdown
# Partitura Técnica de Roteiro - Porquê BR
## Episódio: stickman-sinal-amarelo-acelera-v1
## Título Conceitual: Por que o sinal amarelo no Brasil significa 'acelera que dá tempo'?
## Duração Estimada: 52.0s | Palavras: 118

<!-- INICIO_ROTEIRO -->
### [00.00 - 03.00] AMARELO = ACELERA?
- **Tempo:** 00.00 - 03.00 (safe zones 9:16 respeitadas)
- **Visual:** Stickman em carro minimalista preto vê semáforo amarelar, arregala os olhos, engata marcha e pisa com força no acelerador levantando poeira.
- **Narração:** ...por que no Brasil sinal amarelo virou 'pisa fundo que dá tempo'?
- **Texto na tela / Legenda:** AMARELO = ACELERA?
- **SFX:** Aceleração brusca e pneu cantando

### [03.00 - 45.00] CÁLCULO QUÂNTICO DO BRASILEIRO
- **Tempo:** 03.00 - 45.00 (safe zones 9:16 respeitadas)
- **Visual:** Livro de trânsito vira cinzas; Stickman olha retrovisor apavorado com carro colado atrás soltando fumaça; Stickman coloca óculos escuros estilo corrida; fórmulas matemáticas absurdas flutuam na tela; carro cruza cruzamento raspando no milissegundo em que luz vermelha acende.
- **Narração:** No Código de Trânsito, amarelo significa atenção e parada segura. Mas na física das ruas brasileiras, amarelo significa duas coisas: pânico e oportunidade. Se você freia de boa, o motorista colado atrás quase entra no seu porta-malas buzinando com ódio. Se você pisa fundo, vira piloto de fuga tentando vencer o radar implacável. O cérebro faz um cálculo quântico em meio segundo: distância da faixa, peso do sapato e coragem. Todo mundo jura que passa no amarelo queimado, mas no fundo é só aquele medo clássico de perder três minutos da vida.
- **Texto na tela / Legenda:** CÁLCULO QUÂNTICO DO BRASILEIRO
- **SFX:** Buzinaça contínua, bip de radar eletrônico e 'whoosh' de passagem rápida

### [45.00 - 52.00] SEGUE O @PORQUEBR
- **Tempo:** 45.00 - 52.00 (safe zones 9:16 respeitadas)
- **Visual:** Stickman limpa suor da testa com expressão de alívio e aponta animado para o ícone do Porquê BR piscando na tela.
- **Narração:** Pra não levar multa nem buzinada na orelha, segue agora o Porquê BR pra descobrir...
- **Texto na tela / Legenda:** SEGUE O @PORQUEBR
- **SFX:** Som de clique e sino suave

### [Loop-CTA Conector Obrigatório]
- **CTA:** Segue o Porquê BR pra não perder nenhuma novidade e curiosidade todo dia!
<!-- FIM_ROTEIRO -->
```
- **Transcrição da narração:** `não encontrado` arquivo separado. Narração expressa nas seções `Narração:` do roteiro.
- **Prompts usados:**
  - **Steering / Instruções:**
```text
<!-- INICIO_STEERING -->
Animação 2D limpa Stickman minimalista. Fundo plano cream #FDFBF7 sem textura de papel. Traço preto sólido, sem gradientes. PROIBIDO papercut, PROIBIDO bordas brancas die-cut, PROIBIDO sombras drop shadow de papel recortado.
Idioma oficial: Português do Brasil (pt-br).
ESTRUTURA DE FECHAMENTO (LOOP-CTA CONECTOR OBRIGATÓRIO):
Nos 4 segundos finais, a locução DEVE falar textualmente a chamada conectada ao início: "Segue o Porquê BR pra não perder nenhuma novidade e curiosidade todo dia!".
Na tela, exibir grafismo/legenda "Segue @porquebr" com o Stickman apontando.
Sem despedidas estanques, conectando a última palavra diretamente na frase inicial do vídeo para reprodução contínua em loop infinito.
<!-- FIM_STEERING -->
```
  - **SEO:**
    - Título Principal: `Por que o sinal amarelo no Brasil significa 'acelera que dá tempo'? #Shorts`
    - Descrição: `Sinal amarelo manda parar no papel. Na rua vira prova de arrancada contra radar. Quando sinal amarela você pisa no freio ou no acelerador? Inscreva-se no @porquebr-t4c...`
    - Tags: `Shorts, Porquê BR, Curiosidades BR, sinal amarelo, transito brasil, semaforo, ctb, radar de transito, motorista brasileiro, multas, piloto de fuga, curiosidades brasil, porque br`
- **Caminhos dos arquivos:**
  - `06-publicacao.json`: `/workspace/yt-llm-bot/episodios/stickman-sinal-amarelo-acelera-v1/06-publicacao.json`
  - `02-roteiro`: `/workspace/yt-llm-bot/episodios/stickman-sinal-amarelo-acelera-v1/02-roteiro-stickman-sinal-amarelo-acelera-v1.md`
  - `02-steering`: `/workspace/yt-llm-bot/episodios/stickman-sinal-amarelo-acelera-v1/02-steering-stickman-sinal-amarelo-acelera-v1.txt`
  - `05-seo-pack`: `/workspace/yt-llm-bot/episodios/stickman-sinal-amarelo-acelera-v1/05-seo-pack-stickman-sinal-amarelo-acelera-v1.md`

---

### 3. Episódio Controle Remoto (Controle com Durex)

- **Título publicado, data e ID/link:**
  - Título: "Por Que Todo Controle Remoto no Brasil Tem Fita Adesiva? 📺🔋 #shorts"
  - Data: 2026-10-06T22:14:20Z
  - ID/Link: `não encontrado` campo URL no JSON do episódio (presente registro de publicação no canal `@porquebr-t4c`)
- **Roteiro usado (texto integral):**
```markdown
# Roteiro: Por Que Todo Controle Remoto no Brasil Tem Fita Adesiva?

**Personagem:** Stickman sentado no sofá tentando mudar de canal na TV.
**Tom:** Cômico, nostálgico, científico e altamente identificável.

[00:00 - 00:10] Gancho: Stickman aperta o botão do controle remoto... nada acontece! Ele dá 3 tapas secos na palma da mão, ajusta o durex amarelo enrolado atrás e a TV liga magicamente!
[00:10 - 00:25] O Enigma Nacional: 'Por que em toda casa brasileira o controle tem fita adesiva e só funciona na base da porrada?'
[00:25 - 00:45] A Ciência do Durex: Não é só porque a tampinha quebrou! Raio-X nas molas traseiras: com o tempo, o metal das molas perde a tensão elástica e forma uma camada invisível de óxido que bloqueia a passagem dos 3 volts. A fita adesiva ultra-apertada mantém a pilha prensada com força constante!
[00:45 - 00:55] O Segredo do Tapa: O tapa na mão faz a pilha deslizar micromilímetros, raspando a oxidação e restaurando a condutividade elétrica instantaneamente!
[00:55 - 01:00] CTA: Stickman erguendo o controle com orgulho como troféu. 'Inscreva-se no @porquebr-t4c para mais segredos do cotidiano brasileiro!'
```
- **Transcrição da narração:** `não encontrado` arquivo separado.
- **Prompts usados:**
  - **Steering / Instruções:**
```text
Estilo: Animação stickman 2D simplificada, traço vetor preto sobre fundo branco minimalista.
Personagem: Stickman no sofá com controle remoto envolto em fita adesiva amarela.
Cenas: Close no controle com durex, raio-X didático das pilhas e molas com faíscas azuis de eletricidade e micro-oxidação sendo raspada.
Áudio: Locução bem-humorada, ritmo ágil, efeitos sonoros cômicos de estalos e 'tapinha' seco na mão.
CTA final: Stickman apontando para o botão de inscrição com o controle funcionando perfeitamente.
```
  - **SEO:**
    - Título: `Por Que Todo Controle Remoto no Brasil Tem Fita Adesiva? 📺🔋 #shorts`
    - Descrição: `O mistério do durex no controle remoto revelado! Entenda por que a fita adesiva e o famoso tapinha fazem o controle voltar a funcionar. Inscreva-se no @porquebr-t4c!`
    - Tags: `Shorts, Porquê BR, controle remoto, durex, gambiarra, ciencia do cotidiano, curiosidades, brasil`
- **Caminhos dos arquivos:**
  - `06-publicacao.json`: `/workspace/yt-llm-bot/episodios/stickman-controle-com-durex-v1/06-publicacao.json`
  - `02-roteiro`: `/workspace/yt-llm-bot/episodios/stickman-controle-com-durex-v1/02-roteiro-stickman-controle-com-durex-v1.md`
  - `02-steering`: `/workspace/yt-llm-bot/episodios/stickman-controle-com-durex-v1/02-steering-stickman-controle-com-durex-v1.txt`
  - `05-seo-pack`: `/workspace/yt-llm-bot/episodios/stickman-controle-com-durex-v1/05-seo-pack-stickman-controle-com-durex-v1.md`

---

### 4. Episódio Tomada do Chuveiro (Tomada Derretida)

- **Título publicado, data e ID/link:**
  - Título: "Por Que a Tomada do Chuveiro Sempre Derrete e Vira Carvão? 🔥 #shorts"
  - Data: 2026-10-04T20:48:06-0300
  - ID/Link: https://youtube.com/shorts/hRTK91_9N0Q
- **Roteiro usado (texto integral):**
```markdown
# Partitura Técnica de Roteiro - Porquê BR
## Episódio: stickman-tomada-derretida-chuveiro-v1
## Título Conceitual: Por que a tomada do chuveiro sempre derrete e vira carvão?
## Duração Estimada: 50.0s | Palavras: 110

<!-- INICIO_ROTEIRO -->
### [00.00 - 03.00] TOMADA DERRETIDA
- **Tempo:** 00.00 - 03.00 (safe zones 9:16 respeitadas)
- **Visual:** Stickman tomando banho quentinho feliz; de repente a tomada acima do chuveiro começa a chiar, solta fumaça preta e derrete igual plástico queimado.
- **Narração:** ...por que toda tomada de chuveiro no Brasil parece condenada a derreter e virar carvão?
- **Texto na tela / Legenda:** TOMADA DERRETIDA!
- **SFX:** Zumbido elétrico forte, faísca e estalo

### [03.00 - 45.00] O EFEITO JOULE ASSASSINO
- **Tempo:** 03.00 - 45.00 (safe zones 9:16 respeitadas)
- **Visual:** Raio-X do plugue com elétrons em engarrafamento monstro; tomada comum de 10A ou 20A espremendo corrente de 30A a 50A; faíscas invisíveis criam calor brutal (Efeito Joule); fita isolante derretendo e conector de porcelana salvador aparecendo com aura dourada.
- **Narração:** A culpa é da matemática da física. Um chuveiro elétrico comum puxa mais de trinta a cinquenta amperes em potência máxima. Nenhuma tomada convencional de parede foi feita pra aguentar essa porrada de corrente contínua. O plugue fica frouxo, a resistência de contato sobe nas alturas e o Efeito Joule transforma o ponto de encaixe num miniforno que cozinha o plástico até carbonizar. É por isso que norma técnica proíbe plugue comum: chuveiro exige conector cerâmico ou emenda direta bem prensada.
- **Texto na tela / Legenda:** EFEITO JOULE ASSASSINO
- **SFX:** Fritura, estalo de plástico partindo e alarme de perigo

### [45.00 - 50.00] SEGUE O @PORQUEBR
- **Tempo:** 45.00 - 50.00 (safe zones 9:16 respeitadas)
- **Visual:** Stickman segura conector cerâmico como um troféu elétrico e aponta sorrindo para o botão do Porquê BR.
- **Narração:** Pra não colocar fogo no banheiro nem tomar banho gelado, segue o Porquê BR pra descobrir...
- **Texto na tela / Legenda:** SEGUE O @PORQUEBR
- **SFX:** Som de sino suave e clique

### [Loop-CTA Conector Obrigatório]
- **CTA:** Segue o Porquê BR pra não perder nenhuma novidade e curiosidade todo dia!
<!-- FIM_ROTEIRO -->
```
- **Transcrição da narração:** `não encontrado` arquivo separado. Narração expressa nas seções `Narração:` do roteiro.
- **Prompts usados:**
  - **Steering / Instruções:**
```text
<!-- INICIO_STEERING -->
Animação 2D limpa Stickman minimalista. Fundo plano cream #FDFBF7 sem textura de papel. Traço preto sólido, sem gradientes. PROIBIDO papercut, PROIBIDO bordas brancas die-cut, PROIBIDO sombras drop shadow de papel recortado.
Idioma oficial: Português do Brasil (pt-br).
ESTRUTURA DE FECHAMENTO (LOOP-CTA CONECTOR OBRIGATÓRIO):
Nos 4 segundos finais, a locução DEVE falar textualmente a chamada conectada ao início: "Segue o Porquê BR pra não perder nenhuma novidade e curiosidade todo dia!".
Na tela, exibir grafismo/legenda "Segue @porquebr" com o Stickman apontando.
Sem despedidas estanques, conectando a última palavra diretamente na frase inicial do vídeo para reprodução contínua em loop infinito.
<!-- FIM_STEERING -->
```
  - **SEO:**
    - Título: `Por Que a Tomada do Chuveiro Sempre Derrete e Vira Carvão? 🔥 #shorts`
    - Descrição: `Tomada de chuveiro derretida é perigo real. Entenda o Efeito Joule e por que plugue comum não aguenta a corrente do chuveiro. Inscreva-se no @porquebr-t4c!`
    - Tags: `Shorts, Porquê BR, Curiosidades BR, chuveiro eletrico, tomada derretida, efeito joule, eletricidade residencial, disjuntor, conector ceramico, seguranca eletrica, curiosidades, ciencia cotidiana, porque br`
- **Caminhos dos arquivos:**
  - `06-publicacao.json`: `/workspace/yt-llm-bot/episodios/stickman-tomada-derretida-chuveiro-v1/06-publicacao.json`
  - `02-roteiro`: `/workspace/yt-llm-bot/episodios/stickman-tomada-derretida-chuveiro-v1/02-roteiro-stickman-tomada-derretida-chuveiro-v1.md`
  - `02-steering`: `/workspace/yt-llm-bot/episodios/stickman-tomada-derretida-chuveiro-v1/02-steering-stickman-tomada-derretida-chuveiro-v1.txt`
  - `05-seo-pack`: `/workspace/yt-llm-bot/episodios/stickman-tomada-derretida-chuveiro-v1/05-seo-pack-stickman-tomada-derretida-chuveiro-v1.md`
