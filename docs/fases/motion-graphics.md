# Fases — motion graphics no pós

José aprovou o motion graphics no pós em 28/10/2026 (t145u, REGRAS §26) e, no mesmo dia, deu o retorno sobre o piloto (t147u): o vídeo usado no piloto está obsoleto (o modelo cartum 2D não será mais usado), a ideia do motion é interessante e fica, e o visual precisa melhorar, com referência atual e uma coletânea de referências para os vídeos não ficarem iguais — um padrão, com mudanças sutis que atendam ao tipo de conteúdo.

As fases abaixo separam decisão, direção visual, coletânea e trabalho, como em `docs/fases/stickman.md`.

## Fase 0 — Decisão e mecânica (t145u, feito)

- Regra: REGRAS §26. O pós aceita motion graphics sobre o vídeo da cadeia Flow/Vids/Vibes. Ambiente limpo, bom senso, rotina fixa com transição padrão, bloco de números travados.
- Motor e catálogo v1 em `src/pqbr/pos/motion/`: quadro como função pura do tempo, molas fechadas, ruído com semente, Chrome headless quadro a quadro, FFmpeg junta e preserva a narração. Contrato `PlanoMotion` 1.0.0. Papel `motion` (nono, híbrido, preso ao catálogo, sem activity no worker).
- Piloto de t145u (EP1003, cartum 2D): visual reprovado em t147u e pasta deletada em t152u (originais em `runtime/lote-saldo/cafe-fraco/`, lote inteiro **obsoleto** desde t156u — Higgsfield DESCARTADO); a autocrítica 6,5 → 8 segue em `biblioteca/historico.md`. O padrão de cartão vigente (MG-03, `runtime/piloto-motion/mg03/folha-cartoes-v2.png`) foi aprovado pelo José em 28/10. O piloto 2 (MG-05) usa o layout padrão do canal com cenas reais do Flow, quando o Flow estiver em operação regular.

## Fase 1 — Avaliação do piloto e direção visual (t147u, feito)

O piloto prova a **mecânica** (contrato, motor, render, composição, autocrítica) e **não prova o visual**:

1. O vídeo de base é o EP1003 em cartum 2D, modelo que o José aposentou. O piloto não pode virar referência de nada além da mecânica.
2. O visual v1 (cartão branco chapado, Liberation Sans, azul de interface) não conversa com o traço do canal fixado em t146u: nanquim preto com hachura sobre papel creme `#f5f0e4`, dois olhos sempre visíveis. Um Short que alterna cena nanquim com gráfico de software entrega dois canais em um.

**Direção aprovada como regra (REGRAS §26, "Base visual"):** o motion é desenhado na **mesma folha do stickman** — papel creme com textura, traço de nanquim, hachura, cores do elenco como acento e **uma tipografia manuscrita única** (licença OFL, com acentos do português, a escolher em MG-03). A referência que ninguém copia é a própria biblioteca do canal (mesma lição do material de estudo de t145u: nomear um visual e alimentar o modelo com um frame dele).

**Atualização t148u (28/10, depois desta entrega):** as fichas nanquim de t146u foram descartadas pelo José e o padrão visual definitivo do canal passou a ser o conjunto flat colorido entregue por ele no Drive (`Fontes/Imagens` → `banco-fichas/`, `indice.json` 2.0.0). A "mesma folha do stickman" citada acima passa a ser esse conjunto. A mecânica e o desenho das fases não mudam.

**Atualização t149u/t150u (28/10):** a "tipografia manuscrita a escolher" foi resolvida: a fonte do canal é a **Fredoka** (t149u, banco de fontes em `banco-fichas/referencias-motion/fontes/`, `PlanoMotion.fonte`). Em t150u a paleta do motor (`catalogo.PALETA` e `motor.js`) e o `PlanoMotion.elenco` (agora `masculino`/`feminino`) foram re-basiados no padrão flat colorido (fundo creme claro, azul-aço para o protagonista masculino, rosa para a feminina; letra colorida sobre fundo claro usa o tom escuro, porque o rosa chapado dá só 2,3:1 no creme). O papel creme `#f5f0e4`, o nanquim e a hachura **saíram** do padrão: onde este documento ainda os cita, é histórico de t146u/t147u. O desenho dos cartões do catálogo (MG-03) ainda não foi refeito.

## Fase 2 — Coletânea de referências (`banco-fichas/referencias-motion/`)

Responde ao pedido "um padrão, com mudanças sutis que atendam ao tipo de conteúdo".

