# PQBR — onboarding do agente (gerado; não editar à mão)

## ESTADO ATUAL da PQBR — continue daqui

Fonte única de "onde estamos". Não repete o ROADMAP: aponta os itens por id. **Atualize este arquivo a cada correção ou pendência resolvida.** O hook pre-commit exige isso quando o commit toca ROADMAP, LACUNAS, DECISOES-LOG ou CHANGELOG, e o `registrar_alteracao` exige isso para `tipo` correcao ou pendencia_resolvida.

Atualizado: 27/10/2026 (t129u: lacunas conferidas no código; documentos obsoletos movidos) · versão 0.16.10

## Onde estamos
- **Produção:** o lote do saldo está em `runtime/lote-saldo/` (um diretório por tema). O EP1002 olhos-da-cara foi reprovado e descartado (`runtime/lote-saldo/_descartado/`), e o tema voltou a `proposto`.
- **Publicação (ROADMAP F8-01):** o fluxo pelo Temporal está pronto. O worker foi reiniciado em 27/10 às 08:56 (-03, São Paulo; t128u) e carrega o fallback do refresh e o ensaio. `YOUTUBE_DRY_RUN=true`. Nada foi enviado. Até a produção ativa, vídeo aprovado que subir fica privado; público só depois, na ordem dos roteiros e nas janelas.
- **Agente externo:** o servidor MCP 0.2+ só funciona pela tailnet. A memória escrita leva o autor (o cliente) e o commit. O protocolo obrigatório está no AGENTS.md. O `initialize` do `pqbr-mcp` já devolve a frase de honestidade (t126u), desde o reinício das 08:56. Hindsight: bank `pqbr` com 877 documentos; as 7 candidatas restantes foram apagadas (t128u).
- **Documentos (t129u):** `docs/LACUNAS-fluxo.md` só lista o que ainda falta no código. O roster vigente está em `docs/AGENTES.md`. Briefing, checklist pré-E2E, rascunho de SOUL e propostas não aplicadas foram para `docs/_obsoleto/`. As provas do F3-05 continuam em `docs/sdd/` porque o item segue aberto no ROADMAP.

## Próximo passo
José vê os outros vídeos do lote quando puder. Em 27/10 ele disse que não consegue vê-los agora. O EP1003 cafe-fraco segue o único aprovado. Nenhum vídeo vai a público até ele declarar a produção ativa.

## Pendências abertas
| # | Pendência | Ref. ROADMAP | Dono | Bloqueio |
|---|---|---|---|---|
| P1 | José ainda vê os outros vídeos do lote. Em 27/10 ele disse que não consegue vê-los agora. O EP1003 cafe-fraco já está aprovado (26/10, único até agora); não roda o LOOP nesse episódio | Estado 26/10 · Próximo 5 | José | aguardando José nos demais |
| P2 | Publicação: worker reiniciado 27/10 08:56 (-03), 0 workflows Running antes e depois. Código t124u–t126u neste processo. `YOUTUBE_DRY_RUN=true`. Envio real desligado. Refresh do app em teste vence ~2/11 21:20 (-03). Mapa de cliques continua vazio: nenhuma tela foi vista | F8-01 | agente | sem envio até a produção ativa |
| P3 | Teste: LOOP por cena vs o atual | Estado 26/10 · Testes pendentes | agente | depois do fluxo de publicação |
| P4 | **Feito (t108u/t109u).** Juiz por etapa (`gemini_juiz` v1.0.0): pré-produção usa 3.8 Flash; produção (VISUAL e LOOP) usa 4 Argon Baixo. O worker `pqbr-episodio-worker` foi reiniciado com OK do José às 16:57 (-03), e o poller está ativo na fila `episodio-pqbr`, ns `pqbr` | Estado 26/10 · DECISOES-LOG t109u | agente | concluído |
| P5 | Imagens de referência do elenco (`ASSET_personagem_{masculino,feminino}-v1`) | Estado 26/10 · Próximo 4 | agente | geração paga: OK do José (postergado) |
| P6 | Activity do Storyboard no Temporal (bloqueia a geração sem ele) | Estado 26/10 · Próximo 2; R2 | agente | postergado |
| P7 | **Feito (t108u).** O gate VISUAL agora tem `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco` (FichaCena/REGRAS §25), e cada um reprova sozinho. Validado no EP1002 (`loop-gemini-4argon-v2.json`): reprova, com S01 corte+grotesco, S04 corte e S02/S05/S09 boca | Estado 26/10 · CHANGELOG 0.14.0 | agente | concluído |
| P8 | **Feito (t128u).** As 7 memórias `obsoleto_candidato` do roster antigo de `docs/AGENTES.md` foram apagadas em 27/10 ~08:57 (-03). Bank 884 → 877. Backup fora do git | `docs/operacao/hindsight-descarte-candidatos.md` | agente | concluído |
| P9 | **Feito (t112u–t116u).** Papel `mantenedor` (política 1.4.0) lê todas as tags e o repo todo; pqbr-mcp 0.4.0 exclusivo do mantenedor; onboarding em `docs/operacao/onboarding-agente-externo.md`. Falta só entregar token por cliente novo (`scripts/mcp/novo_cliente.py <nome> mantenedor`) | Fase Conhecimento | agente | concluído |
| P10 | Hindsight conferido 27/10 08:10 (São Paulo): API healthy, banco conectado. A reconsolidação segue automática | Fase Conhecimento | Hindsight (automático) | só conferir de novo se o bank acusar falha |
| P11 | Merge da branch `feat/f8-01-publicacao-automatica` (já no GitHub) na main | — | José | merge/PR exige OK |
| P12 | ERR-01: revisar os erros aceitáveis | ERR-01 | agente | depois dos primeiros dias de produção |

