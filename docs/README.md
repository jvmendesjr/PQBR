# Documentação da PQBR — mapa e autoridade

Atualizado em 16/10/2026. Este índice distingue os documentos normativos, o roadmap oficial do projeto e os planos auxiliares por módulo. Não é uma nova fonte de decisão.

## Ordem de autoridade

Siga a ordem definida em `REGRAS.md` §0:

1. `REGRAS.md` — regras de negócio e governança.
2. `SPEC.md` — requisitos.
3. `ARQUITETURA.md` — decisões e desenho técnico.
4. `TESTES.md` — critérios e evidências de validação.
5. `ROADMAP.md` — tarefas, estado atual, dependências e gates do projeto.

A `AGENTS.md` da raiz do repositório é a entrada de instruções para agentes; `company/agents/<slug>/AGENTS.md` contém as instruções específicas de cada papel. `docs/AGENTES.md` (com E depois do G) é o roster e desenho dos papéis, não o arquivo de instruções. `RASTREABILIDADE.md` liga requisito → desenho → tarefa → teste e `LACUNAS-fluxo.md` lista lacunas operacionais. `CONTRATO-EDITORIAL.md` é um rascunho sujeito às restrições de leitura de `REGRAS.md` §0; contém referências de planejamento históricas e não deve substituir o roadmap canônico.

## Os dois roadmaps não são intercambiáveis

- `docs/ROADMAP.md` é o roadmap canônico de toda a PQBR. Abrange as fases gerais de infraestrutura, organização, canal, produção e liberação; contém o anexo de fases, gates e rollback antes mantido em `PLANO.md`. O primeiro gate operacional ainda aberto é F05-06; F05-08 e F05-09 também permanecem abertos. F00-01 é outra revisão e não deve ser confundida com o G0 do módulo de vídeo.
- `docs/blueprints/modulo-producao-video/ROADMAP.md` é um checklist auxiliar somente do módulo de produção de vídeo. O G0 deste módulo foi aceito por José em 15/10/2026; isso não fecha os itens técnicos da Fase 0, não substitui o roadmap canônico e não autoriza geração real, upload ou publicação.

## Documentos por diretório

### `blueprints/canal-chat-pqbr/`

Documentação da conversa Discord/Paperclip e da migração dos avisos. O `README.md` desse diretório resume o estado; `GUIA-USO-DISCORD.md` orienta o uso do canal; blueprint, avaliação e inventário guardam decisões, evidências e lacunas. Aprovação Temporal e alertas proativos duráveis continuam dependentes dos gates F05-06/F05-08.

### `blueprints/modulo-producao-video/`

Documentos do módulo visual com Flow como rota primária e Vids como fallback. `README.md` é o índice local; `BLUEPRINT.md` define arquitetura, escopo e decisões; `ROADMAP.md` lista fases e evidências. São documentos de planejamento, não implementação já concluída.

### `sdd/`

ADRs, relatórios de gate e evidências de testes. Leia seu status e data antes de aplicar qualquer passo: alguns arquivos registram snapshots históricos. Em particular, `f1-02-dryrun.md` documenta um dry-run antigo de criação de uma segunda organização, nunca executado; F1-01/F1-02 estão suspensos no roadmap canônico e o comando `--target new` não deve ser repetido.

### Outros documentos vivos

- `REFERENCIA-sessao-google.md` — referência operacional da sessão Google/Camofox.
- `hermes-pqbr/` — configuração legada preservada como rollback durante a migração; não pausar antes de F05-09.
- `LICOES-pre-E2E.md` — lições para o E2E.
- `operacao/GUIA-ACESSO-PC-PAPERCLIP-CLI.md` — caminhos verificados para acessar o PC, a interface e a CLI do Paperclip, sem credenciais.

## Preservação e descarte

Não foi identificado um arquivo seguro para excluir nesta revisão. Relatórios de dry-run e snapshots antigos são mantidos como evidência, com seu caráter histórico explicitado, em vez de apagados. `docs/arquivo/`, `docs/pesquisas/` e `docs/DECISOES-LOG.md` continuam sujeitos às restrições de consulta de `REGRAS.md` §0; esta revisão não os abriu nem os alterou.
