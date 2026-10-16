# Guia de acesso ao PC, à interface e à CLI do Paperclip

Este documento registra caminhos de acesso já verificados para apoiar agentes que trabalham no PQBR. É uma referência operacional, não concede permissões, não altera a política de rede e não substitui as regras do repositório ou as autorizações do proprietário.

Verificado em 16/10/2026.

## Resumo rápido

- Interface web do Paperclip: `https://<MAGICDNS-DO-PC>:3100/`
- API base para a CLI: `https://<MAGICDNS-DO-PC>:3100`
- Acesso ao terminal do PC: use o executor autorizado disponível no ambiente, como `debian-server status` e `debian-server exec '<comando>'` quando estiver disponível.
- SSH/Tailscale SSH não é requisito; se estiver bloqueado pela política do servidor, não tente contornar o bloqueio nem altere tags ou ACLs.

Substitua `<MAGICDNS-DO-PC>` pelo hostname privado MagicDNS fornecido pelo proprietário para o servidor `pc`. O hostname e o IP privados não são registrados neste guia para não espalhar dados de rede sensíveis.

## Acessar o PC

No ambiente que já possui o executor autorizado:

```bash
debian-server status
debian-server exec 'hostname; id'
```

O executor encaminha o comando ao Debian `pc` sem exigir SSH interativo. A disponibilidade do utilitário depende do ambiente do agente. Se ele não estiver disponível, não suponha que o PC esteja fora da rede e não tente substituir a identidade do dispositivo, usar credenciais de outro usuário ou contornar a política de SSH. Peça ao proprietário que habilite um caminho de execução aprovado para aquele agente.

## Abrir a interface do Paperclip

Use HTTPS pelo nome MagicDNS aprovado, na porta 3100:

```text
https://<MAGICDNS-DO-PC>:3100/
```

A página e a rota de saúde responderam com HTTP 200 quando verificadas no PC. A página inicial carregar não prova, por si só, que uma API autenticada está funcionando; valide também a CLI conforme a próxima seção.

## Validar a CLI autenticada

Execute a CLI no PC, com a sessão local já configurada. O comando abaixo listou cinco organizações e confirmou que PQBR estava disponível na verificação de 16/10/2026:

```bash
n="$HOME/.hermes/node/bin/node"
p="$HOME/.paperclip/cli/current/node_modules/paperclipai/dist/index.js"
PAPERCLIP_BASE_URL="https://<MAGICDNS-DO-PC>:3100"
"$n" "$p" company list --api-base "$PAPERCLIP_BASE_URL" --json
```

Para consultar issues, use o ID da organização PQBR e a mesma base:

```bash
"$n" "$p" issue list --company-id be3980d6-51ae-4cee-b85f-923b4568188c --api-base "$PAPERCLIP_BASE_URL" --json
```

Use o contexto de CLI existente no próprio PC. Não refaça login se a sessão já funciona; não copie, imprima ou envie o arquivo de autenticação, tokens ou senhas. Se a CLI não estiver autenticada, o proprietário deve concluir a autenticação localmente e confirmar que se trata da conta Owner da organização PQBR. Nunca solicite ou cole credenciais no chat.

## Erros comuns e diagnóstico

- O caminho validado usa HTTPS pelo nome MagicDNS e a porta 3100.
- A chamada HTTP pelo IP direto na porta 3100 retornou HTTP 400 durante a validação; isso não demonstrou falha de conectividade. Prefira HTTPS pelo nome MagicDNS aprovado.
- A porta 3100 é o endereço validado para acesso à interface/API. Não troque automaticamente para 3101, que pode ser uma porta interna de serviço.
- HTTP 200 na página ou em `/api/health` confirma apenas resposta do servidor; `company list` pela CLI confirma leitura autenticada da API.
- SSH bloqueado é uma regra de acesso do servidor, não um defeito que se resolva mudando identidade, tags ou ACL Tailscale. Use somente um executor já autorizado.
- Cada agente pode executar em um ambiente ou `HOME` diferente. A sessão CLI do usuário no PC não implica que outro agente herde essa sessão. Não copie tokens entre ambientes; solicite ao proprietário o acesso aprovado necessário.

## Segurança e escopo

Este guia não autoriza mudanças de rede, ACL, identidade, autenticação, organização ou configuração do Paperclip. Comece por comandos somente de leitura. Não crie uma segunda organização. Preserve a autenticação existente, não exponha segredos e peça autorização específica antes de alterações de acesso ou infraestrutura.
