# PQBR — onboarding do agente (gerado; não editar à mão)

## ESTADO ATUAL da PQBR — continue daqui

Fonte única de "onde estamos". Não repete o ROADMAP: aponta os itens por id. **Atualize este arquivo a cada correção ou pendência resolvida.** O hook pre-commit exige isso quando o commit toca ROADMAP, LACUNAS, DECISOES-LOG ou CHANGELOG, e o `registrar_alteracao` exige isso para `tipo` correcao ou pendencia_resolvida.

Atualizado: 28/10/2026 (t142u: documentos, mapa e memória alinhados para retomar; JEV-EF segue no ROADMAP) · versão 0.17.9

## Onde estamos
- **Produção:** o lote do saldo está em `runtime/lote-saldo/` (um diretório por tema). O EP1002 olhos-da-cara foi reprovado e descartado (`runtime/lote-saldo/_descartado/`), e o tema voltou a `proposto`.
- **Publicação (ROADMAP F8-01):** o fluxo pelo Temporal está pronto. O worker foi reiniciado em 27/10 às 08:56 (-03, São Paulo; t128u) e carrega o fallback do refresh e o ensaio. `YOUTUBE_DRY_RUN=true`. Nada foi enviado. Até a produção ativa, vídeo aprovado que subir fica privado; público só depois, na ordem dos roteiros e nas janelas.
- **Agente externo:** o servidor MCP 0.2+ só funciona pela tailnet. A memória escrita leva o autor (o cliente) e o commit. O protocolo obrigatório está no AGENTS.md. O `initialize` do `pqbr-mcp` já devolve a frase de honestidade (t126u), desde o reinício das 08:56. Hindsight: bank `pqbr` com 877 documentos; as 7 candidatas restantes foram apagadas (t128u).
- **Documentos (t129u):** `docs/LACUNAS-fluxo.md` só lista o que ainda falta no código. O roster vigente está em `docs/AGENTES.md`. Briefing, checklist pré-E2E, rascunho de SOUL e propostas não aplicadas foram para `docs/_obsoleto/`. As provas do F3-05 continuam em `docs/sdd/` porque o item segue aberto no ROADMAP.
- **Fluxo (t130u):** o episódio para no storyboard. O NotebookLM entrega roteiro, compliance e SEO, e não gera vídeo. `YOUTUBE_DRY_RUN=true`. Os vídeos de `runtime/lote-saldo/` ficam parados até a etapa de publicação.
- **Paperclip (t130u):** `paperclipai.service` parado e desabilitado em 27/10. Sem desinstalar e sem apagar dados. `config/paperclip.json` está `parado_proposital`.
- **Stickman (t133u, t141u):** identidade única. O desenho sem roupa foi recusado. A roupa chapada ainda não tem cor. O material de 28/10 inspira o desenho e o prompt; NotebookLM, Flow e o resto do fluxo ficam. 3D não se pede. Fases em `docs/fases/stickman.md`.

## Próximo passo
Ponto para retomar: o José escolhe a cor da roupa chapada do PERS-M e da PERS-F. Sem essa cor, não há folha nova e não há geração no Flow. Arquitetura, NotebookLM, mapa e a cadeia Flow → Vids → Vibes estão alinhados (t142u). Nada está agendado no YouTube. O LOOP e o drop-in do Telegram ficam para depois.

