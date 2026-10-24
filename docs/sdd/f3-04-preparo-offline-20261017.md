# F3-04 — preparação offline, sem acesso ao Drive

**F3-04 continua aberto.** Foram adicionados apenas um planejador local e testes com arquivos sintéticos no checkout do `pc`. Os **24 testes novos passaram** e a regressão de segurança, unitários e kit terminou com **240 testes passando**. Nenhum backup fora do servidor foi realizado ou validado.

## O que foi encontrado

O [roadmap canônico](../ROADMAP.md) limita F3-04 aos dumps do banco do app e do Hindsight, com destino `PQBR/backups-db`. A dependência F3-03 está concluída; autorização Google e retenção remota continuam pendentes. Paperclip e Temporal não foram acrescentados ao escopo.

A inspeção de nomes, tamanhos e permissões encontrou sete dumps em `~/Backups/pqbr-db` e sete em `~/Backups/hindsight`, de 11 a 17/10/2026. Os mais recentes são `pqbr-20261017-0334.dump` e `hindsight-20261017-0345.dump`. As pastas têm modo `700` e os arquivos, `600`. Isso não comprova validade dos dumps nem restauração. Seus conteúdos não foram abertos, copiados ou hasheados nesta tarefa.

`rclone` não foi localizado no PATH do usuário `pc`; não foi instalado. Nenhum arquivo de configuração do rclone, token ou segredo foi consultado.

Os scripts atuais mantêm sete dumps locais e removem excedentes. Essa rotação **não define a retenção no Drive** e não deve ser transplantada automaticamente para ele. App: timer 03:30 com até dez minutos de atraso; Hindsight: 03:45 com até cinco minutos. Esses horários não garantem término dos dumps nem uma fotografia consistente entre bancos.

## Preparação adicionada

- `scripts/backup_offsite/planejar.py`: Python padrão, sem dependências adicionais. Recebe uma raiz explícita, examina apenas `pqbr-db/` e `hindsight/` e emite JSON na saída padrão. Não tem integração com rclone, funções de envio, exclusão, login, subprocessos ou rede.
- `tests/unit/test_f3_04_offline.py`: fixtures temporárias sintéticas; rede, subprocessos e `os.system` bloqueados durante o planejamento.

O JSON inclui nomes, tamanhos, SHA-256 e **destinos lógicos propostos** separados por origem dentro de `PQBR/backups-db`. Essa separação ainda não foi criada nem verificada no Drive. O plano é marcado `PLANO_OFFLINE_NAO_AUTORIZA_ENVIO`, com retenção pendente e sem exclusão. Não contém payload dos arquivos nem caminhos absolutos de origem.

Os testes cobrem nomes/datas/horários inválidos, ausência de origem ou dump final, arquivos vazios, dono e permissões inadequados, links simbólicos, diretório com nome de dump, mudança de arquivo durante leitura, repetibilidade e ausência de escrita/remoção. Temporários, logs e arquivos sem extensão final `.dump` são ignorados; um `.dump` de nome inesperado faz o plano falhar.

A CLI foi exercitada somente com fixtures: JSON válido para duas origens e código 2, sem JSON parcial ou caminho sensível na mensagem, para raiz inexistente. Fixtures foram removidas pelo harness ao terminar. O planejador não foi executado sobre os backups reais.

## Reproduzir no pc

No checkout `/home/pc/Workspace/PQBR`, sem serviços externos:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tests/unit -p test_f3_04_offline.py -v
# 24 testes: OK

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest \
  -q -p no:cacheprovider tests/seguranca tests/unit tests/test_kit.py
# 240 passed in 1.73s
```

## O que ainda depende de outra etapa autorizada

A instalação em escopo de usuário, seleção e validação do escopo OAuth mínimo e autorização Google não foram feitas. Acesso ao destino, privacidade e adequação da proteção de dumps sensíveis continuam sem teste. Nenhuma credencial foi solicitada.

Ainda faltam a decisão de retenção remota — sem presumir autorização para exclusão definitiva —, implementação de envio/verificação, coordenação com conclusão dos dumps, tratamento de falhas e validação de recuperação. **`rclone --dry-run` com um remote não é um teste offline:** pode carregar credenciais e acessar o Drive, portanto não foi executado. Não se validaram OAuth, rclone, quota, upload, download, integridade remota ou restauração PostgreSQL. Hash de fixture não substitui nenhum desses aceites. Este planejador também não comprova consistência entre bancos, atualidade dos dumps ou segurança contra alterações adversariais concorrentes nos diretórios.

## Limites preservados

Somente arquivos novos foram criados; os status preexistentes do Git foram preservados. Não houve commit, push, alteração de configuração, timer, serviço, ACL, rede, Tailscale ou ativação de produção. O roadmap canônico não foi editado. F7-02/G7 e PQBR-114 seguem pausados; F05-06 segue no-arm. Não foram consultados `docs/arquivo/`, `docs/pesquisas/` nem `docs/DECISOES-LOG.md`.
