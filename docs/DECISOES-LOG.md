# Registro de decisões do José (DECISOES-LOG)

> ⛔ **ARQUIVO DE PRÉ-CONSTRUÇÃO: AGENTES NÃO CONSULTAM (t287).** Este registro é a prova histórica das decisões. Ler este arquivo exige **aprovação explícita do José**, porque entradas antigas ou superadas podem ser mal interpretadas e aplicadas em produção. As regras válidas estão em `docs/REGRAS.md`.

> Registro cronológico, só acrescenta. Em divergência com `REGRAS.md`, vale a entrada mais nova deste log e o REGRAS.md é corrigido no mesmo commit. Toda decisão nova entra aqui **e** no REGRAS.md.
> Unificação de 09/10: junta o registro de 07/10 (só existia no box), o de 08/10 do servidor e a entrada t280 (só existia no box). Host da tailnet substituído por nome lógico.

---

## 07/10/2026: decisões e ressalvas antes do blueprint (cópia que existia só no box; unificada em 09/10)

- Nome da skill: recriar como `rotina-producao-porque-br` (corrigir o "e" que falta em `porqu-br`). Ressalva no blueprint.
- OpenViking FORA do build. Memória migra para o Hindsight; importar do OpenViking só o que for aproveitável (o blueprint deve dizer como).
- Guardrail: produção NUNCA no caderno raiz do NotebookLM; sempre caderno efêmero por roteiro. Limpar o chat do caderno raiz a cada troca de projeto ou de produção.
- 1 Publicação: Camofox no Studio (como hoje); a API fica para depois.
- 2 Template: pacote próprio `pqbr-company` (recomendado).
- 3 `yt_production` vai para o Supabase do projeto Paperclip; o Hindsight também vai para o Supabase.
- 4 Memória: um bank único por organização, no mesmo projeto Supabase do Paperclip (confirmar).
- 5 Criar o perfil Hermes `pqbr`; pausar o `rede` durante a validação da transição.
- 6 4 Shorts/dia, nos mesmos horários de hoje.
- 7 Stickman 2D puro + bíblia/model sheet do personagem; antes, pesquisar quais estilos de personagem performam melhor.
- 8 Auditor via Gemini Web/Camofox, mas precisa ficar mais eficiente: checar CTA, finalização correta e corte; guardrails determinísticos.
- 9 @prod-analista: provável sim; José precisa de mais subsídios.
- 10 Governança: máximo de determinismo; detectar problemas, registrar a ação humana e repetir automaticamente na próxima vez. Orçamento: em aberto.

### Rodada 2 (07/10, ~21h)
- Não existe agente de dev na PQBR. Manutenção (inclusive do caderno raiz) só via ticket para a core-eng; a permissão temporária vem com o ticket aprovado.
- Hindsight fica LOCAL (com backup diário). A migração para o Supabase é uma fase futura opcional.
- Roadmap dentro do blueprint (documento único). Quem escreve a documentação é o core-eng.
- Fase 1: a core-eng faz a primeira documentação; o CTO recebe e distribui para os agentes.
- Fase 4: o `rede` perde a automação/cron e passa a rodar só sob demanda (o José pede cada etapa); a PQBR publica os 4 Shorts de forma autônoma, em observação.
- Fluxo de ticket: canal automatizado via issue inter-org no Paperclip, com 2 aprovações do José (abertura do ticket e merge). Detalhes na conversa.
- Rodada 3: José aprovou o fluxo de ticket, as boas práticas e as fases. A ativação da core-eng (acionamento automático do CTO, orçamento, toolsets) vai para uma conversa separada. Próximo tema aqui: o auditor.
- Rodada 4 (auditor FECHADO): CTA conferido nos últimos 8 s; rubrica inclui "capa legível e coerente com o título" (imagem própria se o canal for parceiro, senão o melhor frame, definido via Camofox); avisos por um perfil Hermes `pqbr` no Telegram (allowlist, botões, dupla confirmação para merge e permissão, sem comandos livres). Discord fica como opção futura.
- Rodada 5 (07/10 23h): o Drive já está previsto (drive_client.py, disco local só como cache). Propor 8 pastas mais 00_Biblia_Visual e confirmar a cota da conta juniormoedavirtual. Hoje o áudio vem embutido no vídeo do NotebookLM; áudio separado fica só como expansão futura.
- Personagens: 2 protagonistas (masculino e feminino) e 2 coadjuvantes, num tom levemente cômico; atenção à diferenciação, já que stickmen são muito parecidos.
- A biblioteca de cartões (objetos, ambientes, animais) é criada sob demanda, por roteiro, e reaproveitada.
- A pesquisa e a criação dos cartões são delegadas ao NotebookLM para economizar tokens, sempre em caderno temporário, nunca no raiz.
- Rodada 6: José aprovou a reestruturação do Drive (8 pastas + 00_Biblia_Visual). Pediu os cartões iniciais de teste já nesta conversa: o que for aprovado será reaproveitado. Liberou o uso da conta jv e a clonagem do caderno raiz para testes (o raiz em si fica intocado).

---

## 08/10/2026 e 09/10/2026 (registro original do servidor)
- Bíblia visual v002 aprovada (Zé, Lia, Valdemar, Sandra, AMB-001, OBJ-001).
- Estratégia: fichas no Drive em 00_Biblia_Visual; catálogo no Supabase (tabelas visual_assets e episode_assets); wiki/galeria gerada automaticamente a partir da tabela; o roteirista lista as entidades da cena; um resolvedor sem LLM injeta só as fichas necessárias no caderno temporário; ficha que falta é criada na hora.
- SEM aprovação bloqueante: a ficha nova entra em uso imediatamente e José recebe só um aviso. Ele pode verificar quando quiser: "Verificado", ou "Não Aprovado" com observação. "Não Aprovado" abre ticket e a ficha é refeita (vale para os próximos vídeos). O vídeo publicado só é despublicado e refeito se José pedir; correção leve vale só para os próximos.
- Interface de verificação: botões no Telegram e status/issue no Paperclip, sincronizados pela mesma tabela.
- Interface de verificação: prever no futuro um plugin do Paperclip (sem mexer no código-fonte) ou um painel próprio da produção PQBR.
- NOME: a organização se chama "PQBR". Os documentos explicam a sigla (Porquê BR); o nome do canal tem o "porquê" por extenso. Ajustar no blueprint final.