## Painel
Aba **Roadmap** no painel (:8088): Próximos passos, Falta e Feito gerados deste arquivo e do ROADMAP por `scripts/mapa/roadmap.py` (via `gerar_index.py`; o pre-commit regenera quando ROADMAP/ESTADO-ATUAL/mapa mudam). Itens com ☑ (feito) e ☐ (falta/próximos), só símbolo, nada clicável. Só leitura.

## Operacional e persistência (verificado 26/10/2026 18:21 -03)
pqbr-mcp 0.4.0 (user unit, enabled, Restart=on-failure, linger=yes), hindsight-api (enabled, Restart=always), Docker DB/Temporal (`unless-stopped`), worker enabled. Comando de checagem e detalhes: `docs/operacao/onboarding-agente-externo.md` § Operacional e persistência.

## Como atualizar
Resolveu ou corrigiu algo: tire a linha da tabela (ou mude o bloqueio), ajuste "Próximo passo" e a data acima, faça o commit junto com o DECISOES-LOG/CHANGELOG e chame `registrar_alteracao` com `tipo` igual a `pendencia_resolvida` ou `correcao`.


Fontes canônicas: docs/ESTADO-ATUAL.md (onde estamos), docs/REGRAS.md, docs/DECISOES-LOG.md, docs/ROADMAP.md, docs/LACUNAS-fluxo.md, docs/ARQUITETURA.md, docs/AGENTES.md, docs/mapa/. Em conflito, vale o doc canônico. O briefing do YT-LLM está em docs/_obsoleto/BRIEFING-novo-agente-pqbr.md e não é procedimento.

# Instruções para agentes que trabalham no repositório PQBR

Este arquivo é o ponto de entrada operacional para trabalho no checkout. Ele não cria uma nova fonte de decisão nem substitui as regras do projeto.

## Antes de trabalhar

1. Leia `docs/README.md` para localizar documentos e distinguir os roadmaps.
2. Para trabalho geral, siga a ordem autoritativa indicada em `docs/REGRAS.md` §0: REGRAS → SPEC → ARQUITETURA → TESTES → ROADMAP. Preserve decisões e gates; em conflito, vale o documento de maior autoridade.
3. Para uma tarefa de vídeo, leia `docs/blueprints/modulo-producao-video/README.md`, depois o blueprint e o roadmap do módulo. Esse roadmap é auxiliar: o estado global continua em `docs/ROADMAP.md`.
4. Canal do José: Telegram (bot próprio do PQBR, t538) + sinais do Temporal; painel: Temporal UI (t471/t474). Agentes: PydanticAI em activities do Temporal (ADR-011); o Paperclip está sendo retirado.
5. Trate relatórios em `docs/sdd/` como snapshots: confira data e status antes de usá-los como estado atual.

