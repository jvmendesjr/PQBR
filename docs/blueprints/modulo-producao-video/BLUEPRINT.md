> **t516 (José, 24/10/2026):** sem API Google (Gemini/Veo/Omni, inclusive free tier) e sem Meta Vibes. O sistema usa só cotas já pagas pelo navegador (Flow, NotebookLM). Trechos abaixo que citam essas opções estão descartados.

# Blueprint — Módulo de Produção de Vídeo

> **Estado:** proposta documental; não implementado.
> **Data da pesquisa-base:** 2026-10-14. **Atualização documental de acesso/uso:** 2026-10-17; proposta, sem implementação ou geração.
> **Escopo desta entrega:** desenho do módulo, papéis, contratos, fases, riscos e critérios de teste. Não instalar extensões, alterar código/configuração, autenticar contas, criar conectores, fazer uploads ou publicar.

## 1. Síntese executiva

Construir um módulo de produção **orientado por contratos e independente de provedor**. **Google Flow é a rota principal; Google Vids é uma camada adicional e fallback**. Gemini Web fica como terceiro candidato e Meta Vibes como quarto/futuro. O primeiro ciclo consolida/testa Flow e verifica o caminho de fallback Vids, um de cada vez, sem publicação. O **Temporal** executa os workflows e efeitos; o **Paperclip** é a superfície de controle, agentes, issues e trilha de auditoria. Nenhum agente aciona diretamente os provedores nem publica.

O caminho de geração é implementado como adapters versionados e determinísticos, chamados pelo Temporal através da sessão autorizada do Camofox. Os agentes de plataforma, se vierem a ser necessários, não substituem adapters ou contratos. A equipe transversal existente observa, mantém, revisa, protege e avalia conformidade; cada plataforma recebe um perfil/runbook/skill versionado.

O piloto é exclusivamente **Short de 50–70 segundos**, com storyboard e clipes em série. A cadência de dois Shorts por dia não é prometida por nenhuma quota; só poderá ser avaliada após medir limites reais, taxa de retrabalho e custo no Flow e no fallback Vids.

O blueprint preserva pesquisa profunda, fontes, persona e roteiro canônicos no pacote durável; NotebookLM continua sendo a ferramenta de pesquisa e roteiro por meio de cadernos efêmeros. A produção visual passa pelos provedores candidatos. O long-form fica para uma especificação posterior separada.

As extensões e a aplicação Darkplanner são **referências conceituais**, não componentes do PQBR. Podem inspirar fila por cena, estados legíveis, vínculos com referências, reconciliação de jobs e visibilidade de versões; seus mecanismos de browser, interceptação e controle não serão copiados.

## 2. Premissas, decisões e gates

### Decisões consolidadas

1. Instruções técnicas de geração podem ser compostas em **inglês**; roteiro, narração, identidade e texto final permanecem em **português brasileiro**.
2. NotebookLM continua responsável por pesquisa profunda, fontes, síntese e roteiro canônico. O pacote canônico versionado é a fonte de verdade, não um caderno mestre permanente; episódios usam cadernos efêmeros e arquivam os resultados nos locais duráveis definidos pelo projeto.
3. O piloto usa somente **50–70 segundos**; a referência a 50–70 minutos está superada para este escopo. Long-form não será desenhado nem produzido neste módulo-piloto.
4. Identidade visual-alvo: stickmen e fichas de personagens, objetos e cenários consistentes, com ID, origem, versão/hash e direitos. Essa é uma decisão aprovada (t465); a implementação das fichas/resolvedor ainda precisa ser verificada e planejada.
5. CTA contextual: usar trocadilho ligado ao tema quando natural; caso contrário, convite natural a seguir o canal, com “Segue o Porquê BR” como fallback. Nunca pedir comentários.
6. Narração em terceira pessoa, com voz/ID ElevenLabs selecionado/aprovado; efeitos sonoros por ação/timecode; **sem música**.
7. A marca PQBR é um selo editorial separado da marca/proveniência do provedor. Nenhum processo remove, corta, cobre ou falsifica uma marca do provedor.
8. Hierarquia: Flow é primário; Vids é camada adicional/fallback; Gemini Web vem depois e Meta Vibes é a última opção. Este ciclo consolida/testa Flow e verifica Vids como fallback; Gemini Web e Vibes ficam explicitamente abertos para ciclos posteriores.

### Gates que precisam ser resolvidos antes de assumir operação em escala

- **Elegibilidade e quota Vids:** a documentação atual contém limites descritos como “até 50 vídeos por mês” para a maioria dos usuários e também limite de “até 500 segundos de clipes por mês” em informação de disponibilidade; há diferenças por conta/plano. Não somar esses valores como dois orçamentos. O limite aplicável à conta e à região deve ser confirmado na própria UI antes do piloto e medido durante ele.
- **Capacidade versus cadência:** dois Shorts diários de 50–70 s cobertos com clipes de 10 s exigiriam cerca de 300–420 gerações ou 3.000–4.200 segundos por mês. Isso excede a referência pública do Vids; o plano não garante que Vids, sozinho, sustente a cadência.
- **Exportação Vids:** a ajuda oficial confirma que o projeto final pode ser compartilhado como MP4 baixado no dispositivo ou no Drive, e há exportação direta ao YouTube. Para preservar o Vids como fallback e minimizar dependências, compor no próprio Vids e baixar apenas o MP4 final no piloto; não pressupor extração/uso externo dos clipes gerados individualmente.
- **Watermark Vids:** o anúncio oficial consultado descreve SynthID imperceptível, mas não confirma marca visual sobreposta. “A mesma solução do NotebookLM” não define por si só um procedimento permitido para marca visível. Verificar a saída real e usar o selo PQBR sem remover, cortar ou cobrir proveniência.
- **Integração existente:** documentos de fluxo ainda apontam pendências da ponte Paperclip/Temporal e do E2E. Nenhuma produção real começa até a primeira tarefa aplicável do Roadmap e os gates operacionais passarem.
- **Roster Paperclip:** os documentos descrevem perfis no pacote da empresa, mas a consulta somente leitura ao Paperclip ao vivo retornou HTTP 400. Portanto, o elenco ativo não foi confirmado; não atribuir tickets nem afirmar contratação/ativação com base somente no pacote.

