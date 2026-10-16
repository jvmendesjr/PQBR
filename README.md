# PQBR (Porquê BR)

Aplicação de produção do canal Porquê BR: Shorts de sátira leve, em stickman, sobre manias e rotinas dos brasileiros.

## Orientação para agentes e mapa documental

`AGENTS.md` na raiz é a porta de entrada para agentes que trabalham neste checkout. `docs/README.md` é o mapa de documentos, diretórios e autoridade. O roster de papéis fica em `docs/AGENTES.md`; as instruções específicas de cada agente Paperclip ficam em `company/agents/<slug>/AGENTS.md`.

Há dois roadmaps com escopos diferentes. `docs/ROADMAP.md` é o roadmap canônico geral e fonte do estado oficial. `docs/blueprints/modulo-producao-video/ROADMAP.md` é auxiliar e cobre apenas o módulo de produção de vídeo. Não misture nem use um para substituir o outro.

## Ordem de autoridade e de leitura

Em conflito, vale o documento de maior autoridade, nesta ordem:

1. `docs/REGRAS.md`: regras aprovadas pelo José; §0–§3 são a constituição.
2. `docs/SPEC.md`: requisitos funcionais e não funcionais, histórias e critérios de aceite.
3. `docs/ARQUITETURA.md`: ADRs, modelo de dados, workflows do Temporal, integração com o Paperclip e contratos Pydantic v2.
4. `docs/TESTES.md`: plano de testes e critérios de validação.
5. `docs/ROADMAP.md`: tarefas, estado e próximo passo do projeto.

`docs/RASTREABILIDADE.md` liga requisito → desenho → tarefa → teste. As fases, gates e rollback antes descritos em `PLANO.md` foram incorporados ao anexo de `docs/ROADMAP.md`; não há um `docs/PLANO.md` atual separado.

## ⛔ Documentos restritos

Arquivos de pré-construção e material legado não devem ser consultados sem aprovação explícita do José, conforme `docs/REGRAS.md` §0. Isso inclui `docs/CONTRATO-EDITORIAL.md`, `docs/DECISOES-LOG.md`, `docs/pesquisas/`, `docs/arquivo/` e qualquer rascunho legado. O que vale como regra editorial está em `docs/REGRAS.md` §5.

## Regras do repositório

- Dúvida ou conflito sem certeza: não adivinhar; marcar “EM CONSTRUÇÃO — aguardando José” (t323).
- Decisão nova entra no `DECISOES-LOG.md` e no `REGRAS.md` no mesmo commit; atualizar também requisitos, desenho, testes e tarefas afetados.
- Não colocar senhas, tokens, cookies, dados pessoais, IPs ou IDs internos neste repositório.
- **Sessão Google (referência viva):** [`docs/REFERENCIA-sessao-google.md`](docs/REFERENCIA-sessao-google.md) — Camofox é a fonte/renovador da sessão; NotebookLM só a lê.
- **Antes de qualquer E2E:** [docs/LICOES-pre-E2E.md](docs/LICOES-pre-E2E.md), seguindo o checklist em ordem.
