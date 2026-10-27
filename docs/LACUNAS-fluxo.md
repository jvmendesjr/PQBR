# Lacunas: etapas feitas à mão em 12/10 → fluxo determinístico (José 17:18)

Regra (José 17:17): nenhuma etapa de fluxo à mão. Se o fluxo não está ativo: parar, registrar e consertar o fluxo. José usa o Telegram PQBR (Hermes `pqbr`) e a Temporal UI; aprovações são sinais do Temporal (t471/t474; o plano Discord/Paperclip de t464 foi revogado).

| # | Etapa manual hoje | Dono | Contrato Pydantic | Temporal | Agente → código → ferramenta | Instrução do agente (instructions-file:put) | Teste | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Temas via 9router fora do Paperclip (`repor_temas_sem_ponte.py`) | Líder Editorial | `PropostaAgente` / `PropostaBruta` (temas.py) | `ReposicaoTemasWorkflow` + agenda `pqbr-reposicao-temas` 00:30 | issue no Paperclip → agente propõe JSON → `temas_inserir` → Postgres | "Mantenha 7 dias de temas (≥80% curiosidades), ≤5 por proposta, ≤480 caracteres; responda só o bloco json" | `tests/unit/test_temas_t465.py` | Agenda ativa; **bloqueado pela ponte (pedido #2: login da CLI do Paperclip)** |
| 2 | Revisão do Auditor feita à mão | Auditor (agente) + `auditor_gemini` | `RespostaAuditorGemini` / `ResultadoAuditorGemini` | atividade `auditor_gemini` (fila camofox-pqbr), chamada no `EpisodioWorkflow` após o pós | episódio → quadros → Camofox/Gemini → contrato → `erros_aceitaveis`; terceira_rodada → sinal para o Auditor no Paperclip | "Só atue em terceira_rodada; decida aprova/reprova com os motivos do contrato; nunca peça roteiro novo à mão" | test_auditor_visual + teste de `validar` | Atividade registrada no worker; **falta ligar no EpisodioWorkflow** e o teste no EP1002 (Google voltou 17:25) |
| 3 | Auditoria Gemini por script (`auditor_gemini_ep.py`) | código | idem 2 | idem 2 | — | — | idem | Script aposentado após o item 2 entrar no fluxo |
| 4 | Arquivar e apagar cadernos de teste (`arquivar_estilos.py`) | código | `PedidoDescarteTeste`, `CopiasVerificadas` (descarte.py) | `DescartarCadernoTesteWorkflow` → filho `ApagarCadernoWorkflow(teste=True)` | fluxo → CLI notebooklm (exportar) → Drive 00_Biblia_Visual/cadernos-teste + repo `docs/pesquisas/arquivo-cadernos` + `pqbr.arquivo_caderno` + Hindsight → verificar → apagar pelo id | — | `tests/unit/test_descarte.py` | **Feito** (18:06); 1º uso: EP1001 |
| 5 | Regra de espera da publicação bloqueava EP1001 (nunca publicado) | código + decisão do José (18:06) | `registro_reclassificar_teste` (só não publicado) + `registro_autorizar_apagar_teste` | `DescartarCadernoTesteWorkflow` (reclassifica para `pesquisa`) | — | — | idem 4 | **Feito**: reclassificado e descartado pelo fluxo |
| 6 | Teste de estilos por script (`teste_estilos.py`) | Diretor de Arte | `PedidoNotebookLM.steering` + `config/estilo_visual.json` | `EpisodioWorkflow` com `steering`/estilo ativo (próximo teste: estilo D via fluxo) | issue do Diretor de Arte → config de estilo → fluxo do episódio | "Proponha estilo em config/estilo_visual.json via proposta; não gere vídeo fora do fluxo" | unit de `steering_short` | Estilo D ativo via config; **próximo teste 100% pelo fluxo** |
| 7 | VNC/login Google | José (pedido automático) | `EstadoAcesso`, `PedidoJose` | `AcessosWorkflow` (de hora em hora) + keepalive dispara ao cair | fluxo → `revisao_humana` → cron Hermes `pqbr-pedidos-jose` → Telegram | — | `tests/unit/test_acesso.py` | **Feito** (pedido #1 aberto 17:21 e fechado sozinho 17:25) |
| 8 | Login da CLI do Paperclip | José (pedido automático) | idem 7 | idem 7 (`acesso_paperclip`) | idem 7 | — | idem | **Pedido #2 pendente** (aviso pelo Telegram/Hermes `pqbr`) |
| 9 | Restauração da sessão por import de cookies | código (automático, aprovado 18:06) | `EstadoAcesso`, `EventoAcesso` | `AcessosWorkflow`: queda → `registrar_evento` → `restaurar_sessao_camofox` → `registrar_evento` → `avisar_jose` (ou `pedir_jose` se falhar) | fluxo → `pqbr.eventos_acesso` + changelog REFERENCIA → `revisao_humana` → Telegram | Observador: confere eventos; não age à mão | `test_acesso.py`, `test_descarte.py::test_causa_provavel` | **Feito** |
| 10 | E2E disparado por script (`e2e_iniciar.py`) | Diretor (agente) | `PedidoEpisodioE2E` | `EpisodioWorkflow` via issue do Diretor (ponte) | issue → ponte → workflow | "Inicie episódio só pela ponte; nunca por script" | test_producao | **Bloqueado pela ponte (#2)** |
| 11 | Início do `DescartarCadernoTesteWorkflow` (EP1001, 12/10 18:41) por comando avulso no pc | Diretor (agente) via ponte | `PedidoDescarteTeste` | gatilho: issue/painel → ponte → workflow (a criar) | painel → ponte Paperclip → Temporal | "Peça descarte de caderno de teste só pela issue de descarte" | — | **Avulso registrado**: não há caminho contratado enquanto a ponte (#2) está fora |

## Atualização 15/10/2026 — avisos operacionais e canal Discord [HISTÓRICO: Discord revogado por t474]

PQBA-87 mapeou pedidos de acesso/sessão, aprovação Temporal, incidentes de compliance/pós-publicação e relatórios/consumo. PQBA-89 separou apenas a formatação dos pedidos de acesso; agenda, `avisado_em`, stdout e Telegram permaneceram inalterados. A validação executou 4 testes focados e 49/49 no worktree Dev; depois, 69/69 na suíte unitária em worktree temporário limpo do HEAD 85e3060, via pytest. A alteração está isolada, sem commit/merge/implantação.

Lacuna identificada por inspeção estática: `pedidos_telegram.py` atualiza `avisado_em` antes de imprimir a mensagem; se o consumidor falhar após o commit, o pedido pode ficar marcado como avisado sem confirmação de entrega. A sequência foi reproduzida por simulação local com DB stub e stdout simulando OSError; nenhum banco ou transporte real foi acessado. A primeira implementação da correção em PQBA-91 falhou revisão no HEAD limpo 96579e5 (84 testes passaram, 1 falhou), por colisão da migração 0012, falta de policy RLS para pqbr_app e ausência de uso da outbox no dispatcher. O ticket foi devolvido ao Dev; o caso permanente deve provar também queda após envio e antes do commit. Definir e testar uma saída durável com chave idempotente, confirmação após entrega e retry seguro antes de migrar os avisos. O item `aviso:` sem lembrete periódico merece cobertura explícita.

Próximo passo: corrigir e revalidar PQBA-91 no worktree isolado; só então revisar o diff independentemente. ~~Depois ligar o adaptador de saída Discord/Paperclip~~ (revogado, t474): os avisos operacionais saem pelo Telegram (Hermes `pqbr`); falta resolver o token do bot do perfil `pqbr` (decisão pendente do José).

## Pendência t526 (24/10/2026) — migração Camofox [GATILHO: próxima integração de projeto]
- Migrar PQBR 9387 → `camofox@pqbr` (runbook §3) e ligar `NavegadorIdentidade` em `acesso.py`.
- Ativar a instância reservada `proxima`:9397 para a conta do novo projeto (runbook §2).
- ~~Script de criação não idempotente / `--instalar` falhava na 2ª execução~~ — resolvido em t528.
- Pendentes do plano ADR-012: backup diário com teste de restauração, canário diário, renovador único.

## Lacuna t529 (24/10/2026) — vídeo em série e HOLD
- O código ainda não tem Flow, Vids nem Meta Vibes: o `EpisodioWorkflow` baixa o vídeo do NotebookLM (`nlm_baixar_video`). A cadeia existe só como decisão. → ROADMAP Fase 4V R1–R6.
- HOLD quando as 3 rotas falham: **decidido** (t529), ainda não implementado. → R7.
- Storyboard em série (prompts do NotebookLM → imagens nomeadas e ordenadas → vídeos): só pesquisa (`docs/pesquisas/PESQUISA-extensoes-geracao-em-serie.md`).

## Lacuna lote 25/10/2026 — pacotes de roteiro para produção externa (Higgsfield/Runway/ElevenLabs)
Feito pelo agente externo (Grok Bot). Sem vídeo, imagem ou voz gerados e sem publicação. A parte criativa saiu do NotebookLM pela fila `notebooklm-pqbr`, com a sessão do Camofox 9387 e as flags `NOTEBOOKLM_DISABLE_KEEPALIVE_POKE=1` e `NOTEBOOKLM_HEADLESS_REAUTH=0`.
- **Falta um modo "só roteiro" no Temporal:** com `tipo=short` + `roteirizar`, o `NotebookLMWorkflow` sempre segue para `nlm_gerar_short`, que gera o vídeo no NotebookLM. Para não gerar vídeo, usei `tipo=pesquisa` com o pacote canônico, a pesquisa web e o `PROMPT_ROTEIRO` como pergunta. → Criar `tipo=roteiro_pacote` que pare depois de `_roteirizar`.
- **Validação fora do workflow:** `validar_roteiro`, `compliance_roteiro`, os arquivos de cenas e narração e o `meta.json` foram rodados por script (`/tmp/pos.py`), fora do Temporal. → Tornar activities do modo acima.
- **Checagem de atualidade fora da grade:** a classificação "do momento" ou "de sempre" foi um pedido avulso ao NotebookLM (caderno `0d266053`). O `GradeDiariaWorkflow` não tem esse passo, e `temas_pendentes` não tem coluna de classe.
- **Caderno e registro:** os temas do lote não têm código `PQBR-EP`, então os cadernos ficaram sem `registro_caderno` e `fontes_caderno` e não há cópia no Drive (`drive_enviar` exige um episódio). Os cadernos ficam no NotebookLM sem apagamento agendado. → Definir os códigos e o descarte.
- **Barreira 2 vs. R10 semântico:** a variação por palavras deixou passar temas próximos de publicados, como sacola dobrada × sacola bonita e caixinha de suco × caixa de leite. Tirei esses temas à mão (o Jev ainda não está ligado na faixa de dúvida).
- **Tema com marca real:** "botijão azul ou cinza" exige citar distribuidoras, e o compliance reprovou por marca real e por afirmação errada. → Filtrar temas de marca antes de roteirizar.
- **EP1002 no formato v1:** `~/.pqbr/rot-EP1002.json` não tem `tipo_cta` nem fontes e não passa no `validar_roteiro` v2. Foi roteirizado de novo no caderno `c47ccd24`.

## Lacuna legenda 25/10/2026 — legenda gravada fora do Temporal
- `scripts/legendar_short.py` (faster-whisper local, CPU, venv `~/.venvs/whisper`, modelo small) roda à mão, fora de qualquer workflow do Temporal. Ele transcreve com tempo por palavra, alinha ao `narracao.txt`, gera .ass/.srt e grava em `<short>-legendado.mp4` sem sobrescrever. Piloto: café fraco. → Virar activity no fluxo de pós-produção.

## Lacuna lote-2510 — alocação dos prontos (25/10/2026)

- Os 9 `<tema>-pronto.mp4` não têm código `PQBR-EP`: sem `drive_enviar` e sem registro de episódio no Postgres. Identificador provisório `lote-2510/<tema>`; registro em `docs/pesquisas/lote-2510/<slug>/gate-pronto.json`. → José define os códigos; depois Drive/Postgres pelo fluxo.
- Gate: juiz Gemini (VISUAL+LOOP) e pacote editorial (título/descrição/tags) ausentes na produção externa → todos P1_HOLD.
- Sting final ainda usa logo stickman v1 (placeholder) — trabalho de produção do logo 2D.

## Lacuna publicação real pelo flow (t69s317/t70, 25/10/2026)
- **Credenciais OAuth do YouTube (t122u):** as três chaves `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` e `YOUTUBE_REFRESH_TOKEN` estão em `~/.pqbr/secrets/episodio.env` (600), projeto `pqbr-publicacao`, escopos `youtube.upload` + `youtube.readonly`, canal Porquê BR conferido por `channels.list`. O `pqbr-episodio-worker` foi reiniciado às 22:06 de 26/10 (t123u) e carregou as chaves. `YOUTUBE_DRY_RUN` segue `true`, então não há envio. O app OAuth está em Testando: o refresh expira em 7 dias (~2/11 21:20 Fortaleza). Com as flags de envio real ligadas, `pub_upload_privado` deixa de falhar por credencial ausente.
- **Agendamento:** corrigido no flow. O upload vai `private` + `status.publishAt` (próxima janela 11:40/18:35 America/Fortaleza), e o workflow confirma a janela.
- **Escopo do modo real:** corrigido no flow. `PQBR_PUBLICACAO_REAL_CODIGOS` (lista de códigos), e fora dela modo real = erro não retentável.
- **Registro no worker:** corrigido. `PublicacaoAgendadaWorkflow`, `ControlePublicacaoWorkflow` e `ATIVIDADES_PUBLICACAO` no `worker_episodio` (fila `episodio-pqbr`). Reinícios: t109u (16:57) e t123u (22:06).
- **Aviso Telegram pelo outbox no worker do episódio:** o `pqbr-episodio-worker` não tem o drop-in `telegram.conf` (só o `pqbr-temporal-worker` tem). O aviso real pode sair como "desligado"; é melhor esforço e não bloqueia.

## Testes pendentes pós-fluxo (t71u–t72u, só registro, não executar agora)
1. **LOOP do Gemini por cena:** julgar cada cena separadamente, depois uma consolidação final só em texto (capa×título). O gate reprova se qualquer cena reprovar. Comparar com o método atual em tempo, memória e qualidade.
2. **Modelo:** 4 Argon com raciocínio baixo vs 3.8 Flash no mesmo lote.

## Lacuna storyboard (t75u–t77u, 26/10/2026), auditoria do lote 2510
- (a) Storyboard geral: **parcial**. O `cenas.md` de cada tema tem bloco de estilo + ficha de personagem, mas não tem norte geral do episódio.
- (b) Revisão das imagens antes do vídeo: **não**. O `producao.json` vai de 8 imagens (Higgsfield flux, âncora cena 1) direto aos clipes (Seedance/Runway). O juiz Gemini só viu o vídeo pronto.
- (c) Storyboard por cena com norte/início/fim: **não**. As 67 fichas têm só "Fala" e "Prompt visual"; não há norte, início, fim nem frame final.
- (d) Prompt por cena: **parcial**. Há prompt de imagem por cena, mas a animação usou sufixo genérico ("Flat 2D cartoon, bold black outlines…"), sem prompt de movimento por cena, sem "lips closed" e sem plano nomeado.
- Extensões e tutoriais (`PESQUISA-extensoes-geracao-em-serie.md`, t529: VEO Automation, Flow Queue, Flow Automator, AutoFlow, GUÍA VOX): **não seguidos**. O lote 2510 foi gerado no Higgsfield e no Runway, sem Flow, sem manifesto JSONL e sem rótulo `<ep>_cNN`.
- → Implementado: contrato `FichaCena`/`Storyboard` 1.0.0 + testes. Falta: (1) uma activity que gere o Storyboard (NotebookLM → fichas) e bloqueie a geração sem ele; (2) o VISUAL do juiz Gemini ganhar 3 critérios fail-closed: `personagem_mexe_labios`, `corte_oculos_cabeca`, `grotesco` (muda o schema do JSON do juiz, então fica para a próxima versão do `auditor_gemini`).

## Lacuna personagem, cenário e elenco (t78u, 26/10/2026)
- Regra em CONTRATO-EDITORIAL §18.3–9 e contrato `FichaCena` 1.1.0 (`papel_personagem` observa|participa, `figurino` epoca_local|atual_variavel, `expressao`, `cenario_encaixe`, `Storyboard.elenco` alternado).
- Falta: (1) gerar as imagens de referência dos dois personagens (paga, exige OK do José); (2) o roteirista e o storyboard (NotebookLM) preencherem esses campos; (3) o VISUAL checar a coerência do figurino com o papel.
- O consolidado do dia está em ROADMAP, "Estado em 26/10/2026".