Não há decisão sobre provedor principal/fallback após o piloto. Comparação por qualidade, quota efetiva, custo, disponibilidade, política e possibilidade de retomada precede qualquer decisão de portfólio.

## 3. Limites de escopo

### Incluído no blueprint

- Um contrato visual e editorial de episódio que possa ser enviado a mais de um provedor.
- Adapters separados para Flow e Vids no primeiro ciclo, chamados pelo Temporal através da UI autorizada em Camofox; Gemini Web e Meta Vibes ficam reservados para avaliação futura.
- Preparação de storyboard/referências, geração em fila, ingestão local, controle de tentativas, QC, montagem, áudio e registro de artefatos.
- Medição de créditos/limites, falhas, qualidade por clipe, tempo para geração e taxa de seleção.
- Papel de Paperclip, Temporal, Pydantic v2, Camofox, Postgres, Drive, FFmpeg e agentes.

### Fora do escopo

- Instalar ou executar extensões de terceiros; reproduzir requests privados, bypass de quotas, CAPTCHA, rate limits ou controles da Meta/Google.
- Fazer login, solicitar credenciais/API keys, mudar configuração de conta/Watermark, abrir conta ou comprar plano.
- Alterar código do PQBR, contratos existentes, configurações canônicas, Paperclip, Schedules, banco ou Roadmap.
- Fazer upload, cross-post, publicação, agendamento ou compartilhamento público.
- Tratar disponibilidade/cotas de qualquer provedor como ilimitadas; assumir quota do Vids sem conferir a conta; assumir que um tutorial reflete a UI/limites atuais ou usar contorno de watermark/proveniência.

## 4. Arquitetura-alvo

```text
Paperclip (painel, agentes, issues, ownership, auditoria)
          │ propostas/estados estruturados; sem efeito externo direto
          ▼
Temporal — VideoProductionWorkflow / EpisodioWorkflow
          │ contratos Pydantic v2; execução durável, fila, retries, sinais
          ├── pesquisa/narrativa: pacote canônico + NotebookLM efêmero via atividade notebooklm-py
          ├── pré-produção: fichas visuais + storyboard + prompts por cena + narração/SFX
          ├── ProviderAdapter selecionado, um por vez
          │      ├── FlowAdapter (primário) ── Camofox → UI oficial → artefato permitido
          │      ├── GoogleVidsAdapter (fallback) ─ Camofox → composição no Vids → MP4 final
          │      ├── GeminiWebAdapter ──── futuro, não neste ciclo
          │      └── MetaVibesAdapter ───── futuro, não neste ciclo
          ├── ingestão/ledger: hash, cena, referência, origem, tentativa, quota e QC
          └── montagem conforme rota: FFmpeg para material permitido fora do Vids;
              Vids compõe seus clips e exporta o MP4 final pela opção oficial
                    │
                    └── Postgres de negócio / arquivo Drive só na etapa autorizada
```

### Divisão de responsabilidades

- **Paperclip — plano de controle:** issues por episódio e por mudança de plataforma; fase, provedor, tentativas, consumo observado, bloqueios, owners, runbooks e evidências não sensíveis. Não substitui o ledger nem executa geração.
- **Temporal — plano de execução:** máquina de estados, filas, concorrência, idempotência, retries, timers e efeitos externos. Persistência de negócio em Postgres via outbox; nenhum agente lê diretamente o Postgres do Temporal.
- **NotebookLM / notebooklm-py:** Activity serializada do Temporal para pesquisa profunda e roteiro em caderno efêmero, com fontes/canonical package injetados e resultados arquivados. O Roteirista é o dono editorial; NotebookLM não é um agente separado.
- **Camofox:** única automação de browser autorizada para os sites e contas aprovados, com as regras de sessão e serialização existentes. Não criar perfil paralelo nem copiar cookies entre serviços.
- **FFmpeg:** composição local de material cujo uso/exportação externa esteja permitido; não usar para remover marca ou proveniência.
- **Google Vids:** rota própria, que pode compor o vídeo dentro do Vids. O pipeline não assume baixar clipes gerados e editá-los em FFmpeg antes de verificar a permissão e o fluxo oficial.
- **Postgres/Drive:** Postgres mantém o estado operacional/ledger; o pacote canônico e fontes ficam nos destinos duráveis já definidos. Drive só recebe artefatos conforme fluxo e autorização do projeto.

### Adapter comum e perfis de plataforma

Interface conceitual `VideoProviderAdapter`:

- `capabilities()`: entradas, aspect ratios, durações, áudio, edição/exportação e limitações observadas.
- `preflight(request)`: aplicar o contrato de acesso/uso proposto da §6 antes de qualquer submissão: perfil PQBR exclusivo, conta/titularidade, consentimento/privacidade, quota/custo e autorização específica da etapa. Acesso não equivale a permissão para gerar; fallback Vids exige seu próprio pré-voo.
- `submit(scene_request)`, `wait(job_ref)`, `collect(job_ref)`, `inspect(artifact)`, `cancel_if_supported(job_ref)`.
- Retornar `ProviderJob` e `ArtifactRecord` com origem, versão do adapter, hash do request, tempos, quota observada e evidência não sensível.
- Em timeout ambíguo, reconciliar histórico/artefatos antes de repetir; não criar duplicata.
- Interface inesperada, limite, desafio ou bloqueio gera `SITE_CHANGED`/`PAUSED_QUOTA`/`PAUSED_AUTH`, issue e pausa; sem contorno ou repetição cega.

Adapters: `FlowAdapter` (primário) e `GoogleVidsAdapter` (fallback) no primeiro ciclo. `GeminiWebAdapter` e `MetaVibesAdapter` são candidatos futuros, não fluxos prontos. Manter um `PlatformProfile` versionado por produto com domínio oficial, rota autorizada, capacidades, quotas/limites, termos/políticas observados, sessão, owner, runbook, data/fonte de verificação, smoke tests, changelog e plano de pausa/rollback. Um perfil/skill por plataforma **não implica um agente exclusivo por plataforma**.

## 5. Papéis dos agentes, plataformas e memória

