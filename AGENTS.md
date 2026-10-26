# PQBR — onboarding do agente (gerado; não editar à mão)

## ESTADO ATUAL da PQBR — continue daqui

Fonte única de "onde estamos". Não repete o ROADMAP: aponta os itens por id. **Atualize este arquivo a cada correção ou pendência resolvida.** O hook pre-commit exige isso quando o commit toca ROADMAP, LACUNAS, DECISOES-LOG ou CHANGELOG, e o `registrar_alteracao` exige isso para `tipo` correcao ou pendencia_resolvida.

Atualizado: 26/10/2026 (t112u–t116u: papel mantenedor externo, MCP exclusivo do mantenedor, pqbr-mcp reiniciado) · versão 0.15.0

## Onde estamos
- **Produção:** o lote do saldo está em `runtime/lote-saldo/` (um diretório por tema). O EP1002 olhos-da-cara foi reprovado e descartado (`runtime/lote-saldo/_descartado/`), e o tema voltou a `proposto`.
- **Publicação (ROADMAP F8-01):** o fluxo pelo Temporal está pronto (`PublicacaoAgendadaWorkflow` no `worker_episodio`). O upload real está bloqueado por falta das credenciais OAuth do YouTube.
- **Agente externo:** o servidor MCP 0.2+ só funciona pela tailnet. A memória escrita leva o autor (o cliente) e o commit. O protocolo obrigatório está no AGENTS.md. Hindsight: bank `pqbr` reclassificado, com as obsoletas apagadas.

## Próximo passo
José assiste o EP1003 cafe-fraco (`runtime/lote-saldo/cafe-fraco/cafe-fraco-final.mp4`). Só depois disso roda o LOOP do Gemini nesse episódio.

## Pendências abertas
| # | Pendência | Ref. ROADMAP | Dono | Bloqueio |
|---|---|---|---|---|
| P1 | EP1003 cafe-fraco: José assiste antes do LOOP do Gemini | Estado 26/10 · Próximo 5 | José | aguardando José |
| P2 | Publicação: (a) José ativa a verificação em 2 etapas na conta juniormoedavirtual → (b) criar o OAuth do YouTube via Camofox (projeto `pqbr-publicacao`, chaves em `episodio.env`) → (c) aplicar a migração 0020 e reiniciar o worker → (d) upload pelo `PublicacaoAgendadaWorkflow` | F8-01 · Estado 26/10 · Próximo 1 | José (a); agente (b–d) | (a) José; (c) exige OK do José |
| P3 | Teste: LOOP por cena vs o atual | Estado 26/10 · Testes pendentes | agente | depois do fluxo de publicação |
| P4 | **Feito (t108u/t109u).** Juiz por etapa (`gemini_juiz` v1.0.0): pré-produção usa 3.8 Flash; produção (VISUAL e LOOP) usa 4 Argon Baixo. O worker `pqbr-episodio-worker` foi reiniciado com OK do José às 16:57 (-03), e o poller está ativo na fila `episodio-pqbr`, ns `pqbr` | Estado 26/10 · DECISOES-LOG t109u | agente | concluído |
| P5 | Imagens de referência do elenco (`ASSET_personagem_{masculino,feminino}-v1`) | Estado 26/10 · Próximo 4 | agente | geração paga: OK do José (postergado) |
| P6 | Activity do Storyboard no Temporal (bloqueia a geração sem ele) | Estado 26/10 · Próximo 2; R2 | agente | postergado |
| P7 | **Feito (t108u).** O gate VISUAL agora tem `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco` (FichaCena/REGRAS §25), e cada um reprova sozinho. Validado no EP1002 (`loop-gemini-4argon-v2.json`): reprova, com S01 corte+grotesco, S04 corte e S02/S05/S09 boca | Estado 26/10 · CHANGELOG 0.14.0 | agente | concluído |
| P8 | 7 memórias `obsoleto_candidato` para revisão | `docs/operacao/hindsight-descarte-candidatos.md` | José | apagar exige OK |
| P9 | **Feito (t112u–t116u).** Papel `mantenedor` (política 1.4.0) lê todas as tags e o repo todo; pqbr-mcp 0.4.0 exclusivo do mantenedor; onboarding em `docs/operacao/onboarding-agente-externo.md`. Falta só entregar token por cliente novo (`scripts/mcp/novo_cliente.py <nome> mantenedor`) | Fase Conhecimento | agente | concluído |
| P10 | Reconsolidação do Hindsight em andamento (observações sendo refeitas) | Fase Conhecimento | Hindsight (automático) | só conferir |
| P11 | Merge da branch `feat/f8-01-publicacao-automatica` (já no GitHub) na main | — | José | merge/PR exige OK |
| P12 | ERR-01: revisar os erros aceitáveis | ERR-01 | agente | depois dos primeiros dias de produção |

