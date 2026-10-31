# PROPOSTA — revisão da skill `produ-o-short-b1-notebooklm` (t532)

Proposta não aplicada: o José grava a skill. A skill atual está em `/home/box/agent-data/workflows/produ-o-short-b1-notebooklm/SKILL.md` (box, herdada do YT-LLM, set/2026).

## O que está desatualizado
| # | Trecho atual | Problema | Fonte vigente |
|---|---|---|---|
| 1 | Passo 7 "Generate Studio → Video Overview → Short" | O NotebookLM **não gera vídeo** | DECISOES t512; ROADMAP 4V |
| 2 | "VOX/papercut style", 4.2 "prefer papercut / kraft collage" | O estilo é **Stickman** (papercut abortado) | REGRAS §6 (t465) |
| 3 | Passo 1 "notebooklm auth check" no box; notebooklm-py do box | Sessão só no venv isolado da PQBR no servidor pc e no Camofox 9387; o box não tem mais o binário (t532) | REGRAS §10–§11, t516 |
| 4 | Cadernos owned "Produção/Episódio/Channel Clone" usados direto | Caderno **efêmero** por roteiro/semana, nunca o mestre; produção nunca no raiz | REGRAS §9, adr-003 |
| 5 | "pilot 3–5 posts/day", "Schedule 19h30" | A cadência vem da grade Temporal; publicação **só dry-run** até a F8 | ROADMAP F8 |
| 6 | Passo 8 "trim ~2.5s NotebookLM end card" | Sem vídeo do NotebookLM não há end card; o pós vale para a saída de Flow/Vids/Meta Vibes (overlay v8 e logo v4) | ROADMAP 4V |
| 7 | "skill only orchestrates and posts" | A orquestração é do **Temporal**; a skill não publica | ADR-011, t514 |
| 8 | Prompt 4.3 com áudio gerado no NotebookLM | Narração e áudio ficam a cargo da rota de vídeo e do pós | CONTRATO v2 |
| 9 | Nenhuma menção a contrato, Auditor, Compliance, HOLD nem Telegram | Saída precisa caber em contratos Pydantic; HOLD + sinal `decisao_video` | t515, t529 |
| 10 | Pro "~20 VO/day" | Cotas só medidas por `usage --json` | REGRAS §9 (t465) |

## Texto proposto (SKILL.md novo)
```markdown
---
name: Produção Short PQBR (motor NotebookLM + vídeo pela cadeia 4V)
description: >-
  Use when preparing a Porquê BR (PQBR) Short: NotebookLM (ephemeral notebook)
  only for theme, script, direction, SEO and the storyboard prompts; video via
  the browser chain Flow → Google Vids → Meta Vibes → HOLD, orchestrated by
  Temporal in the PQBR repo on server pc. Never generate video in NotebookLM.
---
# Produção Short PQBR

## Fonte de verdade
Repo `jvmendesjr/PQBR` (`/home/pc/Workspace/PQBR`). Ler antes: `docs/REGRAS.md`, `docs/CONTRATO-EDITORIAL.md`, `docs/ROADMAP.md` (Fase 4V), `docs/BRIEFING-novo-agente-pqbr.md`.
Em conflito, o repo prevalece sobre esta skill.

## Etapas (cada uma é uma activity do Temporal, não um passo manual)
1. **Tema:** vem da `ReposicaoTemasWorkflow` (`PropostaTemas`). Nicho B1, curiosidade do Brasil, série/bloco. Um vídeo, avaliar e só então refazer.
2. **Roteiro e direção (motor NotebookLM):**
   - caderno **efêmero** clonado, nunca o mestre nem o raiz; 1 a 3 fontes do tema;
   - prompts Fábrica 1.1–4.2 adaptados (PT-BR, Stickman, 40 a 55 s);
   - saída validada pelo Líder Editorial no contrato Pydantic.
3. **Storyboard em série (método GUÍA VOX):**
   - beats de 2,5 a 3 s, com 2 a 4 movimentos críticos por cena;
   - `.txt` com um prompt por bloco, separados por linha em branco, sem números;
   - bloco de estilo Stickman repetido e prompt de animação universal;
   - imagens nomeadas e em ordem.
4. **Vídeo (pelo navegador, nas cotas já pagas, sem APIs de geração):**
   - Flow primeiro, depois Google Vids, depois Meta Vibes;
   - se as três falharem, **HOLD** e pedido no Telegram, respondido pelo sinal `decisao_video`.
5. **Pós:** overlay v8 e logo v4; legenda alinhada ao áudio (Auditor confere: palavras puladas = FAIL).
6. **Gate pré-publicação** fail-closed (`gate-pr-publish-porqu-br`) + Auditor + Compliance. Publicação **só dry-run** até a F8; live só com ordem explícita do José.
7. **Higiene:**
   - descartar o caderno efêmero;
   - registrar a decisão no DECISOES-LOG e no CHANGELOG quando aplicável.

## Regras duras
- Nunca gerar vídeo no NotebookLM.
- Sessão Google só no Camofox PQBR 9387 e no notebooklm-py isolado do pc. Nenhum login em outro navegador; sem re-login headless.
- Cotas só medidas (`usage --json`); sem números estimados.
- Sem dado inventado; fonte citada; explicar o sistema ≠ aconselhar.
- Nunca imprimir segredos ou cookies; publicar ou enviar só com OK do José.
```