| Agente/papel documentado | Encaixe no módulo | Recomendação |
|---|---|---|
| Diretor | Prioriza issues e exceções; coordena o fluxo no Paperclip. | Reaproveitar; não gerar nem executar provider. |
| Líder Editorial | Grade, tema, variedade e CTA contextual. | Reaproveitar; sem pedidos de comentários. |
| Pesquisador de Origem | Pesquisa verificável e contexto cultural. | Reaproveitar. |
| Roteirista | Orquestra pesquisa/roteiro NotebookLM-first e produz storyboard/prompt por cena. | Reaproveitar; NotebookLM permanece Activity serializada, não um agente por si só. |
| Diretor de Arte 2D (pausado no documento) | Stickmen e fichas de personagem, objeto e cenário. | Reativar o perfil existente de forma controlada antes de executar esse papel; verificar status ao vivo primeiro. Não criar agente de arte duplicado. |
| Auditor | QC técnico/editorial/visual, consistência das fichas, fala↔cena, segurança e relatório tipado. | Reaproveitar; ajustar o teste para stickmen e cada provider. |
| Líder Compliance | Política, direitos, restrições e HOLD. | Reaproveitar; validar condição de uso/exportação Vids antes de integrar. |
| Observador | Sessão, disponibilidade, quotas, falhas, tempos e resultados; detecção de alterações. | Reaproveitar; observar e abrir issues, não editar adapters nem corrigir dados. |
| Guardião de Segurança | Segredos, escopo de sessão, prompt injection e atividade fora da allowlist. | Reaproveitar; bloquear/escalar, sem operar produção. |
| Dev Corretor | Implementa/mantém adapters, contratos, runbooks de recuperação e testes; registra lições sanitizadas no Hindsight. | Reaproveitar, com branch/worktree e testes. |
| Dev Revisor | Revisão independente dos changesets e testes. | Reaproveitar. |
| Especialista SEO, Comunidade e Caçador Sazonal | SEO, comunidade e pautas sazonais. | Permanecem no ecossistema, fora da produção visual neste piloto. |

### Recomendação sobre agentes exclusivos por plataforma

Não criar agora um agente para cada produto. A especificidade deve começar em `PlatformProfile` e skills/runbooks versionados — `flow`, `google-vids`, `gemini-web` (futuro), `meta-vibes` (futuro), `youtube-studio` e `notebooklm-py` — vinculados aos papéis existentes. A divisão por produto evita misturar instruções e cotas sem multiplicar agentes, credenciais, custos, sessões ou ownership. Observador detecta mudanças; Dev Corretor atualiza adapter/testes; Dev Revisor revisa; Compliance trata política/uso; Guardião cobre segurança.

Reavaliar um novo agente “Operações de Plataformas” ou especialistas exclusivos somente depois dos pilotos, se a frequência de mudança, fila de manutenção, escopo de conhecimento ou necessidade de independência justificar capacidade distinta. Uma contratação passa pelo processo de sugestão do Diretor/owner de trilha/José documentado; não é criada por este blueprint. O desenho `docs/AGENTES.md` descreve 14 agentes operacionais e o pacote inclui ainda `pqbr-assistente` como perfil de canal fora do organograma; nenhum desses dados comprova o roster ativo ao vivo.

### Hindsight e gestão do conhecimento

Não adicionar agora um agente “guardião de memória”: `docs/AGENTES.md` já define HS-01 — **Dev Corretor** mantém o bank `pqbr` (reindexação/consolidação diária, deduplicação e poda com backup), **Observador** mede hit rate, staleness, duplicatas e crescimento e abre issue se a rotina não rodar; **Guardião de Segurança** trata segredos/PII. Essa separação evita que quem mede também corrija. Hindsight armazena aprendizados sanitizados; segredos/PII nunca entram.

Para evitar confundir memória com estado operacional: workflow, job, quota observada e artifact ledger pertencem a Temporal/Postgres; instruções canônicas, skills/runbooks e platform profiles são versionados em seus locais próprios; Hindsight guarda lições recuperáveis e sanitizadas. O “conhecimento vivo” significa verificação de frescor, deduplicação, recuperação relevante e aplicação em tarefas — não inserir indiscriminadamente todas as memórias em cada prompt. Mudanças em regras canônicas continuam sob o gate do José.

O ownership ao vivo ainda depende de validar a organização Paperclip: a consulta somente leitura atual falhou com HTTP 400. Até essa consulta funcionar, as responsabilidades acima são o desenho documental, não status verificado de contratação/ativação.

## 6. Contratos de dados propostos

Schemas abaixo são nomes/intenções para validação futura; nenhum código foi criado.

- `VideoProductionRequest`: `production_id`, `episode_code`, `format` (`short`/`long_form`), duração-alvo, idioma, persona hash, fonte/roteiro versionado, lista de provedor(es) permitidos, limite operacional aprovado, `dry_run`.
- `EpisodeCreativePlan`: capítulos/cenas ordenados, objetivo narrativo, proporção, referência visual e hashes, prompt em inglês por cena, fala PT-BR, ficha/ID de assets, timecodes de narração/SFX, zonas seguras de marca.
- `SceneGenerationRequest`: ID idempotente, `scene_id`, provider, prompt hash, referências permitidas, requisitos de duração/aspect ratio, proibições (sem fala dos personagens; sem música; não inventar texto), nota de áudio opcional, origem/direitos dos inputs.
- `ProviderCapabilities` e `QuotaObservation`: plano/feature visível, modalidade, limite ou saldo observado, unidade (créditos, segundos, tentativas ou desconhecido), momento da leitura, fonte (UI oficial/ajuda/relato comunitário), confiança e validade. `unknown` é válido; não somar limites concorrentes nem converter anedota em cota.
- `PlatformProfile` / `PlatformChange`: domínio oficial, login/rota autorizada, capabilities, limites/políticas, owner, runbook/skill e hash/version; cada mudança recebe fonte/evidência, data, impacto, status de verificação e próxima ação. Não tratar changelog manual como monitor automático.
- `ProviderJob`: ID local, referência visível ao job, idempotency key, estado, timestamps, tentativa, mensagens normalizadas, necessidade de intervenção e snapshot não sensível.
- `ArtifactRecord`: caminho temporário, SHA-256, mime/codec/dimensões/duração, provedor, prompt/schema/pacote hashes, job, cena, custo observado, metadados de watermarks/proveniência, estado de QC e decisão de retenção.
- `QualityReview`: integridade técnica, fidelidade ao roteiro, consistência de personagem/objetos/cenário, legibilidade mobile, áudio, direitos/risco, defeitos e nota por métrica; separar defeitos de segurança (bloqueadores) de preferências editoriais.
- `ProductionManifest`: ordem de cenas, escolhas/rejeições de variantes com justificativa, cortes, narração/SFX, mapeamento de marca, versão FFmpeg/presets, saídas e checksum.