## Regras de segurança e escopo

- `docs/REGRAS.md` é a autoridade para decisões, permissões, fluxo e limites. Este arquivo não pode alterá-la.
- Não consulte `docs/arquivo/`, `docs/pesquisas/`, `docs/DECISOES-LOG.md`, `docs/_obsoleto/` ou outro material marcado como rascunho/legado sem a aprovação explícita exigida em `docs/REGRAS.md` §0. **Exceção (t530, José):** `docs/pesquisas/PESQUISA-extensoes-geracao-em-serie.md` pode ser lido por qualquer agente, **somente leitura** (referência da Fase 4V).
- Não altere, apague ou sobrescreva mudanças preexistentes; verifique `git status` antes de editar e use commits seletivos. Não faça push sem autorização.
- O Paperclip está em retirada (ADR-011): não crie organização, agente ou integração nova nele e não altere o código dele. `company/` continua como fonte das personas (`company/agents/<slug>/AGENTS.md`) e dos playbooks.
- Não marque um item como concluído sem evidência verificável. Um aceite de gate não fecha automaticamente checklists técnicos.
- Não publique vídeos, faça upload, use quota real ou acione efeitos externos sem cumprir os gates e autorizações previstos.
- NotebookLM continua sendo a fonte intelectual para pesquisa profunda, temas, ideias, roteiros e SEO; agentes (PydanticAI em activities do Temporal) orquestram e validam, sem duplicar esse trabalho, salvo complemento de relatório ou indisponibilidade documentada da ferramenta central.

## Identificação rápida dos documentos

- `docs/ROADMAP.md` — roadmap canônico geral, com estado oficial, dependências, tarefas e gates.
- `docs/blueprints/modulo-producao-video/ROADMAP.md` — plano auxiliar do módulo visual; não é o roadmap geral.
- `docs/AGENTES.md` — roster e desenho dos papéis; não é este arquivo de instruções.
- `company/agents/<slug>/AGENTS.md` — persona/instruções versionadas de cada papel (usadas pelos agentes PydanticAI).

## Mapa do sistema (t517)
- `docs/mapa/` (Mermaid + `index.html`) é gerado do código e serve de comunicação com o José e entre agentes.
- **Agentes nunca alteram o mapa sozinhos.** Mudança só por proposta aprovada pelo José. Divergência código × mapa: sinalizar (Observador/Dev) e propor o diff; `tests/unit/test_mapa.py` acusa.
- O registro de cliques (`config/mapa_cliques.json`, t126u) é outra coisa: elemento visto na tela, com data. Pop-up e botão fora do lugar atualizam esse registro e o processo segue.

## Honestidade (t126u)
- Dizer o que foi visto e o que não foi. Não inventar seletor, medida ou resultado.
- Se uma ideia do José não se sustenta, ou só aumenta o sistema, dizer isso antes de construir.
- Vale para todos os papéis e para quem entra pelo MCP.


## Conexão MCP

Servidor MCP da PQBR (só tailnet): porta HTTPS 8791 do host pc na tailnet (nome MagicDNS fora do repo), caminho /mcp, Streamable HTTP, Bearer token por cliente. Ferramentas conforme o papel: onboarding, buscar_memoria, codigo, estado (leitura) e registrar_memoria, registrar_alteracao (única escrita: Hindsight).

## Protocolo obrigatório do agente externo (t95u/t96u)

1. `onboarding` (este pacote).
2. `buscar_memoria` sobre o assunto antes de agir; em conflito, vale o doc canônico.
3. Implementar no checkout com commit local (sem push) e registrar a decisão em docs/DECISOES-LOG.md e a versão em CHANGELOG.md (SemVer).
4. Atualizar docs/ESTADO-ATUAL.md a cada correção ou pendência resolvida (o hook pre-commit exige quando ROADMAP/LACUNAS/DECISOES-LOG/CHANGELOG mudam).
5. Ao final, `registrar_alteracao` com o hash do commit e `tipo` (alteracao | correcao | pendencia_resolvida), citando arquivos; ele grava também o handoff. Sem commit, `registrar_memoria`. Sem esse registro a alteração não conta como entregue.

## BRIEFING

