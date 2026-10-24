# PROPOSTA — 8 papéis e habilidades (skills) por papel (t512–t515, 24/10/2026)

> **Status: PROPOSTA, não aplicada.** Nada aqui altera personas, skills, workflows ou serviços. Aplicar exige OK do José, papel por papel.

## 0. Base (princípios que valem para todos)
- **Temporal = sistema nervoso** (t514): toda decisão que exigiria humano e roda sozinha é determinística e passa pelo Temporal (durável, registrada, replay, retentativas, sinais). Sem camada de abstração sobre o Temporal.
- **Contratos Pydantic v2 = determinismo** (t515): entrada e saída de todo papel e motor por contrato de `src/pqbr/contratos/`, versionado em SemVer (`VERSOES`).
- **Motores trocáveis** (t513): `MotorIntelectual` (hoje NotebookLM) e `GeradorVideo` (hoje Flow; alternativas NotebookLM vídeo e Google Vids, sempre pelo navegador nas cotas já pagas). **Sem API Google (Gemini/Veo/Omni) e sem Meta Vibes** (t516), selecionados em `config/motores.json`. Papéis chamam a **porta**, nunca o serviço.
- **NotebookLM = motor editorial** (t512): temas, roteiros, decisões e direção do canal; **não gera vídeo**.
- **Agente só gera e valida**; efeito externo é activity separada. Personas: `company/agents/<papel>/AGENTS.md`; combos: `config/modelos_9router.json`.

## 1. Inventário (o que existe hoje)
| Item | Onde | Estado |
|---|---|---|
| Personas dos 8 papéis | `company/agents/{diretor,lider-editorial,pesquisador-origem,auditor,lider-compliance,guardiao-seguranca,observador,dev}` | `dev` nova (t512); demais ainda citam Paperclip/kit (`paperclip_*`) nas "Regras de execução" |
| Skills | `company/skills/pqbr-{contrato,direcao,editorial,auditoria,compliance,seguranca,observabilidade,dev,seo,arte,comunidade}` | texto da era Paperclip; `seo`, `arte`, `comunidade` ficam sem dono-agente |
| Playbooks | `company/playbooks/{nlm-auth,nlm-cadernos,camofox-sessao,camofox-watchdog,saida-invalida,tarefa-bloqueada}.md` | válidos |
| Motor NotebookLM | `src/pqbr/workflows/notebooklm.py` (notebooklm-py **0.8.4**, perfil `pqbr`, sessão do Camofox 9387) + porta `src/pqbr/motores/notebooklm.py` | ativo |
| Vídeo (Flow) | fila `camofox-pqbr` (`worker_camofox.py`), pós em `episodio-pqbr` | ativo; ainda não extraído para a porta `GeradorVideo` |
| Contratos | `src/pqbr/contratos/` (33, todos 1.0.0) | ativo |
| Kit MCP / agente_texto | `src/pqbr/kit/{mcp_kit,agente_texto}.py`, `scripts/paperclip/` | legado Paperclip (em retirada) |
| Jev | decisor/classificador estruturado | ativo |
| Hindsight | memória (`scripts/hindsight/`) | ativo |
| Run preso | `scripts/temporal/runs_presos.py` + timer | ativo (só journal) |