## Pendências abertas
| # | Pendência | Ref. ROADMAP | Dono | Bloqueio |
|---|---|---|---|---|
| P1 | Vídeos do saldo ficam parados. José assiste quando puder. O EP1003 cafe-fraco já está aprovado (26/10, único até agora). Não roda o LOOP e não publica agora | Estado 27/10 · t130u | José | sem mexer nos arquivos até a etapa do Studio |
| P2 | Publicação: worker reiniciado 27/10 11:50 (-03), 0 workflows Running. `YOUTUBE_DRY_RUN=true`. Nada agendado (`agenda_publicacao` com 0 linhas). Envio real desligado. Refresh do app em teste vence ~2/11 21:20 (-03) | F8-01 | agente | sem envio até a produção ativa |
| P3 | Teste: LOOP por cena vs o atual | Estado 26/10 · Testes pendentes | agente | depois do fluxo de publicação |
| P4 | **Feito (t108u/t109u).** Juiz por etapa (`gemini_juiz` v1.0.0): pré-produção usa 3.8 Flash; produção (VISUAL e LOOP) usa 4 Argon Baixo. O worker `pqbr-episodio-worker` foi reiniciado com OK do José às 16:57 (-03), e o poller está ativo na fila `episodio-pqbr`, ns `pqbr` | Estado 26/10 · DECISOES-LOG t109u | agente | concluído |
| P5 | Folha do elenco. Os PNG sem roupa foram recusados (t140u). Falta a cor da roupa chapada | t140u · Fase 3 | José | sem a cor, não desenhar de novo e não gerar no Flow |
| P6 | **Feito (t130u).** `storyboard_criar` valida o Storyboard 1.2.0, grava a ficha e deixa `pode_gerar_video` false. O episódio para aí. Imagem e vídeo desta etapa não rodam | Estado 27/10 · DECISOES-LOG t130u | agente | concluído |
| P7 | **Feito (t108u).** O gate VISUAL agora tem `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco` (FichaCena/REGRAS §25), e cada um reprova sozinho. Validado no EP1002 (`loop-gemini-4argon-v2.json`): reprova, com S01 corte+grotesco, S04 corte e S02/S05/S09 boca | Estado 26/10 · CHANGELOG 0.14.0 | agente | concluído |
| P8 | **Feito (t128u).** As 7 memórias `obsoleto_candidato` do roster antigo de `docs/AGENTES.md` foram apagadas em 27/10 ~08:57 (-03). Bank 884 → 877. Backup fora do git | `docs/operacao/hindsight-descarte-candidatos.md` | agente | concluído |
| P9 | **Feito (t112u–t116u).** Papel `mantenedor` (política 1.4.0) lê todas as tags e o repo todo; pqbr-mcp 0.4.0 exclusivo do mantenedor; onboarding em `docs/operacao/onboarding-agente-externo.md`. Falta só entregar token por cliente novo (`scripts/mcp/novo_cliente.py <nome> mantenedor`) | Fase Conhecimento | agente | concluído |
| P10 | Hindsight conferido 27/10 08:10 (São Paulo): API healthy, banco conectado. A reconsolidação segue automática | Fase Conhecimento | Hindsight (automático) | só conferir de novo se o bank acusar falha |
| P11 | Merge da branch `feat/f8-01-publicacao-automatica` (já no GitHub) na main | — | José | merge/PR exige OK |
| P12 | ERR-01: revisar os erros aceitáveis | ERR-01 | agente | depois dos primeiros dias de produção |
| P13 | Proposta não aplicada: ferramentas só leitura para os agentes PydanticAI, sem MCP interno | F1-05 · t134u | José | sem efeito externo |
| P14 | Proposta não aplicada: acompanhamento de mudanças (vigia de fallbacks, canário, deriva de contrato, `dev_diagnosticar`). Sem agente novo. O NotebookLM não entra no canário | F6-02 · t135u/t136u | José | registro no worker exige reinício |
| P15 | **Prioritário.** Efetivar o Jev (`decide()`), item JEV-EF. Chave OpenRouter (JEV-02) só na hora de 

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
- **NotebookLM (t130u):** não gera vídeo. Entrega pesquisa, roteiro, compliance e SEO. `storyboard_criar` valida o `Storyboard` 1.2.0 e grava a ficha. `imagens_revisadas` fica false. Esta etapa não gera imagem nem vídeo.
- **Gasto (t130u):** o contrato da etapa diz se pode gastar, qual modelo e qual meio (`src/pqbr/contratos/gasto.py`). O que o contrato não autoriza não roda. Storyboard: chat do NotebookLM, sim. Vídeo e infográfico do NotebookLM, não. O fallback de SEO usa o 9router no combo `especialista-seo` só depois de duas respostas inválidas do caderno.
- **Paperclip (t130u):** `paperclipai.service` parado e desabilitado, sem desinstalar e sem apagar dados. `config/paperclip.json` está `parado_proposital`, então a checagem não abre pedido. Apagar o produto fica para depois, com novo OK.
- **Login (t130u):** consentimento permanente para manter as sessões ativas. José entra só se a reautenticação autônoma não fechar. Parar um fluxo, pelo Telegram ou por pedido ao mantenedor, não desloga.
- **Saldo e cliques (t130u, ajustado t131u):** os vídeos já prontos ficam parados até a etapa de publicação no YouTube Studio. Envio real continua desligado. Não inventar seletor. O arquivo `config/mapa_cliques.json` não é catálogo: a tela do Camofox manda. O arquivo só anota surpresa, com data.
- **Logo (t131u):** a silhueta do mapa do Brasil não bloqueia geração nem subida. Antes de tornar público, avisar o José para ele olhar o logo. A correção do desenho pode ficar para depois.
- **Gasto visual (t131u):** imagem no Google Flow é gratuita e pode ser gerada na quantidade que o storyboard pedir. Vídeo gasta o saldo que houver no Flow; acabou, Google Vids; depois, Meta Vibes.
- **Flow, primeira tela (t132u) [VERIFICADO]:** em 27/10 a sessão já logada abriu `https://flow.google.com/`. Duas imagens estáticas, modelo Nano Banana 2 Lite, 9:16, 768×1376. A ficha da imagem não mostrou crédito. O pedido de stickman de tubos saiu cartum de pessoa, nas duas. O líquido claro só apareceu na segunda. O menu Baixar oferece 2K e 4K; só o 1K original foi baixado. Vídeo não foi gerado. O episódio ainda não chama o Flow. Não repetir o mesmo prompt.
- **Honestidade (t126u, José):** o agente diz o que viu e o que não viu. Não inventa seletor, número ou resultado para a conta fechar. Se uma ideia do José não se sustenta, ou só aumenta o sistema, o agente diz isso antes de construir. Vale para todos os papéis e para o agente externo no MCP.
- **Decisão nova:** entra no `DECISOES-LOG.md` (tNNN) **e** aqui, no mesmo commit. Se este arquivo divergir do log, vale a entrada mais nova do log e este arquivo é corrigido.
- **Legenda:** [APROVADO] decisão do José · [VERIFICADO] testado/visto na fonte · [HIPÓTESE] a confirmar antes de construir o que depende dela · EM CONSTRUÇÃO — aguardando José.
- Origem: os códigos (tNNN, "item N", nomes de bloco) remetem ao `DECISOES-LOG.md`; "07/10" = registro de 07/10/2026.