### Contrato proposto de pré-voo de acesso e uso — Flow/Vids

Este contrato complementa `VideoProductionRequest`, `PlatformProfile`, `QuotaObservation` e `ProviderJob`; **é proposta documental**, não schema implementado, aprovação canônica nova ou aceite operacional. Flow permanece principal e Vids fallback. A leitura/navegação autorizada e o aceite de um aviso não autorizam criar projeto, enviar arquivos, gerar mídia, consumir créditos, comprar plano ou publicar.

**Campos propostos, a versionar na Fase 1 do roadmap do módulo:**

| Vínculo existente | Dados mínimos propostos (sem segredos/PII) |
|---|---|
| `PlatformProfile` | Produto/domínio oficial; instância `pqbr-camofox`, endpoint `127.0.0.1:9387`, `userId=pqbr`, perfil persistente e fila `camofox-pqbr`; referência protegida à conta esperada e resultado da conferência de conta/titularidade na UI, sem nome/e-mail no ledger. |
| `VideoProductionRequest` | Escopo da ação (`access_only` ou geração especificamente autorizada), provedor/cenas/prompts e referências por hash/versão, modelo/duração/variantes, orçamento máximo aprovado e referência da autorização humana autenticada, com autoria, instante e validade/escopo. Mudança material exige nova autorização. |
| `QuotaObservation` | Produto/feature/modelo; plano e saldo/limite **visíveis** com unidade, instante/fuso, fonte oficial e referência de evidência sanitizada; custo previsto por geração e renovação/janela separadamente, com `unknown` quando ausentes. Saldo não é quota garantida nem autorização. Não converter créditos Flow em quota Vids. |
| Resultado de `preflight` vinculado ao request/job | Referência do aviso/versão de privacidade visível, decisão/autorização de consentimento e pós-condição; marketing e pesquisa `false`; estado de conta/consentimento/quota/custo (`confirmed`/`unknown`/`blocked`), evidências e motivo de pausa; separar `access_ready` de `generation_ready`. `unknown` é dado válido, mas não libera geração. |

**Sequência/gate proposto antes do primeiro uso e novamente antes de gerar:**

1. **Sessão exclusiva:** usar somente o mesmo perfil persistente `userId=pqbr` da instância PQBR em `127.0.0.1:9387`. O Camofox global em `9377` é de outro contexto e fica fora desta rota; não criar perfil/processo/login paralelo, copiar/capturar sessão nem interceptar cookies. A implementação futura segue Activity Temporal/fila serializada, sem alegar que as pendências F4C-05/06/08 já foram resolvidas.
2. **Conta e titularidade pela UI oficial:** comparar a identidade autenticada com a conta de produção autorizada e conferir elegibilidade/assinatura quando expostas. Identidade exibida não prova sozinha direitos sobre inputs ou titularidade contratual; divergência ou vínculo incerto pausa em `PAUSED_AUTH` e exige esclarecimento do proprietário. Não trocar conta automaticamente.
3. **Privacidade/consentimento antes do primeiro uso:** ler o aviso e aceitar somente no escopo humano autorizado, mantendo marketing e pesquisa desativados. Rolar pelo fluxo normal para habilitar o botão, clicar uma vez e verificar a pós-condição; não forçar controles nem presumir aceite porque houve clique. Novo aviso, opção obrigatória inesperada, opt-in incerto ou ausência de pós-condição pausa em `PAUSED_REVIEW` (ou `PAUSED_AUTH` se envolver autenticação). O aceite específico já informado em 17/10 está registrado na §9; não é consentimento genérico para avisos futuros.
4. **Quota e custo:** conferir na UI oficial plano/feature, saldo/quota/unidade, custo do modelo/duração/variantes e janela/renovação aplicável; registrar fonte, data/hora e evidência sanitizada. Ausência ou contradição permanece `unknown`. Não assumir custo zero, franquia renovada, limite público ou capacidade diária. Com quota/custo necessário incerto, pausar em `PAUSED_QUOTA`; renovação não visível impede depender de uma janela futura presumida. Não gerar para descobrir o custo.
5. **Autorização específica de geração:** somente após os gates existentes e pré-voo válido, exigir autorização humana autenticada que vincule provedor, cenas/prompts, referências, modelo/variantes e teto de consumo/custo. Permissão para navegar/aceitar privacidade, plano PRO ou créditos visíveis não bastam. Sem autorização válida, manter `PAUSED_REVIEW`; não criar projeto/job, não gerar mídia nem acionar fallback. Upload e publicação continuam sujeitos a permissões separadas.
6. **Revalidação e prova:** mudança de conta, consentimento, saldo, custo, modelo ou interface invalida a liberação afetada. Revalidar antes da ação; registrar o motivo e pausar se houver incerteza. Evidência contém somente dados mínimos sanitizados/referência protegida; nunca cookies, tokens, sessão, nome/e-mail ou screenshot bruto com PII. A foto de acesso da §9 não fecha smoke, teste operacional ou produção.

**Fila, estados e reconciliação:** aproveitar somente os padrões conceituais permitidos da §8: painel derivado de Temporal/Postgres; vínculo estável produção↔cena↔prompt↔referência (IDs/hash/versão)↔job↔artefato; uma operação idempotente por cena/variante. Após timeout/ACK incerto, reconciliar apenas por leitura da UI/histórico/artefato antes de considerar nova submissão; sem certeza, preservar pendência e pausar, sem repetir o efeito. Não prometer exactly-once externo nem mudar a política operacional de exceções por esta proposta.

**Proibições preservadas da §8:** nada de extensões executadas, requests privados, interceptação de requests/cookies, captura de sessão, hooks (inclusive `fetch`/XHR/telemetria), execução de tokens de CAPTCHA, bypass de CAPTCHA/bloqueios/quotas ou ocultação de automação. Desafio ou bloqueio pausa e escala, sem contorno, conta secundária ou repetição cega.

