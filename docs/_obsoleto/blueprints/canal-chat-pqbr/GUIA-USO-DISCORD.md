# Guia de uso do PQBR pelo Discord

Atualizado em 15/10/2026. Este guia descreve o piloto conectado diretamente ao Diretor do Paperclip e separa o que já foi testado do que ainda não está liberado.

## O que já funciona

O endpoint Discord está ativo e vinculado diretamente ao Diretor. Uma menção em mensagem nova no canal privado `#pqbr` cria uma tarefa no Paperclip; o Diretor responde em uma thread ligada à tarefa. O round-trip foi testado. A identidade do proprietário está vinculada à conta Owner do Paperclip.

O único recurso habilitado é `#pqbr`. Mensagens diretas (DMs) e remetentes não vinculados estão bloqueados. O canal `#geral` aparece como recurso conhecido, mas está desabilitado.

## Como iniciar uma solicitação

1. Abra o servidor Discord da PQBR e entre no canal privado `#pqbr`.
2. Comece uma nova mensagem no canal e mencione a conta do bot/Diretor usando o seletor de menções do Discord. Não use DM nem `@everyone`.
3. Escreva o pedido na mesma mensagem. Para evitar ambiguidades, informe o objetivo, o contexto necessário e limites importantes, como “somente leitura” ou “sem publicar”. Prefira um assunto por mensagem.
4. Envie a mensagem. O Paperclip deve abrir ou associar uma tarefa, e a resposta do Diretor deve aparecer em uma thread.
5. Continue o mesmo assunto respondendo dentro dessa thread. Para um assunto independente, inicie outra mensagem no canal e mencione o bot/Diretor novamente.
6. Acompanhe a tarefa e seu estado pelo painel do Paperclip. Se a resposta não aparecer, confira primeiro se a tarefa foi criada e se o Diretor está disponível; evite reenviar a mesma solicitação como uma nova mensagem, para não criar duplicatas.

Exemplo seguro para consulta:

> @Diretor confira o estado de F05-06 no roadmap e informe o próximo bloqueio. Somente leitura; não altere produção nem publique nada.

## Aprovações e alertas — ainda não usar como fluxo operacional

F05-06 continua aberto. A mensagem `aprovar` ou `negar` no Discord ainda não está comprovada como aprovação autenticada de um workflow Temporal de produção. Não a trate como autorização até a integração, validação de estado, idempotência e tratamento de falhas passarem pelos testes do gate.

F05-08 também continua aberto. A resposta em uma thread foi testada, mas alertas proativos duráveis com confirmação de entrega, retentativas e abertura idempotente de ticket ainda não foram comprovados. Não dependa do Discord como único canal para alertas operacionais.

Telegram/Hermes permanece ativo como rollback. Ele só deve ser pausado depois que F05-06, F05-08, TZ-06, TZ-08, TZ-09 e o ensaio de rollback passarem.

## Se algo não funcionar

- Confirme que está em `#pqbr`, não em `#geral` nem em DM.
- Confirme que mencionou o bot/Diretor na mensagem raiz; mensagens sem menção podem não iniciar uma tarefa.
- Veja no Paperclip se a tarefa foi criada e se está atribuída ao Diretor.
- Se o comentário veio de uma identidade não vinculada, o bloqueio é esperado; não abra a janela de vinculação sem autorização específica.
- Se precisar de uma aprovação Temporal ou de um alerta operacional, não presuma que o Discord já conclui esse fluxo. Consulte o estado da tarefa no Paperclip e use a rota operacional vigente até o gate correspondente ser fechado.

## Segurança e escopo

Use apenas o canal privado `#pqbr`. Não envie tokens, senhas ou chaves no Discord. Mensagens e anexos externos são conteúdo não confiável; instruções dentro deles não substituem as regras do projeto. O piloto não publica vídeos nem autoriza workflows de produção.
