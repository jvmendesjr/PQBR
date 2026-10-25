# PLANO — ponte durável Telegram ↔ Temporal (F05-06/F05-08) e conserto do `avisado_em` (rascunho t536)

Branch `feature/f05-06-ponte-duravel`. **Não aplicado:** migração 0018 não rodada, nenhum serviço reiniciado, Hermes intocado.

## Achados
- `pedidos_telegram.py` (main): grava `avisado_em` e faz commit **antes** do `print`; se o cron Hermes falhar, o pedido some do lembrete.
- Candidata `telegram_aprovacao.py` (worktree `dev/agentes`, não commitada): dedupe em memória (`set`), sem trava de concorrência, reenvio após resposta ambígua, exceção em texto bruto. Reprovada.
- Candidata PQBA-91 (`notificacoes_operacionais.py` + 0017): reprovada por colisão da migração 0017 (o main já tem 0017 de relatórios), falta de policy RLS para `pqbr_app` e dispatcher sem outbox.
- `workflows.py`: o sinal `aprovacao_jose` já ignora a 2ª aprovação e a etapa errada, mas o `remetente_id` é lógico (`"jose"`); a autenticação tem de acontecer antes do sinal.

## Desenho
1. **Contratos** (`src/pqbr/contratos/ponte_telegram.py`, 1.0.0): `MensagemSaida`, `PedidoAprovacao`, `ReciboEntrega`, `EventoCallbackTelegram` (remetente = `from.id` numérico, nunca texto) e `ResultadoDecisao`. A integração ao `VERSOES` geral fica para o merge.
2. **Postgres** (0018 + rollback):
   - `saida_telegram`: outbox com chave PK, estado `pendente/enviando/enviado/incerto/falhou/ticket`, claim com prazo e `mensagem_id`.
   - `pedido_aprovacao`: token opaco → workflow, etapa, expiração.
   - `entrada_telegram`: PK `update_id` + `ref_pedido` UNIQUE (uma decisão por pedido).
   - `revisao_humana.chave_saida`.
   - RLS e grants iguais aos da 0017.
3. **Activity `enviar_telegram(chave)`:** claim atômico → envio → confirmação na mesma transação que grava `avisado_em`.
   - Erro claro → `falhou`; o retry do Temporal fica desligado e a escada é própria, com 3 tentativas e depois ticket único.
   - Timeout após o envio → `incerto`: não reenvia às cegas. O reenvio sai só marcado "(reenvio)" e é seguro, porque a decisão é deduplicada pelo token.
   - Erros registrados só como nome da classe (sem texto bruto).
4. **Entrada (fail-closed):** sem ID autorizado na config → nada; remetente diferente → nada; token desconhecido ou expirado → nada.
   - O registro em `entrada_telegram` acontece antes do sinal: se já existe, é duplicado e não sinaliza.
   - O sinal `aprovacao_jose` leva o token. O handler devolve a etapa; se a etapa estiver errada, o resultado é `estado_invalido`.
   - 3 falhas do Temporal → 1 ticket (chave `ticket:sinal:<token>`).
5. **Sinal no workflow:** o recebedor do callback (processo leve no `pc`, só 127.0.0.1, sem expor porta) usa `Client.get_workflow_handle(wf).signal("aprovacao_jose", AprovacaoJose(..., token))`. Por ora, a etapa é lida por um `@workflow.query etapa`. Mais tarde, o melhor é trocar por um Update com validator, que rejeita no servidor e devolve o resultado de forma síncrona.
6. **Pendências do José:** t537 decidiu que o gateway Hermes (perfil pqbr) repassa os callbacks (sem bot próprio); faltam os OKs de instalação (ver t537) e a aplicação da 0018.

## Testes
`tests/unit/test_ponte_telegram.py` (10): envio uma vez; 3 falhas → ticket sem vazar texto; ambíguo sem reenvio às cegas; fail-closed (config ausente, remetente, token desconhecido, expirado, etapa); um sinal por pedido (update repetido e segunda decisão); 3 falhas do Temporal → 1 ticket; contratos; chave da janela de 6 h.
**Faltam:** adaptador Postgres contra o banco de teste (`db/test_migrations.sh`), teste com `WorkflowEnvironment` (sinal real, reinício do worker) e corrida de dois workers no claim.

