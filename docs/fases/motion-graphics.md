# Fases — motion graphics no pós

José aprovou o motion graphics no pós em 28/10/2026 (t145u, REGRAS §26) e, no mesmo dia, deu o retorno sobre o piloto (t147u): o vídeo usado no piloto está obsoleto (o modelo cartum 2D não será mais usado), a ideia do motion é interessante e fica, e o visual precisa melhorar, com referência atual e uma coletânea de referências para os vídeos não ficarem iguais — um padrão, com mudanças sutis que atendam ao tipo de conteúdo.

As fases abaixo separam decisão, direção visual, coletânea e trabalho, como em `docs/fases/stickman.md`.

## Fase 0 — Decisão e mecânica (t145u, feito)

- Regra: REGRAS §26. O pós aceita motion graphics sobre o vídeo da cadeia Flow/Vids/Vibes. Ambiente limpo, bom senso, rotina fixa com transição padrão, bloco de números travados.
- Motor e catálogo v1 em `src/pqbr/pos/motion/`: quadro como função pura do tempo, molas fechadas, ruído com semente, Chrome headless quadro a quadro, FFmpeg junta e preserva a narração. Contrato `PlanoMotion` 1.0.0. Papel `motion` (nono, híbrido, preso ao catálogo, sem activity no worker).
- Piloto em `runtime/piloto-motion/cafe-fraco/` (fora do git): bloco do porquê 14,87–33,5 s sobre o EP1003, original intacto, áudio idêntico, render determinístico, autocrítica 6,5 → 8 (`biblioteca/historico.md`).

## Fase 1 — Avaliação do piloto e direção visual (t147u, feito)

O piloto prova a **mecânica** (contrato, motor, render, composição, autocrítica) e **não prova o visual**:

1. O vídeo de base é o EP1003 em cartum 2D, modelo que o José aposentou. O piloto não pode virar referência de nada além da mecânica.
2. O visual v1 (cartão branco chapado, Liberation Sans, azul de interface) não conversa com o traço do canal fixado em t146u: nanquim preto com hachura sobre papel creme `#f5f0e4`, dois olhos sempre visíveis. Um Short que alterna cena nanquim com gráfico de software entrega dois canais em um.

**Direção aprovada como regra (REGRAS §26, "Base visual"):** o motion é desenhado na **mesma folha do stickman** — papel creme com textura, traço de nanquim, hachura, cores do elenco como acento e **uma tipografia manuscrita única** (licença OFL, com acentos do português, a escolher em MG-03). A referência que ninguém copia é a própria biblioteca do canal (mesma lição do material de estudo de t145u: nomear um visual e alimentar o modelo com um frame dele).

**Atualização t148u (28/10, depois desta entrega):** as fichas nanquim de t146u foram descartadas pelo José e o padrão visual definitivo do canal passou a ser o conjunto flat colorido entregue por ele no Drive (`Fontes/Imagens` → `banco-fichas/`, `indice.json` 2.0.0). A "mesma folha do stickman" citada acima passa a ser esse conjunto: o catálogo v2 (MG-03), a paleta do motor e a REF-MG-00 são re-baixados para ele. A mecânica e o desenho das fases não mudam.

## Fase 2 — Coletânea de referências (`banco-fichas/referencias-motion/`)

Responde ao pedido "um padrão, com mudanças sutis que atendam ao tipo de conteúdo".

**O que é fixo (o padrão, não varia nunca):** o conjunto flat colorido de `banco-fichas/` (t148u) — fundo creme claro, contorno preto, cabeça redonda branca, dois olhos sempre visíveis, roupa chapada fixa por personagem; mais tipografia única, molas, cortina padrão, zonas seguras 9:16 e bloco de números travados. Até o MG-03 o catálogo v1 e a REF-MG-00 seguem no nanquim de t146u, valendo como prova de mecânica.

**O que varia (lista fechada, uma escolha por episódio):** acento de cor do elenco; textura do fundo; forma do cartão (folha solta, ficha pautada, cartão com clipe); idioma de entrada (surgir, riscar, datilografar); ornamento do tema (p.ex. vapor para café, floco para gelo); direção da cortina.

**Como se escolhe:** o tipo de conteúdo do episódio (expressão/origem; curiosidade do cotidiano; sazonal; risco doméstico/trânsito — CONTRATO §4) restringe o conjunto; dentro dele, uma semente derivada do código do episódio (`PQBR-EPnnnn`) escolhe a variante, **sem repetir a variante do episódio anterior**. A escolha fica registrada no `PlanoMotion`; o Auditor confere a aderência à ficha (quem monta não julga). Determinístico: o mesmo episódio gera sempre a mesma variante.

