# Avaliação: Discord nativo do Paperclip como canal PQBR

**Data:** 14/10/2026
**Status:** avaliação técnica inicial; nenhuma alteração de configuração ou rede foi aplicada por este documento.

**Atualização t464:** esta avaliação é histórica e foi superada pela decisão aprovada de conectar o Discord nativo diretamente ao Diretor, migrar também aprovações Temporal e avisos operacionais, e só então pausar Hermes/Telegram PQBR. O plano vigente é `BLUEPRINT-MIGRACAO-DISCORD-PQBR.md` no mesmo diretório.

## Síntese

O Discord nativo do Paperclip é o candidato mais promissor para substituir o Hermes como interface de chat do PQBR, porque liga uma conversa diretamente a um agente Paperclip e não documenta a exigência de ingresso HTTPS público que existe para Telegram e Slack. A integração é experimental e precisa ser testada na instância real antes de qualquer migração. Não habilitei flags, instalei bot, atualizei o Paperclip nem alterei exposição de rede.

## Como está hoje

A arquitetura canônica do PQBR diz que o perfil Hermes `pqbr` recebe as mensagens Telegram de José e apenas consulta, roteia e abre trabalho para o Diretor; o Paperclip é onde os agentes de produção e desenvolvimento executam suas tarefas (`docs/REGRAS.md`, `docs/ARQUITETURA.md` e `docs/AGENTES.md`).

O registro Paperclip **Canal José (pqbr)** não é atualmente um segundo agente executável. A consulta de configuração mostrou `adapterType=process`, com comando `scripts/paperclip/agente_pausado.sh`; o script é um stub que apenas informa “sem execução” e termina. Portanto, a duplicidade é entre o assistente Hermes em funcionamento e um registro/stub no Paperclip — não dois assistentes independentes fazendo o mesmo trabalho. O Diretor é um agente Paperclip ativo e pode ser selecionado diretamente como agente de resposta de uma conexão de chat.

O CLI/pacote Paperclip instalado é **2026.1001.0**. A consulta às configurações experimentais da instância mostrou `enableChatConnectors=false` e `enableAgentChat=false`. Os conectores nativos de chat foram introduzidos em 2026.916.0, portanto a versão instalada é posterior à introdução; a disponibilidade real deve ser confirmada no painel antes de planejar habilitação.

## Discord nativo

A documentação do Paperclip descreve Discord como canal experimental. Uma conexão atende um servidor e um agente. Uma menção raiz ao bot cria uma tarefa e thread; as respostas continuam a mesma tarefa. O fluxo documentado é em canal; o uso por DM não está confirmado.

A configuração requer aplicativo/bot Discord dedicado, token, Application ID e Server ID, intent de conteúdo de mensagens e permissões mínimas no canal para ler, responder e abrir threads. O acesso deve ser limitado no próprio Discord a um canal privado de teste. No Paperclip, a pessoa que fala deve estar vinculada a uma identidade ativa da empresa; manter “Allow unlinked people” desligado evita que desconhecidos iniciem trabalho.

O guia oficial de Discord não lista uma URL HTTPS pública como pré-requisito, ao contrário dos guias oficiais de Telegram e Slack. O PR oficial de implementação registra testes reais de inicialização do Discord Gateway e ciclos pause/resume. Isso torna Discord potencialmente compatível com a instância privada na tailnet, mas o caminho real deve ser comprovado num piloto antes de tratar essa hipótese como garantida.

## Comparação com as rotas atuais

| Rota | Requisito relevante | Adequação ao servidor privado |
|---|---|---|
| Paperclip + Discord nativo | Conector experimental, bot dedicado e acesso por canal/identidade | Melhor candidato; não há requisito público HTTPS no guia, mas precisa de teste real |
| Paperclip + Telegram nativo | URL HTTPS pública em porta 443, 80, 88 ou 8443; bot dedicado e webhook único; sem allowlist de remetente no Telegram | Fraco enquanto o servidor permanecer somente na tailnet |
| Paperclip + Slack nativo | URL HTTPS pública e app Slack; chat experimental | Também exige ingresso público; não é a primeira opção para este ambiente |
| Hermes + Telegram atual | Canal já usado pelo PQBR, separado do runtime dos agentes Paperclip | Continua sendo a rota funcional até uma migração aprovada e validada |

