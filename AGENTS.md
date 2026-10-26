# PQBR — onboarding do agente (gerado; não editar à mão)

Fontes canônicas: docs/BRIEFING-novo-agente-pqbr.md, docs/REGRAS.md, docs/DECISOES-LOG.md, docs/ROADMAP.md, docs/LACUNAS-fluxo.md, docs/ARQUITETURA.md, docs/mapa/. Em conflito, vale o doc canônico.

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
4. Ao final, `registrar_alteracao` com o hash do commit (ou `registrar_memoria` se não houve commit), citando arquivos. Sem esse registro a alteração não conta como entregue.

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

## t89u (26/10/2026) — Servidor MCP dentro da PQBR, só tailnet; saúde do Hindsight
- José confirmou: o servidor MCP fica na própria aplicação; acesso autorizado só pela tailnet (127.0.0.1 + `tailscale serve`, nunca Funnel/0.0.0.0). Só leitura; papel por token de cliente; papel desconhecido ⇒ negado.
- Hindsight verificado saudável (0.10.2, bank `pqbr` com 5.012 memórias). O filtro de tags funciona no servidor; as memórias legadas sem tag ficam fora da política.


## t90u (26/10/2026) — Licença do GitNexus aceita; reclassificação do Hindsight por papel
- **Licença GitNexus (PolyForm Noncommercial) aceita pelo José:** a PQBR é de uso pessoal, sem revenda nem inclusão em produto vendido. Pendência do ROADMAP encerrada.
- **Opção A — reclassificar:** `scripts/hindsight/reclassificar.py` (determinístico, idempotente, dry-run por padrão) deu tags de conteúdo da política 1.1.0 aos 947 documentos legados (origem do retain + palavras-chave) e autor `papel:indexador`. Nenhum documento ficou sem tag de leitura. Backup antes: `~/.pqbr/hindsight/backup/` (export do bank + JSON, 600).
- **Obsoletos:** 220 documentos (1.303 unidades) marcados `obsoleto_candidato` (versão superada da fonte, decisão revogada sem fonte vigente, teste). **Nada apagado**; lista em `docs/operacao/hindsight-descarte-candidatos.md`. Apagar exige OK do José. Observações derivadas foram invalidadas pelo próprio Hindsight e se refazem na reconsolidação.


## t90s398 (26/10/2026) — Docs corrigidos, regra única de tags e descarte no Hindsight
- José aprovou (card t90s398): corrigir ROADMAP, AGENTES.md e `memoria:jev`; indexador com a mesma regra de tags; apagar as candidatas após a próxima indexação.
- Docs: Paperclip marcado como histórico no ROADMAP (Fase 0.5, Fase 3, Riscos, Premissas, JEV-01) e na REFERENCIA §8; AGENTES.md fica só com os 8 papéis (equipe de 14 e mapa @prod-* movidos para `docs/_obsoleto/agentes-equipe-14-t395.md`); `memoria:jev` aponta a chave só no `~/.pqbr/worker.env` (600).
- `pqbr.storage.hindsight_tags` é a regra única (indexador e reclassificação); política 1.2.0 deixa o indexador escrever as tags de conteúdo.
- Indexação manual rodada (sem reinício); 0 seções vigentes faltando no bank. Descarte: 231 documentos apagados (backup antes), 7 mantidos para revisão. IDs em `docs/operacao/hindsight-descarte-candidatos.md`.


## t95u/t96u (26/10/2026) — Agentes externos registram memória pelo MCP
- José pediu que as alterações de agentes externos sejam também memorizadas. O MCP deixa de ser só leitura: `registrar_memoria` e `registrar_alteracao` (esta exige commit existente), contrato Pydantic 1.0.0, via `hindsight.reter`.
- Só escreve papel com escrita na política (o indexador não escreve pelo MCP); tags dentro das tags de escrita do papel, `obsoleto_candidato` proibida; autor `autor:<cliente>` vem do token, nunca do pedido; texto passa pela barreira de segredos.
- Protocolo obrigatório no onboarding/AGENTS.md: onboarding → buscar_memoria antes de agir → commit local + DECISOES-LOG/CHANGELOG → registrar ao final. Servidor 0.2.0 (reinício só do `pqbr-mcp`). Teste de agente do zero aprovado.