## Como atualizar
Resolveu ou corrigiu algo: tire a linha da tabela (ou mude o bloqueio), ajuste "Próximo passo" e a data acima, faça o commit junto com o DECISOES-LOG/CHANGELOG e chame `registrar_alteracao` com `tipo` igual a `pendencia_resolvida` ou `correcao`.


Fontes canônicas: docs/ESTADO-ATUAL.md (onde estamos), docs/BRIEFING-novo-agente-pqbr.md, docs/REGRAS.md, docs/DECISOES-LOG.md, docs/ROADMAP.md, docs/LACUNAS-fluxo.md, docs/ARQUITETURA.md, docs/mapa/. Em conflito, vale o doc canônico.

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


## Conexão MCP

Servidor MCP da PQBR (só tailnet): porta HTTPS 8791 do host pc na tailnet (nome MagicDNS fora do repo), caminho /mcp, Streamable HTTP, Bearer token por cliente. Ferramentas conforme o papel: onboarding, buscar_memoria, codigo, estado (leitura) e registrar_memoria, registrar_alteracao (única escrita: Hindsight).

## Protocolo obrigatório do agente externo (t95u/t96u)

1. `onboarding` (este pacote).
2. `buscar_memoria` sobre o assunto antes de agir; em conflito, vale o doc canônico.
3. Implementar no checkout com commit local (sem push) e registrar a decisão em docs/DECISOES-LOG.md e a versão em CHANGELOG.md (SemVer).
4. Atualizar docs/ESTADO-ATUAL.md a cada correção ou pendência resolvida (o hook pre-commit exige quando ROADMAP/LACUNAS/DECISOES-LOG/CHANGELOG mudam).
5. Ao final, `registrar_alteracao` com o hash do commit e `tipo` (alteracao | correcao | pendencia_resolvida), citando arquivos; ele grava também o handoff. Sem commit, `registrar_memoria`. Sem esse registro a alteração não conta como entregue.

## BRIEFING

# BRIEFING — novo agente específico PQBR / Porquê BR (substitui o YT-LLM)

t531 · 24/10/2026 · pedido do José. **Só leitura e proposta.** **Atualização t533–t535:** o novo agente PQBR **foi criado** (id `0ade9874-b724-4055-9000-d61825244b12`); o keepalive do YT-LLM está **pausado (confirmado)**. Originalmente: o novo agente ainda não tinha sido criado, nenhuma mensagem foi mandada ao YT-LLM e os arquivos dele não foram alterados. O **jr** continua como agente generalista do José.

**Fontes**
- Conversa YT-LLM (agente `018f2ef8-…`): 3100 posições, de 16/09 a 28/09/2026. Lidas quase todas; ficaram de fora só lacunas de 1 a 4 mensagens.
- Arquivos do YT-LLM em `/workspace/yt-llm-bot/` no box: `playbook-decisoes.md`, `roadmap-b1.md`, `ops/`, `branding/`, `notebooks/`, `sources/`, `scripts/`, `temas/`.
- No repo PQBR: `docs/REGRAS.md`, `docs/ARQUITETURA.md` (ADR-011 e ADR-012), `docs/CONTRATO-EDITORIAL.md`, `docs/ROADMAP.md`, `docs/AGENTES.md` e as entradas de 23 e 24/10 do `docs/DECISOES-LOG.md` (t474, t476/t512–t517, t525–t530).