**O que é fixo (o padrão, não varia nunca):** o conjunto flat colorido de `banco-fichas/` (t148u) — fundo creme claro, contorno preto, cabeça redonda branca, dois olhos sempre visíveis, roupa chapada fixa por personagem; mais a Fredoka como fonte única, molas, cortina padrão, zonas seguras 9:16 e bloco de números travados. Até o MG-03 as peças do catálogo v1 mantêm o desenho do piloto (só a paleta já é a nova), valendo como prova de mecânica.

**O que varia (lista fechada, uma escolha por episódio):** acento de cor do elenco; textura do fundo; forma do cartão (folha solta, ficha pautada, cartão com clipe); idioma de entrada (surgir, riscar, datilografar); ornamento do tema (p.ex. vapor para café, floco para gelo); direção da cortina.

**Como se escolhe:** o tipo de conteúdo do episódio (expressão/origem; curiosidade do cotidiano; sazonal; risco doméstico/trânsito — CONTRATO §4) restringe o conjunto; dentro dele, uma semente derivada do código do episódio (`PQBR-EPnnnn`) escolhe a variante, **sem repetir a variante do episódio anterior**. A escolha fica registrada no `PlanoMotion`; o Auditor confere a aderência à ficha (quem monta não julga). Determinístico: o mesmo episódio gera sempre a mesma variante.

**De onde saem:** três fontes, detalhadas no README da coletânea — a biblioteca do próprio canal (âncora), o material de estudo que o José trouxe em t145u e a pesquisa nova de referências externas (MG-02, propostas minhas, escolha dele).

**Referências externas:** entram só como **gramática** (paleta, tipografia, textura, ritmo), nunca conteúdo, personagem, logo ou música. No repositório ficam a ficha em texto, o link, a data da consulta e a **prova renderizada pelo nosso motor**; nenhum frame de terceiro é guardado. Referência nova nasce `aguardando_ok_jose` e só vira `aprovada` com OK do José, como as fichas permanentes. A coletânea abre com a `REF-MG-00` (o padrão flat colorido do canal, âncora; re-basiada em t150u), seguida da `REF-MG-01` (gramática de movimento do dossiê, t150u, abaixo); as propostas de referências externas são o item MG-02, para o José escolher.

## Fase 2b — Personagem presente no layout (t150u, feito no código)

O José pediu que o bloco de motion possa ter um **personagem do catálogo dentro do layout**, num "quadradinho" num canto, com criatividade liberada ao papel `motion` (REGRAS §26, "Personagem presente no layout").

- **Peça:** `catalogo/personagem-moldura.js` (tela cheia). Parâmetros: `personagem` (id `PERS-*`), `pose` (nome de recorte da ficha: `giro-*`, `exp-*`), `canto` (inf-dir, inf-esq, sup-dir, sup-esq), `tamanho` (220–460), `espelhar`. Entra com mola e leve inclinação, respira por ruído e sai encolhendo. A moldura usa a cor principal do elenco.
- **Contrato:** `PlanoMotion` 1.2.0. `elenco` = gênero do protagonista (`masculino`/`feminino`; o legado `PERS-M`/`PERS-F` converte). Os tipos de parâmetro `personagem` e `pose` só aceitam ficha individual (`PERS-*`) com imagem local e ao menos um recorte; ficha `aguardando_ok_jose` vale.
- **Render:** o recorte vem da ficha do `banco-fichas/`, não de `recursos`. `render.quadros()` gera a prévia sem compor, usada nos testes. O render acusa quando o personagem cobre texto ou cartão (`semSobreposicao`) e reprova.
- **Limites:** só dentro do bloco de tela cheia; recorte estático, boca de reação e nunca de fala; entra por bom senso, não o bloco inteiro.
- **Falta:** o visual dos cartões em volta dele (MG-03) e um vídeo de episódio real (MG-05). A autocrítica de 8/10 com personagem ainda não foi feita.

## Fase 2c — Vocabulário de movimento do dossiê (t150u, proposta MG-10)

O José trouxe três fontes de movimento: a galeria whatships.com, o artigo do 0xMovez e o estudo `minimax-h3-max-motion` ("motion study" de 15 s sobre *1984*, 100% gerado por IA), pedindo para **adaptar a paleta, o visual e os gráficos e manter só os movimentos gráficos**.