Histórico, fora do procedimento: docs/_obsoleto/BRIEFING-novo-agente-pqbr.md (herança do YT-LLM, 24/10/2026). O que vale está em REGRAS, CONTRATO-EDITORIAL e ESTADO-ATUAL.

## REGRAS (início)

# REGRAS da PQBR (Porquê BR)

## 0. Autoridade e uso deste arquivo

- **Este é o arquivo de autoridade.** As §0–§3 são a **constituição** do projeto (t328). Ordem: `docs/REGRAS.md` > `docs/SPEC.md` (requisitos) > `docs/ARQUITETURA.md` (desenho) > `docs/TESTES.md` (testes e validação) > `docs/ROADMAP.md` (tarefas, estado, fases e portões; o PLANO foi incorporado). `docs/AGENTES.md` é o roster vigente (8 papéis, ADR-011). O corpo antigo, com contratação e issues do Paperclip, está em `docs/_obsoleto/` e não é instrução (t129u). `docs/CONTRATO-EDITORIAL.md` é canônico para tom, categorias e gabarito (t394). `docs/RASTREABILIDADE.md` liga requisito → desenho → tarefa → teste. Agentes leem nessa ordem. As regras são o núcleo e não podem se perder; a arquitetura se adapta a elas (t285).
- **Leitura (t536, José, 25/10/2026, ajusta t287):** o **agente PQBR** (auxiliar do José, t533) pode ler **todos** os documentos do PQBR, inclusive `docs/DECISOES-LOG.md`, `docs/arquivo/`, `docs/pesquisas/` e `docs/_obsoleto/`. Ele usa o material legado como histórico e aplica sempre o que é vigente neste arquivo. A restrição abaixo vale para os **agentes especialistas** do sistema, que se limitam às suas áreas.
- ⛔ **Agentes especialistas — proibido consultar sem aprovação explícita do José (t287):** `docs/arquivo/`, `docs/pesquisas/`, `docs/DECISOES-LOG.md` (só para registrar decisão nova) e qualquer rascunho ou material legado. Eles podem ser mal interpretados e aplicados em produção. Tudo o que vale deles já está aqui. **Exceção (t530, José):** `docs/pesquisas/PESQUISA-extensoes-geracao-em-serie.md` pode ser lido por qualquer agente, **somente leitura** (referência da Fase 4V).
- **Dúvida ou conflito sem certeza** nas decisões aprovadas: não adivinhar. Marcar "EM CONSTRUÇÃO — aguardando José" e levar a ele (t323).
- **Lacuna (t129u):** só entra em `docs/LACUNAS-fluxo.md` o que foi conferido no código e ainda falta. Login, issue ou ponte do Paperclip não são lacuna. O Paperclip aparece como histórico e como infraestrutura em retirada (ADR-011, F05-09).
- **Honestidade (t126u, José):** o agente diz o que viu e o que não viu. Não inventa seletor, número ou resultado para a conta fechar. Se uma ideia do José não se sustenta, ou só aumenta o sistema, o agente diz isso antes de construir. Vale para todos os papéis e para o agente externo no MCP.
- **Decisão nova:** entra no `DECISOES-LOG.md` (tNNN) **e** aqui, no mesmo commit. Se este arquivo divergir do log, vale a entrada mais nova do log e este arquivo é corrigido.
- **Legenda:** [APROVADO] decisão do José · [VERIFICADO] testado/visto na fonte · [HIPÓTESE] a confirmar antes de construir o que depende dela · EM CONSTRUÇÃO — aguardando José.
- Origem: os códigos (tNNN, "item N", nomes de bloco) remetem ao `DECISOES-LOG.md`; "07/10" = registro de 07/10/2026.