Cada tabela/linha deve registrar quem/qual componente fez a ação, `workflow_id`, tentativa, timestamps e versão de contrato. Nunca registrar senha, cookie, token, prompt privado ou PII em log/ticket.

## 7. Workflow, estados e retomada

Estados sugeridos: `REQUESTED` → `RESEARCH_READY` → `SCRIPT_READY` → `VISUAL_ASSETS_READY` → `STORYBOARD_READY` → `PLATFORM_PREFLIGHT` → `QUEUED` → `GENERATING` → `ARTIFACTS_INGESTED` → `QC_PENDING` → `QC_PASSED`/`QC_REJECTED` → `RENDER_READY` → `RENDERED_LOCAL` → `TEST_COMPLETE`.

Terminais de controle: `PAUSED_QUOTA`, `PAUSED_AUTH`, `PAUSED_SITE_CHANGE`, `PAUSED_REVIEW`, `FAILED_RETRYABLE`, `FAILED_FINAL`. Publicar/upload nunca é transição automática do módulo-piloto.

Regras de execução:
0. `PLATFORM_PREFLIGHT` só libera `QUEUED` de geração com conta, consentimento, quota/custo e autorização específica válidos conforme §6. Acesso confirmado sem autorização de geração permanece sem submissão; o fallback Vids não herda a liberação do Flow.

1. Um workflow por produção e um job por cena/variante, com idempotency key estável. Uma repetição só é permitida após verificar que o job/artefato anterior não existe ou foi explicitamente classificado como inválido.
2. Camofox é serializado; a sessão Google existente mantém seu dono e fila únicos. Testes Meta usam sessão/conta Meta aprovada, sem cruzar cookies. Nenhuma sessão duplicada ou `userId` improvisado.
3. Política do provedor governa a cadência. Se a interface exibir limite, erro de risco, desafio, login expirado ou bloqueio: suspender fila, registrar, abrir issue no Paperclip e não tentar contornar com delays alternativos, conta secundária ou prompts artificiais.
4. Retry é limitado, com backoff e sinal claro; não fazer loop cego. No erro parcial, retomar da cena faltante e preservar artefatos aprovados; nunca apagar todos os resultados de uma rodada para recomeçar.
5. Ingestão valida arquivo, checksum, metadados e vínculo cena↔prompt antes do QC. O fluxo termina em artefato local para testes; upload/publicação exigem autorização posterior específica.

## 8. Aprendizados do Darkplanner e das extensões

### Padrões conceituais úteis para o PQBR

- **Fila e painel de produção:** a extensão DarkPlanner demonstra uma fila de projetos/prompt com estados, progresso, tentativas e logs locais; a aplicação tem Kanban/checklists por vídeo. Aproveitar a ideia de visualizar fase, owner, estado, tentativa e evidência. No PQBR, a fonte de verdade deve continuar sendo Temporal/Postgres; não criar um estado manual concorrente no Paperclip nem usar IndexedDB como ledger.
- **Vínculo cena↔prompt↔referência:** projeto, personagens e frames separados sugerem preservar IDs e versões de referências por cena. Implementar isso nos contratos e artefatos do PQBR, com stickmen e fichas próprias, sem assumir que a `ReferenciasPage` do Darkplanner já faz essa função — o componente fornecido cadastra referências de canais/nichos e notas, não fichas visuais de personagem/objeto/cenário.
- **Retomada e reconciliação:** após timeout, procurar job/artefato existente por identificador/metadados antes de repetir; retomada apenas na cena faltante e preservação de resultados aprovados. Nome do arquivo não substitui ID idempotente.
- **Changelog de plataformas:** `PlatformUpdatesPanel.jsx` oferece CRUD para versões e itens de mudança. É um exemplo de registro curado, não monitor automático de sites. No PQBR, combinar registro com Observador detectando alterações, evidência/data, impacto e issue para Dev Corretor/Compliance conforme domínio.
- **Skills/documentação:** o gerenciador de skills sustenta a ideia de instruções e referências por plataforma com rótulos e versões; criar um registry versionado que distingue draft, testado, obsoleto e fonte. Não inferir que uma edição da UI valide ou publique uma skill no Paperclip.
- **Prova operacional:** usar checklists de QC por episódio e por cena; o estado visível deriva do estado do workflow e não de checkbox editável como autoridade.
- **Áudio:** a aplicação separa biblioteca/preview de vozes e edição SRT; isso pode inspirar separação de faixas e metadados. O contrato PQBR continua específico: ElevenLabs, terceira pessoa, PT-BR, efeitos por ação/timecode, sem música.

### Não copiar da extensão nem presumir do dossiê

A inspeção estática da extensão DarkPlanner mostra `manifest.json` com permissões amplas e scripts no mundo `MAIN`, interceptação de `fetch`/XHR, leitura/captura de chamadas privadas do Flow e download automático de resultados; o runner inspeciona estado interno de reCAPTCHA e tenta executar tokens programaticamente; também desativa diálogos de saída. Esses mecanismos não entram no PQBR. Não reproduzir requests privados, interceptação de sessão, hooks de telemetria, CAPTCHA, bypass de bloqueios ou comportamento que esconda automação.

A extensão e o dossiê também mencionam configuração remota de seletores, filas simultâneas e técnicas de automação que não são política de taxa/limite para a conta do José. No PQBR, apenas UI oficial autorizada via Camofox, concorrência controlada pelo Temporal e limites/cadência mostrados pelo provedor. Se um desafio, quota ou mudança de UI bloquear o fluxo, pausar e registrar.

O dossiê reconstruído do Darkplanner contém recomendações de scraping, fingerprinting e proxy/CORS; não as reutilizar. O código fornecido não é auditoria de segurança independente nem autoridade sobre condições de serviço do Google/Meta. Nenhum arquivo do Darkplanner foi executado ou modificado nesta análise.

## 9. Provedores, cotas, custos e marcas d’água

Informações consultadas em **2026-10-14**. Condições podem mudar; a UI e a conta autorizada decidem a disponibilidade efetiva.

