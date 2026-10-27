# PQBR — wiki da stack e das implementações

> **Ponto de partida: leia [REGRAS](REGRAS.md) → [SPEC](SPEC.md) → [ARQUITETURA](ARQUITETURA.md) → [TESTES](TESTES.md) → [ROADMAP canônico](ROADMAP.md), nessa ordem, antes de retomar qualquer trabalho.** Este resumo é um mapa de navegação, não uma nova regra, autorização ou fonte de status. Retrato documental de 17/10/2026; consulte o roadmap novamente para avanços posteriores.

**A PQBR está em construção, sem liberação geral de produção.** A espinha Temporal/Postgres, o isolamento do Camofox e diversas peças de código já têm evidências. Isso não significa que geração, auditoria, publicação, alertas e recuperação estejam integrados de ponta a ponta. O aceite de um gate também não conclui automaticamente outro item com nome semelhante.

## Navegação

[Como ler os estados](#como-ler-os-estados) · [Stack](#stack) · [Implementações](#implementações) · [Correção autônoma](#correção-autônoma-f3-05) · [Canal e painel](#canal-do-josé-e-painel-t471t474) · [Pendências](#pendências-e-pausas) · [Documentação completa](#documentação-completa)

## Como ler os estados

- **Implementado/testado localmente:** há código e evidência de testes, com o ambiente e seus limites indicados. Não implica deploy.
- **Operação registrada:** as fontes relatam instalação, ativação ou execução real em determinada ocasião. Nenhum serviço foi sondado ou revalidado ao vivo para este resumo.
- **Candidato/protótipo desligado:** experimento separado, mocks ou composição descartável; não conectado aos Workers persistentes ou não autorizado para gerar efeitos reais.
- **Pendente/pausado:** falta implementação, integração, evidência, decisão ou aceite. Uma pausa explícita prevalece sobre testes anteriores.

Contagens de testes abaixo pertencem a snapshots distintos: **não devem ser somadas como se fossem uma única suíte atual**. Nesta revisão foram lidos documentos e código; não foram executados testes, modelos, serviços ou workflows.

## Stack

### Execução e controle

| Camada | Tecnologia e função | Estado e onde aprofundar |
|---|---|---|
| Código e contratos | Python, Pydantic v2 e SDK Python do Temporal; contratos estruturados com rejeição de campos extras. | **Implementado/testado localmente.** F3-01/G3 fechado em 16/10. [Contratos no código](../src/pqbr/contratos/__init__.py), [interfaces e desenho](ARQUITETURA.md), [critérios de teste](TESTES.md). |
| Orquestração durável | Temporal self-hosted 1.32.1; Schedules, Activities, timers, sinais e replay. PostgreSQL dedicado ao estado do motor. | **Operação registrada e motor escolhido.** Soak documentado de 122 execuções em aproximadamente 20 h, sem perdas/duplicatas, pico de 340 MiB no compose. DBOS não foi necessário. [ADR e resultados completos](sdd/adr-001-orquestrador.md), [compose](../infra/temporal/docker-compose.yml). |
| Agentes e painel | **Em transição (ADR-011, t474):** agentes PydanticAI (Pydantic v2) dentro de activities do Temporal; painel = Temporal UI; canal = Telegram/Hermes `pqbr`. O Paperclip (plano de controle, issues e agentes, adapters `process`/`opencode_local`) está sendo retirado. | Organização PQBR existente e integração de conversa **registradas**; disponibilidade atual do roster não foi consultada. F1-01/F1-02 estão suspensos: não importar uma segunda organização. [Regras vigentes](REGRAS.md), [arquitetura](ARQUITETURA.md), [roadmap](ROADMAP.md). |
| Modelos dos agentes | 9router, com papéis mapeados para `core-alto`, `core-medio`, `core-baixo` e `core-revisao`. Jev/TypeSafe fica na decisão estruturada, não na redação. | **Configuração presente**, sem presumir credenciais ou todos os backends ligados. O roadmap ainda registra pendências de 9router/ponte CLI e fallbacks do Jev. [Mapa único de modelos](../config/modelos_9router.json), [configuração documentada](../config/README.md), [papéis e decisões](ARQUITETURA.md). |
| Navegador | Camofox sobre Camoufox, instância PQBR isolada em `127.0.0.1:9387`, autenticação, perfil `pqbr`, keepalive e fila própria. | **Operação registrada** em F4C-01..04: saúde/autenticação, duas execuções em série, login e persistência após restart. A migração dos clientes antigos e o agente corretor completo seguem pendentes. [Infra e limites](../infra/pqbr-camofox/README.md), [Worker](../src/pqbr/workflows/worker_camofox.py), [F4C no roadmap](ROADMAP.md). |

**Filas não são todas equivalentes.** Os entrypoints consultados declaram `pqbr-episodio` no [Worker principal](../src/pqbr/workflows/worker.py), `camofox-pqbr` no [Worker Camofox](../src/pqbr/workflows/worker_camofox.py), `episodio-pqbr` no [Worker de episódio](../src/pqbr/workflows/worker_episodio.py) e `notebooklm-pqbr` no [Worker NotebookLM](../src/pqbr/workflows/worker_notebooklm.py). Registro no código não prova que um processo já carregou a versão do checkout. `max_concurrent_activities=1` limita aquela instância de Worker; **não é exclusão global por sessão** — veja [F3-05](#correção-autônoma-f3-05).

### Dados, memória e proteção

| Recurso | Separação e uso | Estado e referências |
|---|---|---|
| Banco do app | PostgreSQL 17 local, schema `pqbr`, loopback `55433`, RLS forçado e papéis separados. Dados de negócio: temas, grade, episódios, ações, auditorias e consumo. | **Implantação/restauração registradas.** Agentes não ganham escrita direta; o Temporal é o caminho de escrita. [Modelo de dados](ARQUITETURA.md), [compose](../infra/pqbr-db/docker-compose.yml), [acesso protegido](../src/pqbr/storage/banco.py). |
| Banco do Temporal | PostgreSQL próprio, separado dos dados de negócio. | **Implantação/testes registrados.** Agentes, painel e relatórios não devem consultá-lo diretamente. O teste inicial de outbox foi com stub, não prova completa contra o banco do app real. [ADR-001](sdd/adr-001-orquestrador.md), [TZ-03](TESTES.md). |
| Banco do Paperclip | PostgreSQL 17 local dedicado, loopback `55434`; migração do Supabase registrada como concluída. | **Operação registrada** em L-01/t412. A fonte prevê Supabase apenas como rollback até 18/10, não como backend ativo; descarte não é automático. [Runbook completo](../infra/paperclip-db/README.md), [roadmap](ROADMAP.md). |
| Memória | Hindsight local com armazenamento próprio em PostgreSQL pg0; diretriz de um bank por organização, sem segredos/PII. | Backup/restauração **registrados** em F3-03. Não confundir com integração pronta do aprendizado da correção: essa parte de F3-05 continua pendente. [Regras de memória](REGRAS.md), [script de backup](../infra/hindsight-backup/backup.sh). |
| Arquivos | Google Drive como destino definitivo; estrutura PQBR e teste de upload registrados, IDs versionados na configuração. | Ter a estrutura não conclui F8-02 nem backup offsite. [Regras de armazenamento](REGRAS.md), [IDs das pastas](../config/drive_pastas.json), [F8 no roadmap](ROADMAP.md). |

**Backups locais:** os registros apontam app às 03:30, Hindsight às 03:45 e Paperclip às 04:00, com rotação e evidências de restauração. Os horários são de configuração, não prova de execução recente ou consistência entre bancos. Consulte os timers do [app](../infra/pqbr-db/systemd/pqbr-db-backup.timer), [Hindsight](../infra/hindsight-backup/systemd/hindsight-backup.timer) e [Paperclip](../infra/paperclip-db/systemd/paperclip-db-backup.timer).

**Segredos/PII — F3-02 concluído localmente:** a barreira protege Hindsight, tickets/API/CLI, conexão/cursor/SQL em lote, logs com exceções/extras, stdout/MCP e hook. A evidência registra 190 testes, com dados sintéticos e sem serviços reais. Não garante detecção de todo formato possível nem que processos persistentes já carregaram as mudanças. [Relatório TS-SEC](sdd/f3-02-ts-sec-20261017.md), [barreira](../src/pqbr/seguranca/barreira.py), [detector](../src/pqbr/seguranca/segredos.py).

**Backup externo — F3-04 aberto:** há um [planejador offline](../scripts/backup_offsite/planejar.py), validado com 24 testes específicos e regressão de 240 testes naquele snapshot. Não envia arquivos nem integra rclone. OAuth, retenção remota, envio e recuperação pelo Drive continuam sem validação. [Evidência e limites completos](sdd/f3-04-preparo-offline-20261017.md).

## Implementações

### Temas, grade e contrato editorial

**F5-01 implementado/testado localmente:** grade por data, três barreiras contra repetição, R10 inclusive para sugestão do proprietário, categorias bloqueadas e pontuação de polêmica. Pesos/limiares assinalados como proposta não viram parâmetros aprovados por aparecerem no código. [Implementação da grade](../src/pqbr/pipeline/grade.py), [RF-01..05](SPEC.md), [estado oficial](ROADMAP.md).

**F3-01/G3 e F7-01/G7 concluídos:** contratos Pydantic e contrato editorial v2 aprovado; oficial desde 23/10/2026 como [CONTRATO-EDITORIAL.md](CONTRATO-EDITORIAL.md) (t473). CTA contextual, convite natural a seguir e fallback “Segue o Porquê BR”; nunca pedir comentários. Diretrizes R1–R4/R6/R8/R9 são revisáveis e R5 é alerta não bloqueante. Os testes locais não equivalem a um vídeo final aprovado.

**F7-03/G7 concluído em 17/10:** `RoteiroShort` exige bloco visual; contadores locais de **500 chats/dia e 20 vídeos/dia são limites de segurança, não quotas oficiais**. O roadmap registra 25 testes focados e 107 unitários naquele snapshot, sem consumo real do NotebookLM. [Contratos](../src/pqbr/contratos/__init__.py), [código NotebookLM](../src/pqbr/workflows/notebooklm.py), [critérios e evidência registrada](TESTES.md).

**Identidade vigente:** t465 aprova stickmen e fichas consistentes para o módulo Flow, superando o planejamento anterior de 2D genérico. A decisão **não implanta fichas, catálogo ou resolvedor**: F5-04 permanece aberto. [Regras §§5–6](REGRAS.md), [requisitos RF-08/09](SPEC.md).

### NotebookLM e geração visual

NotebookLM é a **fonte intelectual** de pesquisa, temas, ideias, roteiro e SEO; agentes orquestram e validam, sem substituir esse trabalho por criação independente fora das exceções documentadas. **NotebookLM não é a rota vigente para gerar vídeo.** A hierarquia aprovada é Flow primário → Vids fallback/camada adicional → Gemini Web → Meta Vibes futuro. Isso é direção arquitetural, não confirmação de adapters operacionais. [ADR-010](ARQUITETURA.md), [blueprint completo](blueprints/modulo-producao-video/BLUEPRINT.md).

Há instalação PQBR de `notebooklm-py` 0.8.4, wrapper/perfil isolado e login registrados em F4-01/03/05. O roadmap também registra código de pacote canônico e cadernos efêmeros em NLM-EF-01. **Migração completa, dono único da sessão e ciclo E2E permanecem com etapas abertas**; sessões pessoais e dependências do MP32 não podem ser tratadas como migradas. **Papéis da sessão esclarecidos:** Toda a gestão do serviço Google NotebookLM é feita pela CLI `notebooklm-py`; a sessão lógica e o armazenamento do cliente não representam nova conta ou identidade de navegador. Camofox é a fonte única de autenticação/renovação da mesma conta Google usada por NotebookLM, Flow e Vids, no perfil persistente único `userId=pqbr`; o NotebookLM consome o estado pelo mecanismo existente `NOTEBOOKLM_REFRESH_CMD`/`nlm-sync.sh`, sem outro navegador ou renovador. A [referência viva, §3/§5](REFERENCIA-sessao-google.md) registra reauth headless e keepalive poke do cliente desativados. O esclarecimento não autoriza criar sessão, identidade, credencial ou serviço, não comprova operação atual nem fecha gate por si só; o aceite posterior de F00-01/G0 limita-se a SPEC, TESTES e RASTREABILIDADE, conforme roadmap. [F4 e NLM-EF no roadmap](ROADMAP.md), [arquitetura](ARQUITETURA.md), [código NotebookLM](../src/pqbr/workflows/notebooklm.py).

O [roadmap auxiliar de vídeo](blueprints/modulo-producao-video/ROADMAP.md) prevê piloto local de 50–70 s, iniciando por uma cena, sem publicação ou uploads nos testes. O G0 desse módulo foi aceito; contratos/adapters Flow/Vids, quotas/elegibilidade reais, E2E e QC ainda têm checkboxes abertos. O [índice do módulo](blueprints/modulo-producao-video/README.md) deve ser lido junto do plano atualizado, que já contém a implementação mockada de voz descrita abaixo.

### Narração ElevenLabs: ligada no código, geração bloqueada

A implementação backend de TTS está presente: [cliente ElevenLabs](../src/pqbr/integrations/elevenlabs.py) e [Activity de narração](../src/pqbr/workflows/narracao.py), chamada após auditoria aprovada no [workflow de produção](../src/pqbr/workflows/producao.py). O roadmap auxiliar registra **78 testes unitários e 6 de workflow com mocks**, não síntese real nessa implementação.

A [configuração versionada da voz](../config/voz_narracao.json) seleciona **Larissa — Vibrant and Playful**, `eleven_v3`, sem fallback de voz. `runtime_integrated=true` indica integração no código; **`generation_authorized=false` e `publication_authorized=false` mantêm geração/publicação bloqueadas**. Não é prova de deploy. Há manifesto/hash e reaproveitamento de artefato local; erro de transporte/resultado ambíguo não recebe retry automático. Isso não garante exactly-once remoto após perda de resposta. [Decisão e limites completos](blueprints/modulo-producao-video/ROADMAP.md).

### Produção, auditoria e pós

**F5-02 parcial:** `GradeDiariaWorkflow` e `EpisodioProducaoWorkflow` têm código/testes de prazo, reserva, reprovação e espera por polêmica. O roadmap registra Schedules de grade/lote **pausados**; NotebookLM/auditor/publicação reais dessa composição falham sem simulação. A integração mockada de TTS não remove esses bloqueios. [Código de produção](../src/pqbr/workflows/producao.py), [testes e resultados registrados](TESTES.md), [gate G5](ROADMAP.md).

**F7-02/G7 e PQBR-114 pausados/bloqueados:** existem [decisor visual](../src/pqbr/pipeline/auditor_visual.py), [adapter Gemini/Camofox](../src/pqbr/workflows/auditor_gemini.py), [checagens textuais LOOP](../src/pqbr/pipeline/auditor_texto.py) e [seletor de capa](../src/pqbr/pipeline/capa.py). Código e execução exploratória anterior não tornam o auditor integrado/calibrado. O roadmap registra 35 testes focados e 93 unitários em uma rodada, mas **faltam rótulos humanos validados para medir falsos aprovados/reprovados**; a pausa do proprietário continua valendo.

Segurança pode reprovar; imagem×fala e outras métricas não reprovam sozinhas. O experimento t461 corrigido foi exploratório, sem gabarito suficiente para fechar V3/G7. O seletor de capa ainda é descrito sem caller no workflow; adapter Jev do LOOP e integração seguem pendentes. **F5-05 render/pós FFmpeg permanece aberto**, mesmo havendo peças locais. [Estado e limites detalhados](ROADMAP.md), [TS-03/V3](TESTES.md).

**Consumo e retenção — F3-06/F3-07 concluídos com limites:** há registro de consumo por modelo, seção de relatório, migração 0011 aplicada e Schedule de retenção registrado como ativo às 04:15. Retenção: brutos 90 dias, resumo 25 meses. A ligação de todas as chamadas de modelo depende dos backends; relatório entregue pelo canal não está comprovado por isso. [Roadmap](ROADMAP.md), [critérios TS-12 e resultados](TESTES.md).

## Correção autônoma F3-05

**Mapa das decisões documentais de 17/10/2026 — não é nova autoridade:** [REGRAS §3.1](REGRAS.md) define **5–15 min de pacing local entre o término de uma intervenção Camofox e o início da próxima na mesma sessão**, não duração nem padrão universal anti-detecção. Usar espera por condição/prontidão da UI e respeitar regras do provedor e `Retry-After` mais longo. CAPTCHA/bloqueio ou consentimento necessário interrompem, sem bypass. Exceção técnica permanece **terminal, sem retry/fallback automático ou reexecução**. As fontes públicas já citadas estão em REGRAS §3.1.

Para RNF-11/12, consultar [SPEC §2](SPEC.md), [ARQUITETURA §6](ARQUITETURA.md) e [TESTES §4](TESTES.md): cobertura documental transversal e caso negativo de leitura somente onde houver controle técnico verificável, com fixtures sintéticas, sem presumir proteção implementada. **TS-11 = correção; TS-12 = retenção; TS-ARM = armazenamento; TS-MON = monitores**; TS-GOV-01/02 detalham a cobertura transversal. Novos critérios apenas especificados, não executados. O [ROADMAP, F00-01/F3-05](ROADMAP.md) registra **F00-01/G0 fechado por aceite explícito de José em 17/10/2026 de SPEC, TESTES e RASTREABILIDADE; F3-05/G4 aberto; F05-06 no-arm**. TS-GOV-01 teve revisão documental concluída; o controle técnico de leitura RNF-12 não foi demonstrado e TS-GOV-02 não foi executado, sem alegação de proteção implementada ou waiver de evidência técnica exigível. Este mapa não altera os fatos V1/V2 ou B3 abaixo.


**Verificador offline posterior:** [V1](sdd/evidencias-f3-05-verificador-offline-20261017-V1/README.md) e [V2](sdd/evidencias-f3-05-verificador-integrado-offline-20261017-V2/README.md); a V2 registra **33 testes (20 da V1 + 13 novos)** e integra apenas verificação offline de dados/arquivos, não runner B3, coleta operacional ou serviços. Não reclassifica a B3: **exit 1 / FAILED_FINAL_VERIFIER**, manifesto consumido/não reutilizável e **F3-05/G4 aberto**. Para estado e limites, consulte [F3-05 no roadmap canônico](ROADMAP.md).


**Resultado posterior — prova única PQBR-121:** aceite humano canônico validado; `result.outcome=accepted` é o campo real, não `result.decision`. Uma rodada em Temporal 1.32.1 descartável: **runtime PASS**, primeira FAILED/1 tentativa/sem reexecução; segunda retomada uma vez/1 efeito falso; receipt/outbox SQLite local (1/1), dedup comprovada e 3 históricos com replay ok. **O orquestrador falhou no verificador final (`KeyError: operational_states`, exit 1)** depois de concluir teste e limpeza; não houve nova execução nem ocultação da falha. Verificação suplementar somente leitura confirmou limpeza integral, inventário igual, 1.664 hashes/quatro Workers persistentes preservados e Temporal operacional sem restart. Manifesto agora consumido e não reutilizável. [Evidência, limites e limpeza](sdd/evidencias-f3-05-confirmacao-janela-20261017-B3-v2/README.md). Isso não prova integração operacional, crash safety, transação distribuída, fencing ou exactly-once externo; **F3-05/G4 continua aberto**. A nota de preparação abaixo é histórica.

**Nova preparação B3 v2 — PQBR-121:** confirmação `ee39501d-3787-470a-b871-7800669759b9` criada em Engenharia/backlog, sem agente, para tutibom Board; `request_confirmation`, `human_only`, `continuationPolicy=none`, status **pending** no objeto retornado da criação. Validade fixada de **17/10/2026 19:15 até 18/10/2026 19:15 (UTC−03)**. [Evidência e manifesto durável](sdd/evidencias-f3-05-confirmacao-janela-20261017-B3-v2/README.md) em `awaiting_paperclip_approval`, **não ativo até novo aceite**. P120 não se aplica e não foi alterado. Esta etapa não executou ensaio/runtime, não consumiu autorização nem registrou receipt; **F3-05/G4 permanece aberto**.

**F3-05/G4 permanece aberto.** É importante separar três níveis que coexistem no checkout:

| Nível | O que foi comprovado | O que não está entregue |
|---|---|---|
| Workflow existente | [correcao.py](../src/pqbr/workflows/correcao.py) contém triagem → até três intervenções → verificação → registro com barreira. As Activities reais falham fechadas sem simulação. A [validação local](sdd/f3-05-local-20261017.md) registra 26 testes e regressão de 216 naquele momento. A [espera determinística](sdd/f3-05-intervalo-deterministico-20261017.md) acrescentou timers Camofox de 300–900 s com patch/replay. | Backends reais Jev/Paperclip, checagem real de conta antes da ação, escrita de registro/outbox e aprendizado Hindsight. `registrar_correcao` ainda é stub. |
| Roteamento operacional | O [diagnóstico em Temporal isolado](sdd/f3-05-roteamento-temporal-20261017.md) demonstrou que a Activity de intervenção herda a fila do workflow; ferramenta/sessão não a redirecionam automaticamente. | Corrigir a topologia operacional e garantir exclusão por sessão; a capacidade 1 de um Worker não resolve isso globalmente. |
| Candidata separada | [candidato_sessao.py](../src/pqbr/workflows/candidato_sessao.py) usa ator por sessão, Signal-With-Start, dedup por ID/payload e fila Camofox explícita experimental. A [evidência da integração candidata](sdd/f3-05-integracao-candidata-20261017.md) registra 10 cenários em Temporal 1.32.1 descartável, 81 testes em memória e replay de 40 capturas de 38 runs. | Não registrada nos Workers persistentes, sem backends/efeitos reais. RPC de Signal não confirma processamento. Sem exactly-once, fencing ou recuperação geral de ator terminal. |

O [supervisor sintético por sessão](sdd/f3-05-supervisor-sessao-20261017.md) passou 3 testes runtime e replay de 11 capturas de 7 runs: preservou uma operação pendente após a anterior falhar, retomando somente por comando correlacionado. Registro e Activities são falsos; correlação não é autenticação.

O [protótipo offline de autorização humana](sdd/evidencias-f3-05-autorizacao-humana-20261017-H1/README.md) passou 57 testes com Paperclip, Discord e supervisor falsos. Ticket, revisão, allowlist, receipt e persistência antes do resume são exercitados **em memória**, sem autenticação real, crash safety ou integração Temporal nessa rodada.

**H2 — adaptador da confirmação canônica, protótipo fake/desligado:** o [relatório H2](sdd/evidencias-f3-05-confirmacao-canonica-20261017-H2/README.md) registra **104/104 testes com fakes em memória**, sem falhas, erros ou pulados. O adaptador usa `request_confirmation` no **mesmo ticket existente** para painel e Discord, com a mesma interação/chave de confirmação, política solicitada e efetiva `human_only`, destinatário humano pelo vínculo já aprovado e `continuationPolicy="none"`; sem destinatário agente nem alvo `plan`. A decisão canônica falsa é gravada e relida antes do consumo; revisão, pendentes exatos, receipt e deduplicação são exercitados somente em memória. Recusa/expiração, identidade inválida, divergência e receipt incerto bloqueiam, sem retry/fallback automático nem reexecução da operação terminal. **Não houve tickets ou mensagens reais, autenticação ou integração real, HTTP ou comando Temporal real; nada foi conectado aos Workers persistentes. Integração durável real ainda falta**, incluindo transporte/receptor reais, recuperação após crash e persistência durável. Não foram provados replay Temporal, fencing ou exactly-once externo. O protótipo não redefine o autorizador nem a integração já aprovada. **F3-05/G4 continua aberto; F7-02/G7 e PQBR-114 pausados; F05-06 no-arm.**

**Política preservada:** exceção técnica de intervenção continua terminal, sem retry/fallback que a transforme em sucesso; pode bloquear pendentes. Revisão futura dessa política é uma proposta, não implementação aprovada nem lembrete criado. Os protótipos não fecham TS-11, F3-05/G4 ou F05-06. Para notas posteriores e outras evidências, retorne ao [item F3-05 do roadmap](ROADMAP.md); esta wiki não acompanha automaticamente novas atualizações.

## Canal do José e painel (t471/t474)

**Decisão 23/10/2026:** o plano Discord/Paperclip (t464) foi revogado. O canal do José é o **Telegram (Hermes `pqbr`)**; aprovações são **sinais do Temporal**; o painel é a **Temporal UI** (painel próprio fica para depois). Os documentos do piloto Discord estão em `docs/_obsoleto/blueprints/canal-chat-pqbr/` (histórico; a lista de fontes de aviso do inventário pode ser reaproveitada). Pendente: token de bot próprio do perfil `pqbr` para os avisos (`pqbr-pedidos-jose` não entrega).

## Pendências e pausas

| Frente | Estado a preservar | Fonte completa |
|---|---|---|
| Gates de entrada | F00-01/G0 geral fechado por aceite explícito de José em 17/10/2026 de SPEC, TESTES e RASTREABILIDADE, sem liberação operacional. Independente do G0 do módulo de vídeo; nenhum outro gate fechado. | [Roadmap geral](ROADMAP.md), [roadmap do módulo](blueprints/modulo-producao-video/ROADMAP.md). |
| Organização | F1-01/F1-02 suspensos para reconciliação com a organização existente; não executar importação nova. F1-04 ainda aberto. | [Roadmap geral](ROADMAP.md). |
| Sessões e resiliência | F4 tem migração parcial; F4C-05/06/08 e F6-01 continuam abertos. Keepalive não equivale ao guardião completo validado. | [Roadmap geral](ROADMAP.md). |
| Correção e auditor | F3-05/G4 aberto; F7-02/seu G7 e PQBR-114 pausados. F7-01 e F7-03 concluídos não removem a pausa do auditor. | [Roadmap geral](ROADMAP.md), [testes](TESTES.md). |
| Publicação e arquivos | F8-01/02/03 pendentes: publicação/item 5 completos, armazenamento/limpeza e local de revisão humana. Código parcial não é autorização de upload/agendamento. | [Fase 8](ROADMAP.md). |
| Monitores e interação | F9 e F10 pendentes: relatório/monitores, compliance/HOLD, analista, banco aprovado de frases e comunidade com sombra. Requisitos de ações automáticas não comprovam implementação. | [Roadmap](ROADMAP.md), [requisitos](SPEC.md). |
| Liberação | F12-01/G12 e validações V1–V7 pendentes como conjunto; metas do piloto ainda em construção. | [Validação completa](TESTES.md), [roadmap](ROADMAP.md). |

## Documentação completa

**Para retomar:** leia as fontes na ordem canônica [REGRAS](REGRAS.md) → [SPEC](SPEC.md) → [ARQUITETURA](ARQUITETURA.md) → [TESTES](TESTES.md) → [ROADMAP](ROADMAP.md); então use o roadmap para localizar o estado e o próximo passo autorizado. O [índice documental](README.md) e as [instruções de entrada dos agentes](../AGENTS.md) explicam a navegação. Blueprints e evidências não substituem essas autoridades.

**Para aprofundar por assunto:** [produção de vídeo](blueprints/modulo-producao-video/BLUEPRINT.md), [checklist técnico do módulo](blueprints/modulo-producao-video/ROADMAP.md), [motor Temporal](sdd/adr-001-orquestrador.md), [segurança local](sdd/f3-02-ts-sec-20261017.md), [backup offsite ainda offline](sdd/f3-04-preparo-offline-20261017.md) e [candidata de correção](sdd/f3-05-integracao-candidata-20261017.md).

As descrições se baseiam nas fontes lidas diretamente ou na análise paralela; os links também facilitam o acesso a recursos/código existentes, sem atribuir a eles capacidades não verificadas. Não foram abertos `docs/arquivo/`, `docs/pesquisas/`, `docs/DECISOES-LOG.md`, o contrato editorial antigo ou outros documentos legados/rascunhos. A versão v2 de nome histórico `CANDIDATO` foi consultada porque o roadmap registra seu aceite. Nenhum documento existente foi editado por este trabalho; não houve commit/push, ticket, mensagem real, geração ou ativação.
