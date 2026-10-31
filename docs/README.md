# Documentação da PQBR — mapa e autoridade

Atualizado em 27/10/2026 (t129u). Este índice distingue os documentos normativos, o roadmap oficial e os planos auxiliares. Não é uma nova fonte de decisão. Paperclip só aparece como histórico ou como infraestrutura em retirada.

## Ordem de autoridade

Siga a ordem definida em `REGRAS.md`
- **Processo de criação (t160u):** [`processos/CRIACAO-README.md`](processos/CRIACAO-README.md) — consultar antes de cada produção; playbooks por plataforma em `processos/` §0:

1. `REGRAS.md` — regras de negócio e governança.
2. `SPEC.md` — requisitos.
3. `ARQUITETURA.md` — decisões e desenho técnico.
4. `TESTES.md` — critérios e evidências de validação.
5. `ROADMAP.md` — tarefas, estado atual, dependências e gates do projeto.

A `AGENTS.md` da raiz é gerada do onboarding. `company/agents/<slug>/AGENTS.md` guarda a persona de cada papel. `docs/AGENTES.md` é o roster vigente (9 papéis). `RASTREABILIDADE.md` liga requisito → desenho → tarefa → teste. `LACUNAS-fluxo.md` lista só o que ainda falta no código. `CONTRATO-EDITORIAL.md` é o contrato editorial oficial (v2, t473).

## Os dois roadmaps não são intercambiáveis

- `docs/ROADMAP.md` é o roadmap canônico de toda a PQBR. Abrange as fases gerais de infraestrutura, organização, canal, produção e liberação; contém o anexo de fases, gates e rollback antes mantido em `PLANO.md`. O primeiro gate operacional ainda aberto é F05-06; F05-08 e F05-09 também permanecem abertos. F00-01 é outra revisão e não deve ser confundida com o G0 do módulo de vídeo.
- `docs/blueprints/modulo-producao-video/ROADMAP.md` é um checklist auxiliar somente do módulo de produção de vídeo. O G0 deste módulo foi aceito por José em 15/10/2026; isso não fecha os itens técnicos da Fase 0, não substitui o roadmap canônico e não autoriza geração real, upload ou publicação.

## Documentos por diretório

### `blueprints/modulo-producao-video/`

Documentos do módulo visual com Flow como rota primária e Vids como fallback. `README.md` é o índice local; `BLUEPRINT.md` define arquitetura, escopo e decisões; `ROADMAP.md` lista fases e evidências. São documentos de planejamento, não implementação já concluída.

### `sdd/`

ADRs vigentes e evidências. Leia a data antes de aplicar qualquer passo. O dry-run de uma segunda organização está em `_obsoleto/sdd/f1-02-dryrun.md` e não se repete. As pastas `evidencias-f3-05-*` ficam aqui porque o F3-05 ainda está aberto no ROADMAP.

### Outros documentos vivos

- `REFERENCIA-sessao-google.md` — referência operacional da sessão Google/Camofox.
- `operacao/onboarding-agente-externo.md` — como o agente externo entra pelo MCP.
- O rascunho de SOUL, o briefing do YT-LLM, o resumo de stack de 17/10 e o checklist pré-E2E de 12/10 estão em `_obsoleto/` (t129u).
- `operacao/GUIA-ACESSO-PC-TEMPORAL.md` — caminhos verificados para acessar o PC e o Temporal (UI = painel do José), sem credenciais.
- `sdd/adr-011-agentes-pydanticai-temporal.md` — agentes PydanticAI em activities do Temporal (substitui ADR-002).
- `../CHANGELOG.md` — mudanças relevantes do repositório.

## Preservação e descarte

`docs/_obsoleto/` é a lixeira temporária (t472): arquivos obsoletos movidos com `git mv`, nada apagado; o índice `_obsoleto/README.md` diz motivo e substituto. José decide depois o destino. Relatórios de dry-run e evidências em `sdd/` continuam como snapshots históricos. `docs/arquivo/`, `docs/_obsoleto/`, `docs/pesquisas/` e `docs/DECISOES-LOG.md` seguem as restrições de consulta de `REGRAS.md` §0.