## Pauta pendente (registrada pelo José em 08/10, encaixar sem repetir)
1. Regra canônica: proibição de temas repetidos. Mesmo que o usuário sugira um tema repetido, o sistema recusa e avisa ou abre ticket informando que o tema já foi abordado.
2. Interação do usuário: quem recebe e como são tratadas as sugestões sobre temas, fluxos, processos e regras; quem tem permissão para alterar o quê.
3. Agente do Telegram: vem do Paperclip ou direto do Hermes? Qual o papel do perfil Hermes (pqbr) no processo? Um agente que converse com o José sobre fluxo, sugestões e alterações.
4. Instabilidade atual (incidente de 08/10): o fluxo não iniciou sozinho. O rede respondeu com a grade do dia 7 e disse que já estava tudo publicado; a nova grade do dia 8 tinha 3 de 4 temas repetidos e só foi corrigida após a segunda cobrança, mesmo com Pydantic v2 já em uso. Exigência: garantir início automático, grade do dia correta e não repetição de forma determinística, com autonomia máxima e intervenção humana mínima.
- ESTABILIDADE (aprovado): agendador do sistema operacional com horários fixos mais um vigia de prazo; grade gerada por código a partir da data e gravada no banco; tema repetido barrado em 3 barreiras; máquina de estados com checkpoint e "publicado" só com o ID confirmado; agente responde sempre pelo banco; relatório diário e corte só após vários dias sem falha.
- INTERAÇÃO (aprovado): @pqbr-assistente no Hermes pqbr pelo Telegram, registrado na org PQBR; só consulta, roteia e responde (perguntas, temas, propostas de regra para o @prod-director ou ticket para a core-eng, verificação). Permissões: José altera regras canônicas e aprova merges; @prod-director altera parâmetros operacionais; core-eng altera código e infraestrutura por ticket.
- @prod-analista (aprovado): coleta diária por código via YouTube Analytics API (OAuth, só leitura; app do GCP publicado em produção para uso interno, para o token não expirar; Camofox no Studio como reserva). Análise semanal ou por anomalia; propõe ajustes ao @prod-director e salva os aprendizados no Hindsight; só observa até ~30 Shorts/90 dias.
- Após a decisão 10, José tem mais questões a lançar.
- CAMADA DE DECISÃO (aprovado): uma interface única decide() no código, com provedor trocável. Começa com o TypeSafe Jev (API já liberada; José informou US$ 0,042/1M tokens), só texto: tema repetido (barreira 2), roteamento do assistente, correspondência de fichas, checagens objetivas do auditor sobre a transcrição, gravidade de tickets, notas do analista. Troca para a OpenAI Decisions (gpt-6-luna) se precisar de imagem. Calibrar os limites de confiança com casos reais; confiança baixa escala para um LLM ou para o José. Roteiro, ideação e SEO continuam em LLM.

## DELEGAÇÃO AO NOTEBOOKLM / GEMINI WEB (t184–t186, 08/10/2026), aprovado
- Ideação, roteiro, SEO e pesquisa ficam com o NotebookLM (caderno efêmero), e o Gemini Web é a reserva. Os agentes só orquestram: entregam o conhecimento, reforçam com pesquisa própria, extraem a saída por código, validam com Pydantic, checam com o Jev e acompanham com observabilidade.
- Monitor do notebooklm-py: rotina semanal lê releases e CHANGELOG; o Jev julga se a mudança afeta o fluxo e a urgência; se afetar, pede autorização ao José no Telegram; com autorização, abre ticket para a core-eng (atualiza numa worktree, smoke test num caderno temporário, versão fixada, rollback para a anterior). Nunca atualiza sozinho.
- Atualização inicial 0.8.2 -> 0.8.4 recomendada: correções de autenticação e o medidor de uso.
- Limites do Pro: medidor de computação com janela de 5 h e teto semanal (Pro = 4x o padrão), mais os limites por recurso (500 chats/dia, 20 vídeos/dia, 2 cinematográficos, 300 fontes por caderno, 500 cadernos). Sem custo por uso.
- Medidor de saldo: o notebooklm-py 0.8.4 já tem `notebooklm usage` (e `--json`, `--categories`), com o percentual usado e restante nas janelas de 5 h e semanal, horário de reset, ações sem saldo e custo estimado por ação (ADR-0037, ListQuotaSummary). Só funciona se a conta estiver no grupo com medição ativa; caso contrário, usa contagem própria e os erros tipados de cota (retry_after_seconds).
- Monitor de consumo desde o dia 1: `notebooklm usage --json` antes e depois de cada geração, gravado no Supabase; relatório diário junto com a produção; acima de 80% numa janela, o agendador espaça as próximas produções.
- Camofox fica (inegociável). Mouse humano, colar texto longo, digitar texto curto com cadência humana. O Jev entra na navegação só para perguntas pontuais sobre o texto/DOM da página. Não acelera ações: o ritmo é da camada do Camofox.
- Orçamento (decisão 10): o teto mensal será definido com dados do monitor após a primeira semana.

## INSTALAÇÃO EXCLUSIVA DO NOTEBOOKLM-PY PARA A PQBR (t187–t188, 08/10/2026), aprovado em princípio
- José decidiu abortar a instalação global e deixar uma instalação exclusiva para a PQBR.
- Mapeamento só de leitura no host pc: uma única instalação global (pipx, 0.8.2, usuário pc), usada pelo Porquê BR atual (Hermes `rede` + cron */15 de `auth refresh`, perfil default = juniormoedavirtual) e pelo MP32 (mp32-worker + keepalive, NOTEBOOKLM_HOME=~/.mp32/notebooklm, perfil tutibom10). Paperclip, core-eng e configs MCP não usam.
- Riscos: versão compartilhada com o MP32; dois escritores na sessão do Porquê BR (cron e agente rede, mais cópia de cookies Camofox<->NotebookLM nas skills); perfil velho juniormoedavirtual dentro do ~/.mp32; 55 erros no refresh.log (CSRF/DNS); nota errada no .env.example do MP32.
- Plano (TAREFA DE MIGRAÇÃO da fase de desenvolvimento no blueprint, não ticket; tickets são só para produção; cada passo com autorização, critérios de aceite e rollback): (1) venv da PQBR com 0.8.4 fixada, NOTEBOOKLM_HOME=/home/pc/.pqbr/notebooklm, perfil pqbr, login novo, testes só em caderno clonado; (2) serviço único da PQBR dono da sessão (refresh por timer, fila de uma tarefa, usage --json no banco); (3) MP32 com instalação própria fixada em 0.8.2 e caminhos ajustados; (4) skills do rede aposentadas ou apontadas para o serviço, sem cópia de cookies; (5) remover o pipx global por último, manter ~/.notebooklm por 7 dias, backup do crontab, rollback documentado.
- (t191) Na fase da migração, antes do login no notebooklm-py exclusivo da PQBR, deslogar a sessão antiga do Porquê BR (cron de refresh e agente rede) para não haver chamadas de mais de um dispositivo. Interromper a produção atual nesse momento está autorizado por José. Até lá, nada muda.

