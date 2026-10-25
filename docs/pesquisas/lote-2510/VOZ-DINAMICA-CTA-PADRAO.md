# lote-2510 — voz dinâmica + CTA padrão (25/10/2026)

Decisões de José (25/10/2026): voz dinâmica (Larissa xcNJswC7UcxsIiCuih19, eleven_v3, tags de emoção com moderação, conta meioquedigital, speed 1,1 via atempo); take B `cta-padrao-B.mp3` ("[cheerful] Segue o Porquê BR!") = **referência de entonação** do fechamento (frase inteira chamativa, natural, sem exagero) — NÃO substitui o CTA do roteiro; legenda gravada via `scripts/legendar_short.py`.

Processo: gerar só o corpo (sem a frase final de CTA), `scripts/montar_voz_dinamica.py` anexa o CTA B após ~0,3 s e remonta com os mesmos clipes. Não publicado.

Saídas por tema em `runtime/lote-saldo/<tema>/`: `<tema>-final.mp4` (legendado), `<tema>-final-sem-legenda.mp4`, `narracao-final.mp3`, `narracao-final.txt` (texto da legenda), `montagem-final.json` (cortes). Versões anteriores preservadas.

Desvio de texto: a última linha de cada roteiro (CTA com variação, ex. "Tranca essa ansiedade na chave e segue o Porquê BR!") foi substituída pelo CTA padrão "Segue o Porquê BR!". Exceção: brigadeiro mantém "Pra não perder o ponto," falado antes do CTA B.

## CORREÇÃO (25/10/2026, ERR-MON-02) — o parágrafo "Desvio de texto" acima foi um ERRO
REGRA do José (t34u): cada Short fecha com o **CTA personalizado do roteiro** (última frase original de `narracao.txt`, ligada ao tema; REGRAS §5 / t467). O take B só define a entonação. Corrigido: CTA de cada roteiro gerado com a mesma receita da B (`[cheerful]`, eleven_v3, speed 1,1, trim), emendado no corpo e remontado → `runtime/lote-saldo/<tema>/<tema>-pronto-v2.mp4` (6 temas; cafe-fraco, garrafa e liquidificador já tinham o fallback literal como CTA original). `scripts/montar_voz_dinamica.py` agora recusa `cta-padrao*` salvo `--permitir-cta-generico`, aplica fades de 30 ms e, quando falta clipe no fim, reutiliza/encadeia clipes em vez de still. Ver `GATE-PRONTO-LOTE.md` e catálogo `ERR-MON-02`.
