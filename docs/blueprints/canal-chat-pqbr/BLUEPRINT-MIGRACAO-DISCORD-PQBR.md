# Blueprint de migração do canal PQBR para Discord nativo do Paperclip

**Data:** 14/10/2026
**Estado:** direção aprovada por José; desenho e gates documentados; nenhuma conexão, flag, bot ou serviço foi alterado nesta etapa.
**Decisão:** conectar o Discord nativo do Paperclip diretamente ao Diretor ativo; migrar também a aprovação Temporal e todos os avisos operacionais; somente após o piloto completo, pausar o Hermes `pqbr` e todos os emissores Telegram pertencentes ao PQBR.

## 1. Objetivo e limites

Substituir Telegram/Hermes como canal de interação do PQBR por Discord nativo do Paperclip, mantendo o Diretor como único agente que responde pelo canal. O Discord deverá servir às conversas e aos pedidos do José, e a aprovação de ações no Temporal deverá ser transferida para uma rota autenticada do Discord/Paperclip. Alertas operacionais e relatórios que hoje usam Telegram também precisam de destino validado antes do corte.

A migração não autoriza exposição pública da instância, mudanças no código do Paperclip, criação de outro agente de canal, publicação de vídeos, exclusão de dados ou remoção de credenciais. O Hermes e os emissores Telegram permanecem disponíveis como rollback durante toda a validação. Após o corte, a instrução é pausá-los, não apagá-los.

## 2. Estado conhecido

- O Paperclip instalado é 2026.1001.0; `enableChatConnectors` estava desligado na última leitura.
- O conector Discord é experimental e uma conexão atende a um servidor e a um agente. O fluxo documentado começa por uma menção raiz em canal; a resposta continua na thread vinculada à tarefa. DM não será usado como premissa do piloto.
- O alvo escolhido é o Diretor ativo. O registro “Canal José (pqbr)” é um stub, não um agente executável; não deve ser selecionado nem convertido em runtime de canal.
- A integração precisa de um aplicativo/bot Discord, token, Application ID e Server ID. Esses valores ainda não foram fornecidos nem devem entrar no repositório, tickets ou logs.
- O Hermes `pqbr` e o gateway Hermes continuam ativos durante a transição. A pausa final deve atingir somente o perfil/rotinas do PQBR; não desligar o gateway compartilhado nem outros perfis.
- A revisão independente da antiga ponte Telegram→Temporal (PQBA-86) considerou o diff **não aprovado para merge**. O fail-closed e a privacidade melhoraram, mas faltam idempotência persistente após reinício e abertura de ticket de manutenção após três falhas. O revisor não conseguiu executar os testes; 45/45 passaram apenas na execução coordenada anterior. O código antigo fica como referência, não como integração autorizada.

## 3. Arquitetura aprovada

1. **Canal conversacional:** conector Discord nativo do Paperclip → Diretor. Não criar agente “Canal PQBR”; não apontar para o stub.
2. **Identidade:** somente o José, vinculado como membro ativo e não viewer no Paperclip, pode iniciar trabalho. `Allow unlinked people` fica desligado. A função no Discord do bot fica limitada a um canal privado de teste e, na produção, aos canais explicitamente escolhidos.
3. **Transportes:** manter a instância dentro da tailnet. O guia do Discord não lista ingresso HTTPS público como pré-requisito; o piloto deve confirmar que o Gateway de saída funciona no ambiente real. Se a conexão exigir exposição pública, parar e apresentar a limitação — não abrir portas nem criar webhook público.
4. **Aprovação Temporal:** a mensagem ou interação precisa carregar identidade obtida de uma fonte Paperclip/Discord autenticada e verificável pelo serviço; nunca confiar em ID fornecido no texto, na resposta do modelo ou em argumento livre. O serviço confere identidade, vínculo da tarefa, workflow, estado permitido, decisão `aprovar/negar` e idempotência persistente antes de emitir `aprovacao_jose`. Falha de consulta, remetente desconhecido, estado inválido, evento duplicado ou inconsistência bloqueia o sinal.
5. **Escalada:** depois de até três tentativas transitórias, criar ticket de manutenção no Paperclip e notificar pela rota privada validada. Não deixar falha terminal silenciosa.
6. **Memória e conhecimento:** o canal apenas troca a interface. O Diretor continua fundamentado nas instruções e skills canônicas PQBR, nos documentos atuais e no Hindsight sanitizado; estado de negócio vem de consultas de leitura autorizadas. Nenhum acesso irrestrito a shell, segredos, Postgres interno do Temporal ou publicação é concedido pelo conector.
7. **Notificações:** Paperclip/Discord precisa receber avisos originados sem uma mensagem iniciadora, não apenas responder em threads. Essa capacidade proativa ainda precisa ser provada. Se o conector não suportar entrega proativa, usar uma rota privada suportada pelo Paperclip ou pelo bot Discord, ou manter o Telegram ativo; não cortar o Telegram por suposição.