## SESSÃO DO YOUTUBE STUDIO E MONITOR DE ATUALIZAÇÕES AMPLIADO (t194–t196, 08/10/2026), aprovado
- Causa provável das quedas no Studio: cookies copiados do Chrome para o Camofox (dois navegadores, mesmo login) e/ou identidade de aparelho do Camofox mudando entre reinícios (verificar).
- Camofox (camofox-browser, que roda o Camoufox por baixo) é o único dono do login do Studio no perfil `porquebr`. Login manual inicial pelo plugin VNC/noVNC do próprio Camofox, aberto na tela XFCE do servidor (José acessa via RustDesk) ou pelo navegador local do servidor; noVNC fica preso ao localhost/Tailscale com senha e é desligado fora da hora do login. Sem Camoufox separado.
- Guardião determinístico da sessão (código, timer ~20 min com variação): testa Studio, Gemini Web e NotebookLM; checagem extra ~30 min antes de cada publicação; escada de recuperação (renovar no Camofox -> sincronizar cookies do Chrome como reserva -> login manual via noVNC com aviso no Telegram); publicação fica em espera e retoma sozinha. Se uma renovação falhar: aviso no Telegram + ticket automático. O agente só observa; age apenas com roteiro pronto quando a escada esgota.
- Monitor de atualizações ampliado: mesmas regras do notebooklm-py (Jev julga relevância, José autoriza, versão fixada, teste em ambiente isolado, rollback) para Camofox/camofox-browser, Camoufox, Paperclip, Hermes, FFmpeg, Whisper, Pydantic, Supabase CLI, Jev SDK e demais dependências da PQBR.

## OBSERVADOR DE CONFORMIDADE — @prod-compliance (t192 ponto 1, aprovado t198)
- Risco principal: desmonetização por "conteúdo inautêntico" (política esclarecida jul/2026: conteúdo repetitivo/templated, "mesma situação, mesmo desfecho"; IA dando conselho especializado). Rito: aviso no Studio → 7 dias p/ recurso → saída do YPP, reaplicação após 90 dias. Diretrizes da comunidade: aviso único → strikes (3 em 90 dias = encerramento).
- Coleta determinística (código), agente só analisa:
  - E-mail da conta do canal (juniormoedavirtual): e-mails do YouTube; Jev classifica gravidade.
  - Studio via Camofox (só leitura, ritmo humano): coluna Restrições/Avisos, Status e recursos do canal, aba Monetização, notificações (inclui rótulo de IA automático).
  - YouTube Data API: status por vídeo (rejeitado, bloqueado, privado forçado, restrição regional).
- Gravidade: informativo → relatório diário; atenção (claim, anúncio limitado) → Telegram + lição para roteiros; crítico (aviso/strike, aviso de inautêntico, remoção) → HOLD automático da fila + Telegram + ticket + prazo de recurso monitorado; agente prepara rascunho de recurso, José envia. Agente nunca recorre, apaga ou altera sem dupla confirmação do José.
- Prevenção: item de conformidade no auditor pré-publicação (variedade vs. vídeos recentes em situação/desfecho/estrutura; sem tom de especialista em saúde/direito/finanças/política; direitos de áudio; marcação de IA decidida por upload, normalmente "não" para stickman). Checagem de advertência ativa antes de cada horário de publicação. Relatório semanal de variedade do canal.
- Fontes: support.google.com/youtube/answer/1311392 ; techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/ ; support.google.com/youtube/answer/9890437 ; support.google.com/youtube/answer/14328491

## GRADE DIÁRIA DE TEMAS EM ALTA (t192 ponto 3, proposta t198, mistura aprovada t199)
- Coleta por código de madrugada (YouTube Data API: em alta BR + Shorts mais vistos 24–48h com termos do escopo) → caderno diário de tendências (separado do raiz, limpo diariamente) → NotebookLM Deep Research focada no YouTube (1/20 diárias) filtra para sátira stickman de costumes BR → filtros em código (barreiras de repetição, variedade do compliance, exclusões sensíveis) → grade no Supabase com pontuação e fonte → script da grade consome.
- Mistura aprovada: ~70% temas em alta / ~30% perenes do banco.
- Em avaliação (t199): agent-reach, Firecrawl e skills da comunidade para comentários/dores; tema "limiar" (ex.: sinal amarelo) como referência de engajamento.
- APROVADO (t200) — Comentários e pontuação de polêmica:
  - Rejeitados: agent-reach (cookies/risco de ban, sem TikTok, falhas de segurança abertas), Firecrawl (recusa redes sociais), PostPlus youtube-research (intermediário pago), apidojo comments/trending skills (Apify pago, mal mantidas), ClawHub youtube-keyword-research (só prompt). Reserva paga opcional: actor Apify de comentários chamado direto (~US$25/mês, só se precisar). yt-dlp sem login como reserva, nunca com cookies do José.
  - Fonte fase 1: só YouTube, API oficial (commentThreads.list 1 unidade/página de 100). 100–200 comentários × 20–30 vídeos virais/dia + nossos vídeos para calibrar (~50 unidades/dia). Atenção: search.list tem limite próprio de 100 chamadas/dia.
  - Pré-processamento em código: anonimizar autores, remover spam/emoji/duplicatas, marcar perguntas, reclamações e discussões.
  - Resumo diário de comentários (≤ ~300) como fonte no caderno de tendências; NotebookLM agrupa dores "por que o brasileiro…" ranqueadas por nº de vídeos distintos.
  - Pontuação de polêmica 0–100 em código (comentários/visualização, respostas/comentário, velocidade, nº de vídeos, termos sensíveis): faixa-alvo 50–75; >75 aguarda aprovação do José; bloqueio absoluto: política partidária, tragédias, religião, grupos protegidos, conselho de saúde/finanças/jurídico, incentivo a ato ilegal/perigoso. Satirizar, nunca incentivar. Recalibrar após 2–4 semanas com @prod-analista + compliance.
  - Supabase guarda só agregados; brutos apagados após N dias (verificar política de retenção de dados da API do YouTube antes de fixar N).