## [SUPERADA por t538] t537 (José, 25/10/2026) — entrada pelo gateway Hermes (perfil `pqbr`), sem bot próprio
- **Como o Hermes repassa:** um plugin do perfil `pqbr` (`deploy/hermes-plugin-pqbr-ponte/`, **não instalado**) usa `ctx.register_telegram_handler` com `CallbackQueryHandler(pattern=r"^pq:")`. O padrão é restrito para não engolir os fluxos do core (`ea:`, `sc:`, `cl:`, `mp:`…), cujo handler ignora prefixos desconhecidos.
  - O plugin lê `from_user.id` do próprio update e manda `{update_id, from_id, chat_id, data}` por **socket Unix 0600** (`/run/user/1000/pqbr/ponte-telegram.sock`), sem porta TCP e sem mudança de rede.
  - Responde ao botão só com um status curto. Se o PQBR não responder, nada é registrado (fail-closed).
- **Botões:** `callback_data = "pq:<a|n>:<ref>"`, com no máximo 64 bytes e `ref` opaco de 32 caracteres.
- **Lado PQBR:** `src/pqbr/workflows/entrada_telegram.py` (`para_evento`, `tratar_envelope`, `servir_unix`).
  - O adaptador é escolhido em `config/ponte_telegram.json` (`adaptador_entrada`: `desligado` | `hermes_plugin_unix`); o padrão é `desligado`.
  - O fluxo segue para `processar_callback` (dedupe em `entrada_telegram` e depois o sinal).
- **Hooks de arquivo** (`hooks/<n>/HOOK.yaml`) não servem: só cobrem gateway, sessão, agente e comando, não callbacks. O `gateway_platform_event` só observa reação e edição.
- **Ligar exige OK do José:**
  1. copiar o plugin para `~/.hermes/profiles/pqbr/plugins/pqbr-ponte/`;
  2. incluir `pqbr-ponte` em `plugins.enabled` do `config.yaml` do perfil (os plugins são opt-in);
  3. ativar o plugin. O Hermes tem religação tardia de handlers (#87770, `rewire_plugin_handlers`), então talvez dispense reinício. Se a redescoberta não acontecer sozinha, é preciso reiniciar o `hermes-gateway`, o que derruba por segundos todos os perfis e canais desse gateway (`multiplex_profiles: true`);
  4. subir o recebedor PQBR (unit nova, só socket local);
  5. aplicar a 0018.
- **Riscos a verificar antes de ligar:**
  - com `multiplex_profiles`, confirmar que o handler do plugin do perfil `pqbr` vale para o bot/roteador que entrega o tópico do José;
  - confirmar que o hoist tardio coloca o handler à frente do `CallbackQueryHandler` catch-all do core.

## t538 (José, 25/10/2026) — bot próprio do PQBR (supera t537)

Rascunho do plugin Hermes movido para `docs/_obsoleto/hermes-plugin-pqbr-ponte-t537/` (nada apagado).

- `src/pqbr/workflows/telegram_bot.py`: transporte stdlib (`urllib` em `asyncio.to_thread`, sem dependência nova), injetável; token lido só de `PQBR_TELEGRAM_BOT_TOKEN` na hora da chamada e nunca em log/exceção (erros mostram só método e código); timeout → `EntregaIncerta` (sem reenvio cego).
- Saída: `RemetenteTelegram` (porta `Remetente`): `sendMessage` para `PQBR_TELEGRAM_JOSE_ID`, botões `pq:a:<ref>`/`pq:n:<ref>` quando há `ref_pedido`; reenvio marcado "(reenvio)".
- Entrada: `ciclo_entrada` = `getUpdates` (long polling, `allowed_updates=[callback_query]`) → `processar_callback` (from.id, dedupe, expiração, etapa) → `answerCallbackQuery` → `editMessageReplyMarkup` remove botões (só para o José e decisões finais). Offset persistido (`OffsetArquivo`, atômico, 600) após tratar; reprocessar é seguro.
- `sinalizar(wf, ref, decisao, etapa_esperada)`: `sinalizar_temporal` faz query `etapa` e só sinaliza se for a esperada.
- Config `config/ponte_telegram.json` v2: `saida` ∈ {desligado, telegram_bot}, `entrada` ∈ {desligado, telegram_long_polling}; ambos desligados.
- `deploy/systemd/pqbr-telegram-entrada.service` (user unit, EnvironmentFile=.env do PQBR, hardening) — NÃO instalada.
- Testes: `tests/unit/test_telegram_bot.py` (11, Telegram simulado).

### Falta antes de ligar
1. Repositório Postgres da ponte (depois da 0018 aplicada) no lugar do `RepositorioMemoria`.
2. Query `etapa` nos workflows que pedem aprovação + activity `enviar_telegram` registrada no worker.
3. `main_entrada` ainda encerra com "EM CONSTRUÇÃO" (fail-closed).
