# Manus — modelos disponíveis (consulta 2026-10-25, ~20:31 BRT)

- Tarefa: SsrDXTJh9jeW7CkFdr7gFW (https://manus.im/app/SsrDXTJh9jeW7CkFdr7gFW), privada, visível no painel.
- Chamada: API v2 `POST https://api.manus.ai/v2/task.create`, header `x-manus-api-key` (env `MANUS_API_KEY` da box), `agent_profile: lite` (Flex; registrado como `manus-1.6-lite`), sem conectores.
- Custo: 16 créditos. Nenhuma geração feita.

## Vídeo (todos aceitam 9:16 e imagem de referência)
| Modelo | Duração/resolução | Referências |
|---|---|---|
| Seedance 2.5 | 4–30 s; 480p/720p | até 30 imgs (+vídeo/áudio) |
| Seedance 2.0 | 4–15 s; 720p/1080p | até 9 |
| Seedance 2.0 Fast | 4–15 s; 720p | até 9 |
| Veo 3.1 / Veo 3.1 Fast | 4/6/8 s; 720p/1080p | 1 |
| Gemini Omni Flash | 3–10 s; 720p | 1 (primeiro quadro) |
| MiniMax H3 | 5–15 s; 768p/1080p | até 9 (referência OU primeiro/último quadro) |

## Imagem (todas 9:16, com referência)
GPT Image 2.5; Nano Banana Pro (2K, até 5 refs); Nano Banana 2 (2K, até 5 refs); Nano Banana 2.1; Nano Banana 2 Flash Lite; `default` (auto).

## Custo por clipe/imagem
Manus não informou: não há tabela fixa pública nem campo na ferramenta; consumo varia por plano/complexidade/duração. Ver no painel autenticado.

## Pular confirmação manual de mídia
Não há opção documentada (sem `skip_confirmation`/`auto_confirm`). Imagens prontas podem ir como `references`/`keyframes`, mas a confirmação segue o fluxo do app.

## Observação
A API v2 não tem endpoint de listagem de modelos de mídia; `agent_profile` aceita `lite`, `standard`, `max*` (docs: https://open.manus.ai/docs/api-reference/create-task). Referência de imagem 9:16 deve ser realmente vertical.

## Teste Seedance 2.0 Fast 15 s — pagar-o-pato (25/10/2026, ~20:45 UTC-3)

- Tarefa Manus: https://manus.im/app/e4JD2jERXkgErNQ5WeMADq (API v2, agent_profile `standard`, interactive_mode=false)
- Runway: 3 keyframes nano-banana-2.1 9:16 (768x1376), saldo 1437 -> 1425 (12 cr). Arquivos `kf-manus-{1,2,3}.png` (box). Descartados por mudança do José (refs devem vir do GPT Image 2.5 no Manus).
- Manus turno 1 (refs Runway): chamada Seedance 2.0 Fast "cancelada antes de criar o job"; nenhum vídeo.
- Manus turno 2: GPT Image 2.5 gerou 3 refs 9:16 reais 1440x2560 (`manus-gptimg25-ref{1,2,3}.png`), praticamente edições das refs Runway, agora com boca fechada. Vídeo cancelado de novo da mesma forma; nenhuma confirmação/estimativa de mídia apareceu na API (sem evento `waiting` de confirmação).
- Hipótese: com `interactive_mode=false` a confirmação manual de mídia é auto-cancelada. Próximo teste (exige OK do José): `interactive_mode=true` e responder via `task.confirmAction`, ou disparar pelo app.
- Sem mp4; freezedetect não aplicável. Créditos Manus: conferir no painel (refs GPT Image 2.5 + 2 turnos standard).