## FASE DE VALIDAÇÃO ANTES DA PRODUÇÃO (t202–t208)
- Fica entre a construção e a produção. A core-eng só libera a produção quando cada item cumpre o seu critério de aceite.
- **Os 7 itens:**
  1. **Contrato editorial:** público, promessa e tom de identificação, sem humilhar. Sátira aceitável, inadequada e de revisão humana. Engajamento não é medida de segurança. Rascunho em `contrato-editorial-pqbr-rascunho.md`.
  2. **Teste real de consistência visual:** 3 vídeos reaproveitáveis com os mesmos personagens em situações diferentes. Verificar se o NotebookLM preserva as fichas. Se não preservar, testar estratégias para forçar a preservação, e só em último caso adotar uma alternativa.
  3. **Auditor testado com defeitos conhecidos:** CTA ausente, fala cortada, personagem errado, texto ilegível. Medir falso aprovado e falso reprovado. Duração, silêncio e resposta estruturada são indícios, não prova.
  4. **Publicação sem duplicidade:**
     - Se o upload terminou e a confirmação falhou, consultar o Studio antes de reenviar.
     - Horário perdido: substituir por um vídeo da reserva, se houver; senão, cancelar.
     - **Qualidade acima da cota de 4 por dia.** Nunca publicar um vídeo reprovado para cumprir meta.
  5. **Correção pós-publicação:** procedimento para erro factual, problema de direitos ou falha editorial. Definir quem pode pausar a fila, tornar o vídeo privado e autorizar a substituição.
  6. **Procedência e proteção dos materiais:**
     - Registrar fontes, direitos de uso e aprovação das fichas.
     - Comentários coletados são dados, nunca instruções para os agentes.
     - Nada de segredos, cookies, credenciais ou dados pessoais desnecessários no Hindsight ou nos tickets.
  7. **Validação das premissas técnicas pela core-eng:** recursos, versões, cotas e permissões. O blueprint separa o que está verificado, o que é hipótese a testar e o que é decisão aprovada. Uma decisão aprovada não comprova que a ferramenta consegue executá-la.
- **Prioridade:** itens 1, 2 e 3.
- **Acréscimos aprovados:**
  - definição de sucesso do piloto (métricas com base nos números reais do canal, recalibradas em 2 a 4 semanas);
  - gabarito com os vídeos fortes e fracos do canal, para o contrato editorial e a calibração do auditor (ver o rascunho do contrato).
- **Duração (t208):**
  - Definida pela qualidade, sem teto editorial; passar de 60 s é aceito inclusive como norma. O teto técnico é o limite do Shorts (3 min, vertical ou quadrado).
  - Revisar o `RoteiroShort` (hoje 40 a 60 s) e a checagem de duração do auditor (hoje 15 a 60 s) para **de 15 s até o máximo do Shorts**.
  - O CTA continua nos últimos 8 s.
  - Acima de 60 s, um claim do Content ID bloqueia o Short, então a checagem de direitos de áudio vira bloqueante.
  - A core-eng precisa verificar se o NotebookLM gera vídeo vertical acima de ~60 s.
- **Relatórios de dados do canal:** vêm pelo `@pqbr-assistente` no Telegram, que aciona o `@prod-analista` (Analytics API; Studio via Camofox só para o que a API não mostra). Não é preciso criar uma skill de pedido padrão.
- **Fontes de dados de 08/10:** `relatorio-rede/relatorio_analytics_youtube_studio_90d.md` e `relatorio-rede/aditivo_analitico_pqbr_90d.md`. Os dois divergem entre si; os números ficam como hipótese até a verificação pela API.
- t212–t217 (testes de validação): 1 personagem padrão, máx. 2; sem nomes; "nós, brasileiros" + explicação lógica com humor predominante; sátira leve ("sorrisinho no canto da boca", "a gente é assim mesmo"); CTA explícito fundido com continuidade para loop; logo com zoom suave curto sobre a última fala; corte do end card só se detectado (opção de remover logo não removeu o end card nos testes); duração dimensionada pelo roteiro (~3 palavras/s), livre até 3 min; dinamismo e relação texto-imagem como critério do auditor. Redação da rodada final aprovada. Roteiros de referência (TV, sinal amarelo, controle remoto/fita, tomada do chuveiro) a pedir ao rede.

## AUDITOR — correções de papel (t228–t230, 08/10 ~21:16 PT)
- O Jev só devolve decisão estruturada (sim/não, classificação, JSON). Não redige texto. No auditor, ele cuida das checagens de texto sobre a transcrição: o loop emenda, a frase final está cortada, o tom está ok, aparece nome. O relatório é montado por código com modelo fixo (veredito, motivo, ID da cena).
- O Qwen (Alibaba) fica fora por enquanto. O juiz visual é o Gemini web (jvmendesjr) para os testes.
- Regra de trabalho: antes de atribuir um papel a qualquer componente, conferir a ficha dele no blueprint.

## ITEM 3 FECHADO (t232, 08/10 ~22:06 PT)
Auditor aprovado: o código extrai um quadro por cena e a transcrição (Whisper). O Gemini 3.8 Flash (modo normal; o "Flash Estendido" recusa as pranchas) responde só sim/não por traço, em 2 rodadas; uma divergência vai para revisão do José. O código aplica a tabela leve/grave e decide. Loop, CTA, nomes e fala cortada são checados por texto (o Jev pode assumir, com resposta estruturada). O relatório é montado por template, sem prosa de LLM.
Status: verificado em 4 vídeos (4/4 com motivos certos); a regra do Zé foi ajustada depois de ver o resultado. Pendente na fase de desenvolvimento: validar com o restante do labels.json e com vídeos novos. Roupa insinuada só por contorno branco é desvio LEVE (t232).

