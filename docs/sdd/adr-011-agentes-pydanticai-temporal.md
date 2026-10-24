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

## Consequências
- Docs com org/issues/heartbeats do Paperclip (ARQUITETURA §10, partes do `docs/AGENTES.md`, ROADMAP F05-06/F05-08/F1-*) são históricos até a reescrita.
- Primeiro workflow a migrar (proposta): `ReposicaoTemasWorkflow`, testado sem publicação.
- Testes unitários sem rede para cada agente (modelo fake do PydanticAI).
