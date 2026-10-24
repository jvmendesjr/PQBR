# Canal de chat da PQBR — Discord/Paperclip

Atualizado em 16/10/2026. Este diretório reúne os documentos do canal privado Discord conectado diretamente ao Diretor do Paperclip e da migração de avisos ainda em andamento.

## Estado comprovado

A menção raiz em `#pqbr` cria uma tarefa e a resposta do Diretor aparece na thread. O endpoint está ativo; apenas `#pqbr` está habilitado; DMs e identidades não vinculadas estão bloqueadas. Telegram/Hermes permanece ativo como rollback.

## Gates ainda abertos

F05-06/TZ-06 ainda precisa da aprovação Temporal autenticada com validação de estado, fail-closed, idempotência persistente e ticket após três falhas. F05-08/TZ-09 ainda precisa de transporte proativo durável, ACK, retry, deduplicação e integração de todas as rotas. F05-09/TZ-10 só pode pausar a rota antiga após esses gates e ensaio de rollback. O status oficial está sempre em `docs/ROADMAP.md` e `docs/TESTES.md`.

## Arquivos

- `GUIA-USO-DISCORD.md` — instruções de uso e solução de problemas; não declara aprovação Temporal ou alertas operacionais como disponíveis.
- `BLUEPRINT-MIGRACAO-DISCORD-PQBR.md` — arquitetura, fases, limites e rollback da migração.
- `AVALIACAO-DISCORD-NATIVO-PAPERCLIP.md` — avaliação da opção nativa.
- `INVENTARIO-NOTIFICACOES.md` — fontes e estado das notificações a migrar.

Não use este diretório como substituto do roadmap canônico nem desligue Telegram/Hermes com base apenas no round-trip de conversa.