## 2. Achados da comunidade e atualizações (2025–2026)
| Tema | Achado | Impacto proposto | Fonte |
|---|---|---|---|
| notebooklm-py | 0.8.5 (12/10/2026): sessão deslogada deixa de aparecer como "CSRF token not found / page structure changed" e vira `Authentication expired`; captura headless/CDP recusa sessão deslogada sem sobrescrever a auth salva; `doctor` melhorado; journal de geração. Desde 0.8.0: servidores MCP e REST. | **Feito em t516** (0.8.5, `doctor` ok); simplificar `_AUTH_ERR`; usar `doctor` no canário. Avaliar o REST server como adaptador mais estável que o CLI. | https://github.com/teng-lin/notebooklm-py/releases |
| NotebookLM | Deep Research (relatório citado, 3–5 min) além de Fast; Video Overviews Short (~60 s), Explainer, Cinematic (só inglês/Ultra). API oficial (Enterprise) só cobre audio overview. | Pesquisador de Origem/etapa de temas: `add-research --mode deep` para temas novos; manter vídeo fora do NotebookLM (só alternativa da porta). | https://support.google.com/gemininotebook/answer/16454555 · https://blog.google/innovation-and-ai/products/notebooklm/generate-your-own-cinematic-video-overviews-in-notebooklm/ · https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-audio-overview |
| Flow / Veo | Veo 3.1 com 9:16 nativo e Ingredients to Video (imagens de referência = personagem consistente), upscale 1080p/4K. No Flow, só Veo 3.1 faz retrato; Veo 2 é só paisagem. | Adaptador Flow (navegador, cota já paga) fixa Veo 3.1 e 9:16 e falha fechado se o Flow trocar para Veo 2. Ingredients to Video para personagem consistente. | https://blog.google/innovation-and-ai/technology/ai/veo-3-1-ingredients-to-video/ · https://support.google.com/flow/answer/16893917 |
| Google Vids | Gera clipes 9:16 na UI; sem API REST oficial. | Só alternativa via Camofox, prioridade baixa (ADR-010). Meta Vibes e APIs Google: fora (t516). | https://support.google.com/docs/answer/16143507 |
| YouTube Data API | Shorts = `videos.insert` normal (vertical/quadrado ≤ 3 min); desde 01/06/2026 upload tem balde próprio de 100/dia (custo 1); demais métodos 10.000 unidades; thumbnail 50; `publishAt` só com `private`. | Contrato `DecisaoPublicacao`/upload: validar ≤ 180 s, 9:16, título ≤ 100, tags ≤ 500, `publishAt` só privado; canário de quota. | https://developers.google.com/youtube/v3/determine_quota_cost · https://developers.google.com/youtube/v3/docs/videos/insert |
| Camoufox | Mantido de novo em 2026 (v158.0-beta.40, 19/10/2026), ainda beta. | Fixar versão, testar upgrade no canário antes de trocar. | https://github.com/daijro/camoufox/releases |
| PydanticAI + Temporal | `TemporalDurability` (capability) substitui `TemporalAgent` (deprecated, sai na v3): chamadas de modelo/ferramenta viram activities automaticamente com `PydanticAIPlugin`. | Hoje usamos agente dentro de activity (simples e compatível com t514). Avaliar `TemporalDurability` só para agentes com ferramentas (Diretor/Dev), sem camada extra sobre o Temporal. | https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/ · https://github.com/pydantic/pydantic-ai/pull/4977 |
| Temporal + agentes | LLM/ferramentas/I-O em activities; humano por Signal/Update com timeout, validação de quem aprova, dedup e trilha (quem, motivo, quando). | Padrão de aprovação Telegram → sinal (F05-06) segue exatamente isso. | https://docs.temporal.io/ai/cookbook/human-in-the-loop-python · https://docs.temporal.io/design-patterns/approval |

## 3. Papéis (8)
Formato: missão · entradas → saídas (contratos) · ferramentas/skills (existente / melhorada / nova, com fonte) · combo · **NÃO faz**.