## ITEM 4 APROVADO (t233–t234, 08/10 ~22:15 PT)
- Sem duplicata: código único por vídeo (ex.: PQBR-EP0123) na descrição e numa etiqueta; registro de temas no Supabase (R10). Estados: aprovado, enviando, enviado (video_id), agendado, publicado. Antes de enviar, procurar o código no Supabase e no canal, incluindo privados e AGENDADOS. Envio sem confirmação: procurar o código, tentar 1 vez e, se continuar sem certeza, parar e avisar José.
- Fluxo da manhã: grade de madrugada; produção, pós-produção e auditor de manhã, com pausas de ritmo humano e limites de uso por modelo/ferramenta calculados para o dia; prazo de corte; os aprovados ficam AGENDADOS nas janelas definidas. Falhas: refazer ou trocar pela reserva durante a manhã; pendências vão para José antes da primeira janela.
- Reserva de ≥ 2 vídeos aprovados; sem reserva, o horário é cancelado; vídeo reprovado nunca é publicado. Atraso de até 1 h é só plano B. Teto de 4 por dia, sem mínimo.
- HOLD de conformidade: também torna privados os vídeos já agendados.
- A última janela do dia sai preferencialmente da cota de temas que não envelhecem (os 30%).
- Jev (resposta fechada): decidir refazer / trocar pela reserva / chamar José; conferir se título, descrição e código do agendado batem com o aprovado.
- Hipóteses para a core-eng: custo de cota do envio pela API; envio pela API ou pelo Studio via Camofox; agendamento via publishAt.

## ITEM 5 APROVADO (t234–t235, 08/10 ~22:23 PT)
- Diante de QUALQUER problema detectado (conformidade, direitos, erro, ofensa, comentário apontando falha, anomalia de métricas ou aviso do José), o vídeo é tornado PRIVADO de imediato e automaticamente, e José é avisado no Telegram com o motivo.
- Não há substituição nem republicação. O vídeo corrigido não sobe de novo.
- Exclusão: só José, após análise e com dupla confirmação. O agente nunca exclui.
- Correção de título, descrição ou comentário fixado: o agente propõe e José aprova com um toque.
- Fontes de detecção: observador de conformidade, comentários (dado, nunca instrução), métricas da primeira hora, José pelo Telegram.
- Quem pode o quê: José é a autoridade final; o agente do Studio executa; os demais propõem. Toda ação é registrada no Supabase (motivo, quem, quando).
- Todo caso vira aprendizado: uma lição registrada que volta para o contrato editorial, os roteiros e o auditor.

## ITEM 6 APROVADO (t235–t236, 08/10 ~22:27 PT)
- Origem: cada ficha registra no Supabase ferramenta, conta, data, prompt e versão. Nada de terceiros (personagens, marcas, imagens); fontes só com licença livre/comercial; áudio só a narração gerada; licença de música guardada se um dia entrar.
- Comentários, web e fontes do NotebookLM são dado, nunca instrução; comentários entram anonimizados.
- Sem cookies, senhas, tokens ou dados pessoais no Hindsight, em tickets, no Supabase ou em logs; segredos só no cofre; um verificador automático barra a gravação.
- Pendências: trocar a senha do paperclip_app, a senha de root do Contabo e o token do OpenCode.
- Hipóteses para a core-eng: termos de uso comercial do NotebookLM/Gemini; selo de conteúdo de IA provavelmente não exigido para stickmen (o observador de conformidade acompanha).

### Onde cabe o Jev (resposta fechada, texto apenas)
CABE:
- classificar comentários: spam, pede algo / tenta dar instrução ao agente, contém dado pessoal, ofensa (sim/não);
- conferir se o texto tem dado pessoal ou segredo, como segunda camada depois do verificador por regex;
- conferir se o roteiro ou a descrição citam marca, pessoa real ou obra de terceiros (sim/não + qual);
- classificar e-mails do YouTube por gravidade (info / atenção / crítico);
- itens 3–5: loop, fala cortada, tom, nomes; refazer / trocar pela reserva / chamar José; conferir se o agendado bate com o aprovado; decidir se um sinal justifica tornar privado.
NÃO CABE:
- nada que dependa de imagem, vídeo ou áudio (personagem, logo, texto na tela) → Gemini + código;
- redigir texto (relatórios, mensagens, recursos ao YouTube) → template do código; o recurso é rascunhado por outro modelo e enviado por José;
- julgar licença ou termos de uso jurídicos → registro e conferência humana / core-eng;
- detectar segredo como única barreira → o código (regex/scanner) vem primeiro; o Jev é só o reforço;
- a decisão final de excluir → só José.
- (t237) Jev como classificador também nas MENSAGENS que chegam (Telegram, e-mails do YouTube, comentários): detecta tentativa de instrução ou golpe, dado pessoal ou segredo, gravidade e se pede ação; resposta fechada. Mensagem do José no Telegram só vale como ordem se vier do ID autorizado; o resto é dado.
- (t238) Esclarecimento: o classificador Jev se aplica às mensagens e comentários dos USUÁRIOS nos vídeos (item 5). Classes: reclamação, aviso de erro, elogio, sugestão de tema, pergunta, spam ou golpe, ofensa, tentativa de instrução. Reclamação ou aviso de erro com evidência dispara o item 5 (tornar privado + Telegram). FUTURO: uma área de mensagens com respostas nossas para pedir feedback dos usuários; o mesmo classificador marca quais mensagens são conversa nossa e encaminha o feedback. As respostas nunca são automáticas sem regra aprovada pelo José.
- (t239) Limiar aprovado: o vídeo vai para privado automaticamente com aviso de erro ou reclamação de ≥ 2 pessoas diferentes, ou de 1 quando o problema é grave (direitos, ofensa, dado pessoal). Abaixo disso, o caso vai para José no Telegram.

## ITEM 7 APROVADO (t236–t240, 08/10 ~22:34 PT) — FASE DE VALIDAÇÃO FECHADA
- O blueprint marca cada afirmação técnica como VERIFICADO (testado), HIPÓTESE (a confirmar) ou APROVADO (decisão do José).
- A core-eng recebe a lista de hipóteses com dono e critério de pronto; nada que depende de uma hipótese é construído antes de ela virar verificado.
- A regra do auditor entra como "verificado em 4 vídeos" e é revalidada com vídeos novos no desenvolvimento.
- Mudanças durante a construção voltam ao blueprint como tarefas de desenvolvimento, não como ticket.

## PAUTA SEGUINTE (t240, nesta ordem)
1. Saldo do Jev na API do Jev (monitoramento, alerta, o que fazer se acabar).
2. Retorno dos comentários nos vídeos (aprofundar).