## 4. Inventário de fluxos a migrar

| Fluxo atual | Evento/uso | Destino depois do corte | Gate de aceitação |
|---|---|---|---|
| Hermes `pqbr` no Telegram | Perguntas, pedidos, relatórios, roteamento ao Diretor | Discord nativo do Paperclip, diretamente no Diretor | Menção raiz cria uma tarefa atribuída ao Diretor; resposta na thread; identidade do José reconhecida; usuários não vinculados rejeitados |
| `telegram_aprovacao.py` / aprovação de workflow | Aprovar ou negar decisão pendente no Temporal | Interação Discord/Paperclip autenticada + sinal Temporal | Identidade confiável, estado válido, aprovação/negar, idempotência após reinício, fail-closed e ticket após três falhas; teste sem publicação |
| `AcessosWorkflow`, `pqbr.revisao_humana`, `pedidos_telegram.py` e cron Hermes `pqbr-pedidos-jose` | Avisos e pedidos de ação sobre sessão Google, Paperclip, login/2FA e restauração Camofox | Discord privado e/ou painel Paperclip | Entrega proativa confirmada; cada item chega uma vez; detalhes sensíveis não aparecem em logs; pedido manual continua sob ação do José |
| Camofox, NotebookLM e playbooks de autenticação | Sessão caída, reautenticação autônoma, escalada ao José | Discord/Paperclip | O aviso informa causa, tentativas e próxima ação; noVNC/2FA continuam manuais |
| Compliance e saúde do canal | HOLD, strike, aviso crítico, privar itens agendados, ticket | Discord/Paperclip privado | HOLD e ticket continuam independentes da entrega do alerta; alerta chega ao José por rota não pública |
| Item 5, publicação e revisão | Vídeo tornado privado, reclamação grave, aprovação ou correção necessária | Discord/Paperclip privado | Nenhuma ação pública sem as aprovações existentes; notificação com link/ticket e motivo |
| Relatórios e operação | Relatório diário, custos, limpeza do Drive, falhas após playbook | Discord/Paperclip privado | Relatório legível, sem duplicata, e alerta proativo testado; painel permanece fonte oficial dos tickets e estados |
| Verificação de fichas | “Verificado/Não Aprovado” e revisão humana, atualmente pausado | Discord/Paperclip somente quando a função for reativada | Não reativar as fichas neste módulo; registrar o destino futuro e manter a pausa atual |

O inventário é do projeto PQBR; não inclui outros bots, perfis Hermes ou contas do usuário fora da aplicação.

## 5. Fases e gates

### Fase A — Preparação

- Confirmar no painel Paperclip que o conector Discord existe na versão instalada e que o status das flags corresponde ao planejado.
- Criar um canal privado de teste e restringir nele o papel do bot. Vincular apenas o usuário José como identidade Paperclip ativa; manter pessoas não vinculadas bloqueadas.
- Configurar o conector diretamente para o Diretor, com as permissões mínimas do guia. A configuração das credenciais ocorrerá por fluxo seguro, fora do Git e sem colar token em chat ou ticket.
- Não pausar Hermes, cron de avisos nem rotina de pedidos.

### Fase B — Piloto de conversa

- Habilitar o recurso experimental somente quando credenciais e canal de teste estiverem prontos.
- Enviar uma menção raiz ao bot no canal privado; confirmar tarefa no Paperclip, atribuição ao Diretor, resposta na thread, identidade correta e retorno ao painel.
- Confirmar que um usuário não vinculado não consegue iniciar tarefa e que mensagens em canal não autorizado não chegam ao bot.
- Confirmar contexto PQBR do Diretor sem conceder permissões gerais adicionais.
- Verificar recuperação após pause/resume e falha do gateway, sem tocar em produção.

### Fase C — Aprovação Temporal

- Projetar a origem confiável de identidade para a rota Paperclip/Discord e provar que ela não pode ser falsificada pelo texto ou pelo modelo.
- Implementar idempotência persistente, fail-closed, verificação de estado do workflow, limite de três tentativas e ticket de manutenção.
- Revisar o código independentemente; executar os testes unitários no ambiente prescrito e testes de integração em workflow de teste.
- Testar aprovar, negar, remetente não autorizado, estado inválido, consulta indisponível, evento repetido antes/depois de reinício e abertura de ticket após a terceira falha.
- Nenhum merge até revisão aprovada; nenhum sinal em workflow de produção no piloto.