- **Atualização 11/10 (t384–t394), prevalece sobre qualquer trecho abaixo que diga o contrário:**
  1. **Estratégia:** a entrega à core-eng foi abolida; o jr constrói a PQBR **no Paperclip** (t394). **[SUPERADO por ADR-011/t510 e t536:** agentes em PydanticAI nas activities do Temporal; o Paperclip fica **parado e desabilitado** até a nova arquitetura ser validada, e só depois é desinstalado.**]** A ENTREGA está em `arquivo/`. A equipe vigente e o mapa @prod-* → agentes estão em `AGENTES.md` (§3 e §11).
  2. **Autonomia/proatividade (t384, t390):** a empresa opera semanas ou meses sem o José. Agentes aplicam sozinhos dentro de faixas e playbooks; o José só vê no relatório. Ainda exigem o José: excluir/rejeitar/banir; voltar a público vídeo do item 5 ou recorrer ao YouTube; gastar dinheiro; login manual pelo noVNC ou 2FA (só depois de esgotada a reautenticação autônoma, item 11); mudar regra canônica; segredos e infraestrutura.
  3. **Equipe:** 14 agentes já contratados (AGENTES.md §2), inclui

## Decisões recentes

## t137u (27/10/2026) — Jev: oráculo, e item prioritário no ROADMAP [APROVADO José]
- Varredura: `decide()` não existe em `src/` nem em `scripts/`. Os contratos de saída existem. `CorrecaoAutonomaWorkflow` levanta `EmConstrucao`. `TYPESAFE_API_KEY` está em `~/.pqbr/worker.env` e nenhum processo da PQBR a lê. A CLI `jev` 0.19.0, fora da PQBR, responde.
- Nenhum documento contradiz o papel de oráculo. REGRAS §7 é esse papel. A frase "o Jev decide refazer/trocar/chamar José" entrega `DecisaoPublicacao` e quem age é o código. Verificação visual é do juiz Gemini; verificação estruturada de uma intervenção é do Jev (`VerificacaoCorrecao`, t356).
- José [APROVADO]: efetivar o Jev. Item prioritário **JEV-EF** no ROADMAP, junto com F1-05 (t134u) e F6-02 (t135u/t136u). A chave OpenRouter (JEV-02) entra no JEV-EF e só é pedida ao ligar.
- No canário, o Jev escolhe um `ref` da lista que o Camofox observou, ou `abstain`. Não escreve seletor nem vê imagem.
- Junção: estas quatro entradas foram escritas na branch `cursor/proposta-ferramentas-agentes-b9f6` e reaplicadas em cima de `57f8b97` (stickman, t133u). O stickman, o `banco-fichas/` e o código desse commit não foram alterados.


