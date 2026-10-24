# Documentação da PQBR — mapa e autoridade

Atualizado em 23/10/2026 (t471–t474: canal Telegram + sinais do Temporal, painel Temporal UI, agentes PydanticAI em activities do Temporal — ADR-011; Paperclip em retirada). Este índice distingue os documentos normativos, o roadmap oficial do projeto e os planos auxiliares por módulo. Não é uma nova fonte de decisão.

## Ordem de autoridade

Siga a ordem definida em `REGRAS.md` §0:

1. `REGRAS.md` — regras de negócio e governança.
2. `SPEC.md` — requisitos.
3. `ARQUITETURA.md` — decisões e desenho técnico.
4. `TESTES.md` — critérios e evidências de validação.
5. `ROADMAP.md` — tarefas, estado atual, dependências e gates do projeto.

A `AGENTS.md` da raiz do repositório é a entrada de instruções para agentes; `company/agents/<slug>/AGENTS.md` contém as instruções específicas de cada papel. `docs/AGENTES.md` (com E depois do G) é o roster e desenho dos papéis, não o arquivo de instruções. `RASTREABILIDADE.md` liga requisito → desenho → tarefa → teste e `LACUNAS-fluxo.md` lista lacunas operacionais. `CONTRATO-EDITORIAL.md` é o contrato editorial oficial (v2, t473), com as seções canônicas do v1 no Anexo A.

## Os dois roadmaps não são intercambiáveis

- `docs/ROADMAP.md` é o roadmap canônico de toda a PQBR. Abrange as fases gerais de infraestrutura, organização, canal, produção e liberação; contém o anexo de fases, gates e rollback antes mantido em `PLANO.md`. O primeiro gate operacional ainda aberto é F05-06; F05-08 e F05-09 também permanecem abertos. F00-01 é outra revisão e não deve ser confundida com o G0 do módulo de vídeo.
- `docs/blueprints/modulo-producao-video/ROADMAP.md` é um checklist auxiliar somente do módulo de produção de vídeo. O G0 deste módulo foi aceito por José em 15/10/2026; isso não fecha os itens técnicos da Fase 0, não substitui o roadmap canônico e não autoriza geração real, upload ou publicação.

## Documentos por diretório

### `blueprints/modulo-producao-video/`

Documentos do módulo visual com Flow como rota primária e Vids como fallback. `README.md` é o índice local; `BLUEPRINT.md` define arquitetura, escopo e decisões; `ROADMAP.md` lista fases e evidências. São documentos de planejamento, não implementação já concluída.

### `sdd/`

ADRs, relatórios de gate e evidências de testes. Leia seu status e data antes de aplicar qualquer passo: alguns arquivos registram snapshots históricos. Em particular, `f1-02-dryrun.md` documenta um dry-run antigo de criação de uma segunda organização, nunca executado; F1-01/F1-02 estão suspensos no roadmap canônico e o comando `--target new` não deve ser repetido.

### Outros documentos vivos

- `REFERENCIA-sessao-google.md` — referência operacional da sessão Google/Camofox.
- `hermes-pqbr/SOUL-rascunho.md` — persona do perfil Hermes `pqbr`, canal Telegram do José (t474).
- `LICOES-pre-E2E.md` — lições para o E2E.
- `operacao/GUIA-ACESSO-PC-TEMPORAL.md` — caminhos verificados para acessar o PC e o Temporal (UI = painel do José), sem credenciais.
- `sdd/adr-011-agentes-pydanticai-temporal.md` — agentes PydanticAI em activities do Temporal (substitui ADR-002).
- `../CHANGELOG.md` — mudanças relevantes do repositório.

## Preservação e descarte

`docs/_obsoleto/` é a lixeira temporária (t472): arquivos obsoletos movidos com `git mv`, nada apagado; o índice `_obsoleto/README.md` diz motivo e substituto. José decide depois o destino. Relatórios de dry-run e evidências em `sdd/` continuam como snapshots históricos. `docs/arquivo/`, `docs/_obsoleto/`, `docs/pesquisas/` e `docs/DECISOES-LOG.md` seguem as restrições de consulta de `REGRAS.md` §0.
