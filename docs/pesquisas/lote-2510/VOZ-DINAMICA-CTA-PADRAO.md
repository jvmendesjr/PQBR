# lote-2510 — voz dinâmica + CTA padrão (25/10/2026)

Decisões de José (25/10/2026): voz dinâmica (Larissa xcNJswC7UcxsIiCuih19, eleven_v3, tags de emoção com moderação, conta meioquedigital, speed 1,1 via atempo); fechamento padrão fixo = take B `cta-padrao-B.mp3` ("[cheerful] Segue o Porquê BR!"), reutilizado sem regerar; legenda gravada via `scripts/legendar_short.py`.

Processo: gerar só o corpo (sem a frase final de CTA), `scripts/montar_voz_dinamica.py` anexa o CTA B após ~0,3 s e remonta com os mesmos clipes. Não publicado.

Saídas por tema em `runtime/lote-saldo/<tema>/`: `<tema>-final.mp4` (legendado), `<tema>-final-sem-legenda.mp4`, `narracao-final.mp3`, `narracao-final.txt` (texto da legenda), `montagem-final.json` (cortes). Versões anteriores preservadas.

Desvio de texto: a última linha de cada roteiro (CTA com variação, ex. "Tranca essa ansiedade na chave e segue o Porquê BR!") foi substituída pelo CTA padrão "Segue o Porquê BR!". Exceção: brigadeiro mantém "Pra não perder o ponto," falado antes do CTA B.
