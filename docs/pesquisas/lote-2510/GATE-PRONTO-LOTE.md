# Gate pré-publish — lote-2510 (25/10/2026)

Tratamento ordinário sem geração paga. Fail-closed: todos em **P1_HOLD** até juiz Gemini (A4–A8, VISUAL+LOOP) e editorial B1–B10 (título, descrição, tags, fontes, disclosure GenAI). Técnico A1–A3 e A9 local passaram. Capa = frame do próprio vídeo (sem thumb custom, sem geração). Nada publicado.

| tema | pronto | duração s | status |
|---|---|---|---|
| cafe-fraco | `runtime/lote-saldo/cafe-fraco/cafe-fraco-pronto.mp4` | 43.48 | P1_HOLD |
| fechadura | `runtime/lote-saldo/fechadura/fechadura-pronto.mp4` | 40.16 | P1_HOLD |
| formiga | `runtime/lote-saldo/formiga/formiga-pronto.mp4` | 42.7 | P1_HOLD |
| crostinha | `runtime/lote-saldo/crostinha/crostinha-pronto.mp4` | 33.9 | P1_HOLD |
| garrafa | `runtime/lote-saldo/garrafa/garrafa-pronto.mp4` | 36.44 | P1_HOLD |
| brigadeiro | `runtime/lote-saldo/brigadeiro/brigadeiro-pronto.mp4` | 45.79 | P1_HOLD |
| liquidificador | `runtime/lote-saldo/liquidificador/liquidificador-pronto.mp4` | 45.12 | P1_HOLD |
| nao-e-bem-assim | `runtime/lote-saldo/nao-e-bem-assim/nao-e-bem-assim-pronto.mp4` | 39.78 | P1_HOLD |
| olhos-da-cara | `runtime/lote-saldo/olhos-da-cara/olhos-da-cara-pronto.mp4` | 45.44 | P1_HOLD ~7 s de imagem parada no fim (clipes < voz). |

## Correção ERR-MON-02 — CTA personalizado (25/10/2026, 0.3.19)
Os prontos v1 de 6 temas fecharam com o CTA genérico B. Gerado o CTA original de cada roteiro ([cheerful], eleven_v3, Larissa, speed 1,1, 1 take cada, Whisper sem erro), emendado após ~0,3 s com fades de 30 ms, remontado com os mesmos clipes (sem quadro congelado), legendado e com pós ordinária. Vigente = `-pronto-v2.mp4`. cafe-fraco, garrafa e liquidificador: CTA original já é "Segue o Porquê BR" (fallback literal) → v1 vigente. Todos seguem **P1_HOLD**.

| tema | CTA | créditos | duração s | alinhamento legenda | pronto v2 |
|---|---|---|---|---|---|
| crostinha | Segue o Porquê BR pra não ficar na rapa do conhecimento... e corre antes que raspem a panela! | 103.99 | 38.5 | 108/114 | `runtime/lote-saldo/crostinha/crostinha-pronto-v2.mp4` |
| nao-e-bem-assim | Segue o Porquê BR, porque na hora de discordar, não é bem assim que se perde o amigo! | 95.99 | 43.08 | 125/125 | `runtime/lote-saldo/nao-e-bem-assim/nao-e-bem-assim-pronto-v2.mp4` |
| brigadeiro | Pra não perder o ponto, Segue o Porquê BR! | 52.99 | 45.36 | 115/127 | `runtime/lote-saldo/brigadeiro/brigadeiro-pronto-v2.mp4` |
| fechadura | Tranca essa ansiedade na chave e segue o Porquê BR! | 61.99 | 41.98 | 111/112 | `runtime/lote-saldo/fechadura/fechadura-pronto-v2.mp4` |
| olhos-da-cara | Fica de olho e segue o Porquê BR. | 44.0 | 46.47 | 127/129 | `runtime/lote-saldo/olhos-da-cara/olhos-da-cara-pronto-v2.mp4` |
| formiga | Segue o Porquê BR pra essa fila de curiosidades ficar mais doce antes que fechem o pote de açúcar! | 108.99 | 47.44 | 125/127 | `runtime/lote-saldo/formiga/formiga-pronto-v2.mp4` |

