# Guia de acesso ao PC, Paperclip e Temporal

Este documento registra caminhos operacionais verificados para apoiar o desenvolvimento do PQBR. Ele não substitui as autorizações do proprietário nem as regras do repositório. Verificado em 16/10/2026.

## Resumo rápido

- **PC compartilhado:** `ssh pqbr-pc` a partir do computador compartilhado do Cue. O alias usa OpenSSH e uma chave persistente configurada nesse computador.
- **Paperclip:** interface/API em `https://<MAGICDNS-DO-PC>:3100/`; a CLI autenticada funciona no próprio PC.
- **Temporal:** stack Docker Compose em `infra/temporal/docker-compose.yml`; UI local na porta 8233, servidor na 7233 e PostgreSQL interno ao container.
- **Segredos:** não copiar, imprimir, registrar neste guia ou enviar arquivos de autenticação, tokens, senhas ou conteúdo de `.env`.

## Acesso persistente ao PC

No computador compartilhado onde o alias foi instalado:

```bash
ssh pqbr-pc 'id -un; hostname; uname -s'
```

O alias `pqbr-pc` está em `~/.ssh/config` e usa o usuário local `pc`, OpenSSH na porta 2222 e a chave `~/.ssh/id_ed25519_pc`. A chave privada fica apenas no computador compartilhado, sem frase-senha para uso não interativo, com permissão `600`; a chave pública foi adicionada a `/home/pc/.ssh/authorized_keys` sem substituir as entradas anteriores. A impressão digital do host foi conferida por um canal SSH já confiável e está fixada em `known_hosts`; a verificação estrita continua ativa.

Esse acesso persiste entre sessões para agentes que executam **neste mesmo computador compartilhado**, desde que o estado local seja mantido e o PC e o computador compartilhado estejam acessíveis pela tailnet. Se algum deles estiver suspenso/offline, a conexão fica indisponível até voltar; exclusão ou recriação do ambiente pode exigir nova configuração. A chave não é copiada para outros computadores ou ambientes. Não copie a chave privada, não desative `StrictHostKeyChecking` e pare para verificar caso a chave do host mude. O acesso atual é ao usuário `pc`; `sudo -n` foi confirmado, então use privilégios elevados somente quando necessário.

A sessão Tailscale do PC estava online durante a verificação. Se o alias não funcionar, confira primeiro o estado Tailscale e os arquivos locais de configuração; não altere ACLs, tags ou a identidade do dispositivo para contornar uma falha.

## Abrir e validar o Paperclip

Use o nome MagicDNS privado aprovado e HTTPS, sem registrar o endereço privado literal neste documento:

```text
https://<MAGICDNS-DO-PC>:3100/
```

Na verificação de 16/10/2026, a rota `/api/health` respondeu HTTP 200. A porta 3100 é a entrada validada para a interface/API; não a substitua automaticamente por 3101.

Execute a CLI autenticada no próprio PC, onde a sessão existente está configurada:

```bash
n="$HOME/.hermes/node/bin/node"
p="$HOME/.paperclip/cli/current/node_modules/paperclipai/dist/index.js"
PAPERCLIP_BASE_URL="https://<MAGICDNS-DO-PC>:3100"
"$n" "$p" company list --api-base "$PAPERCLIP_BASE_URL" --json
```

A chamada foi validada e confirmou a organização PQBR (`be3980d6-51ae-4cee-b85f-923b4568188c`). Para listar issues da organização:

```bash
"$n" "$p" issue list --company-id be3980d6-51ae-4cee-b85f-923b4568188c --api-base "$PAPERCLIP_BASE_URL" --json
```

Não refaça login se a sessão existente funcionar; não copie tokens nem arquivos de autenticação. Uma resposta HTTP 200, sozinha, não comprova acesso autenticado: valide a CLI quando esse acesso for necessário.

## Temporal e banco de dados

No PC, a stack do PQBR está definida em `/home/pc/Workspace/PQBR/infra/temporal/docker-compose.yml`. O estado validado foi: Temporal Server e PostgreSQL saudáveis; UI em execução e HTTP 200; os três containers do Compose em execução. O `docker compose` disponível é a versão 5.5.1.

Para verificar a stack:

```bash
cd /home/pc/Workspace/PQBR
sudo -n docker compose -f infra/temporal/docker-compose.yml ps
sudo -n docker inspect -f '{{.Name}} state={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' \
  pqbr-temporal-temporal-1 pqbr-temporal-temporal-ui-1 pqbr-temporal-postgresql-1
```

Pontos de acesso observados no PC:

- Temporal Server/gRPC: `127.0.0.1:7233`.
- Temporal UI: `http://127.0.0.1:8233/`.
- PostgreSQL interno do Temporal: container `pqbr-temporal-postgresql-1`, porta 5432 na rede Docker. Essa porta **não** está publicada no host; não confunda com outros bancos/portas locais.

Checagens não destrutivas do banco:

```bash
sudo -n docker exec pqbr-temporal-postgresql-1 pg_isready -h 127.0.0.1 -p 5432
sudo -n docker exec pqbr-temporal-postgresql-1 sh -lc \
  'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atqc "SELECT 1"'
```

Ambas foram validadas; a consulta retorna apenas `1`. Para uma consulta SQL autorizada, use o `psql` dentro do container e as variáveis de ambiente já configuradas nele. Nunca exiba os valores dessas variáveis ou leia/imprima `.env` para obter acesso. A CLI `temporal` não está instalada separadamente no host nem no container do servidor; Docker Compose, `psql` no container e os scripts do projeto estão disponíveis (`infra/temporal/scripts/` e `scripts/temporal/`).

Para abrir a UI no navegador do mesmo computador compartilhado, crie um túnel SSH e mantenha-o ativo enquanto usa a página:

```bash
ssh -N -L 18233:127.0.0.1:8233 pqbr-pc
```

Depois abra `http://127.0.0.1:18233/`. O túnel foi testado e respondeu HTTP 200. Se a porta local 18233 estiver ocupada, escolha outra porta local livre; encerre o túnel com `Ctrl+C` ao terminar. A UI e o servidor Temporal não foram expostos em interfaces públicas.

## Ferramentas e escopo do repositório

No PC foram confirmados Git, Node.js, Docker/Compose e o acesso funcional à CLI do Paperclip. O diretório de trabalho é `/home/pc/Workspace/PQBR`; os arquivos de Temporal do projeto estão em `infra/temporal/` e `scripts/temporal/`. Comece com comandos de leitura e verifique `git status` antes de editar.

Para este trabalho, preserve alterações preexistentes; não faça commit ou push sem solicitação. Não consulte `docs/arquivo/`, `docs/pesquisas/` nem `docs/DECISOES-LOG.md` sem aprovação explícita do proprietário. Não crie outra organização, não altere configurações de autenticação/rede/serviços sem autorização específica e não exponha segredos.