## Linha do tempo do YT-LLM (resumo)
- **16/09:**
  - instalou o notebooklm-py e a rotina de keepalive de 20 min no box;
  - analisou o caderno da "Fábrica de Shorts" e montou os cadernos B1;
  - escolheu o nicho B1, "Por que o Brasil funciona assim?";
  - criou o canal **Porquê BR** (`@porquebr-t4c`) e fez o OAuth da YouTube Data API (projeto `yt-llm-b1`) com o MCP `youtube-shorts`;
  - definiu o estilo **Stickman**, no lugar do VOX/papercut.
- **17/09:**
  - fez os Shorts v1 a v7 da tomada de 3 pinos (o v7 foi "quase lá"), o 127V/220V (FAIL) e o terremoto (PASS);
  - travou o overlay v8 e o logo v4;
  - publicou o 1º Short (privado e depois público): https://www.youtube.com/watch?v=-Af4vua4v9c;
  - criou o repo `jvmendesjr/porque-br` e o `BOOTSTRAP-AGENTE.md`.
- **20/09 a 28/09:** só rodou o keepalive, que falhou repetidamente. A última mensagem pede um novo login da conta e diz que a rotina fica parada até lá.
- **Depois disso:** o projeto foi refeito como **PQBR** no servidor `pc` (repo `jvmendesjr/PQBR`). O YT-LLM não acompanhou essa mudança.

## (a) O que continua válido e deve ser herdado
| Item | Onde está | Observação |
|---|---|---|
| Nicho B1 e o nome **Porquê BR** | `playbook-decisoes.md` §3; REGRAS §1 | Igual na PQBR. |
| Identidade **Stickman**: personagem expressivo e humanizado ("caras e bocas"), logo v4 com mapa e "?" teal, kraft + `#0D9488` | `branding/stickman-character-bible.md`, `identidade-stickman-brief.md`, `paleta-stickman-v1.md` | Aprovada na PQBR para o módulo Flow (REGRAS §6, t465). |
| **Overlay v8**: bug no topo direito com −50 % de tamanho e 50 % de alpha; lockup no canto inferior direito; logo final que cresce opaco por ~2,2 s | `ops/overlay-padrao-shorts-v1.md`, `branding/overlay/` | Vale para o pós. |
| Público, voz e postura: irreverente sem ser brega; curiosidades do **Brasil**, não genéricas | `branding/publico-voz-postura.md` | Vale como regra editorial; conferir com o CONTRATO-EDITORIAL. |
| **Um vídeo, avaliar e só então refazer** (substitui "2 por tema"; José, 17/09) | conversa YT-LLM, 17/09 | Bate com a economia de cota da PQBR. |
| **Séries e blocos** em vez de vídeos aleatórios; série 0 de mitos e cultura popular (só ideação) | `ops/ideacao-serie-mitos-cultura-popular.md`, `ops/ideacao-series-pilares-adiada.md` | Pendente; ver (c). |
| Descrever **2 a 4 movimentos críticos** (origem → destino, props nomeados); compor sem espremer os objetos | `ops/nlm-motion-e-composicao.md` | Passa a valer para os prompts de Flow e Vids. |
| Método **VOX / GUÍA VOX**: beats de 2,5 a 3 s, `.txt` com um prompt por bloco sem números, bloco de estilo repetido, prompt de animação universal | `sources/guia-vox.md`; PESQUISA-extensoes §1.1 | Base do storyboard em série (Fase 4V). |
| **Fábrica de Shorts**: prompts 1.1 a 4.3, persona, prévia de 6 vinhetas | `sources/fabrica-shorts.md`, `notebooks/` | O motor de temas e roteiros reaproveita; a geração de vídeo não. |
| **Gate pré-publicação fail-closed** com dry-run por padrão e live só com ordem explícita | `scripts/prepublish-gate.sh`, skill `gate-pr-publish-porqu-br` | Coerente com a Fase 8 da PQBR (só dry-run). |
| Duração 40 a 55 s; CTA de inscrição e like | `ops/duracao-shorts-porque-br.md`, `ops/cta-shorts-inscreva-like.md` | Conferir com o CONTRATO v2. |
| Hooks de documentação (`on_decision_lock`…) | `playbook-decisoes.md` §14, skill `documentar-decis-es-de-projeto` | Na PQBR viram o DECISOES-LOG e o CHANGELOG. |
| Lições de falha: o papercut sem movimento foi abortado, o stickman sumia, as refs de imagem eram ignoradas pelo Video Overview, as legendas pulavam palavras | `ops/log-falhas-stickman-nlm.md`, `ops/aprendizados-stickman-fluxo-v1.md` | Explicam por que o vídeo saiu do NotebookLM (t512). |

