> **t516 (José, 24/10/2026):** sem API Google (Gemini/Veo/Omni, inclusive free tier) e sem Meta Vibes. O sistema usa só cotas já pagas pelo navegador (Flow, NotebookLM). Trechos abaixo que citam essas opções estão descartados.

# Roadmap faseado — Módulo de Produção de Vídeo (PQBR)

> **Estado:** plano de execução proposto; não representa implementação concluída.
> **Data-base:** 2026-10-14. **Atualização documental de acesso/uso:** 2026-10-17; contratos/gates propostos, sem geração.
> **Destino canônico:** `docs/blueprints/modulo-producao-video/ROADMAP.md`.
> **Blueprint de referência:** `docs/blueprints/modulo-producao-video/BLUEPRINT.md`.
> **Escopo deste arquivo:** ordenar a implementação, tornar dependências e gates explícitos e oferecer um checklist atualizável. Não altera código, contratos canônicos, regras, contas ou configurações.
> **Autoridade:** checklist auxiliar do módulo; o estado oficial de tarefas, próximo passo e gates do projeto continua em `docs/ROADMAP.md`; as regras superiores permanecem em `docs/REGRAS.md`.
> **G0 do módulo:** aceite por José em 2026-10-15. Este registro confirma o gate do roadmap de produção de vídeo, mas não marca como concluídos os itens técnicos da Fase 0 nem autoriza geração real, upload ou publicação.

## 1. Direção e limites já definidos

- **Hierarquia de provedores:** Google Flow como rota principal; Google Vids como camada adicional/fallback; Gemini Web como terceiro candidato; Meta Vibes como quarto/futuro.
- **Piloto:** um Short de **50–70 segundos**, storyboardado em cenas/clipes sequenciais. Começar com uma cena; ampliar para 5–7 cenas somente depois de passar os gates da cena única.
- **Sem publicação e sem uploads nos testes:** não publicar, agendar, fazer cross-post, compartilhar publicamente, gravar no Drive ou enviar arquivos de teste aos provedores. Os artefatos de teste ficam locais. Se um teste depender de upload de arquivo, ele fica bloqueado e deve usar mocks/fixtures locais ou aguardar autorização específica.
- **Agentes e execução:** Paperclip é plano de controle; Temporal coordena execução durável; adapters versionados executam operações do provedor por meio da sessão autorizada do Camofox. Agentes não chamam provedores nem publicam diretamente.
- **Proveniência:** não remover, recortar, cobrir ou falsificar marcas ou credenciais de conteúdo dos provedores. O selo PQBR é editorial e separado.
- **Sem promessa de escala:** não assumir que o Vids sustenta dois Shorts por dia. Cotas públicas não são aditivas; disponibilidade e saldo precisam ser medidos na conta e região reais.
- **Escopo futuro:** Gemini Web, Meta Vibes e long-form não fazem parte deste ciclo. Cada um requer decisão e planejamento próprios.

## 2. Estado inicial e progresso comprovado

Os itens marcados abaixo registram decisões/diagnósticos documentais e evidências do projeto. **No marco inicial deste roadmap, nenhuma entrega técnica do módulo estava confirmada como concluída.** A seção de voz abaixo registra a integração TTS posterior, implementada e testada em mocks em 2026-10-17, sem ativar geração real. Os demais checkboxes continuam condicionados às evidências e gates próprios.

| Situação inicial | Estado | Evidência registrada |
|---|---:|---|
| Blueprint do módulo existe e se declara proposta documental, não implementação. | [x] | `docs/blueprints/modulo-producao-video/BLUEPRINT.md`, §§ 1, 6, 13. |
| Hierarquia Flow → Vids → Gemini Web → Meta Vibes e piloto Short 50–70 s estão definidos. | [x] | Blueprint, §§ 1–2 e 12. |
| Piloto sem publicação e sem uploads está definido como restrição. | [x] | Contexto da tarefa e blueprint, §§ 3 e 11. |
| Pendências da ponte Paperclip/Temporal e do E2E estão registradas. | [x] | Blueprint, §§ 2 e 13; também aponta `docs/ROADMAP.md` e `docs/LACUNAS-fluxo.md`. **O diagnóstico está documentado; a integração não está concluída.** |
| Consulta ao roster Paperclip ao vivo falhou com HTTP 400; estado ativo permanece desconhecido. | [x] | Blueprint, §§ 2, 5 e 13. **Isto comprova a lacuna, não a confirmação do roster.** |
| Contratos/adapters propostos e fluxo de vídeo implementados. | [ ] | Blueprint, § 6, diz que os schemas são propostas e nenhum código foi criado; verificar novamente no checkout antes de executar tarefas. |
| Ponte Paperclip/Temporal e E2E funcionais. | [ ] | Blueprint, § 13, registra essas pendências. |
| Elegibilidade, quota e exportação efetivas do Flow/Vids verificadas na conta do piloto. | [ ] | Blueprint, §§ 2, 9 e 11: confirmar na UI oficial e medir durante o piloto. |
| **Este roadmap redigido como artefato de planejamento.** | [x] | `docs/blueprints/modulo-producao-video/ROADMAP.md`, versão inicial de 2026-10-14. |
| Sincronização deste arquivo no checkout oficial. | [x] | Arquivo verificado em `docs/blueprints/modulo-producao-video/ROADMAP.md` no repositório PQBR em 2026-10-14. |