| Provedor | Fato documentado/observado | Implicação para o módulo |
|---|---|---|
| **Google Flow** | A ajuda oficial lista 50 créditos diários para assinantes e não assinantes e 1.000 créditos mensais adicionais no AI Pro. Custos variam por modelo/resolução/duração e por geração; há variantes adicionais. | Flow é a rota principal. Fazer preflight, registrar modelo/saldo e consumo após cada job; 360p/720p e variantes mudam a capacidade. Não fixar custo universal nem usar crédito do Flow como cota de Gemini Apps/Vids. |
| **Google Vids** | A ajuda oficial descreve clips gerados de 3–10 s, 24 fps, 720p/1080p, 16:9 ou 9:16 e até 7 imagens de referência. A página de geração informa até 50 vídeos/mês para a maioria dos usuários; a página de disponibilidade também apresenta até 500 segundos de clipes/mês, e limites variam por conta/plano. O blog Google de 2026-09-23 anuncia Gemini Omni 1.1 Flash, acesso sem custo e SynthID imperceptível. A ajuda oficial também confirma exportação do vídeo final como MP4 baixado no dispositivo/Drive ou diretamente ao YouTube. | Vids é camada adicional e fallback. Tratar 50 clipes/mês e 500 s/mês como referências não cumulativas; confirmar a franquia na UI. Compor dentro do Vids e baixar o MP4 final pelo recurso oficial; não pressupor extração individual de clips de IA para FFmpeg. Não pressupor marca visível; preservar SynthID/proveniência. |
| **Gemini Web (Gemini Apps)** | Candidato terceiro, não no ciclo atual. A ajuda de contas pessoais exige plano Google AI para vídeo; limites são compute-based, renovam em janela e não há contagem fixa universal de vídeos/dia. A configuração de marca visível é específica do Gemini Apps e não governa Flow/Vids. | Adapter de browser separado; não inferir capacidade do Gemini a partir dos créditos Flow. Só planejar teste depois de Flow/Vids, confirmando UI, quota, watermarks e política na conta. |
| **Meta Vibes** | Quarto candidato/futuro, não no ciclo atual. A Meta não publica no material consultado uma contagem universal diária aplicável à conta; relatos comunitários variam. | Manter `daily_quota=unknown`; nenhum agente tenta substituir silenciosamente outro provider, nem contorna bloqueio/limite. Primeiro preflight e smoke se o usuário decidir abrir essa fase. |

### Pré-voo observado em 17/10/2026 — fotografia, não quota operacional

**Fonte/evidência:** atualização recebida do proprietário/coordenador nesta sessão em **2026-10-17T20:14:18-03:00**, relatando navegação nas UIs oficiais Flow/Vids pelo Camofox próprio PQBR. Registro textual sanitizado; esta edição documental não repetiu navegação nem produziu captura de tela. A conta exibida foi conferida como a conta autorizada do proprietário; nome/e-mail não são reproduzidos no repositório. Esta evidência não é auditoria independente de titularidade ou dos gates operacionais.

| Plataforma/item | Observação relatada | Limite/pendência |
|---|---|---|
| Flow — privacidade | Autorização humana para prosseguir no mesmo aviso; rolagem normal habilitou “Continuar”, clicado uma única vez. Marketing e pesquisa permaneceram desmarcados; não apareceu outro consentimento. Flow abriu após a ação. | Onboarding desse aviso confirmado pelo relato, sem inferir consentimento para avisos futuros ou para geração. |
| Flow — conta/plano/saldo | Conta esperada exibida; rótulo **PRO** e **1.050 créditos** visíveis. | Fotografia de saldo naquela leitura; não limite recorrente, promessa de capacidade nem autorização de consumo. **Custo por geração e data de renovação não mostrados**, seguem `unknown`/por confirmar. |
| Vids — acesso | UI abriu na mesma conta/perfil PQBR; rótulo **“Assinatura do Google”**. | Plano específico, quota/saldo, custo e renovação não confirmados; não inferir PRO ou franquia por analogia ao Flow. |
| Efeitos | Nenhum projeto aberto/criado; nenhuma mídia gerada/alterada e nenhum consumo de créditos relatado. | Nenhum smoke de geração, teste operacional, implementação ou produção concluído. Autorização específica de geração segue ausente. |

O acesso/consentimento observado pode informar o futuro pré-voo, mas **não libera geração**. Confirmar custo/renovação Flow, quota/condições Vids e demais gates/autorização antes de qualquer efeito; não gerar mídia para preencher essas lacunas.

### Impacto preliminar da cota Vids

Dois Shorts diários de 50–70 s representam 60 Shorts/mês, ou aproximadamente **3.000–4.200 segundos de vídeo final**. Se cada Short usar cinco a sete clipes de até 10 s, são **300–420 gerações de clipe/mês**. As referências públicas do Vids (até 50 clipes/mês e/ou 500 s/mês, dependendo da documentação/conta) ficam muito abaixo disso; a referência de 500 s equivale a cerca de 7–10 Shorts completos de 50–70 s antes de refações. Isso não invalida um piloto do Vids, mas impede prometer que ele sustente sozinho dois vídeos diários. A escolha de cadência/fallback exige medir a cota, confirmar o plano e avaliar produção híbrida permitida.

### Watermark e proveniência

- Para Google Vids/Omni, o anúncio oficial fala em **SynthID imperceptível** em cada clipe; não confirma logotipo/marca visual aplicada ao quadro. Confirmar a aparência real no smoke; não remover, recortar ou cobrir marca/proveniência do provedor.
- Manter o selo PQBR como marca editorial distinta, em zona segura que não se sobreponha à informação de origem, às legendas, ao personagem ou à ação importante.
- A marca visual de Gemini Apps, quando presente e permitida pelas preferências oficiais, é independente de SynthID/C2PA e não deve ser confundida com comportamento de Flow/Vids. Não programar mudança da configuração nem técnicas de remoção.
- A frase do usuário “usar a mesma solução do NotebookLM” não especifica qual técnica nem confirma que ela seja permitida pelo Vids; registrar como gate para discutir após ver a saída oficial, não como instrução de ocultar marca.

### Sources e validade

A documentação oficial de quota/funcionalidade descreve limites distintos por conta/plano. `QuotaObservation` deve armazenar o valor realmente visível, unidade, hora, conta/feature sem PII, fonte e confiança; sem valor visível, tratar como `unknown` e limitar-se à leitura autorizada; geração/smoke permanece bloqueada até satisfazer o contrato proposto da §6.