- **Estratégia:** o motor segue próprio. A ideia central dos tutoriais (quadro como função pura do tempo, molas, ruído com semente, Chrome headless e FFmpeg) o motor já implementa. Remotion fica de fora (licença paga para empresa de porte maior). Repositório sem licença (`PDoomVideo`, `Austerlitz`) serve só para estudar a técnica, sem copiar código. Com licença permissiva (`ClaudeAnimationBase` e `claude-animation-skill`, MIT; `hyperframes`, Apache-2.0) entram, no máximo, como ideia de catálogo de poses ou piloto isolado. A galeria whatships.com não tem modelo nem código: é só gramática (ritmo, tipografia, transições).
- **Vocabulário candidato (peças novas do catálogo, MG-10):** carimbo (título que cai e assenta), tarja de redação (barra que cobre e revela), zoom que atravessa o texto, recorte-colagem, match cut (um elemento vira o próximo) e tipografia cinética. Cada peça é repintada no padrão flat colorido, com a Fredoka e as cores do elenco; o texto vem só do bloco de números travado e é escrito pelo nosso motor (REGRAS §26 proíbe reaproveitar texto de vídeo gerado por IA). A lição "pare de centralizar tudo" vira regra de composição: alternar lado e eixo entre blocos.
- **Como entra:** ficha `REF-MG-01` (texto, link, data), sem frame de terceiro. Cada peça nova passa pela mesma disciplina do catálogo e nasce `aguardando_ok_jose`; a prova é renderizada pelo nosso motor. Sem música. Imagens e vídeos do Flow podem entrar dentro das peças; o personagem presente (Fase 2b) casa com o vocabulário. O modelo MiniMax não entra na cadeia.

## Fase 2d — As seis referências de t153u e as peças entregues (feito no código)

O José entregou seis vídeos da galeria whatships (bitrig, horizonx, omaphoto, vovy, raylight-2, valendata) e pediu que a manutenção fizesse a análise técnica e decidisse o que aproveitar, respeitando a identidade visual do canal. Ele **não quer escolher movimento a movimento** (delegação registrada em REGRAS §26, "Quem escolhe o movimento").

- **Método:** as páginas têm o mp4 no JSON embutido; o download foi feito só em `/tmp` (o CDN recusa Referer) e a análise foi por **folha de contato 5×5** (um quadro a cada ~0,4–3,6 s, conforme a duração), sem playback completo. Nenhum frame de terceiro entrou no repositório; os mp4 e as folhas foram apagados no fim.
- **Fichas:** REF-MG-02 a REF-MG-07, cada uma com link, data, medida (resolução/fps/duração), gramática observada, o que entra, o que fica de fora e os quadros da prova. `indice.json` 0.4.0. **t155u:** REF-MG-00..07 → `aprovada`; o OK é sobre a ficha e a regra (feito).
- **Peças novas no catálogo (MG-10 parcial, `indice.json` 1.2.0):** `frase-troca` (frases trocadas no mesmo lugar, troca seca, marca do elenco, pontinhos de passo), `marca-texto` (layout por palavra, cursor de leitura e barra chapada atrás do `destaque`, que é **trecho de `texto`** — o contrato confere), `numero-conta` (contador pt-BR, sufixo, rótulo e selo), `leque` (nó central e 2–4 satélites na diagonal do 9:16), `elo-causa` (dois cartões, conector carimbado e traço com seta) e `transicao-pincelada` (fase `cobre`/`revela`, borda ondulada e diagonal, traço de acento; uso interno do bloco, a cortina padrão continua na entrada e na saída).
- **Prova:** `banco-fichas/referencias-motion/provas/mg10-pecas.png`, 12 quadros de um plano de demonstração (PQBR-EP1003, bloco 10–30 s, elenco masculino), todos sem violação de zona segura. Autocrítica 7 → 8,5 em `biblioteca/historico.md` (contraste do marca-texto, base do sufixo, pincelada vertical → diagonal, ordem do terceiro braço no leque).
- **O que ficou de fora, e por quê:** a interface de produto das referências (Bitrig, Vovy, Valendata), o texto e a marca delas, a estética dark/noir, o movimento contínuo de palavras (Raylight), a digitação como cena, ícones substituindo palavras e a íris de câmera. O **riscado** (palavra substituída) é o candidato mais forte para o próximo lote.

## Fase 3 — Trabalho (itens do ROADMAP, Fase MG)