## t139u (27/10/2026) — Corpo do stickman definido
- José pediu para continuar a leitura dos canais e definir de vez. A cor de roupa, que t133u tinha deixado aberta, fecha: não há roupa.
- Corpo igual nos dois: tubo preto grosso, ponta redonda, cabeça branca com o mesmo tamanho, boca fechada, sem pele, sem dedo, sem letra na imagem. PERS-M é mais alto porque a perna é mais longa. Não tem cabelo. O único acento é o óculos redondo vermelho. PERS-F é mais baixa. O coque é um círculo do mesmo tubo, no alto, do lado direito de quem olha. O único acento é a argola amarela, do lado esquerdo de quem olha. A pinta é preta, pequena, ao lado da boca, nesse mesmo lado.
- O desenho está em `banco-fichas/personagens/PERS-M.png`, `PERS-F.png` e `ELENCO-frente.png` (este último só compara a altura e não vai para o Flow). O script que regrava é `scripts/visual/frente_stickman.py`. Não passou pelo Flow. A tentativa 1 de 27/10 (pessoa azul, t138u) continua fora.
- Não afirmo que o José já olhou estes PNG. A regra não volta para "cor a definir". Se o traço não servir, muda o script. Não se abre peça de roupa. A aba Personagens do Flow não recebeu estes arquivos. Ambiente e objeto seguem em texto.
- O espelho `00_Biblia_Visual/banco-fichas` foi atualizado no mesmo dia. Os markdown já existentes foram substituídos no mesmo arquivo, com hash conferido. Os PNG e os SVG entraram na pasta `personagens`. Nada foi apagado.