- **Atualização 11/10 (t384–t394), prevalece sobre qualquer trecho abaixo que diga o contrário:**
  1. **Estratégia:** a entrega à core-eng foi abolida; o jr constrói a PQBR **no Paperclip** (t394). **[SUPERADO por ADR-011/t510 e t536:** agentes em PydanticAI nas activities do Temporal; o Paperclip fica **parado e desabilitado** até a nova arquitetura ser validada, e só depois é desinstalado.**]** A ENTREGA está em `arquivo/`. A equipe vigente e o mapa @prod-* → agentes estão em `AGENTES.md` (§3 e §11).
  2. **Autonomia/proatividade (t384, t390):** a empresa opera semanas ou meses sem o José. Agentes aplicam sozinhos dentro de faixas e playbooks; o José só vê no relatório. Ainda exigem o José: excluir/rejeitar/banir; voltar a público vídeo do item 5 ou recorrer ao YouTube; gastar dinheiro; login manual pelo noVNC ou 2FA (só depois de esgotada a reautenticação autônoma, item 11); mudar regra canônica; segredos e infraestrutura.
  3. **Equipe:** 14 agentes já contratados (AGENTES.md §2), incluindo Observador, Guardião de Segurança e Dev Revisor (t390, t392).
  4. **Contratação (t392):** sem teto de agentes; só com sugestão do Diretor, do dono da trilha ou do José; o Diretor executa, sem aprovação do board.
  5. **Runtime (t392):** os agentes usam modelos do **9router** pelos adapters `process` (texto) e `opencode_local` (ferramenta). Nenhum perfil Hermes além do `pqbr`, que é só o canal do José para o Diretor. Ferramentas = kit PQBR (Temporal, Camofox, NotebookLM py, Pydantic v2) + API Paperclip.
  6. **Rotinas** do Paperclip podem acordar agentes, inclusive para produção (t392). Efeito externo continua só pelo Temporal.
  7. **Orçamento:** warn-only, sem pausa por custo; limite de segurança revisto após os primeiros relatórios (t392).
  8. **Falhas:** na 2ª falha da mesma ação entra o playbook (até 3 tentativas). No Camofox, intervalo sorteado de 5–15 min entre intervenções sucessivas na mesma sessão, não duração da intervenção nem retry automático (t357; precisão aprovada em 17/10/2026, §3.1). Só depois Diretor → canal de controle ativo (Telegram/Hermes `pqbr`; t474).
  9. **Tickets:** abertura automática; merge automático com CI e testes verdes + aprovação do Dev Revisor, se a mudança não tocar regra canônica, segredos nem infra (t390).
  10. **Fonte de verdade:** Postgres local (t343). O Supabase não é usado.

  11. **Camofox PQBR 24/7 (t395):** a instância `pqbr-camofox` fica sempre ligada, com a sessão permanente aberta na mesma tela. Só reinicia se cair (watchdog/`Restart=always`). Se a sessão cair, a reautenticação é **autônoma e por qualquer meio**: renovar no Camofox, depois **sincronizar cookies do Chrome**, depois outro caminho previsto. Cada passo vai para o log + aviso pelo canal privado ativo (Telegram/Hermes `pqbr`; t474). O José só é chamado depois disso (noVNC/2FA). Isso supera a §3.1 (trava "cópia de cookies") e a §11 ("só com OK do José").

---

- **Atualização 23/10 (t474, aprovada por José), revoga a t464 (Discord) e prevalece:** (1) o canal do José é o **Telegram (Hermes `pqbr`)**; pedidos, avisos e aprovações saem por lá. (2) Aprovações são **sinais do Temporal** (sim/não), com principa

## Decisões recentes

## t125u (26/10/2026) — Ensaio de cliques em memória, com a API como base
- José: simular e testar a clicagem das funções que a API faria se ela faltar. Essa informação fica como resíduo e pode estar desatualizada. Quando uma atualização for conhecida, os agentes atualizam contratos, scripts e processos.
- Até aqui os scripts só gravavam o payload da API (`enviar_privado` em simulação e o plano `*-camofox.json`). Não havia ensaio de clique nem de agendamento na tela do Studio.
- O ensaio (contrato `studio_fallback` 0.1.0) percorre em memória subida privada, agenda (`publishAt`) e privacidade, lendo os campos do corpo da API. Campo ausente ou fora da regra reprova o ensaio. Seletor de tela só entra junto com a data em que a tela foi vista. Clique ao vivo permanece desligado: o canal é o de produção e um clique no envio criaria vídeo de verdade.
- Nada enviado. `YOUTUBE_DRY_RUN` segue `true`. O worker em execução continua o das 22:06.