## Recomendação e limites

Prosseguir com um piloto do **Discord nativo conectado diretamente ao Diretor**, em um servidor/canal privado e com identidade do usuário vinculada. Isso elimina o stub “Canal José” como destino funcional e evita criar outro agente redundante. Se José preferir uma persona de canal própria, ela deverá ser um agente Paperclip real, com runtime e escopo explícitos; o registro atual não serve para isso.

O piloto deve verificar, sem publicar nem alterar dados de produção: instalação do bot, menção em canal privado, criação de tarefa no Paperclip, resposta na thread, identidade e atribuição corretas, e comportamento quando o agente está pausado ou indisponível. Aprovações de workflow Temporal são uma etapa separada: o canal de conversa, por si só, não prova que o sinal de aprovação é autorizado nem que passa pelo estado correto do Temporal.

**Não desativar Hermes/Telegram, não remover o registro atual, não habilitar as flags experimentais, não criar ou instalar o bot e não alterar rede/exposição** antes da revisão de segurança e da autorização específica de José. Manter o gate F05-06 sem merge/publicação até alinhar a implementação de aprovação à decisão final sobre canal.

## Trabalho paralelo no Paperclip

- **PQBA-80:** revisão independente da implementação fail-closed da ponte de aprovação Temporal; sem merge/publicação.
- **PQBA-84:** Diretor avalia a substituição Hermes → Agent Chat nativo, versão/flags e plano reversível.
- **PQBA-85:** Guardião de Segurança compara Discord, Telegram e Slack com foco em identidade, exposição e controles de acesso.

As tarefas foram criadas e atribuídas; seus relatórios ainda precisam ser observados antes da decisão final.

## Fontes

- Paperclip Connector Catalog: https://docs.paperclip.ing/connectors/
- Guia oficial do Discord: https://docs.paperclip.ing/connectors/discord/
- Guia oficial do Telegram: https://docs.paperclip.ing/connectors/telegram/
- Guia oficial do Slack: https://docs.paperclip.ing/connectors/slack/
- Changelog Paperclip v2026.916.0, introdução dos conectores nativos: https://paperclip.ing/changelog/v2026.916.0/
- PR oficial do Paperclip #13038, implementação experimental dos conectores: https://github.com/paperclipai/paperclip/pull/13038
- Documentação PQBR: `docs/REGRAS.md`, `docs/ARQUITETURA.md`, `docs/AGENTES.md`; stub local `scripts/paperclip/agente_pausado.sh`.


## Requisitos de conhecimento, memória e acesso do agente

Sim: para responder com propriedade sobre PQBR, o agente selecionado no canal precisa receber contexto e ferramentas adequados; trocar apenas o canal não basta. Isso não significa conceder acesso irrestrito.

- **Conhecimento canônico:** instruções e skills oficiais do projeto, especialmente `pqbr-contrato` e `pqbr-direcao`, além dos runbooks, contratos de workflow e documentação vigente. O registro atual “Canal José (pqbr)” já lista essas duas skills no pacote, mas seu adapter é um stub e não as executa.
- **Memória externa:** o Hindsight da organização PQBR pode guardar aprendizados duráveis e contexto sanitizado, sem segredos nem PII. Essa memória complementa as fontes canônicas, não substitui nem pode sobrepor documentos atuais.
- **Estado operacional atual:** episódios, resultados, métricas e status devem vir de consultas de leitura do banco de negócio e dos tickets do Paperclip. Agentes não consultam diretamente o Postgres interno do Temporal; o workflow expõe somente queries/sinais definidos.
- **Ferramentas graduadas:** leitura do estado e dos documentos primeiro; abrir/atribuir trabalho via Paperclip segundo as permissões do agente; qualquer aprovação ou comando operacional somente por ferramenta estreita que valide a identidade do usuário, o estado permitido e a idempotência no Temporal. Sem shell geral, escrita SQL direta, acesso a segredos ou publicação.
- **Identidade do canal:** cada conector nativo atende um agente Paperclip por vez. A decisão entre apontar Discord ao Diretor existente ou tornar o agente “Canal (PQBR)” um agente Paperclip real com papel de consulta/roteamento ainda está aberta; o atual registro stub não deve ser tratado como runtime ativo.

Esses requisitos são proposta de desenho para o piloto; não são mudanças de acesso já aplicadas.