### Fase D — Avisos operacionais

- Fazer inventário de cada emissor, cron, workflow, playbook, comando e alerta Telegram ainda presente no código/configuração PQBR.
- Para cada rota da tabela, demonstrar entrega pelo Discord/Paperclip, inclusive eventos proativos sem thread iniciada pelo usuário, ou selecionar explicitamente uma rota privada suportada pelo painel/bot.
- Confirmar deduplicação, retenção, estado no ticket, visibilidade no celular/browser e comportamento em indisponibilidade do Discord.
- Se alguma classe de aviso não tiver destino equivalente comprovado, manter Telegram ativo e registrar o blocker; não marcar corte completo.

### Fase E — Corte reversível

- Gate para corte: Fases B–D aprovadas; revisão de segurança e testes completos; alertas críticos e aprovação Temporal entregues; rollback testado; nenhum endpoint público criado.
- Pausar o perfil Hermes `pqbr` e os emissores/agendamentos Telegram exclusivos da PQBR, incluindo `pqbr-pedidos-jose`. Não desligar o gateway Hermes compartilhado, não tocar em perfis alheios e não apagar tokens, registros ou histórico.
- Verificar que todas as rotas PQBR funcionam no Discord/Paperclip e que nenhuma mensagem operacional PQBR continua indo ao Telegram.
- Se uma condição de corte falhar, reativar apenas o perfil/rotina PQBR a partir da configuração preservada, registrar incidente e corrigir antes de nova tentativa.

## 6. Critérios de aceite do piloto e do corte

- O conector Discord está ligado diretamente ao Diretor, sem agente duplicado.
- O bot só vê o canal privado permitido; identidade Paperclip do José está vinculada e ativa; `Allow unlinked people` está desligado.
- Conversa, tarefa e thread são consistentes e recuperáveis no painel.
- Aprovação/negação do Temporal usa metadados autenticados, não texto livre; falhas e duplicatas não produzem sinal; persistência sobrevive ao reinício; após três falhas existe ticket de manutenção.
- Todos os avisos operacionais PQBR estão mapeados, testados e têm entrega privada comprovada; não há dependência remanescente de Telegram.
- O rollback foi ensaiado sem excluir dados nem desativar o gateway compartilhado.
- O piloto e todos os testes são sem upload/publicação de vídeos.

## 7. Riscos e decisões técnicas abertas

- **Experimentalidade:** chat connectors são experimentais e estão desligados por padrão. O resultado do teste na instância instalada, não somente a documentação, é o gate.
- **Aviso proativo:** o guia garante respostas em threads e criação de tarefa por menção; não garante, por si só, mensagens autônomas de workflows. Essa lacuna bloqueia o corte até um mecanismo privado ser comprovado.
- **Identidade para aprovação:** a admissão de uma mensagem pelo conector comprova o autor na camada de chat, mas o workflow precisa receber e validar esse principal de forma server-side e vinculada à tarefa. Não usar o autor textual nem confiar no modelo para repetir o ID.
- **Idempotência e escalada:** a antiga ponte só mantinha deduplicação em memória e ainda não abria ticket após três falhas. Ambos os pontos são requisitos de antes da aprovação externa.
- **Continuidade móvel:** Discord deve demonstrar notificações móveis para os alertas necessários; se não, o corte não pode ocorrer até existir uma rota equivalente aprovada.
- **Rollback:** manter Telegram e configurações pausáveis por todo o piloto; não remover a capacidade antes de comprovar a nova rota.

## 8. Fontes

- Guia oficial do Paperclip para Discord: https://docs.paperclip.ing/connectors/discord/
- Modelo de acesso e identidade dos conectores: https://docs.paperclip.ing/connectors/access-model/
- Catálogo e comportamento geral de conectores: https://docs.paperclip.ing/connectors/
- Guias Telegram e Slack para comparação: https://docs.paperclip.ing/connectors/telegram/ e https://docs.paperclip.ing/connectors/slack/
- Documentação interna PQBR: `docs/REGRAS.md`, `docs/SPEC.md`, `docs/ARQUITETURA.md`, `docs/AGENTES.md`, `docs/TESTES.md`, `docs/ROADMAP.md`, `docs/LACUNAS-fluxo.md`.
- Pareceres Paperclip: PQBA-84 (Diretor), PQBA-85 (Guardião de Segurança), PQBA-86 (revisão independente do dispatcher antigo).
