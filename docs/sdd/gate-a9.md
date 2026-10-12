# Gate A9 — capa/frame do Short (proposta t427, para aprovação do José)

**Referências:** skill `yt-thumbnail-brief` (sergebulaev/youtube-skills, MIT, varredura A; só brief, não gera imagem) — melhor base para copiar/adaptar; `higgsfield-youtube-thumbnail` (MIT, gera via CLI externo, varredura C: baixa/executa código remoto) — só referência, **não instalar**; guias 2026 de capa de Shorts (ContHunt, YCT, Thumix, CTRpilot). Decisão de desenho: **sem geração de imagem** — a capa é **um quadro do próprio vídeo** (estilo único do NotebookLM, §16.3), escolhido por código + juiz.

## Critérios
**Código (`src/pqbr/pipeline/capa.py`, reprova o candidato e tenta o próximo):**
1. 9:16 e altura ≥ 640 px (ideal 1080×1920).
2. Luma média entre 40 e 215 (nem escuro nem estourado); contraste (YHIGH−YLOW)/2 ≥ 28.
3. Nitidez: `blurdetect` ≤ 9 (não é quadro de transição/borrado); não é o end-card (o pós já corta).
4. Ordem de preferência: cena 1 (expressão em cena literal, §16.4) → última (retomada do loop) → maior contraste.

**Juiz visual (junto do pedido VISUAL, sem custo extra de pedido):**
5. Um foco só (personagem ou objeto-gancho) no centro, dentro da zona segura: fora dos ~15% de cima, ~20–25% de baixo e ~15% da borda direita.
6. Legível no teste de ~120–200 px de largura (miniatura da prateleira).
7. Promete o mesmo que o título (sem isca falsa).
8. Texto na imagem: preferível nenhum (estilo §16.4 pede "sem texto nas imagens"); se houver, ≤ 3 palavras e sem erro.
9. **Segurança (reprova o vídeo, §16.6):** semelhança com pessoa real, marca/logo real, estereótipo ofensivo.

**Resultado:** 1–4 e 5–8 são **métrica** (escolhem outro quadro; se nenhum passar, segue com ressalva no relatório); só 9 reprova.