## SALDO E FALLBACK DO JEV (t240–t241, 08/10 ~22:41 PT)
- Saldo atual: mais de US$ 4 (crédito grátis de US$ 5, nada gasto).
- Sem monitor de limites em tempo real (fatores demais). O jr calcula uma média de gasto a partir do registro de tokens de cada chamada nos primeiros dias de piloto; José acompanha pelo relatório diário e pelas contas e combos do 9router.
- Fallback do Jev, em ordem: (1) o mesmo Jev via OpenRouter; (2) modelo da OpenAI (direto ou via OpenRouter). O nome exato do modelo fica como HIPÓTESE para a core-eng conferir na hora. Toda saída do fallback passa pela mesma validação de esquema (Pydantic) e nunca muda o formato da resposta.
- Teste de resposta antes de agir: antes do lote da manhã e antes de cada ação crítica (agendar, tornar privado), o código faz uma chamada mínima a cada modelo e ferramenta usados (Jev, Gemini, NotebookLM, Supabase). Sem resposta no prazo ou com resposta inválida, segue a escada de falhas.
- Escada de falhas (regra já registrada no dossiê, aplicada a modelos, Supabase e 9router): backoff 30 s → 2 min → 8 min; rede fora fica em NETWORK_WAITING sem gastar tentativa; cada nova tentativa usa estratégia diferente (outro provedor/combo); a mesma ação falhando 2 vezes vai para José; 5 chamadas idênticas disparam parada; idempotência antes de cada passo; varredura de recuperação no reboot.
- Supabase fora: proposta de buffer local (fila em arquivo, gravação atômica) e de não agendar nem tornar público nada sem gravar o estado; a sincronização acontece quando o Supabase voltar. APROVADO (t242).
- (t243) APROVADO: leitura de comentários pela API de dados do YouTube (OAuth do analista, sem Studio): a cada 30 min nas primeiras 48 h, a cada 6 h até 7 dias, depois diária; cada comentário passa pelo classificador do Jev e é gravado no Supabase com o código do vídeo. Antes de seguir, José pediu uma pesquisa de boas práticas da comunidade e da indústria sobre moderação e retorno de comentários com classificador.
- (t243 pesquisa) Resultado em testes/2026-10-08/auditor/PESQUISA-comentarios-boas-praticas.md. Mudanças aceitas para análise: multirrótulo + alvo + ironia possível; pessoa distinta exclui canal, spam, imitação e textos quase iguais; grave só sobre o vídeo; ler também comentários retidos e de provável spam; pré-filtro de links/WhatsApp/Telegram/PIX e Unicode; 2 rodadas do Jev só no que gera ação; conjunto pt-BR para medir antes de ligar ações; autor como hash e texto bruto apagado em até 30 dias; Camofox só para ações (não lê comentários); rejeitar comentário = só José.
- (t244) APROVADO: o agente pode RETER sozinho (heldForReview, reversível) comentários de golpe, contato externo, conta imitando o canal, dado pessoal ou ofensa a outra pessoa.
- (t245) APROVADO: vídeo tornado privado por engano volta a público só com um toque do José (mesmo vídeo e link, não conta como republicação); o agente nunca faz isso sozinho.
- (t244) José quer resposta e reação automáticas a todos os comentários não críticos, com variação para não parecer robô; só críticos vão para ele. (t245) Novo agente @prod-comunidade. Pesquisas: PESQUISA-comentarios-boas-praticas.md §8 e PESQUISA-agente-comunidade.md.
- PROPOSTA (aguardando José): respostas via API comments.insert (50 un.), Jev só diz se é elegível e o tipo; o código escolhe de um banco de 60 frases (5 tipos × 12) aprovado pelo José; não repete no vídeo nem nas últimas 30; atraso de 15–120 min, 3–12 min entre respostas, teto de 6/h e 30/dia, 1 por autor por vídeo, das 08h às 22h; ficam de fora reclamação, erro, pergunta, golpe/spam/ofensa, PII/link, ironia possível, tema sensível, possível criança, retido, mais de 7 dias; confere em 60 min se a resposta sumiu e, se sumiu, para; kill switch manual (/pausar_respostas) e automático; 7 dias em sombra. Coração NÃO existe na API (só pela interface, ou seja, Camofox). Sem agente pronto nos templates; persona própria em pt-BR a partir de donchitos community-manager + customer-service.md + developer-community-builder + feedback-synthesizer; skills-base support-ticket-triage, developer-community-moderation, youtube-comments-to-ideas.
- (t247) APROVADO: coração pelo Camofox, até 10 por dia, só na sessão já aberta pelo guardião, abortando ao menor sinal de problema. HIPÓTESE a testar no início do dev: comments.insert (escopo youtube.force-ssl, 50 un.) funciona no app sem auditoria; fazer 1 resposta real de teste antes de ligar o automático.
- (t248) APROVADO: 3 dias em sombra antes de ligar respostas e corações automáticos (ou ~30 respostas simuladas aprovadas sem correção, o que vier primeiro).
- (t249) APROVADO: o NotebookLM rascunha as 60 frases (5 tipos × 12) no tom do contrato editorial e José aprova; tarefa da fase de desenvolvimento. Pendente: confirmar que o @prod-comunidade não torna vídeo privado por conta própria (só sinaliza; quem executa é a regra do item 5).
- (t250) APROVADO: o @prod-comunidade só sinaliza; quem torna privado é a regra do item 5 no código. TEMA RETORNO DOS COMENTÁRIOS FECHADO. Próximo: retomar a sequência anterior (pedir ao rede roteiros/transcrições/prompts de TV, sinal amarelo, controle remoto e tomada do chuveiro; refazer V2 opcional; cota e nomes no Drive; teto de orçamento; blueprint pela core-eng).
- (t262) APROVADO: chamada final padrão = apenas "Segue o Porquê BR", curta e colada ao gancho para fechar o loop; substitui a frase longa atual. O pedido de comentário, se usado, vai para a descrição ou para o comentário fixado, não para a narração. Atualizar contrato e steering/SOP no desenvolvimento.
- (t263) APROVADO: neste canal NÃO se pede comentário explicitamente (nem na narração, nem na descrição, nem no fixado). Próximo: fechar o V2 'último pedaço'.

