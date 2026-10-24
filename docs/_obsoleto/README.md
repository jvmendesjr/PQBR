# docs/_obsoleto/ — lixeira temporária (23/10/2026)

Arquivos tirados do caminho por estarem obsoletos para a arquitetura atual (sem Paperclip; agentes PydanticAI dentro de activities do Temporal; painel = Temporal UI + Telegram/Hermes `pqbr`). **Nada foi apagado.** Caminhos relativos preservados (`docs/_obsoleto/<caminho original sem docs/>`). José revisa com calma e decide: apagar, restaurar (`git mv` de volta) ou mover para `docs/arquivo/`. Agentes: não usar como referência.

| Arquivo (origem) | Motivo | O que substitui |
|---|---|---|
| `docs/blueprints/canal-chat-pqbr/README.md` | Canal Discord nativo do Paperclip (t464); Paperclip sai e o canal é Telegram | DECISOES-LOG 23/10 (painel Temporal UI + Telegram) |
| `docs/blueprints/canal-chat-pqbr/BLUEPRINT-MIGRACAO-DISCORD-PQBR.md` | Plano de migração Telegram→Discord/Paperclip, não será executado | idem |
| `docs/blueprints/canal-chat-pqbr/AVALIACAO-DISCORD-NATIVO-PAPERCLIP.md` | Avaliação da opção Discord/Paperclip | idem |
| `docs/blueprints/canal-chat-pqbr/GUIA-USO-DISCORD.md` | Guia de uso do Discord | idem (guia Telegram a escrever) |
| `docs/blueprints/canal-chat-pqbr/INVENTARIO-NOTIFICACOES.md` | Inventário de avisos voltado à migração p/ Discord (a lista de fontes de aviso pode ser reaproveitada para o Telegram) | idem; reaproveitar a lista ao desenhar os avisos Telegram |
| `docs/hermes-pqbr/perfil/SKILL.md` | Skill Hermes para operar o Paperclip via MCP | Hermes `pqbr` lendo Postgres/Temporal (a definir) |
| `docs/sdd/f1-02-dryrun.md` | Dry-run de import de 2ª org Paperclip, nunca executado, suspenso | — |
| `company/playbooks/lock-preso.md` | 409 de checkout do Paperclip (#6007/#3819) | — (lock/retry passam a ser do Temporal) |