### 3.1 Diretor
- **Missão:** prioridades e direção do canal a partir do que o MotorIntelectual norteia; desbloqueio; resumo semanal ao José.
- **Entradas → saídas:** `ResumoSemanal` (métricas, falhas, runs presos, propostas pendentes) → `PropostaAgente` (prioridade/parâmetro) e `PedidoMotor(tarefa="direcao")`.
- **Skills:** `pqbr-direcao` (melhorada: sem contratação/pausa de agentes Paperclip; foco em Schedules e prioridades); `pqbr-contrato` (existente). Nova: `pqbr-direcao-motor` (perguntas de direção ao NotebookLM com fontes de métricas). Fonte: padrão de aprovação Temporal (https://docs.temporal.io/design-patterns/approval).
- **Combo:** `core-alto`.
- **NÃO faz:** publicar, mudar regra canônica, aprovar no lugar do José, mexer em infra.

### 3.2 Líder Editorial
- **Missão:** montar os pedidos ao MotorIntelectual (temas, roteiro, SEO, sazonais) e validar as respostas.
- **Entradas → saídas:** situação da grade → `PedidoMotor`; resposta → `PropostaTemas`, `RoteiroShort`, `PacoteSEO` (parse determinístico primeiro; LLM só para estruturar).
- **Skills:** `pqbr-editorial` (melhorada: absorve as etapas Roteirista/SEO/Caçador como *pedidos*, não como autoria), `pqbr-seo` (absorvida como regras de validação). Nova: `pqbr-pedidos-motor` (modelos de pergunta com JSON exigido; Deep Research para tema novo — https://support.google.com/gemininotebook/answer/16454555).
- **Combo:** `core-medio` (fallback `core-baixo`).
- **NÃO faz:** inventar tema/roteiro fora do motor, escrever no banco, gerar vídeo.

### 3.3 Pesquisador de Origem
- **Missão:** checar origem/etimologia e fontes do tema (≥ 2 fontes antes de aprovar).
- **Entradas → saídas:** `TemaPendente` + fontes do caderno (`nlm_fontes_urls`) → `VerificacaoOrigem` (nova; fontes, confiança, ressalvas).
- **Skills:** `pqbr-editorial` (parte pesquisa). Nova: `pqbr-origem-deep` (Deep Research via porta; https://github.com/teng-lin/notebooklm-py/releases).
- **Combo:** `core-medio`.
- **NÃO faz:** aprovar tema sozinho, usar fonte sem URL, pesquisar fora da porta do motor.

### 3.4 Auditor
- **Missão:** auditoria pré-publicação (roteiro, vídeo, capa, SEO) contra o CONTRATO; 3ª rodada com modelo distinto.
- **Entradas → saídas:** pacote do episódio → `VereditoAuditor`.
- **Skills:** `pqbr-auditoria` (melhorada: checagens de Shorts — 9:16, ≤ 180 s, metadados — https://developers.google.com/youtube/v3/docs/videos/insert). `pqbr-arte` (regras visuais) passa a ser referência do Auditor.
- **Combo:** `core-alto` (desempate `core-revisao`).
- **NÃO faz:** corrigir o que reprova, publicar.

### 3.5 Compliance (`lider-compliance`)
- **Missão:** políticas do YouTube, direitos, item 5, risco da conta; HOLD.
- **Entradas → saídas:** roteiro/pacote → `PontuacaoPolemica`, `SinalItem5`, `DecisaoPublicacao` (HOLD/segue).
- **Skills:** `pqbr-compliance` (existente; revisar trimestralmente contra políticas). 
- **Combo:** `core-medio` (segunda leitura `revisao`).
- **NÃO faz:** recorrer/apelar (José), apagar vídeo, publicar.

### 3.6 Guardião de Segurança
- **Missão:** segredos, permissões, injeção de prompt em fontes/respostas do motor, isolamento da identidade Google (Camofox 9387).
- **Entradas → saídas:** resposta de motor/fontes/logs → `ClassificacaoPopupCamofox`, `AlertaSeguranca` (novo).
- **Skills:** `pqbr-seguranca` (melhorada: varrer `RespostaMotor` por instruções injetadas antes do parse).
- **Combo:** `core-medio`.
- **NÃO faz:** login, mexer em cookies/sessão, mudar rede/exposição.

### 3.7 Observador
- **Missão:** saúde de conexões, saldos/quotas, runs presos, **deriva de contratos e de serviços web**.
- **Entradas → saídas:** resultados de canários, `usage --json`, quota YouTube, `runs_presos` → `RelatorioSaude` (novo), `Falha`.
- **Skills:** `pqbr-observabilidade` (melhorada). Nova: `pqbr-canarios` (ver §4). Fonte: notebooklm-py `doctor` 0.8.5.
- **Combo:** `core-baixo`.
- **NÃO faz:** corrigir, reiniciar serviço, abrir sessão.

### 3.8 Dev
- **Missão:** conhecer o sistema, **indicar problemas e propor soluções**; José aplica com agentes externos. **Vigia de atualizações (t516):** toda semana, pelo `VigiaAtualizacoesWorkflow` (Temporal), compara versão instalada × publicada de notebooklm-py, Camoufox, Temporal (SDK e CLI), PydanticAI, Pydantic e modelos dos combos do 9router, e entrega `RelatorioAtualizacoes` curto (uma linha por item: versão, risco patch/minor/major, proposta, link das notas). **Nunca aplica** (`aplicado` é sempre `False` no contrato).
- **Entradas → saídas:** `Falha`/histórico Temporal/testes/diff → `DiagnosticoDev` (novo: sintoma, causa com evidência, arquivos, patch proposto, testes, risco).
- **Skills:** `pqbr-dev` (melhorada: só diagnóstico e parecer; remove "corrigir em worktree"). Nova: `pqbr-vigia-atualizacoes` (esqueleto implementado: `src/pqbr/workflows/atualizacoes.py` + contratos `FerramentaVigiada`/`ItemAtualizacao`/`RelatorioAtualizacoes` + testes; falta registrar no worker e criar o Schedule semanal, com OK do José). Nova: `pqbr-contratos-deriva` (propõe bump SemVer e fixture nova quando o canário quebra).
- **Combo:** `core-alto` (segunda opinião `core-revisao`).
- **NÃO faz:** editar, commitar, reiniciar, mudar config, tocar segredos.

### Etapas de workflow (não são agentes)
Roteiro, SEO e Sazonais: activities que chamam `MotorIntelectual` com pedido do Líder Editorial e validam em `RoteiroShort`/`PacoteSEO`/`PropostaTemas`; reserva 9router (`roteirista`, `especialista-seo`, `cacador-sazonal`) só se o motor falhar. Comunidade: adiada.

## 4. Revisão contínua de contratos (t515)
1. **Fonte única + SemVer:** `src/pqbr/contratos/` + `VERSOES` (teste já obriga registro). Bump MAJOR exige migração/nota no CHANGELOG.
2. **Testes de contrato por adaptador:** cada adaptador web (NotebookLM, Flow, YouTube, Drive, Camofox) guarda respostas reais anonimizadas em `tests/fixtures/<adaptador>/` e um teste valida o parse → contrato. Mudou o formato → teste quebra no CI local.
3. **Canários periódicos (Schedule do Temporal, diário):** uma chamada barata e sem efeito por adaptador (NotebookLM: `doctor` + `list`; YouTube: `channels.list` 1 unidade; Flow: abrir projeto sem gerar; Drive: listar pasta). Resultado validado no contrato; falha → `Falha` registrada + Observador → aviso (Telegram quando houver token).
4. **Observador/Dev:** Observador detecta e classifica; Dev propõe a correção (contrato/adaptador/fixture + bump SemVer); José aplica.
5. **Revisão humana trimestral** das regras de serviço (políticas YouTube, limites NotebookLM/Flow) com lista de links da §2.

## 5. Decisões internas (t516)
- **Caderno semanal de temas** (`Short - grade-temas-<ano>w<semana>`): passa pelo fluxo de descarte existente (`DescartarCadernoTesteWorkflow`: exportar → 3 cópias verificadas → apagar pelo id). Pré-requisito: registrar o caderno em `pqbr.cadernos_episodio` na criação (hoje só os de episódio são registrados) — implementar junto com o Schedule.
- **`mcp_kit.PAPEIS`** atualizado para os 8 papéis (legado em retirada).
- **8 papéis confirmados**; `pqbr-assistente` fica fora (persona do canal); Comunidade adiada.

## 6. Dúvidas para o José
1. Google Vids pelo navegador (cota do plano já pago) continua como alternativa ou também sai?
2. Pasta `contratos` (atual) ou renomear para `contracts`?
3. Ligar o Schedule semanal do vigia de atualizações (dia/hora)?
4. Camoufox: discussão própria (pin de versão, beta).