## t126u (26/10/2026) — Honestidade comum; mapa de cliques a partir do que for visto
- José: mapear elementos, componentes e locais de clique, como no Flow e nos outros sites do fluxo. O agente identifica a alteração, corrige, atualiza e segue. Pop-up e botão que mudou de lugar não são risco e não param a publicação. Documentar e registrar no mapa de visualização. Antes de prosseguir: honestidade obrigatória, também no MCP; questionar ideia dele quando não for válida ou quando for excesso de aperfeiçoamento.
- O que existe até t125u não é esse mapa. É um ensaio em memória das funções da API. Nenhum botão de Flow, Vids, Vibes ou Studio foi visto para este registro. Inventar seletor agora seria o excesso que a própria regra nova barra. `config/mapa_cliques.json` fica com a lista vazia.
- O que fica valendo: obstáculo de tela (pop-up, botão fora do lugar) atualiza o registro, com data, e o processo segue. O diagrama em `docs/mapa/` (11 e 07) mostra isso. A trava dura continua: apagar, tornar público fora da regra, gastar, login/2FA, aceitar consentimento OAuth, mexer em segredo. "Não parar" não cobre essas ações. O clique que cria vídeo continua sob simulação por padrão e sob privado até a produção ativa.
- Honestidade: REGRAS §0, onboarding (`AGENTS-base`) e a frase do `initialize` do MCP. O processo do `pqbr-mcp` ainda não foi reiniciado; a frase do handshake entra no próximo reinício, que exige OK. O onboarding já lê a regra no disco. Nada enviado.


## t127u (27/10/2026) — Diagrama 11 alinhado; o que não foi feito nas pendências
- José pediu para prosseguir com os ajustes das pendências. Conferido às 08:10 (São Paulo): `pqbr-episodio-worker` ativo desde 26/10 22:06 (Fortaleza), `NRestarts=0`; `pqbr-mcp` 0.4.0 no ar; Hindsight `healthy` com banco conectado.
- O diagrama 11 ainda dizia que o worker não tinha sido reiniciado, que a migração 0020 faltava e que as chaves do YouTube não estavam no processo. Isso já era falso desde t109u e t123u. Corrigido. O código de t124u–t126u continua fora desse processo até o próximo reinício.
- Não feito, de propósito: reiniciar worker ou `pqbr-mcp`; envio ao YouTube; apagar as 7 memórias (a revisão recomenda apagar: são o roster antigo do AGENTES.md; o OK continua necessário); merge na main; LOOP por cena (a lacuna manda não executar agora); imagens pagas do elenco; activity do Storyboard. Nada enviado.


