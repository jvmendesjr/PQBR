# Lote Runway — saldo e preço (25/10/2026, leitura via conector, nada gerado)

Saldo (whoami): 1834 créditos (plano Pro 1530 + comprados 304).

Tabela oficial Runway (créditos), clipe de 5 s 9:16:
- gen-4-turbo (i2v, 720p): 5/s → 25 por clipe (bate com olhos-da-cara: 5 clipes = 125)
- wan3 480p 5/s → 25 · wan3 720p 10/s → 50
- hailuo3 768p 10/s → 50 · veo3.1 sem áudio 20/s → 100
- kling-3-standard sem áudio 9/s → 45 (com áudio 13/s → 65)
- gen-4.5 12/s → 60
- seedance-2-mini 16/s, mínimo 64 → 80 · seedance-2 36/s → 180
- keyframe: nano-banana-2.1 1K 4/img · gen-4-image-turbo 2/img (exige referência)
Obs.: o teste anterior cobrou 165 créditos, acima da tabela → validar com 1 clipe antes do lote.

Roteiros: 110 clipes no total (10–14 por Short); orçar 12–13 clipes/Short para cobrir ~55 s sem imagem parada.
Por Short com gen-4-turbo: 12–13 × 25 = 300–325 + keyframes 13 × 4 = 52 → ~350–380.
Cabem ~4–5 Shorts nos 1834 (9 Shorts precisariam ~3.300). kling-3-standard: ~3; seedance-2-mini: 1–2.

## Clipe de validação — custo real medido (25/10/2026 ~19:05 BRT)
Saldo antes 1834 → após keyframe 1830 → após clipe 1805.
- Keyframe nano-banana-2.1 1K 9:16 (task d9da2c07): 4 créditos (= tabela)
- Clipe gen-4-turbo i2v 5 s 720x1280 sem áudio (task b9871532): 25 créditos (= tabela)
- Total cena saci c1a: 29 créditos. Os 165 do teste anterior não se repetem neste fluxo.
Arquivos: runtime/lote-runway/dia-do-saci-31-de-outubro/saci-c1a-validacao.mp4 e saci-c1a-keyframe.png
Projeção: ~12–13 clipes/Short × 29 ≈ 350–380 créditos → 1805 cabem ~4–5 Shorts.

## Short completo — Dia do Saci (25/10/2026) — ❌ REPROVADO / TEMA DESCARTADO
- Clipes: 12 (c1a reaproveitado da validação + 11 novos), keyframe nano-banana-2.1 (4 cr) + gen-4-turbo 5 s 9:16 (25 cr) = 29 cr/cena.
- Saldo Runway: 1805 → 1486 (gasto 319 cr = 11 × 29; c1a já contado na validação: 29). Total Saci: 348 cr.
- Repetições: 0. Falhas de task: 0 (só 2 recusas de startFrame ainda RUNNING, sem cobrança).
- Narração ElevenLabs (meioquedigital, Larissa, eleven_v3, 1 take, 50,3 s → 45,4 s com atempo 1.1): 778,92 créditos (~US$ 0,14).
- Saída: runtime/lote-runway/dia-do-saci-31-de-outubro/saci-pronto.mp4 (1080×1920, 45,4 s, legendado, pós-produzido, não publicado).

### Status (25/10/2026, 19:40 UTC-3) — José
- **Saci REPROVADO e tema DESCARTADO de vez:** o personagem parecia falar com a voz da Larissa (ERR-ROT-02; a narração é sempre em 3ª pessoa e o personagem só reage), e o visual do gen-4-turbo foi reprovado. Artefatos movidos, sem apagar, para `docs/pesquisas/lote-runway/_descartado/` e `runtime/lote-runway/_descartado/`; o motivo está em `_descartado/MOTIVO.md`. Postgres: `temas_pendentes` id 31, status `falhou` + `metadados.descarte` (o check da tabela não tem `descartado`).
- **Lote Runway SUSPENSO:** nenhuma geração paga até nova ordem.

## Teste kling-3-standard — pagar-o-pato cena 1 (2026-10-25)

Aprovado por José: 1 clipe único, sem repetição. Lote segue SUSPENSO.

| Item | Valor |
|---|---|
| Keyframe | nano-banana-2.1, 1K, 9:16 (task 81005339…) |
| Vídeo | kling-3-standard (taskType kling_3_0_standard, mode std), i2v, 5 s, 9:16, `sound: false` (task d18dd44f…) |
| Saldo antes | 1486 (plano 1174 + comprado 312) |
| Saldo depois | 1437 (plano 1125 + comprado 312) |
| **Custo real** | **49 cr** (≈4 keyframe + ≈45 vídeo ⇒ ~9 cr/s) |
| Saída | 716×1284, 24 fps, 5,04 s, sem trilha de áudio; freezedetect sem congelamentos |
| Tempo | ~10 min na fila/render (98 % por vários minutos) |

Arquivos: `runtime/lote-runway/pagar-o-pato/teste-kling3.mp4` (+ keyframe, sheet.png, faces.png).

Avaliação: estilo cartum 2D plano fiel ao keyframe (contorno preto, cores chapadas), bem melhor que o gen-4-turbo. Personagem não fala nem faz lip sync; a boca muda de forma como reação (careta com dentes no início → "o" de espanto ~1,5–2,5 s → fechada no fim). Defeitos: zoom forte corta o vaso quebrado (contexto perdido), leve variação nos óculos/cabelo, resolução 716×1284 (abaixo de 720×1280 nativo exige upscale/pad), boca não fica 100 % fechada.