### Pré-voo Flow/Vids observado — 2026-10-17 (parcial; sem aceite técnico)

Fonte: atualização do proprietário/coordenador em `2026-10-17T20:14:18-03:00`, relatando UI oficial via instância PQBR; registro sanitizado detalhado em [Blueprint — pré-voo observado](BLUEPRINT.md#pré-voo-observado-em-17102026--fotografia-não-quota-operacional). Esta edição não repetiu navegação nem obteve screenshot.

- Flow abriu na conta esperada após o aviso de privacidade especificamente autorizado: rolagem normal, “Continuar” uma única vez, marketing/pesquisa desmarcados; nenhum novo consentimento. Rótulo **PRO**, **1.050 créditos** visíveis como fotografia, não quota operacional nem autorização de geração. Custo por geração e renovação não mostrados, por confirmar.
- Vids abriu no mesmo perfil/conta, exibindo somente **“Assinatura do Google”**; plano específico, quota, custo e renovação continuam desconhecidos. Não herdar limites do Flow.
- Sem projeto aberto/criado, geração/alteração de mídia ou consumo de créditos relatado. Conta/titularidade foi conferida na UI conforme relato, sem registrar nome/e-mail; não é auditoria independente nem aceite do pré-voo completo.
- O roadmap geral registra F4C-01..04 concluídos: `pqbr-camofox`, `127.0.0.1:9387`, `userId=pqbr` persistente. F4C-05/06/08 seguem abertos; `9377` global fica fora da rota. A observação não fecha essas pendências, contratos, adapters, smoke ou produção.

### Regra para atualizar os checkboxes

1. Marcar `[x]` somente após a tarefa estar realmente concluída e existir evidência verificável: caminho de arquivo, commit/PR, saída de teste ou relatório, com data e resultado.
2. Registrar a evidência ao lado da tarefa ou em um campo `Evidência`; “planejado”, “em andamento”, configuração presumida ou descrição do blueprint não contam como conclusão técnica.
3. Manter `[ ]` quando bloqueado, parcialmente concluído, sem evidência ou com resultado inconclusivo. Não apagar ou sobrescrever evidência anterior; registrar correções e histórico.
4. Este é um checklist humano de planejamento. Depois da implementação, o estado operacional deve permanecer coerente com o Roadmap canônico do PQBR e com os estados do workflow/ledger; um checkbox não substitui esses sistemas.

## 3. Guardrails permanentes

- Preservar alterações preexistentes no working tree. Antes de trabalhar, inspecionar status, instruções e scripts do checkout oficial; não “limpar” arquivos, resets ou commits fora do fluxo aprovado.
- Seguir a ordem normativa, os workflows e os scripts prescritos no repositório PQBR. Antes da primeira implementação, conferir `AGENTS.md`/instruções aplicáveis, `docs/TESTES.md`, `docs/ROADMAP.md`, `docs/LACUNAS-fluxo.md`, `docs/ARQUITETURA.md`, `docs/AGENTES.md` e `docs/CONTRATO-EDITORIAL.md`, além de `REGRAS`/`SPEC` aplicáveis.
- **Não modificar código-fonte do Paperclip.** A integração será feita pelas interfaces autorizadas e documentadas.
- Não excluir dados nem alterar regras centrais/canônicas, permissões, acesso, segurança, rede ou exposição de serviços sem aprovação explícita e pelo processo do projeto.
- Não instalar extensões de terceiros, reproduzir endpoints privados, interceptar requests, contornar CAPTCHA, quotas, limites, autenticação ou controles anti-automação. Usar somente UI/domínios oficiais autorizados via Camofox.
- Não criar contas, perfis de sessão paralelos, logins extras ou credenciais. Não copiar cookies entre serviços. Sessões de navegador são credenciais.
- Não gravar senha, token, cookie, PII ou conteúdo sensível em logs, issues, memória ou artefatos de evidência.
- Pausar e registrar issue quando surgir quota/limite, auth expirada, desafio, mudança de site, rota desconhecida, conflito de política ou timeout ambíguo. Sem retry cego, troca silenciosa de provedor ou tentativa de contorno.
- Qualquer geração real pode consumir quota; só executar smoke depois de preflight, autorização de conta/sessão e confirmação das regras do projeto. Nada neste roadmap autoriza uma geração real, compra ou ação pública.

## 4. Roadmap por fases

### Fase 0 — Baseline do checkout, governança e pré-condições

**Objetivo:** transformar as pendências documentais em baseline verificável, sem iniciar produção real.

- [x] Abrir o checkout oficial e conferir o estado do working tree; registrar alterações preexistentes sem modificá-las. — 2026-10-15
  - Evidência: antes desta atualização, branch `docs/f00-01-traceability`, HEAD `db3f652`; preexistiam `M docs/REFERENCIA-sessao-google.md`, além dos diretórios não rastreados `docs/blueprints/modulo-producao-video/` e `docs/pesquisas/arquivo-cadernos/f757e751_ep1001-descartado/`. Nenhum deles foi apagado ou sobrescrito.
- [ ] Ler as instruções e os workflows/scripts aplicáveis do repositório; anotar os comandos de teste e validação prescritos antes de tocar no código.
- [ ] Revisar os documentos canônicos citados no §3, localizar tasks já existentes e reconciliar este plano com `docs/ROADMAP.md`/`docs/LACUNAS-fluxo.md` pelo processo vigente, evitando duplicatas.
- [ ] Verificar a organização/roster Paperclip ao vivo por leitura autorizada. Se a consulta continuar em HTTP 400, registrar o bloqueio; não atribuir tickets nem afirmar que agentes estão ativos.
- [ ] Confirmar, por evidência, o estado da ponte Paperclip/Temporal, do E2E, do Camofox, da concorrência/sessão Google e da separação de dados. Reconciliar diferenças entre blueprint, arquitetura canônica e implementação.
- [ ] Registrar papéis responsáveis **sem presumir nomes ou disponibilidade**. O roster documentado não comprova roster ativo; não criar ou reativar agentes nesta fase.
- [ ] Confirmar o limite de teste: dados/fixtures locais; nenhuma publicação, upload de arquivo, compartilhamento público ou escrita no Drive. Se o cenário exigir upload, manter bloqueado e usar mocks.
- [ ] Registrar riscos, dependências, gates e critérios de parada no Roadmap canônico, sem alterar regras centrais.

**Saída:** baseline com estado real, gaps, owners/rotas válidos e evidências; lista de comandos de teste; nenhuma publicação/upload; nenhuma alteração destrutiva ou de regra central.

**Gate G0:** não iniciar workflow com efeitos externos até haver caminho de integração e E2E definido, sessão/escopo autorizado, política de teste clara e instruções do repo cumpridas. Roster não confirmado bloqueia atribuições ao vivo; não deve ser “resolvido” por suposição.

### Fase 1 — Contratos, estados e pacote criativo comum

**Objetivo:** estabelecer dados versionados e independentes do provedor antes de construir adapters.

- [ ] Incorporar e validar o [contrato proposto de pré-voo de acesso e uso](BLUEPRINT.md#contrato-proposto-de-pré-voo-de-acesso-e-uso--flowvids) nos contratos abaixo: conta/titularidade pela UI, perfil PQBR exclusivo, consentimento e opt-ins desativados, quota/custo com fonte/data/evidência, autorização específica e pausa fail-closed. Proposta registrada em 17/10; schema/testes/aceite ainda pendentes.
- [ ] Definir e versionar contratos Pydantic v2/JSON Schema para `VideoProductionRequest`, `EpisodeCreativePlan`, `SceneGenerationRequest`, `ProviderCapabilities`, `QuotaObservation`, `PlatformProfile`/`PlatformChange`, `ProviderJob`, `ArtifactRecord`, `QualityReview` e `ProductionManifest`.
- [ ] Fixar IDs estáveis por produção/cena/variante, hashes de request e referências, versão de contrato, chave de idempotência, timestamps e origem; definir unidades de quota sem somar limites concorrentes. `unknown` deve ser representável.
- [ ] Definir estados de workflow e estados de pausa/erro conforme o blueprint (`PAUSED_QUOTA`, `PAUSED_AUTH`, `PAUSED_SITE_CHANGE`, `PAUSED_REVIEW`, `FAILED_RETRYABLE`, `FAILED_FINAL`), transições válidas, tentativas máximas, backoff e condições de retomada.
- [ ] Definir política de logs, evidências e retenção: sem segredos/PII; incluir dados mínimos para auditoria e reconciliação de jobs.
- [ ] Modelar fichas de stickmen, personagens, objetos e cenários com ID, origem, versão/hash e direitos; vincular storyboard/cena a fichas e assets.
- [ ] Preparar proposta versionada para atualizar documentos canônicos de stickmen/fichas pelo processo do projeto. Aplicar a atualização somente após o gate/owner competente; a decisão de identidade já existe, mas sua atualização documental é tarefa separada.
- [ ] Criar testes de schema, compatibilidade, campos obrigatórios, valores inválidos, hashes, IDs e estados proibidos.

**Aceite:** contratos versionados e validados por testes; fixtures sem segredos/PII; cada cena permite rastrear roteiro, referências, provider, tentativa e artefato. Mudança canônica segue processo aprovado.

**Gate G1:** contratos e alterações canônicas aprovados pelo processo do PQBR antes de iniciar integração que dependa deles.

### Fase 2 — Ponte Paperclip/Temporal e workflow durável

**Objetivo:** resolver as dependências já identificadas e provar retomada segura antes de conectar provedores.

- [ ] Implementar ou concluir a ponte Paperclip/Temporal conforme os contratos existentes, mantendo Paperclip como controle/ownership/auditoria e Temporal como execução/estado durável.
- [ ] Confirmar a API/eventos/outbox e a separação de armazenamento de negócio. Não dar a agentes acesso direto ao banco do Temporal ou credencial SQL ampla; resolver divergências com `docs/ARQUITETURA.md` antes de codificar.
- [ ] Implementar workflow determinístico; chamadas a LLM, browser, APIs e geração apenas em Activities/workers, com saída registrada para replay.
- [ ] Implementar idempotência, timeout, retry limitado por classe de erro, backoff, reconciliação após timeout ambíguo, Signals/Updates de aprovação quando aplicável e trilha de auditoria.
- [ ] Implementar estados visíveis por produção/atividade e caminho de pausa/escalonamento para quota, auth, mudança de site, revisão e erros não recuperáveis.
- [ ] Configurar a atividade de browser pela sessão Camofox autorizada e serializada; manter a concorrência prevista no projeto e não duplicar perfil/sessão.
- [ ] Resolver o bloqueio do E2E de ponta a ponta em ambiente de teste sem efeitos externos; exercitar replay Temporal, outbox, idempotência, timeout ambíguo, pausas e retomada de cena.
- [ ] Confirmar roster Paperclip ao vivo antes de qualquer atribuição ou alegação de ownership ativo; se a leitura falhar, documentar e manter o bloqueio.

**Aceite:** ponte e E2E passam pelos scripts oficiais do projeto; replay não repete decisões/efeitos; retries não criam jobs duplicados; estado e evidências são auditáveis; nenhuma geração, publicação ou upload ocorre nos testes.

**Gate G2:** sem este aceite, não iniciar teste integrado real de Flow nem Vids.

### Fase 3 — Workflow de produção em dry-run e infraestrutura de adapters

**Objetivo:** exercitar a máquina de estados e o contrato comum usando mocks antes de qualquer provedor.

- [ ] Testar em mocks o gate de acesso/uso: conta divergente/incerta → `PAUSED_AUTH`; consentimento/opt-in incerto ou autorização específica ausente → `PAUSED_REVIEW`; quota/custo incerto → `PAUSED_QUOTA`; saldo sem custo/renovação não libera consumo. Confirmar zero submissão e que Vids não herda consentimento/quota/autorização Flow.
- [ ] Definir e testar em mock o catálogo versionado de overlays conhecidos para `FlowAdapter` via sessão Camofox: cada padrão deve ter evidência observável, ação segura explicitamente permitida e pós-condição verificável; overlay desconhecido, ambíguo ou sem pós-condição deve pausar e escalar, sem clique cego nem contorno.
- [ ] Implementar a interface comum `VideoProviderAdapter` (`capabilities`, `preflight`, `submit`, `wait`, `collect`, `inspect`, `cancel_if_supported`) e tipos de resultado.
- [ ] Implementar perfis versionados por plataforma com domínio oficial, capacidades observadas, restrições, owner, fonte/data, validade, smoke test, changelog e plano de pausa/rollback.
- [ ] Implementar workflow até `TEST_COMPLETE`, sem transição automática para upload/publicação. Saída de teste é artefato local.
- [ ] Implementar mocks de UI/provedor para sucesso, limite de quota, auth expirada, mudança de interface, timeout ambíguo, falha transitória e artefato duplicado.
- [ ] Validar que a escolha de provedor é explícita e registrada; nenhum fallback silencioso quando Flow estiver indisponível.
- [ ] Executar testes de unidade/contrato e E2E mockado pelo workflow/script canônico; confirmar que não há tráfego de upload/publicação nem gravação em Drive.

**Aceite:** dry-run determinístico e observável; transições inválidas são recusadas; cada mock de bloqueio pausa sem contorno; nenhum agente aciona provider diretamente.

### Fase 4 — Google Flow: consolidação e piloto controlado

**Objetivo:** consolidar a rota primária primeiro, inicialmente em uma cena e depois no Short completo.

- [ ] Criar `FlowAdapter` e `PlatformProfile` do Flow usando somente a UI/domínio oficial via Camofox; não usar extensões nem endpoints/interceptações privadas.
- [ ] Aplicar o contrato proposto de acesso/uso antes de submeter Flow: somente `pqbr-camofox` em `127.0.0.1:9387`, `userId=pqbr` persistente e fila serializada; nunca `9377`. Conferir conta/titularidade pela UI, consentimento/privacidade antes do primeiro uso, marketing/pesquisa desativados e pós-condição; registrar evidência sanitizada, data/fonte e pausa se incerto.
- [ ] Confirmar quota/saldo, unidade, custo por modelo/duração/variantes e renovação/janela na UI; vincular autorização humana específica de geração ao request/cenas/prompts/referências e teto de custo/consumo. **Parcial em 17/10:** acesso e aviso confirmados por relato, PRO/1.050 créditos visíveis; custo e renovação desconhecidos, geração não autorizada. Manter bloqueado, sem gerar para medir custo.
- [ ] Preparar testes com mocks/fixtures locais. Para smoke real, não enviar arquivos de referência; se o teste exigir upload, interromper e manter o cenário mockado até autorização específica.
- [ ] Após os gates G0–G2 e autorização de sessão/quota, executar no máximo o smoke previsto pelo plano: uma cena, com prompt autorizado, registrando job visível, tempos, consumo e resultado local permitido. Geração real não é parte dos testes mockados e pode consumir quota.
- [ ] Testar timeout e reconciliação consultando histórico/artefato antes de qualquer repetição; provar que uma tentativa não cria duplicata.
- [ ] Só depois do aceite da cena única, expandir a fixture para 5–7 cenas e 50–70 segundos, sem upload de arquivos, publicação ou gravação em Drive.
- [ ] Ingerir apenas artefatos cujo download/uso externo seja permitido; registrar SHA-256, cena, prompt/schema hash, provider, job, quota observada e proveniência.

**Aceite:** preflight e consumo observáveis; uma cena e depois o Short completo retomam sem duplicação; artefatos permitidos estão locais e rastreáveis; pausa correta em limite/auth/site change; zero upload/publicação.

**Gate G3:** o acesso/aviso aceito não libera geração; exigir pré-voo válido e autorização específica antes da cena única. Nenhuma expansão para Short completo até o smoke de uma cena, reconciliação/idempotência e QC da rota Flow passarem.

### Fase 5 — QC, áudio e render local do piloto Flow

**Objetivo:** entregar um Short tecnicamente e editorialmente revisável, sem distribuição.

#### Decisão e evidências de voz — 2026-10-17
- **Decisão fixa do proprietário:** ElevenLabs é a única fonte aprovada para narração e `Larissa - Vibrant and Playful` (`voice_id`: `xcNJswC7UcxsIiCuih19`) é a voz padrão escolhida. Não trocar por outra voz sem nova decisão do proprietário.
- **Evidência do teste:** a amostra em PT-BR foi testada com `eleven_v3`, seed `42`, stability `0.5`, similarity_boost `0.75`, style `0`, `use_speaker_boost: true` e speed `1.0`; foi baixada e enviada ao proprietário. Este ajuste não gera áudio novo.
- **Configuração versionada:** `config/voz_narracao.json` registra a voz e os parâmetros aprovados como fonte de referência para a implementação. A integração backend de TTS está ligada ao workflow como Activity após auditoria aprovada e consome esta configuração sem fallback de voz. `runtime_integrated` está ativo, mas `generation_authorized` e `publication_authorized` permanecem `false`; o fluxo real falha fechado antes da chamada externa. A implementação e os testes usaram apenas transporte HTTP simulado; não houve chamada de API nem síntese nova. A ativação de geração continua sujeita aos gates e a autorização específica.
- **Limites atuais:** não gerar mais áudio, não ativar produção, não fazer upload e não publicar. A configuração não autoriza nenhuma dessas ações. A tentativa anterior de Voice Design no Google AI Studio foi abortada quando a interface exigiu uma chave paga; não retomar essa rota sem nova decisão.
- **Guardrails para implementação:** manter a chave apenas no backend/secret manager, nunca no frontend ou logs; restringir escopo e quota e usar allowlist de IP apenas se o egress for estável; preferir service account no backend/produção se disponível. Manter versionados `voice_id`, modelo, configurações, roteiro e seed quando suportada; a síntese é não determinística. Não registrar segredos neste documento.
- [x] Implementar a Activity backend ElevenLabs integrada ao workflow após auditoria, usar a voz versionada, impedir retry automático ambíguo e salvar artefatos locais idempotentes; manter geração/publicação bloqueadas. — 2026-10-17.
  - Evidência: `src/pqbr/integrations/elevenlabs.py`, `src/pqbr/workflows/narracao.py`, `tests/unit/test_elevenlabs.py`, `tests/unit/test_narracao.py`; 78 testes unitários e 6 de workflow aprovados com transporte/Activity mockados; nenhum áudio real gerado.

- [ ] Aplicar storyboard por cena com continuidade e referências versionadas; validar fala↔cena, enquadramento, composição, ação observável, legibilidade mobile e consistência dos stickmen/fichas.
- [ ] Gerar narração em terceira pessoa e PT-BR usando somente o ID de voz ElevenLabs selecionado/aprovado; indicar efeitos sonoros por ação/timecode e manter **sem música**.
- [ ] Aplicar CTA contextual; quando não houver trocadilho natural, usar convite natural a seguir o canal (por exemplo, “Segue o Porquê BR”); nunca pedir comentários.
- [ ] Usar FFmpeg somente com material Flow cujo download e uso externo estejam permitidos. Normalizar saída conforme o contrato; registrar versão/preset, cortes e checksums no `ProductionManifest`.
- [ ] Aplicar selo PQBR em safe zone determinística, sem cobrir proveniência do provedor, legenda, personagem ou ação importante.
- [ ] Automatizar QC técnico: decode, duração/aspecto/codec, frames pretos/silêncio inesperado, áudio e sincronismo de SFX, duplicatas, hash e integridade do arquivo.
- [ ] Automatizar/registrar QC editorial: narrativa, continuidade, coerência das fichas, adequação cultural, gancho/encerramento e legibilidade.
- [ ] Tratar direitos, segurança e proveniência como bloqueadores; preferências editoriais não devem mascarar bloqueador.

**Aceite:** relatório de QC completo e artefato local pronto para revisão editorial; sem envio ao Drive, compartilhamento, upload, agendamento ou publicação.

### Fase 6 — Google Vids: verificar fallback sem assumir capacidade

**Objetivo:** verificar Vids separadamente, respeitando a rota oficial de composição/exportação e limites reais.

- [ ] Aplicar o mesmo contrato proposto de acesso/uso ao Vids, independentemente do Flow, no perfil persistente PQBR exclusivo: conta/titularidade, consentimento/opt-ins, quota/custo/renovação com fonte/data/evidência e autorização específica. **Parcial em 17/10:** acesso na mesma conta; somente “Assinatura do Google”, sem plano/cota/custo/renovação confirmados. Nenhuma geração autorizada.
- [ ] Confirmar na conta/região piloto a elegibilidade, recursos disponíveis, quota visível e condições de exportação. Não somar referências de “50 vídeos/mês” e “500 segundos/mês” como dois orçamentos.
- [ ] Implementar `GoogleVidsAdapter`/perfil com preflight e estados próprios; registrar `unknown` quando o valor não estiver visível. Não usar quota Flow como quota Vids.
- [ ] Fazer testes de contrato/mocks primeiro. Smoke real só após G0–G2, preflight e autorização; não fazer upload de imagens/arquivos, não compartilhar publicamente e não gravar no Drive.
- [ ] Testar uma cena pela UI oficial e verificar formato, duração, referências permitidas, relação 9:16, saída, marca/proveniência e contabilização, sem contornar limite.
- [ ] Compor dentro do Vids. Baixar **somente o MP4 final diretamente no dispositivo** pela opção oficial; não pressupor extração de clipes individuais, processamento externo em FFmpeg, exportação para Drive ou YouTube.
- [ ] Expandir para Short de 50–70 segundos apenas se a quota/condições reais permitirem. O fallback deve ser selecionado pelo workflow/preflight; nunca trocar de rota silenciosamente.

**Aceite:** elegibilidade e quota aplicável documentadas; saída final local íntegra; composição/exportação e proveniência verificadas; nenhum bypass, upload ou publicação; capacidade suficiente para o escopo medido, sem extrapolar para cadência diária.

**Gate G4:** manter Vids como fallback não operacional se qualquer condição de elegibilidade, quota, uso, exportação ou proveniência permanecer desconhecida.

### Fase 7 — Comparação controlada e encerramento do piloto

**Objetivo:** decidir com evidências se e como usar o fallback, sem comprometer escala.

- [ ] Comparar Flow e Vids usando o mesmo roteiro/storyboard e critérios equivalentes, sem upload de arquivos de entrada; se referências externas forem indispensáveis, interromper a comparação até haver autorização específica.
- [ ] Medir duração total, consumo/quota por unidade, latência, taxa de falha/retry, consistência visual, alinhamento fala↔cena, QC, retrabalho e limitações de exportação/proveniência.
- [ ] Registrar diferenças de conta/plano e confiança das medições; não decidir com base apenas em uma variante isolada ou em quota pública genérica.
- [ ] Produzir relatório do piloto e recomendação de portfólio/cadência, sem ativar fallback automático nem prometer dois Shorts/dia.
- [ ] Revisar incidentes, issues, correções e lições sanitizadas; não armazenar segredos/PII em Hindsight.
- [ ] Confirmar checklist final: zero upload/publicação; nenhuma duplicata/retry cego; artefatos rastreáveis; QC aprovado; consumo/quota e limites documentados; bloqueadores resolvidos ou explicitamente mantidos.

**Aceite do piloto:** um Short local de 50–70 s pronto para revisão editorial, com relatório e proveniência; nenhuma distribuição pública; decisão de portfólio baseada em dados e sujeita ao processo de aprovação do projeto.

### Fase 8 — Ciclos futuros (fora deste plano de implementação)

- [ ] **Gemini Web:** somente após decisão de avançar, com perfil/adapter independente, conta/sessão correta, quota, termos, marcas e smoke próprios.
- [ ] **Meta Vibes:** somente após decisão de avançar; manter quota como `unknown` até evidência oficial da conta; nunca contornar bloqueios nem usar login/conta paralela.
- [ ] **Long-form:** elaborar especificação, orçamento, cadência, duração e gates separados antes de qualquer implementação.
- [ ] Reavaliar a necessidade de agentes específicos por plataforma somente após métricas das fases 4–7 e confirmação do roster ao vivo; perfil/runbook não implica agente novo.

## 5. Gates e dependências resumidos

| Gate | Exige | Se não passar |
|---|---|---|
| G0 — Baseline e governança | Instruções/scripts revisados; working tree preservado; limites de teste claros; gaps e owners registrados. | Não iniciar efeitos externos; corrigir/documentar o baseline. |
| G1 — Contratos | Contratos, estados, versões e alteração canônica pelo processo competente. | Não integrar componentes dependentes. |
| G2 — Paperclip/Temporal/E2E | Ponte funcional, workflow durável, idempotência, replay, pausa/retomada e testes sem side effects. | Não conectar Flow/Vids a execução real. |
| G3 — Flow | Preflight e smoke de uma cena aprovados, reconciliação sem duplicata e uso permitido. | Não ampliar para 5–7 cenas/Short. |
| G4 — Vids | Elegibilidade/quota real, exportação local oficial e proveniência verificadas. | Vids continua apenas documentado como fallback, sem operação. |
| G5 — Piloto | QC técnico/editorial, relatório, artefatos rastreáveis, zero upload/publicação e limites medidos. | Não recomendar escala nem declarar piloto aceito. |

## 6. Testes obrigatórios e evidência mínima

1. **Contratos:** schema válido/inválido, versionamento, hashes, IDs, quota por unidade, ausência de campos sensíveis; pré-voo de acesso/uso com conta/consentimento/quota/custo incertos, opt-ins desativados, autorização específica ausente/expirada/divergente e saldo sem custo conhecido. Validar bloqueio de geração e não herança Flow→Vids; proposta de testes, não execução concluída.
2. **Temporal:** replay, registro único de saída de Activity, outbox, idempotência, retry/backoff, timeout ambíguo, pausa e retomada da cena pendente.
3. **Adapters mockados:** sucesso, limite, auth, site changed, erro transitório/permanente, duplicata e cancelamento quando suportado.
4. **E2E sem efeitos externos:** percorrer workflow até `TEST_COMPLETE` com mocks e fixtures locais; confirmar zero upload, publicação, Drive ou efeitos não autorizados.
5. **Smoke autorizado:** somente depois de G0–G2 e preflight, com confirmação de quota/sessão; registrar consumo e manter saída local. Nunca enviar arquivo de fixture.
6. **QC de mídia:** integridade do arquivo, duração 50–70 s, codec/aspecto, áudio/SFX, sincronismo, proveniência, checksum e relatório editorial.
7. **Segurança/auditoria:** confirmar que logs/issues/evidências não contêm token, cookie, senha ou PII; verificar pausa automática em bloqueios e uso exclusivo do perfil PQBR. Preservar os aprendizados permitidos de fila/estados, vínculo cena↔prompt↔referência e reconciliação/idempotência da §8 do blueprint; proibir interceptação de requests/cookies, captura de sessão, hooks, bypass de CAPTCHA/bloqueios/quotas e extensões executadas. Não alterar por esta proposta a política operacional de exceções.

Para marcar um teste como concluído, registrar comando prescrito, versão/commit, data, ambiente de teste, resultado e caminho do relatório/artefato. Não considerar um smoke real um teste sem custo de quota.

## 7. Papéis, sem atribuição prematura

| Papel descrito no blueprint | Responsabilidade prevista | Situação para este roadmap |
|---|---|---|
| Dev Corretor | Implementar adapters/contratos/testes e registrar lições sanitizadas. | Papel recomendado; roster ativo não confirmado. |
| Dev Revisor | Revisão independente de alterações e testes. | Papel recomendado; roster ativo não confirmado. |
| Compliance / Líder Compliance | Direitos, termos, uso/exportação e HOLD. | Papel recomendado; roster ativo não confirmado. |
| Observador | Medir sessão, quota, falhas/tempos e abrir issues; não editar adapters/dados. | Papel recomendado; roster ativo não confirmado. |
| Guardião de Segurança | Segredos, sessão, prompt injection e allowlist. | Papel recomendado; roster ativo não confirmado. |
| Auditor / QA editorial | QC técnico, editorial, visual e relatório. | Papel recomendado; roster ativo não confirmado. |

Não atribuir tickets, declarar contratação/ativação, criar agente de plataforma ou reativar o Diretor de Arte 2D até a consulta ao Paperclip ao vivo ser validada e o processo existente ser seguido.

## 8. Riscos e respostas planejadas

| Risco/bloqueio | Resposta prevista |
|---|---|
| Ponte Paperclip/Temporal pendente e E2E bloqueado. | Tratar como dependência anterior à geração; executar testes mockados e documentar a correção. |
| Roster Paperclip ao vivo não confirmado (HTTP 400 documentado). | Revalidar em leitura; sem atribuição/ativação presumida. |
| Quota Vids variável ou ambígua. | Consultar UI oficial; registrar valor/unidade/fonte; `unknown` se ausente; não somar limites públicos. |
| Mudança de site, auth, desafio ou bloqueio. | Pausar fila, preservar evidências e abrir issue; sem CAPTCHA bypass ou retry cego. |
| Timeout com job possivelmente criado. | Reconciliar histórico/artefato e idempotency key antes de repetir. |
| Teste exige upload de fixture. | Bloquear esse caminho; usar mock/fixture local ou aguardar autorização específica. |
| Extração de clipes individuais do Vids não confirmada. | Compor no Vids e baixar MP4 final local pela opção oficial; não usar FFmpeg sobre clips de Vids sem confirmação de permissão. |
| Mudança de regras centrais, rede, exposição, acesso ou exclusão necessária. | Parar e pedir aprovação explícita antes da mudança; este plano não a autoriza. |
| Working tree contém alterações preexistentes. | Inventariar e preservar; trabalhar no fluxo/branch permitido, sem limpeza ou reset. |
| Pressão por cadência de dois Shorts/dia. | Não prometer capacidade; decidir somente após medir quota, retrabalho, falhas, custos e qualidade em ambos os caminhos. |

## 9. Sequenciamento sem prazo artificial

A sequência é dependente de gates, não de calendário. **Não há estimativa de duração, custo ou capacidade**, pois o roster ao vivo, a ponte, o E2E, a conta/plano e a quota real não foram confirmados. Quando esses dados estiverem disponíveis, o responsável do projeto pode estimar esforço e inserir datas no Roadmap canônico. A ordem recomendada é: **Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5 → Fase 6 → Fase 7**; a Fase 8 só abre por decisão posterior.

## 10. Referências do projeto

- `docs/blueprints/modulo-producao-video/BLUEPRINT.md` — fonte principal; especialmente §§ 1–2 (decisões/gates), §§ 4–7 (arquitetura, papéis, contratos e estados), §§ 9–12 (provedores, QC, validação e fases) e § 13 (pendências e trabalho existente).
- `docs/ROADMAP.md` e `docs/LACUNAS-fluxo.md` — reconciliação das pendências e registro de tarefas segundo o processo do projeto.
- `docs/ARQUITETURA.md`, `docs/AGENTES.md`, `docs/TESTES.md` e `docs/CONTRATO-EDITORIAL.md` — confirmar estado e workflows antes de implementar; este roadmap não os substitui.

---

## Histórico do roadmap

| Data | Alteração | Evidência |
|---|---|---|
| 2026-10-14 | Roadmap criado e sincronizado no checkout oficial como plano documental. | `docs/blueprints/modulo-producao-video/ROADMAP.md`; nenhuma implementação técnica executada por este documento. |
| 2026-10-15 | José aceitou o G0 deste roadmap; baseline do checkout conferido e alterações preexistentes preservadas. | Mensagem de José; branch `docs/f00-01-traceability` em `db3f652`; checklist da Fase 0 ainda tem itens abertos. |
| 2026-10-17 | Decisão/fatos de narração registrados: ElevenLabs exclusivo, três candidatas e audição pendente de autorização de créditos. | Seção de voz da Fase 5 deste roadmap. |
| 2026-10-17 | Proprietário fixou Larissa como voz padrão; parâmetros de teste versionados sem ativar produção. | `config/voz_narracao.json` e seção de voz da Fase 5. |
| 2026-10-17 | Integração TTS backend implementada e testada em mocks; geração e publicação permanecem bloqueadas. | Activity Temporal, cliente ElevenLabs, 78 testes unitários + 6 workflows; sem tráfego externo ou síntese real. |
| 2026-10-17 | Contrato/gate proposto de acesso e uso Flow/Vids incluído nas Fases 1/3/4/6 e testes previstos; pré-voo observado registrado como parcial. | Blueprint §§6–9; atualização do proprietário/coordenador às 20:14:18-03:00. Flow PRO/1.050 créditos apenas fotografia, custo/renovação e quota Vids pendentes; sem geração, implementação, teste operacional ou produção concluídos por esta edição. |