## 10. Visual, áudio e pós-produção

### Referências visuais

- Restaurar/usar fichas de **stickmen, personagens, objetos e cenários**, com IDs estáveis, origem, licença/direitos, versão e checksum; gerar novas fichas somente para cobrir lacunas e depois de revisão do responsável.
- Cada storyboard vincula `scene_id` ao `character_id`/`object_id`/`setting_id`, versão da ficha, prompt, ação, composição/câmera, fala e artefato. Um personagem principal por padrão; descrição visual literal consistente entre cenas.
- Não inferir que a página “Referências” do Darkplanner implementa esse banco: o trecho inspecionado contém referências de canais, nichos e notas. O PQBR necessita um modelo visual próprio.
- Storyboard por cena com uma ação observável, enquadramento, luz, cenário e aspecto; ordem e continuidade são validadas antes de qualquer submissão.

### Áudio e CTA

- Roteiro/narração em terceira pessoa e PT-BR, gerados no ElevenLabs com o ID de voz selecionado/aprovado. Efeitos pontuais indicados no roteiro por ação/timecode, sem música.
- CTA contextual: trocadilho ligado ao tema quando natural; fallback para convite a seguir, por exemplo “Segue o Porquê BR”. Nunca pedir comentários.
- Áudio nativo do provedor é opcional e comparativo; falas não aprovadas ou música são bloqueadas, silenciadas/substituídas apenas em fluxo permitido e validado.

### Montagem e QC

- Flow: render local/FFmpeg apenas com os artefatos cujo download/uso externo seja permitido. Vids: compor/montar dentro do Vids e baixar o MP4 final pelas opções oficiais de compartilhamento; não presumir que clipes gerados individualmente possam ser retirados e processados em FFmpeg.
- Normalizar frame rate, aspecto, áudio e duração conforme o provider/saída permitida; salvar somente em área de teste local e registrar hash.
- Selo PQBR em safe zone determinística; não encobrir marca, identificador ou conteúdo de proveniência do provedor.
- QC técnico: decode, duração/aspect/codec, ausência de duplicatas por retry, áudio esperado, sincronismo SFX, ausência de frame preto/silêncio inesperado, carimbo fora de áreas de ação/legendas/marca e hash estável.
- QC editorial: narrativa fala↔cena, consistência de stickmen/fichas, continuidade, legibilidade mobile, adequação cultural, gancho e encerramento; segurança/direitos são bloqueadores.

## 11. Plano de validação e critérios de aceite

Todo piloto é **não publicável**: sem postagem no YouTube, upload público, compartilhamento público ou gravação no Drive. Esta atualização documental apenas registra o relato de acesso/consentimento da §9, sem acessar conta ou executar teste; a fase de teste exige as permissões/acessos previstos no projeto e seguirá o gate de sessão.

1. **Pré-condições:** resolver na ordem aplicável as lacunas Paperclip/Temporal e o bloqueio do E2E; verificar status da organização Paperclip; preparar atualização canônica controlada para stickmen/fichas e atualizar testes/prompts no procedimento próprio. Não marcar estas lacunas concluídas por este blueprint.
2. **Consolidar Flow:** um provider, uma sessão, uma cena; confirmar preflight, envio/espera/coleção permitida, IDs/idempotência, consumo e recuperação sem duplicata. Expandir para 5–7 cenas apenas após critérios passarem.
3. **Testar Flow (primeiro):** mesma fixture visual/editorial PQBR; primeiro uma cena, depois Short 50–70 s. QA da consistência visual, alinhamento roteiro, áudio SFX, export permitido, montagem e retomada. Nenhuma publicação.
4. **Verificar Vids como fallback:** mesma fixture e critérios; testar uma cena, confirmar quota e contabilização, recursos, 9:16, duração, referências, marca/proveniência e composição na UI do Vids; então baixar o MP4 final pelas opções oficiais e validar o arquivo local. Expandir para Short apenas se a quota permitir; sem exceder nem contornar o limite.
5. **Gemini Web e Meta Vibes:** permanecem explicitamente abertos para depois da comparação Flow/Vids; cada um exige perfil/adaptador, preflight e smoke independentes, com sessão/conta correta e pausa ao limite. Não criar logins paralelos nem roteamento automático sem evidência.
6. **Comparação controlada:** mesmo roteiro, storyboard, referências e QC; comparar provider, duração, custo/quota, taxa de falha/retry, consistência, tempo total e caminho de exportação permitido. Não decidir pela melhor variante isolada.
7. **Testes automatizados:** schemas, hashes, IDs, quotas por unidade, mocks de UI/erros, replay Temporal, outbox, timeout ambíguo, pausa por limite/auth/site changed e retomada de cena pendente. Testar assets sem publicação.
8. **Aceite do piloto:** zero upload/publicação; nenhum segredo/PII em logs; nenhum retry cego/duplicata; todos artefatos com origem/hash/cena/provider; consumo e quota observáveis registrados; relatório de QC, limites, qualidade, latência, falhas e retrabalho; o vídeo deve ficar pronto para revisão editorial, sem afirmar que já foi publicado.

## 12. Fases sugeridas para implementação posterior

| Fase | Entrega | Gate |
|---|---|---|
| 0 — pré-condições e contrato | Confirmar Paperclip/Temporal/Camofox, fechar ponte/E2E; revisar elegibilidade e permissões Vids, quotas da conta, watermark/proveniência e saída; preparar alteração canônica versionada de stickmen/fichas. | Sem login extra ou mudança de conta; gates de sessão, quota, uso/export e contrato definidos; nenhuma alteração à regra canônica sem o processo do José. |
| 1 — consolidar Flow | Contrato/adaptador/atividade Flow e instrumentação, sem extensão de terceiros. | Preflight, fila, consumo, artefatos permitidos, idempotência, pausa e retomada aprovados. |
| 2 — testar Flow | E2E não publicável de uma cena, depois Short 50–70 s com 5–7 cenas. | QC técnico/editorial; zero publicação/upload. |
| 3 — verificar fallback Google Vids | `GoogleVidsAdapter` e perfil; smoke/composição dentro do Vids; medir quota e baixar MP4 final pela função oficial. | Saída local validada e quota conhecida; nenhum bypass de limite/proveniência. |
| 4 — validar fallback | Mesma fixture; confirmar qualidade e confiabilidade do Vids quando Flow está indisponível/limitado, sem trocar silenciosamente de rota. | Vids só é selecionado dentro do workflow e do preflight aprovados; não prometer dois Shorts/dia sem quota suficiente. |
| 5 — candidatos posteriores | Gemini Web, depois Meta Vibes; perfis e adapters separados, nenhum teste neste ciclo. | Usuário decide avançar; eligibility, quota, watermark/termos e sessão confirmados em cada smoke. |
| 6 — long-form | Contrato/capítulos/estratégia de cobertura e orçamento separados. | Aprovação da duração, volume, custos e permissões antes de ampliar. |

