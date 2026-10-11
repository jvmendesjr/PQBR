> ⛔ **ARQUIVO — não consultar sem aprovação do José.** Superado pelos docs canônicos (README).

# Decisões e ressalvas do José (07/10/2026), antes do blueprint

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

## Rodada 2 (07/10, ~21h)
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