## t128u (27/10/2026) — Worker e MCP reiniciados; 7 memórias apagadas
- José: "Tem meu ok. Só não vou poder ver os vídeos agora. Continue para progredir." Esse OK cobre o reinício dos serviços e o apagamento das 7 memórias que estavam parados à espera dele. Não cobre envio ao YouTube, gasto com imagens, o teste de LOOP por cena, o merge na main, nem ver os vídeos no lugar dele.
- Às 08:56 (-03, São Paulo): 0 workflows `Running` no ns `pqbr`. Reinício do `pqbr-episodio-worker`. Log: `worker episodio em 127.0.0.1:7233 ns=pqbr fila=episodio-pqbr`. O processo lê o checkout desta branch, onde estão t124u–t126u. `YOUTUBE_DRY_RUN=true`. `PQBR_PUBLICACAO_REAL` não está no ambiente. Nada enviado. Depois do reinício, de novo 0 `Running`.
- No mesmo horário, reinício só do `pqbr-mcp`. `GET /saude` devolve 0.4.0. Um `initialize` ao vivo devolve a frase de honestidade (t126u).
- P8: cada uma das 7 memórias foi lida antes de apagar. Todas tinham a tag `obsoleto_candidato` e o contexto em `docs/AGENTES.md` (equipe de 14 ou mapa `@prod-*`). Backup: `~/.pqbr/hindsight/backup/pqbr-7-obsoletos-20261027.json` (600) e o export do bank `pqbr-bank-pre-delete-20261027.zip` (1.602.712 bytes). DELETE 200 nas sete. Conferência: as sete respondem 404; o bank foi de 884 para 877 documentos. Nenhuma outra foi apagada.
- Não feito: ver os vídeos (P1); envio real; imagens pagas do elenco; LOOP por cena; activity do Storyboard; merge na main; preencher `config/mapa_cliques.json` (nenhuma tela de Flow, Vids, 

## t129u (27/10/2026) — Documentos ativos conferidos; o que não é lacuna saiu
- José pediu uma verificação dos documentos ativos: caminho citado tem de existir; documento obsoleto vai para `docs/_obsoleto/` para ele descartar depois; lacuna que o código já não tem sai da lista; Paperclip fica só como histórico e como infraestrutura em retirada.
- Conferido no código, e por isso deixou de ser lacuna: `ReposicaoTemasWorkflow` não usa Paperclip; login da CLI do Paperclip não é passo; `DescartarCadernoTesteWorkflow` e `EpisodioWorkflow` estão no worker do episódio; os três critérios visuais do juiz já reprovam sozinhos (t108u); a legenda extra no pós foi recusada em t435; F4C-04 (login do Camofox) está feito desde t405. As pastas `tests/contratos/`, `tests/replay/`, `tests/integracao/`, `tests/falhas/` e `tests/auditor/` não existem; os testes estão em `tests/unit/`, `tests/workflows/` e `tests/seguranca/`.
- Continua lacuna, porque o código confirma: o episódio espera sinal de auditor e não chama `auditor_gemini`; `tipo=short` com roteiro segue para gerar o vídeo no NotebookLM; o lote 2510 não tem código `PQBR-EP`; Flow/Vids/Vibes não estão no episódio; falta a activity do storyboard; `NavegadorIdentidade` não é importada por workflow; o mapa de cliques segue vazio. O backup e o canário do ADR-012 não foram conferidos: não entram como feitos.
- Movidos com `git mv`, sem apagar: roster operacional antigo, briefing do YT-LLM, resumo de stack de 17/10, lições pré-E2E, rascunho de S

## Fase atual do ROADMAP

## Fase: Conhecimento e agente externo agnóstico (t84u–t86u, 26/10/2026)
- [x] **GitNexus [agora]:** global no servidor (1.6.12, fora do repo), índice da PQBR registrado, reindex no post-commit, pré-requisito fail-closed. ARQUITETURA §12.
- [x] **Política por papel [agora]:** `config/politica_papeis.json` + filtro no Hindsight e no adaptador GitNexus.
- [x] **Servidor MCP da PQBR só na tailnet (t89u, OK do José):** `pqbr-mcp`, 127.0.0.1:8791 + tailscale serve, só leitura, token por cliente.
- [x] **AGENTS.md gerado (t89u)** do onboarding do MCP.
- [x] Reclassificar com tags as memórias legadas sem tag (feito em t90u).
- [x] **Escrita de memória pelo MCP (t95u/t96u):** `registrar_memoria`/`registrar_alteracao` (contrato 1.0.0), só papel com escrita na política, autor = cliente do token, referência a commit verificado e arquivos.
- [x] **ESTADO-ATUAL (t98u/t99u):** `docs/ESTADO-ATUAL.md` é a fonte única do handoff, a 1ª seção do onboarding/AGENTS.md; hook pre-commit e `registrar_alteracao` (tipo correcao/pendencia_resolvida) exigem a atualização; handoff no Hindsight (tag `estado`, todos os papéis).
- [x] **Papel `mantenedor` externo (t112u–t117u):** política 1.4.0 (lê todas as tags, repo todo, constrói/liga módulos; reinício/migração com OK); pqbr-mcp 0.4.0 exclusivo do mantenedor (outro papel 401/403); reiniciado e validado ao vivo; persistência verificada. Doc: `docs/operacao/onboarding-agente-externo.md`.
- [x] **Teste de agente do zero (t96u):** URL tailnet + token `mantenedor-externo` → onboarding → buscar_memoria → commit local `b63fa56` → registrar_alteracao → buscar_memoria retornou em ~10 s; indexador negado; sem token 401.
- [x] Licença do GitNexus aceita (uso pessoal, sem revenda; t90u).
- [x] **Reclassificação do Hindsight por papel (t90u):** `scripts/hindsight/reclassificar.py`; 220 candidatas a descarte em `docs/operacao/hindsight-descarte-candidatos.md`.
- [x] Descarte das candidatas (t90s398): 231 apagadas após a indexação; docs vigentes corrigidos; indexador com a regra única de tags.
- [x] Revisar as 7 candidatas mantidas (sem substituta direta). Feito em t128u (27/10): as sete apagadas com OK do José; backup fora do git; bank 884 → 877.


## LACUNAS (início)

# Lacunas que ainda existem (conferidas no código em 27/10/2026, t129u)

A tabela de 12/10 que bloqueava o fluxo no login da CLI do Paperclip foi para `docs/_obsoleto/lacunas-fluxo-ate-20261027.md`. Não é lacuna. A reposição de temas (`ReposicaoTemasWorkflow`) consulta o NotebookLM e grava no Postgres, sem Paperclip. O descarte de caderno de teste e o episódio estão registrados no `pqbr-episodio-worker`. Itens já feitos (descarte do EP1001, estilo via config, pedido de acesso que se fechou, restauração de sessão) não se repetem aqui.

## Abertas

1. **Auditor no episódio.** `EpisodioWorkflow` (`src/pqbr/workflows/episodio.py`) espera o sinal `veredito_auditor`. Não chama `auditor_gemini` nem `auditor_loop_gemini`. A activity `auditor_gemini` está no worker da fila `camofox-pqbr`. O script `scripts/e2e/auditor_gemini_ep.py` ainda existe. Os critérios `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco` já reprovam sozinhos (t108u); isso não falta.
2. **Pacote só de roteiro.** Com `tipo=short` e `roteirizar`, `NotebookLMWorkflow` segue para `nlm_gerar_short`. Não há um tipo que pare depois do roteiro. Visto em `src/pqbr/workflows/notebooklm.py`.
3. **Códigos do lote 2510.** Os prontos em `docs/pesquisas/lote-2510/` não têm `PQBR-EP`. Sem código não há `drive_enviar` nem episódio no Postgres. Quem define os códigos é o José.
4. **Vídeo em série (Fase 4V).** O episódio ainda baixa o vídeo do NotebookLM. Flow, Vids e Vibes não estão no código. HOLD das três rotas está decidido (t529) e não implementado.
5. **Storyboard.** O contrato `FichaCena`/`Storyboard` existe. Falta a activity que gera o storyboard e impede a geração sem ele. As imagens de referência do elenco são pagas e seguem postergadas.
6. **Navegador.** `NavegadorIdentidade` está em `src/pqbr/motores/navegador.py`. Nenhum workflow importa essa porta. O backup diário e o canário do ADR-012 não foram conferidos nesta passagem: não entram como feitos nem como lacuna confirmada.
7. **Publicação, o que ainda falta.** O envio real está desligado de propósito (`YOUTUBE_DRY_RUN=true`) até a produção ativa. O roteiro de cliques do Studio não foi visto. `config/mapa_cliques.json` está vazio. O worker do episódio não tem o drop-in `telegram.conf`. O resto dessa etapa (chaves, agenda, registro no worker, fallback do refresh) está no ar desde 27/10 08:56 (-03).
8. **Teste adiado, não executar agora.** LOOP do Gemini por cena, e 4 Argon baixo contra 3.8 Flash no mesmo lote.

## Não são lacunas

- Login da CLI do Paperclip, issue no Paperclip para começar episódio ou descarte, e o token do bot Hermes citado em 15/10. O canal vigente é o bot próprio (t538). O corte do serviço Paperclip é o item F05-09 do ROADMAP, não um login pendente.
- Legenda extra no pós. José decidiu em t435 que a legenda do NotebookLM fica e o pós não grava outra. `scripts/legendar_short.py` é sobra, não um passo do fluxo.
- Critérios visuais `personagem_mexe_labios` / corte / grotesco como "próxima versão do auditor". Já estão n

## Mapa visual

docs/mapa/index.html (servido em :8088) — diagramas: 00-visao-geral.mmd, 01-episodio.mmd, 02-reposicao-temas.mmd, 03-acessos.mmd, 04-descarte.mmd, 05-vigia-atualizacoes.mmd, 06-runs-presos.mmd, 07-cadeia-video.mmd, 08-identidade-camofox.mmd, 09-agentes-responsabilidades.mmd, 10-catalogo-erros.mmd, 11-publicacao.mmd, 12-storyboard-elenco.mmd, 13-memoria-mcp-handoff.mmd · aba Roadmap gerada de ROADMAP + ESTADO-ATUAL (scripts/mapa/roadmap.py; edite as fontes, nunca o HTML)