**Skills do usuário que vieram do YT-LLM**: `produ-o-short-b1-notebooklm`, `gate-pr-publish-porqu-br`, `p-s-short-porqu-br`, `capa-canal-porqu-br` e `documentar-decis-es-de-projeto`.
- Herdar: o gate, o pós (trim e logo) e a capa.
- **Revisar antes de usar**: a `produ-o-short-b1-notebooklm`, porque ela gera o vídeo no NotebookLM (ver b).

## (b) O que ficou desatualizado ou mudou
| Antes no YT-LLM | Agora na PQBR | Fonte |
|---|---|---|
| O NotebookLM gera o vídeo (Video Overview Short 9:16 "em volume") | O NotebookLM é o **motor intelectual** (temas, roteiros, direção, SEO). Vídeo pela cadeia **Flow → Google Vids → Meta Vibes → HOLD**, pelo navegador | DECISOES t512, t517, t529; ROADMAP 4V |
| Higgsfield/VOX como camada premium paga | **Sem APIs de geração** (Gemini/Veo/Omni, inclusive free tier); só as cotas já pagas, pelo navegador | DECISOES t516/t517 |
| Agente único que faz tudo pelo chat | **Temporal** como sistema nervoso + **PydanticAI** nas activities + **8 papéis** (Diretor, Líder Editorial, Pesquisador de Origem, Auditor, Compliance, Guardião, Observador, Dev) | ADR-011 (t510), DECISOES t512–t515, AGENTES §2 |
| Sem contratos | Contratos **Pydantic v2** versionados (SemVer em `VER

## REGRAS (início)

# REGRAS da PQBR (Porquê BR)

## 0. Autoridade e uso deste arquivo

- **Este é o arquivo de autoridade.** As §0–§3 são a **constituição** do projeto (t328). Ordem: `docs/REGRAS.md` > `docs/SPEC.md` (requisitos) > `docs/ARQUITETURA.md` (desenho) > `docs/TESTES.md` (testes e validação) > `docs/ROADMAP.md` (tarefas, estado, fases e portões; o PLANO foi incorporado). `docs/AGENTES.md` detalha a equipe do Paperclip (abaixo da ARQUITETURA). `docs/CONTRATO-EDITORIAL.md` é canônico para tom, categorias e gabarito (t394). `docs/RASTREABILIDADE.md` liga requisito → desenho → tarefa → teste. Agentes leem nessa ordem. As regras são o núcleo e não podem se perder; a arquitetura se adapta a elas (t285).
- **Leitura (t536, José, 25/10/2026, ajusta t287):** o **agente PQBR** (auxiliar do José, t533) pode ler **todos** os documentos do PQBR, inclusive `docs/DECISOES-LOG.md`, `docs/arquivo/`, `docs/pesquisas/` e `docs/_obsoleto/`. Ele usa o material legado como histórico e aplica sempre o que é vigente neste arquivo. A restrição abaixo vale para os **agentes especialistas** do sistema, que se limitam às suas áreas.
- ⛔ **Agentes especialistas — proibido consultar sem aprovação explícita do José (t287):** `docs/arquivo/`, `docs/pesquisas/`, `docs/DECISOES-LOG.md` (só para registrar decisão nova) e qualquer rascunho ou material legado. Eles podem ser mal interpretados e aplicados em produção. Tudo o que vale deles já está aqui. **Exceção (t530, José):** `docs/pesquisas/PESQUISA-extensoes-geracao-em-serie.md` pode ser lido por qualquer agente, **somente leitura** (referência da Fase 4V).
- **Dúvida ou conflito sem certeza** nas decisões aprovadas: não adivinhar. Marcar "EM CONSTRUÇÃO — aguardando José" e levar a ele (t323).
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

- **Atualização 23/10 (t474, aprovada por José), revoga a t464 (Discord) e prevalece:** (1) o canal do José é o **Telegram (Hermes `pqbr`)**; pedidos, avisos e aprovações saem por lá. (2) Aprovações são **sinais do Temporal** (sim/não), com principal autenticado (ID autorizado do José), validação de tarefa e estado, fail-closed, idempotência após reinício e ticket de manutenção após três tentativas. (3) O painel é a **Temporal UI** (estado, histórico, erros, runs travados); painel próprio fica para depois (t471). (4) O **Paperclip está sendo retirado** da arquitetura (ADR-011): referências a Paperclip abaixo valem só até o corte. Não desligar o gateway Hermes compartilhado nem afetar outros perfis; nenhuma exposição pública.
## 1. Nome e identidade
- A organização se chama **PQBR**; os documentos explicam a sigla (Porquê BR); o canal usa o "porquê" por extenso. [08/

## Decisões recentes

## t101u (26/10/2026) — Inovações do dia no mapa; publicação depois
- Novo diagrama `docs/mapa/13-memoria-mcp-handoff.mmd` (Hindsight por papel, hindsight_tags e descarte, GitNexus global + instância PQBR, pqbr-mcp, ESTADO-ATUAL + hook + handoff, branch no GitHub). O 09 só aponta para o 13; a visão geral 00 ganhou o nó. ARQUITETURA §12 completada (tags, escrita MCP, handoff).
- José: seguir a ordem do ESTADO-ATUAL e publicar os vídeos prontos só depois de analisá-los pessoalmente.


## t105u (26/10/2026) — LOOP do juiz Gemini com 4 Argon (raciocínio Baixo) no EP1002 descartado
- José pediu o 4 Argon, no nível de raciocínio mais baixo, no mesmo vídeo cheio de problemas. Override só por execução: `PQBR_GEMINI_MODELO` / `PQBR_GEMINI_RACIOCINIO` (Baixo|Médio|Alto). O padrão continua `gemini_modelo: 3.8 Flash` em `config/motores.json`. O nível é confirmado no menu antes de cada envio (evidência do seletor gravada no resultado). Script `scripts/lote/loop_comparar_modelo.py`: mesmos quadros e mesma rubrica; não sobrescreve o resultado oficial.
- Resultado (`loop-gemini-4argon.json`): **reprova** (imagem×fala aprova_com_ressalva, capa aprova, loop reprova). O 3.8 deu terceira_rodada, com todas as métricas visuais em 1.0. O Argon pegou o desvio de estilo (0.1), a legenda sobre o foco na capa e a legenda com erro em S04–S06. Óculos cortados, olho grotesco e lábios mexendo não estão na rubrica, e nenhum dos dois apontou (critérios novos = P7). Tempo: 4 Argon 614 s no total (respostas visuais de 37 s, loop de 9–18 s); o tempo do 3.8 nesse vídeo não foi registrado.


## t108u (26/10/2026) — 3.8 antes da produção, 4 Argon na produção; P7 implementado
- José: "Vamos deixa o 3.8 antes da produção, na produção adicionamos o Argo".
- A config por etapa (`gemini_juiz`) tem a seguinte precedência: env da execução > etapa > `gemini_modelo` legado. A verificação do seletor (modelo e raciocínio) continua sendo feita a cada envio.
- 3 critérios novos que reprovam sozinhos, sempre exigindo as 2 rodadas em acordo (se divergirem, vai para a terceira rodada).
- Validação no EP1002 com 4 Argon Baixo (595 s): reprova. Detectou os 3 problemas apontados pelo José: corte em S01/S04, grotesco em S01, boca em S02/S05/S09.
- O worker Temporal não foi reiniciado. Isso fica pendente de OK do José.


## t109u (26/10/2026) — Migração 0020 e reinício do worker (OK do José, card t109s462)
- Backup antes da migração; `public.pqbr_migracoes` registra a 0020.
- Antes do reinício não havia nenhum workflow em execução no ns `pqbr`. Depois do reinício: unit ativa, poller registrado (workflow e activity), pré = 3.8 Flash / produção = 4 Argon Baixo, `PublicacaoAgendadaWorkflow` registrado. Nada foi publicado e nenhum upload foi disparado.
- Mapa 12 atualizado e com render validado.


## t112u–t116u (26/10/2026) — Papel `mantenedor` para agentes externos
- t112u: agentes externos de manutenção (qualquer cliente MCP) leem TODAS as memórias do Hindsight e todo o código para debug e correção. Política 1.4.0: mantenedor lê as 14 tags de conteúdo (menos `obsoleto_candidato`), vê o repo todo, grava decisao/incidente/licao/playbook/doc/estado. Papéis internos inalterados.
- t113u: o mantenedor também constrói e liga módulos novos (contrato, porta/adaptador, Temporal, agentes, testes, docs, mapa). Ligar algo que peça reinício de serviço ou migração continua exigindo OK do José.
- t114u: o pqbr-mcp externo é exclusivo do `mantenedor` (0.4.0): token de outro papel ⇒ 401; papel declarado (`X-PQBR-Papel`) diferente ⇒ 403; `novo_cliente.py` só cria mantenedor.
- t116u: OK do José para reiniciar SOMENTE o `pqbr-mcp` após a suíte verde.


## Fase atual do ROADMAP

## Fase: Conhecimento e agente externo agnóstico (t84u–t86u, 26/10/2026)
- [x] **GitNexus [agora]:** global no servidor (1.6.12, fora do repo), índice da PQBR registrado, reindex no post-commit, pré-requisito fail-closed. ARQUITETURA §12.
- [x] **Política por papel [agora]:** `config/politica_papeis.json` + filtro no Hindsight e no adaptador GitNexus.
- [x] **Servidor MCP da PQBR só na tailnet (t89u, OK do José):** `pqbr-mcp`, 127.0.0.1:8791 + tailscale serve, só leitura, token por cliente.
- [x] **AGENTS.md gerado (t89u)** do onboarding do MCP.
- [x] Reclassificar com tags as memórias legadas sem tag (feito em t90u).
- [x] **Escrita de memória pelo MCP (t95u/t96u):** `registrar_memoria`/`registrar_alteracao` (contrato 1.0.0), só papel com escrita na política, autor = cliente do token, referência a commit verificado e arquivos.
- [x] **ESTADO-ATUAL (t98u/t99u):** `docs/ESTADO-ATUAL.md` é a fonte única do handoff, a 1ª seção do onboarding/AGENTS.md; hook pre-commit e `registrar_alteracao` (tipo correcao/pendencia_resolvida) exigem a atualização; handoff no Hindsight (tag `estado`, todos os papéis).
- [x] **Teste de agente do zero (t96u):** URL tailnet + token `mantenedor-externo` → onboarding → buscar_memoria → commit local `b63fa56` → registrar_alteracao → buscar_memoria retornou em ~10 s; indexador negado; sem token 401.
- [x] Licença do GitNexus aceita (uso pessoal, sem revenda; t90u).
- [x] **Reclassificação do Hindsight por papel (t90u):** `scripts/hindsight/reclassificar.py`; 220 candidatas a descarte em `docs/operacao/hindsight-descarte-candidatos.md`.
- [x] Descarte das candidatas (t90s398): 231 apagadas após a indexação; docs vigentes corrigidos; indexador com a regra única de tags.
- [ ] Revisar as 7 candidatas mantidas (sem substituta direta).


## LACUNAS (início)

# Lacunas: etapas feitas à mão em 12/10 → fluxo determinístico (José 17:18)

Regra (José 17:17): nenhuma etapa de fluxo à mão. Se o fluxo não está ativo: parar, registrar e consertar o fluxo. José usa o Telegram PQBR (Hermes `pqbr`) e a Temporal UI; aprovações são sinais do Temporal (t471/t474; o plano Discord/Paperclip de t464 foi revogado).

| # | Etapa manual hoje | Dono | Contrato Pydantic | Temporal | Agente → código → ferramenta | Instrução do agente (instructions-file:put) | Teste | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Temas via 9router fora do Paperclip (`repor_temas_sem_ponte.py`) | Líder Editorial | `PropostaAgente` / `PropostaBruta` (temas.py) | `ReposicaoTemasWorkflow` + agenda `pqbr-reposicao-temas` 00:30 | issue no Paperclip → agente propõe JSON → `temas_inserir` → Postgres | "Mantenha 7 dias de temas (≥80% curiosidades), ≤5 por proposta, ≤480 caracteres; responda só o bloco json" | `tests/unit/test_temas_t465.py` | Agenda ativa; **bloqueado pela ponte (pedido #2: login da CLI do Paperclip)** |
| 2 | Revisão do Auditor feita à mão | Auditor (agente) + `auditor_gemini` | `RespostaAuditorGemini` / `ResultadoAuditorGemini` | atividade `auditor_gemini` (fila camofox-pqbr), chamada no `EpisodioWorkflow` após o pós | episódio → quadros → Camofox/Gemini → contrato → `erros_aceitaveis`; terceira_rodada → sinal para o Auditor no Paperclip | "Só atue em terceira_rodada; decida aprova/reprova com os motivos do contrato; nunca peça roteiro novo à mão" | test_auditor_visual + teste de `validar` | Atividade registrada no worker; **falta ligar no EpisodioWorkflow** e o teste no EP1002 (Google voltou 17:25) |
| 3 | Auditoria Gemini por script (`auditor_gemini_ep.py`) | código | idem 2 | idem 2 | — | — | idem | Script aposentado após o item 2 entrar no fluxo |
| 4 | Arquivar e apagar cadernos de teste (`arquivar_estilos.py`) | código | `PedidoDescarteTeste`, `CopiasVerificadas` (descarte.py) | `DescartarCadernoTesteWorkflow` → filho `ApagarCadernoWorkflow(teste=True)` | fluxo → CLI notebooklm (exportar) → Drive 00_Biblia_Visual/cadernos-teste + repo `docs/pesquisas/arquivo-cadernos` + `pqbr.arquivo_caderno` + Hindsight → verificar → apagar pelo id | — | `tests/unit/test_descarte.py` | **Feito** (18:06); 1º uso: EP1001 |
| 5 | Regra de espera da publicação bloqueava EP1001 (nunca publicado) | código + decisão do José (18:06) | `registro_reclassificar_teste` (só não publicado) + `registro_autorizar_apagar_teste` | `DescartarCadernoTesteWorkflow` (reclassifica para `pesquisa`) | — | — | idem 4 | **Feito**: reclassificado e descartado pelo fluxo |
| 6 | Teste de estilos por script (`teste_estilos.py`) | Diretor de Arte | `PedidoNotebookLM.steering` + `config/estilo_visual.json` | `EpisodioWorkflow` com `steering`/estilo ativo (próximo teste: estilo D via fluxo) | issue do Diretor de Arte → config de estilo → fluxo do episódio | "Proponha estilo em config/estilo_visual.json via proposta; não gere vídeo fora do fluxo" | unit de `steering_s

## Mapa visual

docs/mapa/index.html (servido em :8088) — diagramas: 00-visao-geral.mmd, 01-episodio.mmd, 02-reposicao-temas.mmd, 03-acessos.mmd, 04-descarte.mmd, 05-vigia-atualizacoes.mmd, 06-runs-presos.mmd, 07-cadeia-video.mmd, 08-identidade-camofox.mmd, 09-agentes-responsabilidades.mmd, 10-catalogo-erros.mmd, 11-publicacao.mmd, 12-storyboard-elenco.mmd, 13-memoria-mcp-handoff.mmd