## REVISÃO DA TOLERÂNCIA DE IDENTIDADE (t264, 09/10 09:56)
- José: o jr estava rigoroso demais. Personagens coloridos, variação de personagem e mais de 2 em cena são ACEITÁVEIS. A consistência do elenco é buscada (prompts e referências), mas não reprova vídeo.
- O que importa: mensagem, estilo literário, vídeo e imagens dinâmicos, áudio bom e resultado. O canal funciona como "múltiplas vias".
- Padrão desejado: até 2 personagens; mais que isso não reprova.
- Consequência: a tabela LEVE/GRAVE de identidade do item 3 deixa de reprovar por cor, roupa, troca de personagem ou quantidade. O auditor passa a registrar a aderência ao elenco como métrica (não como trava). Ficam como trava: narração, loop, CTA "Segue o Porquê BR", sem pedido de comentário, cortes de fala, nomes, conteúdo de terceiros e segurança. A definir: se estilo 3D ou realista continua sendo trava.
- V2-r3: a1 (sem personagem) e a2/a3 reavaliados por este critério na sequência.
- (t265) APROVADO: 3D ou realista nunca será pedido, mas se vier assim pode aprovar. Nenhum critério visual de estilo reprova; o que reprova é faltar a ironia e a sátira leve e cômica do dia a dia, das manias e rotinas dos brasileiros, além das travas de texto, áudio e segurança. V2-r3 a3 = aprovada pelo critério novo (ressalva: CTA escrito na tela).
- (t266) Drive: conta Pro com 5 TB; cota não é restrição.
- (t267) APROVADO: estrutura do Drive PQBR/ (00_Biblia_Visual, 01_Contrato_e_SOP, 02_Episodios/AAAA-MM/PQBR-EPxxxx_tema, 03_Reservas, 04_Privados_Revisao, 05_Relatorios, 99_Arquivo). Prioridade: disco do servidor livre; o servidor é só temporário. TUDO sobe para o Drive, inclusive a versão original (bruta do NotebookLM) e a editada (pós). Depois de confirmar o upload (tamanho/hash), o arquivo local é apagado.
- (t268) Teto de orçamento: definido após os testes dos primeiros dias. Ciclo do vídeo: assim que o final fica pronto, sobe para o Drive junto com o original; o final fica no servidor até o upload ao YouTube ser confirmado (código PQBR-EPxxxx no canal) e então é apagado do servidor. Limpeza de Drive e servidor de intermediários quando a cópia final estiver pronta.
- (t269) Sanitização periódica do Drive: detectar duplicatas (mesmo hash/tamanho ou mesmo código PQBR-EP) e itens órfãos; move para 99_Arquivo/_duplicados e lista para José; exclusão definitiva só após confirmação dele.
- (t270) APROVADO: limpeza do Drive por script determinístico na rotina noturna do @prod-director; resultado no relatório diário e Telegram; exclusão só pelo José. Próximo: pacote de entrega à core-eng.
- (t271) APROVADO: duração de 15 s a 3 min, alvo de ~50 s; contrato do roteiro e auditor seguem essa faixa.
- (t272) APROVADO: escada de sessão = Camofox renova → login manual pelo noVNC (Telegram); cópia de cookies do Chrome só como último recurso e com OK do José.
- (t273) APROVADO: publicação pela API do YouTube (videos.insert com agendamento); Studio via Camofox de reserva. HIPÓTESE H1: auditoria do app para upload público; até lá, sobe privado e o Camofox agenda.
- (t274) APROVADO com ajuste: limite é 1 resposta por pessoa POR VÍDEO (pode responder a mesma pessoa em vários vídeos); ressalvas: frase diferente para a mesma pessoa (não repetir as últimas usadas com ela) e intervalo mínimo de ~24 h entre respostas à mesma pessoa; demais limites mantidos. Correção do §7 da entrega.
- (t280) Repositório criado por José: https://github.com/jvmendesjr/PQBR (privado, vazio). GitHub conectado na core-eng pelo conector do Paperclip em 09/10 11:19. Tailscale Serve: Paperclip em https://<host-tailnet>:3100 (só tailnet); 443 livre por decisão do José. Core-eng NÃO usa perfis Hermes; José interage pelo chat do Paperclip. _(entrada que existia só na cópia do box; unificada em 09/10)_

---

## 09/10/2026, tarde: novos rumos (t281–t287 e t323)

- (t281) O Telegram fica com o perfil Hermes `pqbr`; o @pqbr-assistente roda lá.
- (t282) O Paperclip é **painel desde o início**: mostra o estado, não é o dono do fluxo.
- (t283) O Temporal é testado primeiro (arquitetura híbrida, pensada para vários canais); o DBOS é o plano B.
- (t284) A org core-eng fica **abortada por enquanto**; a saída do CTO (COR-1) **não é usada**. Arquivada fora do git no Drive (`PQBR/_arquivo-docs-2026-10-09/cor1-cto-2026-10-09.tar.gz`).
- (t285) As **regras aprovadas são o núcleo e não podem se perder**; a arquitetura se adapta a elas.
- (t286) **Tickets de manutenção agnósticos de agente:** qualquer agente de desenvolvimento pode pegar um ticket, acessar o código e corrigir, usando as memórias e o conhecimento do código guardados no Hindsight. Substitui o roteamento para a core-eng. Os agentes especializados da própria PQBR **pré-estruturam cada ticket** com a localização, a falha observada e as correções sugeridas. EM CONSTRUÇÃO — aguardando José: (a) se continuam as 2 aprovações do José por ticket (abertura e merge; o merge pelo José já é regra); (b) bank Hindsight separado para conhecimento de código.
- (t287) Arquivos de pré-construção (`docs/arquivo/`, `docs/pesquisas/`, este `DECISOES-LOG.md` e qualquer rascunho ou material legado) **nunca são consultados por agentes**; consultar exige aprovação explícita do José, porque podem ser mal interpretados e aplicados em produção.
- (t287a) Aprovada e aplicada a proposta de sanitização (`PROPOSTA-sanitizacao-docs.md`): estrutura `REGRAS / ARQUITETURA / PLANO / CONTRATO-EDITORIAL / DECISOES-LOG / pesquisas / arquivo`; levantamento de vídeos fora do git (Drive `PQBR/_arquivo-docs-2026-10-09/`), mantida só a lista de temas publicados (`db/seeds/temas-publicados.csv`).
- (t323) Dúvida ou conflito que não se resolve com certeza pelas decisões aprovadas **não é adivinhado**: fica marcado "EM CONSTRUÇÃO — aguardando José" e é listado para ele decidir.