## t140u (28/10/2026) — O desenho sem roupa foi recusado
- José viu os PNG de t139u e disse que não gostou. Mandou a busca do Google e quatro materiais: transcrição "5 Stick Figure Styles" (youtube.com/watch?v=RyMPBz7LeZc), transcrição "Create Viral Stickman Animation Videos" (youtube.com/watch?v=pe4vBpgbDMg), o pipeline Proventube de 11 páginas, a folha "Historical Stickman Video Instructions" de 6 páginas e o modelo "STICKMAN VIDEO GENERATOR" de 4 páginas.
- O que essas imagens têm em comum, e o nosso tubo não tem: cabeça redonda branca, contorno preto, membros finos, uma roupa chapada, cara com olho, sobrancelha e boca de reação, personagem agindo. Uma das folhas de modelo usa cabeça cor de pele, camiseta branca e bermuda azul. Os quadros de Pompeia usam cabelo, lenço amarelo, camisa e calça.
- O que não entra: o estilo 1 do pipeline (roupa 3D, cabelo com volume, cenário de cinema) e o estilo 5 (corpo de pessoa, não palito). O tutorial pede 16:9 e Nano Banana Pro; o Short da PQBR é 9:16 e a imagem autorizada é o Nano Banana 2 Lite. O mesmo vídeo sugere várias contas Gmail para passar do teto diário do Flow e empurra o site Vsub. Isso não se faz. O número "58M" está desenhado na miniatura; não é uma medição.
- O que se aproveita: um personagem só, enviado ao Flow como imagem ("add to prompt"), e o prompt muda pose, expressão, objeto e lugar. Folha com frente, lado e expressões; na cena, um recorte de um boneco só, porque a folha inteira confunde o modelo. Narração fora. Sem

## t141u (28/10/2026) — O material é inspiração; o fluxo não muda
- José: manter a arquitetura e o fluxo, tudo o que está aparelhado. O material entrou para ver o processo e os prompts que dá para usar. Continua o NotebookLM. Tudo o mais permanece. O que muda é a inspiração da identidade visual e o reajuste do que o fluxo precisa para chegar nesse desenho.
- Não entra ferramenta nova. Claude não escreve o roteiro. Vsub, CapCut e várias contas Gmail ficam de fora. Imagem segue Nano Banana 2 Lite, 9:16, uma por vez, com manifesto. Vídeo segue a cadeia já definida, e o episódio continua parando no storyboard.
- O reajuste cabe no que já existe. O caderno (`templates/notebooklm/comandos-pqbr.md`) passa a pedir, no JSON do storyboard, o frame de início como prompt de imagem, a frase-trava da ficha, e a animação como movimento do corpo até o fim, com "lips closed". A cena usa o recorte de um boneco, não a folha inteira. O contrato §19 item 7 registra isso.
- A cor da roupa continua sem escolha. Sem ela, a folha nova não se desenha.


## t142u (28/10/2026) — Documentos, mapa e memória alinhados para retomar
- José pediu para atualizar os documentos, o mapa visual exposto e as memórias, e parar num ponto em que dá para continuar depois.
- Mapa: `12-storyboard-elenco.mmd` mostra o stickman, a roupa ainda sem cor e o prompt de início com recorte. `07-cadeia-video.mmd` diz que o material não troca a cadeia. `09` deixa de citar só o elenco de t78u. A página `docs/mapa/index.html` foi regenerada. A regra de não editar o mapa sozinho cedeu porque o pedido foi explícito.
- Memória-chave `memoria:bloco-visual` deixa de mandar o cartum 2D de 12/10 e passa a descrever o stickman de t141u. O indexador leva isso ao Hindsight. Documento antigo com o texto de 12/10, se ainda estiver no bank, não é a regra.
- O que continua aberto, e só isso, para a próxima sessão: a cor da roupa chapada. Sem ela, não há folha e não há geração no Flow. Arquitetura, NotebookLM e `YOUTUBE_DRY_RUN` ficam como estão.


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

# Lacunas que ainda existem (conferidas no código em 27/10/2026, t130u)

