# ADR-011: agentes PydanticAI em activities do Temporal

- **Status:** aprovado por José em 23/10/2026 (t474). Substitui a ADR-002 (Paperclip = camada de agentes + painel).
- **Contexto:** o Paperclip duplicava orquestração (issues, heartbeats, rotinas) com o Temporal, trouxe bugs de lock (409), CLI/serve quebrados e um painel que José não quer manter. O princípio do projeto é agente-first: fácil para agentes de programação construírem e manterem.

## Decisão
1. **Temporal** é o único dono do fluxo (workflows, Schedules, retentativas, sinais). **Jev** segue como decisor/classificador estruturado.
2. **Agentes = PydanticAI + Pydantic v2**, chamados **dentro de activities do Temporal**. Cada agente recebe entrada tipada e devolve saída tipada; saída inválida → retry/playbook `saida-invalida`.
3. **O agente só gera e valida.** Efeito externo (Drive, YouTube, Camofox, NotebookLM, banco) fica em activity determinística separada, idempotente.
4. **Modelos** pelo 9router (combos reais). **Personas** em `company/agents/<slug>/AGENTS.md`; **playbooks** em `company/playbooks/`. **Memória** via adaptador Hindsight.
5. **Interface do José:** Telegram (Hermes `pqbr`) para avisos, pedidos e aprovações; aprovação = **sinal do Temporal** (ID autorizado, estado válido, fail-closed, idempotente). **Painel:** Temporal UI; painel próprio mais tarde (t471).
6. **Paperclip em retirada:** o código dele não é alterado; `infra/paperclip-db/` fica até o desligamento; não criar nada novo nele.

## Princípios acrescentados (t512–t514, 24/10/2026)
  1. **Temporal = sistema nervoso** (t514): a peça mais rígida; trocável em tese, mas a última a mudar, pela consistência. Toda decisão que exigiria um humano e roda sozinha é **determinística e passa pelo Temporal** (durável, registrada, reexecutável/replay, com retentativas e sinais). O Temporal **não** é escondido atrás de camadas extras: workflows e activities usam o SDK direto.
  2. **NotebookLM = centro nervoso editorial e motor do canal** (t512): decisões, temas, roteiros e direção do canal; a produção segue os caminhos que ele norteia. A **geração de vídeo saiu do NotebookLM** por determinismo (Flow é a rota primária).
  3. **Sistema modular** (t513): cada motor é peça trocável atrás de um contrato (interface Pydantic + adaptador), escolhida por config (`config/motores.json`; portas em `src/pqbr/motores/`): `MotorIntelectual` (hoje NotebookLM), `GeradorVideo` (hoje Flow; cadeia Flow (primário) → Google Vids pelo navegador → Meta Vibes quando os dois falham ou esgotam a cota; tudo pelo navegador nas cotas já pagas, **sem APIs** (t517); NotebookLM vídeo só como alternativa). Agentes e motores giram em volta do Temporal.
  4. **8 papéis-agente** (t512): Diretor, Líder Editorial (monta pedidos ao motor e valida respostas), Pesquisador de Origem, Auditor, Compliance, Guardião, Observador, Dev (diagnostica e propõe; nunca aplica; José aplica com agentes externos). Roteirista, SEO e Caçador Sazonal viram etapas de workflow que chamam o MotorIntelectual; Comunidade adiada.
  5. **Contratos Pydantic v2 = peça central do determinismo, junto com o Temporal** (t515): todo dado que cruza agente, motor ou serviço web passa por contrato. Ficam **num lugar só** (`src/pqbr/contratos/`, inclusive os das portas de motor), cada um **versionado em SemVer** (`contratos.VERSOES`; MAJOR = quebra, MINOR = campo opcional/regra mais frouxa, PATCH = doc; teste obriga). **Revisão contínua**, porque regras e fluxos dos serviços web mudam: testes de contrato por adaptador (respostas reais gravadas como fixtures), canários periódicos por adaptador web em Schedule do Temporal que detectam deriva, e Observador/Dev sinalizando quebras (proposta em `docs/sdd/PROPOSTA-papeis-skills.md` §Revisão de contratos).

## Consequências
- Docs com org/issues/heartbeats do Paperclip (ARQUITETURA §10, partes do `docs/AGENTES.md`, ROADMAP F05-06/F05-08/F1-*) são históricos até a reescrita.
- Primeiro workflow a migrar (proposta): `ReposicaoTemasWorkflow`, testado sem publicação.
- Testes unitários sem rede para cada agente (modelo fake do PydanticAI).