## 09/10/2026, ~14:47: pendências resolvidas (t324–t326)

- Tickets de manutenção mantêm **duas aprovações do José**: na abertura (ele pode pedir correções no próprio ticket) e no merge.
- Hindsight: **um único bank por organização** (inclui memórias de código).
- **Dois bancos com papéis distintos:** Postgres próprio do Temporal = só estado de workflow (nunca consultado diretamente); Supabase = dados de negócio (temas/R10, vídeos/códigos, comentários, métricas, relatórios, base do painel e do analista). Supabase mantido (recomendação; confirmar no teste de 1 dia do Temporal). Supabase fora = retentativas duráveis do Temporal + outbox para o Supabase na volta; substitui a fila em arquivo da t242 (confirmar no teste).
- Alimentação do painel Paperclip: continua EM CONSTRUÇÃO; será demonstrada no teste do Temporal.
- **Padrão dos agentes pensantes** (director, analista, comunidade): rotina fixa executa tudo; os agentes observam e propõem mudanças só como saída estruturada validada por Pydantic v2; mudanças só se aplicam após aprovação do José.
- **Janelas de publicação:** 11:40, 14:40, 18:35, 21:15 (4 janelas; teto de 4 por dia, sem mínimo).
- **Ritmo da narração** para dimensionar o roteiro: 2,3 palavras/s (o modelo pode esticar ou acelerar).

## 09/10/2026, ~14:57: decisões t327 e t328

- (t327) Arquitetura: ligar o **Temporal** (fluxo determinístico) ao **Paperclip** (camada de agentes e painel). Os agentes vivem no Paperclip.
- (t327) Sem teto mensal de orçamento por enquanto: só monitoramento e levantamento de custos.
- (t327) Imagem que não corresponde à narração **não reprova** o vídeo (pode ser transição breve); não é critério estrito.
- (t327) Refinamentos da pesquisa de comentários (t243): os relatórios devem sinalizar situações excepcionais e avisar quando não houver números estatisticamente significativos.
- (t327) Desligamento automático das respostas só em reclamação muito grave, direitos autorais ou situação visivelmente grave; só esses casos escalam ao José. Tom nessas situações: sempre profissional, direto e formal; não absorve o espírito editorial (sem piada, ironia ou sarcasmo).
- (t327) Revisão humana só quando um item falha em todos os caminhos já previstos: fica num local dedicado do repositório para revisão, o José é avisado e o agente coleta a determinação dele: excluir, corrigir, reaproveitar ou arquivar. Resolve a "revisão humana antes da grade".
- (t327) Personas do compliance e do assistente: sérias, diretas, sem rodeios.
- (t327) Configuração do Studio: já definida. Visualização: já definida. (Ver t331–t332.)
- (t327) Escopo: só o canal PQBR por enquanto; outros canais estudados depois, com os aprendizados; cota da API para vários canais adiada.
- (t327) Metas do piloto: definidas depois.
- (t327) Perfil Hermes `rede`: pausado quando a PQBR estiver definida; usar o novo perfil `pqbr`.
- (t327) Juiz de imagem: Gemini web continua; sem Gemini API.
- (t327) Rotação de senhas/tokens: adiada para um segundo momento.
- (t327) R1–R9 continuam dependendo do contrato v2, salvo o que já estiver coberto.
- (t327) Criar `docs/ROADMAP.md` agnóstico de agente, com checkboxes, para qualquer agente retomar de onde o último parou.
- (t328) Seguir o conjunto completo de SDD: constituição (REGRAS §0–§3), `SPEC.md`, `ARQUITETURA.md`, tarefas no `ROADMAP.md`, `TESTES.md` e matriz de rastreabilidade (`RASTREABILIDADE.md`), sem duplicar conteúdo; desconhecidos marcados EM CONSTRUÇÃO.

## 09/10/2026, ~15:22: decisões t329–t332

- (t329) Teto de RAM do Temporal no `pc`: **1,5 GB** (Temporal + Postgres dedicado). Entra no aceite do TZ-01 e na ARQUITETURA.
- (t330) Confirmado: "só casos graves escalam ao José" vale apenas para respostas automáticas e interação com usuários nos comentários. Item 5 inalterado; polêmica > 75 continua aguardando o José.
- (t331) "Visualização" não era um item separado; não há pendência.
- (t332) Configuração do Studio: deve cumprir todas as REGRAS aprovadas; não há pendência separada.

## 09/10/2026, ~15:25: autorização t333

- (t333) José autorizou instalar e testar o Temporal no `pc` (F05-01, TZ-01..TZ-07): teto de 1,5 GB com limites de memória; só Postgres; portas só em localhost/tailnet; sem mexer em Tailscale Serve/Funnel nem em serviços existentes; escrita no Paperclip só com nova autorização. Resultado em `docs/sdd/adr-001-orquestrador.md`.

## 09/10/2026, ~15:47: autorização t334

- (t334) José autorizou um projeto de teste reversível no Paperclip para TZ-04/TZ-05, separado da core-eng. Agente de teste fica pausado salvo quando estritamente necessário. Se o agente de teste exigir `hermes_local` com `--yolo`, não executar e documentar o bloqueio. Sem restarts de serviços, sem mudanças de exposição. Reboot do servidor dispensado: o restart do motor cobre o TZ-02. Resultado e limpeza em `docs/sdd/adr-001-orquestrador.md`.

## 09/10/2026, ~17:05: t334 (complemento), t335, t336

- (t334/t335) José: **não mexer no código do Paperclip**; o adaptador `hermes_local` fica como está; F05-05 continua pendente.
- (t336) José aprovou seguir para a próxima fase do roadmap enquanto o soak de 24 h roda: base de dados e barreira de segredos (D3, D14). Escopo agora = **preparar**, sem gravar no Supabase e sem perturbar soak, Temporal, Paperclip ou outros serviços.

## 09/10/2026, ~17:21: t337–t338

- (t337–t338) José escolheu um **projeto Supabase novo e dedicado** ao PQBR (não o `paperclip`), na org dele (plano Pro por um ano); pode migrar para local depois, decidindo por projeto. Esquema `pqbr` fora da Data API; acesso só pelo `service_role`. As 2 repetições históricas da R10 foram aceitas como exceção.
- Condição: criar só se o custo fosse US$ 0. O `get_cost` da org informou **US$ 10, recorrência mensal**. **Projeto não criado**; aguarda decisão do José.