A tabela de 12/10 que bloqueava o fluxo no login da CLI do Paperclip foi para `docs/_obsoleto/lacunas-fluxo-ate-20261027.md`. Não é lacuna. A reposição de temas (`ReposicaoTemasWorkflow`) consulta o NotebookLM e grava no Postgres, sem Paperclip. O descarte de caderno de teste e o episódio estão registrados no `pqbr-episodio-worker`. Itens já feitos (descarte do EP1001, estilo via config, pedido de acesso que se fechou, restauração de sessão) não se repetem aqui.

## Abertas

1. **Auditor no episódio.** `EpisodioWorkflow` para na ficha e não espera `veredito_auditor` (t130u). O sinal continua registrado e não é chamado. Não chama `auditor_gemini` nem `auditor_loop_gemini`. A activity `auditor_gemini` está no worker da fila `camofox-pqbr`. O script `scripts/e2e/auditor_gemini_ep.py` ainda existe. Os critérios `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco` já reprovam sozinhos (t108u); isso não falta.
2. **Fechado (t130u).** `tipo=short` não gera vídeo. `nlm_gerar_short` recusa antes do CLI. O episódio segue para roteiro, SEO e `storyboard_criar`.
3. **Códigos do lote 2510.** Os prontos em `docs/pesquisas/lote-2510/` não têm `PQBR-EP`. Sem código não há `drive_enviar` nem episódio no Postgres. Quem define os códigos é o José.
4. **Vídeo em série (Fase 4V).** O episódio para na ficha e não baixa vídeo do NotebookLM (t130u). Flow, Vids e Vibes continuam fora do código. Em 27/10 o Flow foi aberto à mão (t132u): duas imagens, nenhum vídeo. HOLD das três rotas está decidido (t529) e não implementado. O mapa de cliques só tem as três surpresas dessa tela.
5. **Imagens do storyboard.** A activity `storyboard_criar` grava a ficha com `imagens_revisadas` false e não gera imagem. O teste manual (t132u) fez duas imagens no Flow; as duas saíram pessoa de cartum, não stickman. O banco `banco-fichas/` é texto (t133u), sem imagem aprovada. A referência do elenco continua por gerar.
6. **Navegador.** `NavegadorIdentidade` está em `src/pqbr/motores/navegador.py`. Nenhum workflow importa essa porta. O backup diário e o canário do ADR-012 não foram conferidos nesta passagem: não entram como feitos nem como lacuna confirmada.
7. **Publicação, o que ainda falta.** O envio real está desligado de propósito (`YOUTUBE_DRY_RUN=true`) até a produção ativa. O roteiro de cliques do Studio não foi visto. `config/mapa_cliques.json` tem só surpresas do Flow (t132u), não um roteiro do Studio. O worker do episódio não tem o drop-in `telegram.conf`. O resto dessa etapa (chaves, agenda, registro no worker, fallback do refresh) está no ar desde 27/10 08:56 (-03).
8. **Teste adiado, não executar agora.** LOOP do Gemini por cena, e 4 Argon baixo contra 3.8 Flash no mesmo lote.

## Não são lacunas

- Login da CLI do Paperclip, issue no Paperclip para começar episódio ou descarte, e o token do bot Hermes citado em 15/10. O canal vigente é o bot próprio (t538). O corte do serviço Paperclip é o item F05-09 do 

## Mapa visual

docs/mapa/index.html (servido em :8088) — diagramas: 00-visao-geral.mmd, 01-episodio.mmd, 02-reposicao-temas.mmd, 03-acessos.mmd, 04-descarte.mmd, 05-vigia-atualizacoes.mmd, 06-runs-presos.mmd, 07-cadeia-video.mmd, 08-identidade-camofox.mmd, 09-agentes-responsabilidades.mmd, 10-catalogo-erros.mmd, 11-publicacao.mmd, 12-storyboard-elenco.mmd, 13-memoria-mcp-handoff.mmd · aba Roadmap gerada de ROADMAP + ESTADO-ATUAL (scripts/mapa/roadmap.py; edite as fontes, nunca o HTML)
