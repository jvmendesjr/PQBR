# Referências de motion graphics (`referencias-motion/`)

Coletânea de referências visuais do bloco de motion (REGRAS §26, t145u/t147u/t150u). Um padrão fixo (cartoon 2D flat colorido, fundo creme claro, cor do elenco como acento, Fredoka como fonte única, molas, cortina padrão) com variações sutis de lista fechada, escolhidas pelo tipo de conteúdo e por semente do episódio. Desenho completo em `docs/fases/motion-graphics.md`.

> **Nota t148u/t150u (28/10/2026):** o padrão visual do canal mudou. As fichas nanquim de t146u foram reprovadas e descartadas (t148u), e a base passou a ser o conjunto flat colorido de `banco-fichas/`. Em t150u a paleta do motor, a REF-MG-00 e o `indice.json` desta pasta foram re-basiados nele, e entrou a REF-MG-01 (vocabulário de movimento). As duas seguem `aguardando_ok_jose`; o OK vale para as versões atuais.

## Regras da pasta

1. Referência externa entra só como **gramática** (paleta, tipografia, textura, ritmo, movimento). Nunca conteúdo, personagem, logo, texto ou música de terceiros.
2. **Nenhum frame de terceiro é guardado aqui.** De cada referência externa ficam: ficha em texto (`REF-MG-NN.md`), link, data da consulta e a prova renderizada pelo nosso motor (`provas/REF-MG-NN.png`, quando houver).
3. Toda referência nasce `aguardando_ok_jose` e só vira `aprovada` com OK explícito do José, como as fichas permanentes de `banco-fichas/`.
4. O papel `motion` só usa referência `aprovada`. O Auditor confere a aderência do plano à ficha.
5. O índice é `indice.json`, versionado. Mudança de padrão fixo é mudança de regra (DECISOES-LOG + REGRAS §26).
6. **Como o José acrescenta uma referência:** manda o link e o motivo ao agente. O agente abre a ficha `REF-MG-NN.md` com link e data, sem baixar frame, e prepara a prova com o nosso motor. Para fonte tipográfica, o caminho é o banco de fontes (`fontes/`, CLI `python -m pqbr.pos.motion.fontes`), e a aprovação continua sendo dele.

## De onde saem as referências

Quatro fontes, nesta ordem de autoridade:

1. **A biblioteca do próprio canal** (âncora, REF-MG-00): o conjunto definitivo de `banco-fichas/` (t148u). Os frames antigos do canal foram descartados em t149u. É a referência que ninguém copia; toda variação mede distância dela.
2. **O material de estudo que o José trouxe em t145u** (`pasta-temporario-deletar-depois/Motion Graphics VIDEO/`, fora do git): o manual "Stickman & Motion Studio", o artigo do 0xMovez, o "Motion Graphics.pdf" e os kits `motion-graphics-studio` e `motion-reel-kit`. Deles já saíram a técnica (quadro = função do tempo, molas, autocrítica) e a regra "name a look, feed a frame". Valem como gramática de processo. O docx "Paperclip Arquitetura…" está marcado pelo próprio José como chat trocado e **não** é referência.
3. **O dossiê de movimento de t150u** (REF-MG-01): a galeria whatships.com, o estudo "MiniMax H3 MAX motion" e o post do 0xMovez, só pelo vocabulário de movimento (carimbo, tarja de redação, zoom que atravessa o texto, recorte-colagem, match cut, tipografia cinética).
4. **Pesquisa nova de referências externas (MG-02):** o mantenedor prepara propostas (ficha em texto + link + data + prova renderizada pelo nosso motor, nunca frame de terceiro) e o José escolhe de 3 a 5 antes de virarem `aprovada`.

Nenhuma referência entra sem passar por essas regras; nenhuma vira `aprovada` sem OK do José.

## Referências

| id | nome | origem | estado |
|---|---|---|---|
| REF-MG-00 | Padrão flat colorido do canal | interna (conjunto de `banco-fichas/`, t148u; re-basiada em t150u) | aguardando_ok_jose |
| REF-MG-01 | Vocabulário de movimento do dossiê (whatships, MiniMax H3 MAX, 0xMovez) | externa, só gramática de movimento (t150u) | aguardando_ok_jose |
