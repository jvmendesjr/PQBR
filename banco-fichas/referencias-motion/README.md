# Referências de motion graphics (`referencias-motion/`)

Coletânea de referências visuais do bloco de motion (REGRAS §26, t145u/t147u). Um padrão fixo (papel creme `#f5f0e4`, nanquim, hachura, tipografia manuscrita única, molas, cortina padrão) com variações sutis de lista fechada, escolhidas pelo tipo de conteúdo e por semente do episódio. Desenho completo em `docs/fases/motion-graphics.md`.

> **Nota t148u (28/10/2026):** o padrão visual do canal mudou — as fichas nanquim de t146u foram reprovadas e descartadas, e a base passou a ser o conjunto flat colorido de `banco-fichas/` (`indice.json` 2.0.0). Esta coletânea ainda está no nanquim de t146u e é re-basixada no MG-03 (catálogo v2, paleta do motor e REF-MG-00). Ela continua `aguardando_ok_jose`; o OK deve considerar o re-base.

## Regras da pasta

1. Referência externa entra só como **gramática** (paleta, tipografia, textura, ritmo). Nunca conteúdo, personagem, logo ou música de terceiros.
2. **Nenhum frame de terceiro é guardado aqui.** De cada referência externa ficam: ficha em texto (`REF-MG-NN.md`), link, data da consulta e a prova renderizada pelo nosso motor (`provas/REF-MG-NN.png`, quando houver).
3. Toda referência nasce `aguardando_ok_jose` e só vira `aprovada` com OK explícito do José, como as fichas permanentes de `banco-fichas/`.
4. O papel `motion` só usa referência `aprovada`. O Auditor confere a aderência do plano à ficha.
5. O índice é `indice.json`, versionado. Mudança de padrão fixo é mudança de regra (DECISOES-LOG + REGRAS §26).

## De onde saem as referências

Três fontes, nesta ordem de autoridade:

1. **A biblioteca do próprio canal** (âncora, REF-MG-00): os frames reais de `banco-fichas/referencias-canal/` e as fichas permanentes de t146u. É a referência que ninguém copia; toda variação mede distância dela.
2. **O material de estudo que o José trouxe em t145u** (`pasta-temporario-deletar-depois/Motion Graphics VIDEO/`, fora do git): o manual "Stickman & Motion Studio", o artigo do 0xMovez, o "Motion Graphics.pdf" e os kits `motion-graphics-studio` e `motion-reel-kit`. Deles já saíram a técnica (quadro = função do tempo, molas, autocrítica) e a regra "name a look, feed a frame". Valem como gramática de processo. O docx "Paperclip Arquitetura…" está marcado pelo próprio José como chat trocado e **não** é referência.
3. **Pesquisa nova de referências externas (MG-02):** o mantenedor prepara propostas (ficha em texto + link + data + prova renderizada pelo nosso motor, nunca frame de terceiro) e o José aprova uma a uma antes de virarem `aprovada`.

Nenhuma referência entra sem passar por essas regras; nenhuma vira `aprovada` sem OK do José.
## Referências

| id | nome | origem | estado |
|---|---|---|---|
| REF-MG-00 | Papel e nanquim do canal | interna (`banco-fichas/referencias-canal/`, t146u) | aguardando_ok_jose |
