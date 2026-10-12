# Lições pré-E2E: checklist reutilizável (PQBR, 12/10/2026)

Antes do 1º E2E, conferir **nesta ordem**. Cada item saiu de uma falha real do PQBR (12/10) que só apareceu na hora de rodar o E2E.

1. **Identidade única por conta externa.** Inventariar todas as cópias de sessão (storage_state, cookies, perfis Chrome/Firefox/Camofox, .env, crons de keepalive/sync) e deixar **um só dono** por conta.
   *PQBR:* a conta Google estava duplicada em 6+ lugares (Camofox global, mp32, notebooklm global, perfil Chrome, perfil Hermes rede, bootstrap). Isso gerou renovações concorrentes e sessão derrubada.
2. **Rotinas legadas pausadas.** Antes de ligar o fluxo novo, achar e pausar (backup + comentário datado, sem apagar) crons, jobs do Hermes e skills do sistema antigo que tocam o mesmo canal/conta.
3. **Segredos disponíveis para quem executa.** Para cada chave, anotar quem a usa (agente, worker, script) e de onde ela vem.
   *PQBR:* a chave do 9router só existia injetada pelo Paperclip nos agentes; workers e scripts não tinham acesso e o Paperclip não revela segredos. Resolver pelo formulário seguro, nunca por leitura de cofre.
4. **Pontes e portas vivas.** Testar cada ponte (CLI do Paperclip como board, Temporal, APIs) com um comando inofensivo.
   *PQBR:* o Paperclip mudou para a porta 3101 atrás do `tailscale serve` (HTTPS na 3100). O contexto e a credencial board do CLI continuavam em `http://…:3100`, e a ponte Temporal→Paperclip ficou com erro 400/401.
5. **Mapa papel → modelo fora da orquestração.** Ter um config único (`config/modelos_9router.json`) para workers e scripts, igual ao dos agentes, sem nome de modelo fixo no código.
6. **Dados de entrada populados e com reposição.** As tabelas que o fluxo consome (temas) precisam ter estoque (7 dias) **e** reposição automática (tema usado → publicados → novo tema). A tabela vazia só apareceu no E2E.
7. **Quem faz o criativo, de fato.** Conferir se o fluxo implementado reflete a decisão: aqui, **NotebookLM-first** (roteiro, SEO e capa no caderno do episódio; modelos só orquestram e validam com Pydantic; reserva no 9router). O código ainda mandava o roteiro pronto de fora.
8. **Etapas aprovadas existem no código.** Para cada passo do roteiro de teste aprovado, apontar a activity ou workflow. *PQBR:* a auditoria pelo Gemini Web e a capa por infográfico estavam fora do fluxo.
9. **Isolamento e arquivamento.** Cadernos efêmeros por id registrado, fontes registradas e checagem anti-contaminação, arquivar e verificar antes de apagar (ADR-003, playbook nlm-cadernos).
10. **Dry-run real.** Só então rodar o E2E em dry-run (sem upload), com tempos e artefatos por etapa.

Ver também: DECISOES-LOG (12/10), ROADMAP (t462–t465), `company/playbooks/nlm-cadernos.md`.

## Lições de 12/10 (tarde)
11. **Nunca rodar etapa de fluxo à mão** (José 17:17). Se o fluxo não está ativo: parar, registrar, consertar o fluxo e rodar por ele (Paperclip + Temporal).
12. **Uma só ferramenta rotaciona a sessão Google: o Camofox.** Qualquer CLI notebooklm-py com poke ligado derruba o navegador (queda de 12/10 ~16:15). O guarda está no venv (`.pth`) e não depende do script.
13. Antes do E2E: `pqbr-acessos` verde (Google, NotebookLM, Paperclip) e nenhum pedido pendente em `revisao_humana`.
14. O roteiro segue o contrato §17 (ironia brasileira, nunca aula). O Auditor reprova roteiro com cara de aula.