## t97u (26/10/2026) — Memória superada da licença do GitNexus corrigida
- José autorizou ("pode corrigir logo"). Fonte: ARQUITETURA §12 ainda dizia "pode exigir licença comercial" e o log t84u–t86u só "risco registrado"; ambos agora citam a aceitação de t90u.
- Hindsight: 3 documentos superados apagados (2 versões antigas da ARQUITETURA §12 e a seção t84u–t86u), backup em `~/.pqbr/hindsight/backup/licenca-gitnexus-20261026.json` (600); seções reindexadas e a versão correta registrada pelo MCP.


## Estado do ROADMAP

## Estado em 26/10/2026 (consolidação t63s292 → t78u)
**Feito:**
- Camofox PQBR com MemoryMax 3000M (t63s292); pico de 2316 MB no lote.
- Juiz Gemini fixado no **3.8 Flash**, selecionado e conferido antes de cada envio; aceita imagens (2 pranchas de 300 px).
- LOOP do EP1002 com veredito `terceira_rodada`; o José reprovou visualmente (t75u) e o episódio foi **descartado** (reversível) e o tema voltou a `proposto`.
- Fluxo de publicação via Temporal: `publishAt` no upload privado, escopo `PQBR_PUBLICACAO_REAL_CODIGOS`, `PublicacaoAgendadaWorkflow` registrado no `worker_episodio` (fila `episodio-pqbr`).
- Contrato `FichaCena`/`Storyboard` 1.1.0, com ficha por cena, figurino por papel, caras e bocas sem fala e elenco alternado.
- Pesquisa `flow-storyboard-por-cena.md` e auditoria do storyboard do lote 2510.

**Bloqueado:**
- Upload real: sem credenciais OAuth do YouTube no worker, e o Cloud Console exige 2SV na conta do canal (o José ativa).
- Migração 0020 não aplicada; worker não reiniciado.

**Próximo:**
1. 2SV → projeto `pqbr-publicacao` → OAuth Desktop → chaves em `episodio.env` → `channels.list`.
2. Activity que gera o `Storyboard` e bloqueia a geração sem ele.
3. Critérios VISUAL `personagem_mexe_labios`, `corte_oculos_cabeca` e `grotesco`.
4. Referências `ASSET_personagem_{masculino,feminino}-v1` (geração paga: pedir OK).
5. EP1003 cafe-fraco (o José vê antes).

**Testes pendentes (t71u–t72u, não executar ainda):**
- LOOP do Gemini por cena + consolidação final só em texto; comparar tempo, memória e qualidade.
- 4 Argon com raciocínio baixo vs 3.8 Flash.


## Fase: Conhecimento e agente externo agnóstico (t84u–t86u, 26/10/2026)
- [x] **GitNexus [agora]:** global no servidor (1.6.12, fora do repo), índice da PQBR registrado, reindex no post-commit, pré-requisito fail-closed. ARQUITETURA §12.
- [x] **Política por papel [agora]:** `config/politica_papeis.json` + filtro no Hindsight e no adaptador GitNexus.
- [x] **Servidor MCP da PQBR só na tailnet (t89u, OK do José):** `pqbr-mcp`, 127.0.0.1:8791 + tailscale serve, só leitura, token por cliente.
- [x] **AGENTS.md gerado (t89u)** do onboarding do MCP.
- [x] Reclassificar com tags as memórias legadas sem tag (feito em t90u).
- [x] **Escrita de memória pelo MCP (t95u/t96u):** `registrar_memoria`/`registrar_alteracao` (contrato 1.0.0), só papel com escrita na política, autor = cliente do token, referência a commit verificado e arquivos.
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

docs/mapa/index.html (servido em :8088) — diagramas: 00-visao-geral.mmd, 01-episodio.mmd, 02-reposicao-temas.mmd, 03-acessos.mmd, 04-descarte.mmd, 05-vigia-atualizacoes.mmd, 06-runs-presos.mmd, 07-cadeia-video.mmd, 08-identidade-camofox.mmd, 09-agentes-responsabilidades.mmd, 10-catalogo-erros.mmd, 11-publicacao.mmd, 12-storyboard-elenco.mmd