- **MG-01** Regra e documentos (esta entrega, t147u). Aguarda OK do José na coletânea.
- **MG-02** Propostas de referências externas + coletânea inicial para OK do José.
- **MG-03** Catálogo v2 no padrão flat colorido do canal, com a Fredoka (feito em t149u/t150u: fonte, paleta do motor, `PlanoMotion.elenco`; falta refazer o desenho dos 8 cartões e medir o custo de render). O catálogo v1 fica como prova de mecânica.
- **MG-04** Variação determinística no `PlanoMotion` (categoria + semente, lista fechada) e registro do contrato em `VERSOES`.
- **MG-05** Piloto 2, já com cenas stickman reais do Flow, e `gemini_juiz` sobre ele.
- **MG-06** Campo do bloco de números no contrato do storyboard e no template do NotebookLM.
- **MG-07** Activity `pos_motion` no worker (reinício exige OK) e checagem automática tela × bloco no Auditor.
- **MG-08** Finalização e entrada do logotipo (proposta neste documento; o José escolhe o desenho antes do código).
- **MG-09** Personagem presente no layout (t150u, feito no código: peça `personagem-moldura`, `PlanoMotion` 1.2.0). Falta ver num vídeo de episódio real (MG-05).
- **MG-10** Peças do vocabulário do dossiê: carimbo, tarja de redação, zoom que atravessa o texto, recorte-colagem, match cut e tipografia cinética (Fase 2c). Depende de MG-03; cada peça nova nasce `aguardando_ok_jose`. **Feito em t153u (parcial):** seis peças a partir das referências REF-MG-02..07 (Fase 2d), com contrato e prova; carimbo, tarja, zoom, recorte-colagem e match cut seguem como candidatos.
- **MG-11** Lote de refação EP1002–EP1010 sem Higgsfield (t156u): vídeos do `runtime/lote-saldo/` obsoletos; ordem Flow → MG-05 → José assiste → lote.
- **MG-12** Combo `core-ultra` (Opus 5.5) no papel `motion` (t157u, proposta): três camadas (código → Jev → Opus); José cria o combo; trocar `modelos_9router.json` + reinício exigem OK. Até MG-07 a manutenção monta o `PlanoMotion` e o motor renderiza.

## Finalização e entrada do logotipo (proposta, MG-08) — EM CONSTRUÇÃO, aguardando o ajuste do José

O final hoje (REGRAS §26): reconhecimento (vídeo) → CTA + loop (vídeo retoma a cena 1). O José quer ajustar essa finalização, em especial a **entrada do logotipo** (t147u). Assets oficiais em `branding/overlay/`: `logo-sting.png` (marca completa), `logo-corner-br.png` (canto, com a silhueta do mapa) e `logo-bug.png` (marca pequena). Hoje nenhum código aplica logo ao vídeo (F5-05 prevê "logo com zoom" e não foi construído). A regra t532/t131u segue valendo: o mapa do Brasil não bloqueia gerar nem subir, e o José é avisado antes de tornar público.

Três desenhos possíveis, do mais rico ao mais simples:

- **A) Sting em motion no loop.** Nos últimos ~1,5–2 s do CTA, a cortina padrão cobre o vídeo para o papel creme, o `logo-sting.png` oficial entra com a mola padrão (assenta com leve excesso e para) e o loop volta para a cena 1. Vira um modelo novo do catálogo (`logo-sting`), com o PNG oficial como recurso.
- **B) Bug durante o bloco + sting no loop.** O `logo-bug.png` fica no canto superior esquerdo, fora das zonas seguras, durante o bloco de motion inteiro; o final segue o desenho A.
- **C) Só o bug.** Sem sting: o `logo-bug.png` acompanha o bloco de motion e o CTA continua em vídeo, como hoje.

Regras para qualquer um dos três: o PNG oficial do logo é **recurso** do `PlanoMotion`, nunca redesenhado pelo motor (marca não se reinterpreta); a entrada usa a mola padrão, sem brilho, partícula ou fade puro (clichês proibidos, REGRAS §26); o logo nunca cobre fala nem o bloco de números; a escolha fica registrada no plano e o Auditor confere. O José escolhe ou ajusta o desenho em MG-08, antes de qualquer código.
## Riscos

- **Fonte:** resolvida em t149u (Fredoka, OFL, acentos do pt-BR conferidos no banco de fontes). O catálogo v1 usa pesos até 800 e a Fredoka vai a 700; o MG-03 ajusta.
- **Custo de render:** ruído por quadro e a moldura do personagem podem pesar no Chrome headless; medir em MG-03 (o piloto v1, sem textura, levou ~2 min para 18,6 s de bloco).
- **Texto de terceiros:** o estudo do MiniMax tem texto gerado por IA dentro do vídeo; nada disso entra. O texto da tela sai só do bloco de números travado (REGRAS §26).
- **Variação demais vira ruído:** por isso a lista é fechada e a semente é do episódio; variável fora da lista exige peça nova na biblioteca, com a mesma disciplina do catálogo.
- **Dependência das fichas:** MG-05 só anda depois do OK do José nas fichas permanentes (P5) e das cenas geradas no Flow.