A necessidade de agentes específicos por plataforma será reavaliada após as fases 2–4 com métricas reais de fila/manutenção; não é pré-requisito do módulo.

## 13. Pré-condições e registro de trabalho existente

- `docs/AGENTES.md` descreve 14 papéis operacionais, Diretor de Arte 2D pausado, e HS-01 para Hindsight; o pacote `company/agents/` inclui também `pqbr-assistente` como perfil de canal fora do organograma. A consulta ao roster Paperclip ao vivo retornou HTTP 400; estado de contratação/ativação permanece **não verificado**.
- `docs/ARQUITETURA.md` define Temporal como executor durável, Paperclip como camada de agentes/painel, Camofox com concorrência 1, Postgres do app separado de Temporal e Hindsight como banco único de memória da organização.
- `docs/ROADMAP.md` e `docs/LACUNAS-fluxo.md` registram pendências de integração/login do Paperclip e E2E bloqueado pela ponte. Este blueprint não altera a ordem, não autentica a CLI, não conclui nem marca tarefas.
- A inspeção foi estática, sobre documentação e cópias de texto/código fornecidas. Extensão/app Darkplanner não foram executadas nem alteradas; nada foi instalado, autenticado, enviado ou publicado.
- O working tree de PQBR já continha alterações fora deste escopo, incluindo `docs/REFERENCIA-sessao-google.md` e `docs/pesquisas/arquivo-cadernos/f757e751_ep1001-descartado/`; ambos permanecem intocados. A pasta `docs/blueprints/` e este documento já existiam como não rastreados no início da revisão; não foi feita limpeza nem commit.
- Antes de implementar, seguir a ordem normativa do projeto e registrar novas tarefas no Roadmap conforme seu processo. Este documento é blueprint, não uma mudança a REGRAS, SPEC, contratos canônicos, empresa Paperclip ou configuração de conta.

## 14. Fontes consultadas

### Google Flow, Vids e Gemini Apps

- [Google Flow Help — Manage your Google Flow credits](https://support.google.com/flow/answer/16526234?hl=en) — créditos e custos observados para Flow.
- [Google Vids Help — Use AI to generate video clips](https://support.google.com/docs/answer/16143507?hl=en) — formatos, 3–10 s, até 7 imagens, e referência de até 50 clipes/mês para a maioria dos usuários.
- [Google Vids Help — Get started with Google Vids](https://support.google.com/docs/answer/15082958?hl=en) — confirma compartilhar o vídeo final como Vids, MP4 no Drive, MP4 baixado no dispositivo ou vídeo do YouTube.
- [Google Workspace Updates — Export Google Vids directly to YouTube](https://workspaceupdates.googleblog.com/2026/04/export-google-vids-directly-to-youtube.html) (2026-04-02) — exportação direta; saída fica privada inicialmente.
- [Google Vids Help — Availability of Gemini features](https://support.google.com/docs/answer/15609411?hl=en) — disponibilidade por tipo de conta e referência de limite em segundos; confirmar qual limite vale para a conta real.
- [Google Workspace — About AI usage limits](https://knowledge.workspace.google.com/admin/generative-ai/workspace-with-gemini/about-ai-usage-limits) — cotas mensais em segundos por edição Workspace, atualizada em 2026-10-13; não transpor automaticamente para conta pessoal AI Pro.
- [Google Blog — Anyone can make stunning HD videos with Gemini Omni in Google Vids](https://blog.google/products-and-platforms/products/workspace/gemini-omni-in-google-vids/) (2026-09-23) — Gemini Omni 1.1 Flash, acesso e SynthID imperceptível.
- [Google Vids Help — AI labels & content credentials](https://support.google.com/docs/answer/17560328?hl=en) — Content Credentials e proveniência.
- [Gemini Apps Help — Limits & feature availability](https://support.google.com/gemini/answer/16275805?hl=en) — limites compute-based do Gemini Apps.
- [Gemini Apps Help — Manage watermark settings](https://support.google.com/gemini/answer/17405358?hl=en) — configuração de marca visível no Gemini Apps, separada de SynthID/C2PA.
- [Google — 5 tips for getting started with Flow](https://blog.google/innovation-and-ai/products/flow-video-tips/) — prompts de câmera, referências e áudio experimental.
- [Google Cloud — Ultimate prompting guide for Veo](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1) — composição cinematográfica em linguagem natural.

### PQBR e materiais fornecidos

- `docs/AGENTES.md`, `docs/ARQUITETURA.md`, `docs/TESTES.md`, `docs/ROADMAP.md`, `docs/LACUNAS-fluxo.md` e `docs/CONTRATO-EDITORIAL.md` (documento de contexto; REGRAS/SPEC mantêm precedência).
- `/home/pc/Workspace/extensoes/darkplanner/ARQUITETURA_E_FUNCIONAMENTO.md` e os arquivos textuais `source/manifest.json`, `source/background.js`, `source/src/flow/interceptor.js`, `source/src/flow/content-bridge.js`, `source/src/sync/main-captcha-runner.js`, `source/src/ui/sidepanel.js`.
- `/home/pc/Workspace/darkplanner/ARQUITETURA_E_FUNCIONAMENTO.md`, `README.md`, `server.js` e componentes `KanbanVideoModal.jsx`, `PlatformUpdatesPanel.jsx`, `SkillAdminModal.jsx`, `ReferenciasPage.jsx`, `Modelagem.jsx` e `AudioGeneratorPage.jsx`.
- Instruções e decisões do usuário em `/home/ubuntu/upload/pasted_content_12.txt`; referências anteriores sobre persona, stickmen/fichas e áudio incorporadas conforme escopo já confirmado.