**De onde saem:** três fontes, detalhadas no README da coletânea — a biblioteca do próprio canal (âncora), o material de estudo que o José trouxe em t145u e a pesquisa nova de referências externas (MG-02, propostas minhas, escolha dele).

**Referências externas:** entram só como **gramática** (paleta, tipografia, textura, ritmo), nunca conteúdo, personagem, logo ou música. No repositório ficam a ficha em texto, o link, a data da consulta e a **prova renderizada pelo nosso motor**; nenhum frame de terceiro é guardado. Referência nova nasce `aguardando_ok_jose` e só vira `aprovada` com OK do José, como as fichas permanentes. A coletânea abre com a `REF-MG-00` (o papel e o nanquim de t146u, ancorada em `banco-fichas/referencias-canal/`), que é re-basixada no conjunto t148u no MG-03; as propostas de referências externas são o item MG-02, para o José escolher.

## Fase 3 — Trabalho (itens do ROADMAP, Fase MG)

- **MG-01** Regra e documentos (esta entrega, t147u). Aguarda OK do José na coletânea.
- **MG-02** Propostas de referências externas + coletânea inicial para OK do José.
- **MG-03** Catálogo v2 no traço do canal + fonte manuscrita OFL + textura de papel (medir custo de render). O catálogo v1 fica como prova de mecânica.
- **MG-04** Variação determinística no `PlanoMotion` (categoria + semente, lista fechada) e registro do contrato em `VERSOES`.
- **MG-05** Piloto 2, já com cenas stickman reais do Flow, e `gemini_juiz` sobre ele.
- **MG-06** Campo do bloco de números no contrato do storyboard e no template do NotebookLM.
- **MG-07** Activity `pos_motion` no worker (reinício exige OK) e checagem automática tela × bloco no Auditor.
- **MG-08** Finalização e entrada do logotipo (proposta neste documento; o José escolhe o desenho antes do código).

## Finalização e entrada do logotipo (proposta, MG-08) — EM CONSTRUÇÃO, aguardando o ajuste do José

O final hoje (REGRAS §26): reconhecimento (vídeo) → CTA + loop (vídeo retoma a cena 1). O José quer ajustar essa finalização, em especial a **entrada do logotipo** (t147u). Assets oficiais em `branding/overlay/`: `logo-sting.png` (marca completa), `logo-corner-br.png` (canto, com a silhueta do mapa) e `logo-bug.png` (marca pequena). Hoje nenhum código aplica logo ao vídeo (F5-05 prevê "logo com zoom" e não foi construído). A regra t532/t131u segue valendo: o mapa do Brasil não bloqueia gerar nem subir, e o José é avisado antes de tornar público.

Três desenhos possíveis, do mais rico ao mais simples:

- **A) Sting em motion no loop.** Nos últimos ~1,5–2 s do CTA, a cortina padrão cobre o vídeo para o papel creme, o `logo-sting.png` oficial entra com a mola padrão (assenta com leve excesso e para) e o loop volta para a cena 1. Vira um modelo novo do catálogo (`logo-sting`), com o PNG oficial como recurso.
- **B) Bug durante o bloco + sting no loop.** O `logo-bug.png` fica no canto superior esquerdo, fora das zonas seguras, durante o bloco de motion inteiro; o final segue o desenho A.
- **C) Só o bug.** Sem sting: o `logo-bug.png` acompanha o bloco de motion e o CTA continua em vídeo, como hoje.

Regras para qualquer um dos três: o PNG oficial do logo é **recurso** do `PlanoMotion`, nunca redesenhado pelo motor (marca não se reinterpreta); a entrada usa a mola padrão, sem brilho, partícula ou fade puro (clichês proibidos, REGRAS §26); o logo nunca cobre fala nem o bloco de números; a escolha fica registrada no plano e o Auditor confere. O José escolhe ou ajusta o desenho em MG-08, antes de qualquer código.
## Riscos

- **Fonte manuscrita:** licença OFL conferida e acentos do pt-BR completos antes de virar padrão; sem isso, MG-03 não fecha.
- **Custo de render:** textura de papel e ruído por quadro podem pesar no Chrome headless; medir em MG-03 (o piloto v1, sem textura, levou ~2 min para 18,6 s de bloco).
- **Variação demais vira ruído:** por isso a lista é fechada e a semente é do episódio; variável fora da lista exige peça nova na biblioteca, com a mesma disciplina do catálogo.
- **Dependência das fichas:** MG-05 só anda depois do OK do José nas fichas permanentes (P5) e das cenas geradas no Flow.