Total: 467.95 créditos ElevenLabs (teto informado 450; excedido em ~22 porque os 6 takes foram disparados juntos antes da soma; nenhum retake).


## Rerun do gate com códigos PQBR-EP (25/10/2026, 0.3.20)
Códigos, SEO/fontes do NotebookLM (sessão do Camofox), juiz Gemini VISUAL via Camofox (2 rodadas, humanizado), Drive `PQBR/02_Episodios/2026-10/<código>_<slug>` e Postgres `pqbr.temas_pendentes` (status em_producao, metadados.codigo/seo/gate). Todos seguem **P1_HOLD**: o pedido LOOP do juiz não existe no repo (LACUNAS). Nada publicado.

| código | tema | título (NotebookLM) | juiz VISUAL | Drive | Postgres | status |
|---|---|---|---|---|---|---|
| PQBR-EP1008 | nao-e-bem-assim | Por que a gente fala 'não é bem assim' pra discordar? | aprova_com_ressalva | ok | ok | P1_HOLD |
| PQBR-EP1002 | olhos-da-cara | Por que a gente fala que algo custa 'os olhos da cara'? | aprova_com_ressalva | ok | ok | P1_HOLD |
| PQBR-EP1003 | cafe-fraco | Por que chamamos café fraco de chá de bico de chaleira? | aprova_com_ressalva | ok | ok | P1_HOLD |
| PQBR-EP1004 | formiga | Por que as formigas andam em fila reta até o açúcar? | terceira_rodada | ok | ok | P1_HOLD |
| PQBR-EP1006 | fechadura | Por que o brasileiro confere a fechadura 3 vezes antes de sair? | terceira_rodada | ok | ok | P1_HOLD |
| PQBR-EP1009 | garrafa | Por que o brasileiro põe garrafa de água no relógio de luz? | aprova_com_ressalva | ok | ok | P1_HOLD |
| PQBR-EP1010 | crostinha | Por que a gente raspa a panela de arroz até a crostinha? | aprova_com_ressalva | ok | ok | P1_HOLD |
| PQBR-EP1007 | brigadeiro | Por que o brigadeiro só existe no Brasil? | reprova | ok | ok | P1_HOLD |
| PQBR-EP1005 | liquidificador | Por que o liquidificador tem 15 velocidades se usamos só 2? | aprova_com_ressalva | ok | ok | P1_HOLD |


## Gate com LOOP do juiz Gemini (25/10/2026, 0.4.3)
Gate determinístico `pipeline/gate_publicacao.py`. LOOP via Camofox 9387 (humanizado, modelo **3.8 Flash** fixado e conferido antes de cada envio; pranchas 360 px compostas em 3 anexos). Brigadeiro adiado. Nada publicado.

| código | tema | LOOP | imagem×fala / capa×título / loop | status | bloqueios | motivos do juiz (até 4) |
|---|---|---|---|---|---|---|
| PQBR-EP1008 | nao-e-bem-assim | pendente | — | P1_HOLD | loop_gemini_ausente | — |
| PQBR-EP1002 | olhos-da-cara | pendente | — | P1_HOLD | loop_gemini_ausente | — |
| PQBR-EP1003 | cafe-fraco | pendente | — | P1_HOLD | loop_gemini_ausente | — |
| PQBR-EP1004 | formiga | pendente | — | P1_HOLD | loop_gemini_ausente | — |
| PQBR-EP1006 | fechadura | pendente | — | P1_HOLD | loop_gemini_ausente | — |
| PQBR-EP1009 | garrafa | pendente | — | P1_HOLD | loop_gemini_ausente | — |
| PQBR-EP1010 | crostinha | pendente | — | P1_HOLD | loop_gemini_ausente | — |
| PQBR-EP1007 | brigadeiro | pendente | — | P1_HOLD | tema_adiado; loop_gemini_ausente | — |
| PQBR-EP1005 | liquidificador | pendente | — | P1_HOLD | loop_gemini_ausente | — |
