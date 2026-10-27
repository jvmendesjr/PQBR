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
| `docs/CONTRATO-EDITORIAL.md` (v1 + aditivo) → `CONTRATO-EDITORIAL-v1.md` | Substituído pelo v2 oficial (t473) | `docs/CONTRATO-EDITORIAL.md` (v2 + Anexo A com as seções canônicas do v1) |

## Revisão de `docs/pesquisas/` (23/10/2026, autorizada por José)
Nenhum arquivo movido: nenhum é claramente obsoleto e pesquisa nunca se perde. Todos ainda embasam decisões vigentes ou pendentes, e vários são lidos por código (`scripts/hindsight/indexar.py`, `src/pqbr/workflows/descarte.py`). Parcialmente superados (ficam, com a ressalva): `PESQ-agente-comunidade.md` (templates do Paperclip; skills/boas práticas valem), `PESQ-orquestracao-escala.md` (parte Paperclip; base da ADR-001), `PESQ-auditoria-av.md` (60–80 s superado por t271), `pesquisa-caderno-mestre.md` (base da decisão "sem mestre"), `mapa-drive-rede.md` (necessário para a migração do Drive antigo, pendente), `cadernos-inventario-20261012.md` (registro histórico da limpeza).

- t510 (23/10): `paperclip-trechos-t510.md` — ARQUITETURA §10, AGENTES §7/§10 e ROADMAP F1-01..03 da era Paperclip (substituídos pela ADR-011).
- t512 (24/10): `company/agents/{roteirista,especialista-seo,cacador-sazonal,comunidade,dev-corretor,dev-revisor,diretor-arte-2d}` — papéis aposentados/fundidos (8 papéis).
- t129u (27/10): verificação dos documentos ativos. Movidos, sem apagar: `AGENTES-operacao-paperclip-20261011.md`, `BRIEFING-novo-agente-pqbr.md`, `RESUMO-STACK-IMPLEMENTACOES.md`, `LICOES-pre-E2E.md`, `hermes-pqbr/SOUL-rascunho.md`, `lacunas-fluxo-ate-20261027.md`, `sdd/PROPOSTA-papeis-skills.md`, `sdd/PROPOSTA-skill-producao-short-pqbr.md`, `sdd/PLANO-ponte-telegram-duravel.md`, `sdd/teste-e2e-short-1.md`, `sdd/f7-01-dryrun-20261016.md`, `hermes-pqbr/perfil/mcp_paperclip.py`, `hermes-pqbr/perfil/pqbr-paperclip`. Substituto vivo: `docs/AGENTES.md`, `docs/LACUNAS-fluxo.md`, REGRAS, ESTADO-ATUAL e o mapa. As evidências `docs/sdd/evidencias-f3-05-*` ficaram no lugar: o F3-05 ainda está aberto no ROADMAP e os links são o registro dessa prova.
