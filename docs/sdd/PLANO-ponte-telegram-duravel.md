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
6. **Pendências do José:** token próprio do bot `pqbr`, ou como o gateway Hermes entrega o callback ao recebedor (sem reiniciar o gateway); aplicação da 0018.

## Testes
`tests/unit/test_ponte_telegram.py` (10): envio uma vez; 3 falhas → ticket sem vazar texto; ambíguo sem reenvio às cegas; fail-closed (config ausente, remetente, token desconhecido, expirado, etapa); um sinal por pedido (update repetido e segunda decisão); 3 falhas do Temporal → 1 ticket; contratos; chave da janela de 6 h.
**Faltam:** adaptador Postgres contra o banco de teste (`db/test_migrations.sh`), teste com `WorkflowEnvironment` (sinal real, reinício do worker) e corrida de dois workers no claim.
