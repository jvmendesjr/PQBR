# Plano: migrar GitNexus → codebase-memory-mcp (PQBR)

**Status: PLANO — não executar o Passo 3 sem o OK do José.**
**Data do levantamento: 2026-10-29 (America/Fortaleza). Branch de trabalho: `cursor/t132u-flow-imagem-849c`.**
**Motivo:** o GitNexus 1.6.12 usa licença PolyForm Noncommercial 1.0.0, que não serve
para uso com fins lucrativos. O substituto é o
[codebase-memory-mcp](https://github.com/deusdata/codebase-memory-mcp) (MIT, verificado
na página do repositório em 2026-10-29). Nada neste plano apaga nada: o que sai vai
para `_obsoleto/` com índice, e o GitNexus só é desinstalado depois de confirmação
expressa do José.

## 0. Regras duras (não negociáveis nesta migração)

- Sem sudo. Sem abrir porta de rede: MCP só por stdio. Nada de `--http`, nada de
  CBM Lens (`daemon start --open --port=9749` proibido), nada de `--ui`.
- Não mexer no node v20 do sistema. O node 22 do GitNexus (`~/.local/opt/node22`)
  fica intacto até a confirmação de desinstalação.
- Não reiniciar o gateway do Hermes. Não tocar no Camofox 9387 nem em regras de
  rede/tailscale sem OK do José.
- Não tocar no `pqbr-mcp` em produção sem OK: o Passo 3 exige reiniciar a unit
  `pqbr-mcp` (systemd de usuário, não o gateway do Hermes) para carregar o novo
  adaptador — esse reinício faz parte do OK pedido no Passo 2b.
- Sem `bash -x`, sem token/chave/cookie/senha em chat, commit, log ou neste plano.
  Segredos só via stdin ou arquivo `.env` 600. O token do pqbr-mcp usado neste
  levantamento (cliente `muse-mantenedor`, papel `mantenedor`) já existe no pc em
  `~/.pqbr/secrets/mcp_token_muse-mantenedor` (600) e em `~/.pqbr/.env-muse-mcp`
  (600); o valor nunca é exibido, e o acesso foi confirmado com uma consulta de
  leitura (`buscar_memoria "GitNexus"`, bank `pqbr`).
- Validação real, nada simulado. Versionamento SemVer + CHANGELOG + DECISOES-LOG
  no mesmo commit da migração, conforme o protocolo do repo.

## 1. O que o GitNexus é hoje na PQBR (levantamento verificado, não presumido)

### 1.1 Instalação (fora do repo, global do servidor, compartilhada)

| Item | Verificado em 2026-10-29 |
|---|---|
| Versão | `gitnexus --version` = 1.6.12 |
| Node | `~/.local/opt/node22` → node-v22.23.4, `node --version` = v22.23.4 |
| Wrapper | `~/.local/bin/gitnexus` (90 bytes): executa o node 22 sobre o binário do GitNexus |
| Registry global | `~/.gitnexus/registry.json` (8 KB, lista com 2 entradas) |
| Entrada 1 (escopo desta migração) | PQBR, repo principal, `.gitnexus/` no repo, último commit `7f89cfa`, branch `cursor/t132u-flow-imagem-849c`, indexado em 2026-10-29T20:34:46Z |
| Entrada 2 (FORA do escopo) | PQBR, cópia em `~/.pqbr/proposta-ferramentas-agentes/.gitnexus`, último commit `61bba28`, branch `cursor/proposta-ferramentas-agentes-b9f6`. Não migrar, não apagar, não tocar sem ordem separada do José |
| Índice do repo | `.gitnexus/` no repo, 215 MB, ignorado pelo git (`.gitignore`: `.gitnexus/`), 2.441 arquivos, 10.388 nós, 17.905 arestas, 289 comunidades, 299 processos, 0 embeddings |
| Interface usada pela PQBR | CLI local + MCP stdio. `--http` expressamente proibido (ARQUITETURA §12) |

### 1.2 Onde o GitNexus é usado de fato (e onde NÃO é)

**Usado — o núcleo da migração:**

- `src/pqbr/integrations/gitnexus.py` — único adaptador. Chama o binário por
  subprocesso (`PQBR_GITNEXUS_BIN`, padrão `~/.local/bin/gitnexus`), timeout 120 s,
  faz parse do JSON a partir do primeiro `{` da saída. Comandos permitidos:
  **só `query`, `context`, `impact`**. Qualquer outro (ex.: `cypher`) levanta
  `ValueError` — e há teste que exige isso. O resultado é filtrado por caminho
  (`filePath`) conforme o papel; papel desconhecido ou sem a ferramenta
  `gitnexus_consultar` ⇒ negado (fail-closed).
- `src/pqbr/mcp/servidor.py` — ferramenta `codigo` do pqbr-mcp
  (`gitnexus_consultar`, argumentos `comando` + `alvo` de até 200 caracteres).
  **Atenção de arquitetura:** o pqbr-mcp NÃO é o GitNexus. O pqbr-mcp é o servidor
  próprio da PQBR (0.4.0, 127.0.0.1:8791, só tailnet, só papel `mantenedor`,
  token Bearer por cliente). O GitNexus é apenas o backend do `codigo`.
  "Trocar o MCP dos agentes" significa, portanto, trocar o backend do `codigo`,
  mantendo o pqbr-mcp, seu token, sua política e sua interface. Não há MCP
  GitNexus direto a trocar: o perfil Hermes `pqbr` só tem `paperclip-pqbr` e
  `docs-pqbr`; a config opencode `pqbr-kit` não cita GitNexus.
- `config/politica_papeis.json` 1.5.0 — só dois papéis têm `gitnexus_consultar`:
  `dev` (código visível: `src/`, `tests/`, `scripts/`, `config/`, `docs/`) e
  `mantenedor` (código: `[""]` = repo todo). O contrato está em
  `src/pqbr/contratos/politica.py` (`PoliticaPapel.codigo`).
- `scripts/gitnexus/verificar.sh` — pré-requisito fail-closed (t84u–t86u):
  binário executável, versão ≥ 1.6.12, diretório `.gitnexus/` no repo e repo
  registrado no registry (`gitnexus list` contém o repo). Falha ⇒ sai ≠ 0.
- `scripts/gitnexus/hook-post-commit.sh` + `.githooks/post-commit` — reindexação
  em segundo plano após cada commit (`analyze --index-only .`, `nice -n 10`,
  não bloqueia o commit, log em `~/.cache/pqbr-gitnexus-reindex.log`).
  `core.hooksPath` do repo = `.githooks`. O `pre-commit` (barreira de
  segredos/PII + ESTADO-ATUAL exigido + regeneração do mapa) NÃO depende do
  GitNexus e fica como está.

**Não usado / verificado como ausente — não inventar migração para isso:**

- Skills do GitNexus no repo: **nenhuma**. A ARQUITETURA §12 diz explicitamente
  "sem AGENTS.md, skills ou hooks do GitNexus no repo". O diretório `skills/`
  do repo só tem `README.md`. Busca em configs de agentes no pc não achou
  nenhum `mcp.json` apontando para o GitNexus (só logs de sessão antigos que o
  citam, que não são configuração). Consequência: o instalador do CBM NÃO deve
  rodar com setup automático de clientes (`--skip-config` ou equivalente, a
  confirmar no binário fixado) — instalar skills/hooks globais tocaria configs
  de Cursor/Claude/Hermes sem ordem e sem necessidade.
- CLI GitNexus além de `query/context/impact`: `detect-changes`, `trace`,
  `cypher`, `check`, `wiki`, `augment`, `serve`, `publish`, `group` etc. existem
  no binário, mas **nenhum** é chamado pelo código da PQBR (busca em
  `src/`, `scripts/` e `tests/`). São superfície latente, não dependência.
- Vigia de versões: **hoje a vigia NÃO vigia o GitNexus.** Ver §1.3.

**Testes que tocam o GitNexus:**

- `tests/unit/test_politica_papeis.py` — papel desconhecido negado; `auditor`
  sem a ferramenta negado; `dev` filtra caminhos; `cypher` proibido.
  Usa executor falso (mock), não o binário — ou seja, testa o adaptador, não o
  GitNexus em si.
- `tests/unit/test_vigia_atualizacoes.py` — testa classificar/relatório e exige
  que os nomes vigiados incluam notebooklm-py, camoufox, temporal, pydantic-ai
  e 9router (não exige conjunto exato, então adicionar uma entrada é compatível).

**Docs que citam o GitNexus (a atualizar no Passo 5, não agora):**

- `AGENTS.md` (linhas do bloco t84u–t90u: GitNexus [agora], política por papel,
  licença aceita uso pessoal t90u).
- `docs/ARQUITETURA.md` §12 (linhas 381–386: pré-requisitos, global do servidor,
  política por papel, licença PolyForm, pqbr-mcp 0.4.0).
- `docs/ROADMAP.md` (linhas 389–390, 398: GitNexus [agora], política, licença).
- `CHANGELOG.md` (t84u–t86u, t90u, t97u: instalação, licença aceita, correção
  de memória superada da licença).
- `docs/DECISOES-LOG.md` (t84u–t86u, t90u, t97u).
- `docs/mapa/00-visao-geral.mmd` (nó K13), `09-agentes-responsabilidades.mmd`
  (aponta para o 13), `13-memoria-mcp-handoff.mmd` (subgrafo GitNexus 1.6.12).
- `docs/operacao/onboarding-agente-externo.md` (papel mantenedor: "Código
  (GitNexus): o repo todo").
- `docs/operacao/hindsight-descarte-candidatos.md` (só uma linha de memória
  superada que cita o GitNexus; é histórico, não regra — não reescrever o
  histórico, só registrar a migração no DECISOES-LOG novo).
- Memórias Hindsight (bank `pqbr`): dezenas de entradas citam GitNexus 1.6.12,
  licença PolyForm aceita para uso pessoal (t90u) e pré-requisito fail-closed.
  A migração não apaga memórias; o Passo 5 registra uma memória nova
  (decisão) que supera essas entradas, no mesmo padrão da correção t97u.

### 1.3 A vigia de sexta-feira 08:00 — o que ela é de verdade

- Workflow `VigiaAtualizacoesWorkflow` em `src/pqbr/workflows/atualizacoes.py`,
  registrado em `src/pqbr/workflows/worker.py`, Schedule Temporal
  `pqbr-vigia-atualizacoes` criado por `scripts/temporal/schedules.py`:
  **sexta-feira 08:00 America/Fortaleza, ativo, nunca aplica** (só lê, compara
  e grava relatório em `pqbr.relatorios_atualizacoes` + log; "Dev propõe; José
  decide e aplica"). Mapa: `docs/mapa/05-vigia-atualizacoes.mmd`.
- `VIGIADAS` hoje (7 entradas, nenhuma é o GitNexus): notebooklm-py (PyPI),
  camoufox (GitHub), temporalio SDK (PyPI), temporal CLI (GitHub),
  pydantic-ai-slim (PyPI), pydantic (PyPI), 9router (manual).
- `vigia_checar` hoje só sabe ler versão instalada via `importlib.metadata`
  num python indicado (fonte PyPI) ou deixar em branco (fonte GitHub/manual).
  **Não existe leitor de versão de binário npm/CLI.** Portanto "passar a vigia
  para a nova ferramenta" não é renomear uma entrada: é (a) adicionar a entrada
  do codebase-memory-mcp e (b) adicionar um leitor de versão instalada via
  `codebase-memory-mcp --version` + última versão via API de releases do
  GitHub (`DeusData/codebase-memory-mcp`), com o mesmo `classificar`
  (em_dia/patch/minor/major/desconhecido) e a mesma regra de nunca aplicar.
- O docstring de `atualizacoes.py` diz que o workflow "ainda não [estava]
  registrado em worker nem agendado" — isso está desatualizado: hoje ele está
  registrado e o Schedule existe (t517). O plano não muda o Schedule, só o
  conteúdo de `VIGIADAS` + o leitor.

## 2. A ferramenta substituta (verificado no upstream em 2026-10-29)

Fonte: https://github.com/deusdata/codebase-memory-mcp (página do repositório,
crawl de 2026-10-29; README do projeto). Licença: **MIT**.

- Binário nativo único, sem runtime de linguagem, sem Docker, sem API key,
  sem serviço hospedado. Processamento local; índice persistente em SQLite
  (padrão `~/.cache/codebase-memory-mcp/`).
- MCP: **17 ferramentas** no servidor nativo. MCP por stdio com o comando
  direto do binário (config manual documentada no README, sem argumentos).
- Ferramentas (README, seção MCP Tools): indexação — `index_repository`,
  `list_projects`, `delete_project`, `index_status`, `check_index_coverage`;
  consulta — `search_graph`, `trace_path` (alias `trace_call_path`),
  `detect_changes`, `query_graph`, `get_graph_schema`, `compare_graphs`,
  `get_code_snippet`, `get_file_outline`, `get_architecture`, `search_code`,
  `manage_adr`, `ingest_traces`.
- `index_repository`: indexação completa por padrão; modo `async: true` +
  poll com `status: true` para índices longos. Uma chamada MCP bem-sucedida
  registra o alvo no auto-sync **enquanto a sessão dona estiver conectada**
  (`auto_watch`, padrão true); chamadas CLI não registram watch. Isso é
  diferente do post-commit da PQBR (ver risco R4).
- Daemon de coordenação: o primeiro cliente daemon-backed inicia um daemon
  local compartilhado; todos os processos CBM precisam ser **o mesmo build
  exato, mesma ABI de coordenação e mesma raiz de cache** (`CBM_CACHE_DIR`),
  senão o processo novo falha antes de trabalhar (fail-closed do próprio CBM).
  O daemon NÃO é um servidor de rede para este plano: a UI Lens (porta 9749)
  é opcional e fica desligada.
- Versão mais recente vista neste levantamento: **0.12.1** (PyPI wrapper de
  2026-10-16 e relato de instalação de 2026-10-18). **Isso NÃO é o pin.**
  O pin só é fixado no Passo 3, no momento da instalação, conferindo a release
  atual do GitHub + `checksums.txt` (SHA-256) e registrando versão + hash no
  CHANGELOG/DECISOES. Se a release tiver mudado, o plano continua válido; o
  que muda é o número fixado, não o desenho.

## 3. Mapeamento: GitNexus → codebase-memory-mcp

Regra do adaptador novo: a interface externa do pqbr-mcp (`codigo`,
argumentos `comando` + `alvo`) **não muda**. O que muda é o backend, dentro
de um novo adaptador (ex.: `src/pqbr/integrations/codebase_memory.py`), com
o mesmo filtro por caminho e o mesmo fail-closed. A saída NÃO será
byte-idêntica à do GitNexus — a comparação do Passo 4 é semântica (mesmos
símbolos/arquivos, mesmos chamadores/chamados, mesmo blast radius nos
probes), não igualdade de string.

| Uso atual (GitNexus) | Equivalente no CBM | Como fica na PQBR | Grau |
|---|---|---|---|
| `codigo query <termo>` (fluxos/definições) | `search_graph` (estrutural + BM25 + semântico) + `search_code` (texto) | Adaptador resolve o termo, normaliza para `{definitions, filePath, ...}` e filtra por caminho do papel | Direto, com normalização |
| `codigo context <símbolo>` (visão 360: chamadores, chamados, processos) | `search_graph` (resolver o símbolo) + `trace_path` (mode `calls`) + `get_code_snippet` + `get_file_outline` | Adaptador compõe a visão 360 a partir dessas chamadas; **direção chamador/chamado e profundidade devem ser validadas nos probes do Passo 4, não presumidas** | Composto, a validar |
| `codigo impact <símbolo>` (blast radius, direção upstream/downstream, profundidade 3, risco) | `detect_changes` (diff → símbolos afetados + blast radius + risco) para diffs; para um símbolo isolado, `trace_path` upstream com profundidade explícita | Adaptador: se o alvo for um diff/commit, usa `detect_changes`; se for um símbolo, usa `trace_path` upstream (profundidade 3, como o padrão GitNexus) e classifica risco a partir do resultado. **A classificação de risco do GitNexus não tem equivalente 1:1 documentado — validar nos probes** | Parcial, a validar |
| `analyze --index-only .` (reindexação) | `index_repository` (MCP) / `codebase-memory-mcp cli index_repository --repo-path <repo>` (CLI) | Post-commit chama a CLI em segundo plano, sem bloquear, mesmo padrão de log; índice do zero no Passo 3 (ver §4) | Direto |
| `list` / `status` | `list_projects` / `index_status` | Novo `scripts/codebase-memory/verificar.sh` usa esses comandos para o pré-requisito fail-closed | Direto |
| `clean` / `remove` (apagar índice) | `delete_project` | Só após validação do Passo 4 e OK do José; o índice GitNexus fica preservado em `_obsoleto/` até lá (ver §5) | Direto, com portão |
| `detect-changes` (CLI, não usado pelo adaptador) | `detect_changes` (mesmo nome, ferramenta MCP) | Passa a existir via adaptador quando o alvo for diff — ganho real, não perda | Direto |
| `cypher` (CLI; **bloqueado** no adaptador PQBR, com teste) | `query_graph` (subconjunto read-only de openCypher; escrita/MERGE falha) | **Continua bloqueado no adaptador.** Não expor `query_graph` pelo `codigo` sem decisão nova do José: a proibição atual é uma decisão de segurança, não uma limitação técnica a "corrigir" de passagem | Sem equivalente exposto (por decisão) |
| `check` (checagens estruturais do grafo) | `check_index_coverage` + `index_status` (cobertura/frescor, não checagem estrutural) | Usado pelo `verificar.sh` novo como sinal de saúde, não como substituto de `check` | Parcial |
| `wiki` (gerar wiki do grafo) | `get_architecture` (visão geral) + `manage_adr` (ADRs no índice) | **Sem equivalente.** Não é usado pela PQBR hoje, então não há perda funcional; não gerar wiki por outro caminho sem ordem | Sem equivalente, sem uso |
| `trace` (caminho mais curto entre dois símbolos) | `trace_path` (modos `calls`, `data_flow`, `cross_service`, `topology`, `deploy`, `run`; profundidade 1–15) | Disponível via adaptador se o probe do Passo 4 validar; caso contrário, fica fora do `codigo` até decisão | A validar |
| `augment` (hooks: enriquecer busca com contexto do grafo) | Hooks do CBM por cliente (Claude/Codex/etc., fail-open, só contexto, não bloqueiam a chamada) | **Não instalar.** A PQBR não usa hooks do GitNexus; o equivalente funcional na PQBR é o post-commit (reindex) + o `codigo` do pqbr-mcp. Hooks globais do CBM tocariam configs de outros clientes sem necessidade | Sem equivalente adotado (por decisão) |
| `serve` / `mcp --http` | Servidor HTTP / Lens | **Proibidos nos dois.** O CBM na PQBR é stdio/CLI local, como o GitNexus era | Proibido |
| Embeddings (índice GitNexus: 0) | Busca semântica embutida no `search_graph` | Sem perda: o índice atual nem usa embeddings | N/A |
| Comunidades (289) / processos (299) do grafo GitNexus | Clusters/hotspots/`get_architecture` do CBM | **Sem equivalente 1:1.** A saída de `query` que listava "processes" muda de forma. Quem consumir `codigo query` deve ser avisado disso no CHANGELOG/DECISOES | Gap documentado |

### O que o novo adaptador DEVE preservar (contrato, não detalhe)

1. Filtro por caminho do papel (`PoliticaPapel.codigo`), aplicado **depois**
   de cada chamada CBM, sobre todo `filePath` devolvido — o CBM não tem
   conceito de papel, então o filtro não pode ser "delegado" a ele.
2. Fail-closed: papel desconhecido, papel sem `gitnexus_consultar` (o nome da
   ferramenta na política pode ser renomeado para `codigo_consultar` no Passo 3
   — decisão a confirmar no OK, com migração da política 1.5.0 → 1.6.0 — ou
   mantido como está para minimizar diff; o plano recomenda renomear com
   teste atualizado, porque manter o nome `gitnexus_*` após a troca mente
   sobre o backend), comando fora da lista permitida, alvo vazio, timeout,
   projeto errado ⇒ negado/erro, nunca resultado parcial silencioso.
3. Confinamento ao repo: o adaptador fixa o projeto CBM da PQBR
   (nome/raiz) e, se suportado na versão fixada, `CBM_ALLOWED_ROOT` apontando
   para o repo. Nunca indexar/consultar outro projeto pelo `codigo` da PQBR,
   e nunca usar o índice da cópia `proposta-ferramentas-agentes`.
4. Desambiguação explícita: hoje o `context`/`impact` do GitNexus falha
   (exit 1 → erro no MCP) quando o nome é ambíguo (ex.: `consultar` tem 12
   candidatos; o adaptador atual não passa `-f`/`-u`). O adaptador novo deve
   devolver "ambíguo: N candidatos (arquivo:linha)" em vez de escolher o
   primeiro silenciosamente — e o Passo 4 deve ter um probe ambíguo.
5. Timeout e erro: manter o padrão de 120 s do adaptador atual (ou justificar
   mudança no Passo 3, com o tempo real de indexação medido).

## 4. Passo 3 — sequência de aplicação (só após o OK do Passo 2b)

Ordem, sem pular etapas; cada etapa só avança se a anterior estiver verde.
Nenhuma etapa reinicia o gateway do Hermes, toca o Camofox 9387 ou abre porta.

1. **Fixar a versão.** Conferir a release atual do GitHub, baixar o artefato
   Linux do release (não `curl | bash` sem inspeção: baixar, conferir
   `checksums.txt` SHA-256, inspecionar o `install.sh` do artefato antes de
   rodar qualquer coisa dele). Instalar o binário em escopo de usuário
   (`~/.local/bin/codebase-memory-mcp`, sem sudo, sem tocar no node v20 do
   sistema e sem tocar no node 22 do GitNexus). Registrar versão + SHA-256 no
   CHANGELOG/DECISOES. Rodar o instalador com setup de clientes desligado
   (`--skip-config` ou equivalente da versão fixada); se a versão fixada não
   oferecer esse desligamento, instalar o binário manualmente e NÃO rodar o
   setup — documentar o desvio no DECISOES.
2. **Indexar do zero.** O índice GitNexus não é portável (formato próprio,
   215 MB, `.gitnexus/`). Rodar `index_repository` (ou a CLI equivalente)
   para o repo principal, do zero, com `async` + poll de `status` se o índice
   for longo (o README avisa que chamadas síncronas longas podem ser
   canceladas pelo cliente). Medir tempo e tamanho. O contexto útil do índice
   antigo que vale como documento (estatísticas, últimos commits, probes do
   Passo 4) vira texto neste plano + no DECISOES — não há conversão de grafo.
3. **Trocar o backend do `codigo`.** Criar `src/pqbr/integrations/codebase_memory.py`
   (nome a confirmar), adaptar `src/pqbr/mcp/servidor.py` para chamá-lo
   (descrição da ferramenta `codigo` passa a citar o CBM, sem citar GitNexus),
   atualizar `config/politica_papeis.json` (versão 1.6.0) e os testes
   (`test_politica_papeis.py`: mesmo comportamento, novo executor falso;
   manter o teste de `cypher` proibido, agora como `query_graph` proibido).
   **Não** apagar o `gitnexus.py` neste passo: movê-lo para `_obsoleto/`
   (ver §5).
4. **Vigia, hooks e scripts.** Adicionar a entrada do CBM em `VIGIADAS` +
   leitor de versão de binário em `vigia_checar` + teste em
   `test_vigia_atualizacoes.py`; atualizar `docs/mapa/05-vigia-atualizacoes.mmd`
   e regenerar o índice do mapa. Trocar `scripts/gitnexus/` por
   `scripts/codebase-memory/verificar.sh` (mesmo padrão fail-closed: binário,
   versão fixada, projeto listado em `list_projects`, índice fresco em
   `index_status`) e `hook-post-commit.sh` (mesmo padrão: segundo plano,
   não bloqueia, log próprio). O `pre-commit` não muda.
   **Decisão em aberto para o OK:** o post-commit novo deve chamar a CLI
   CBM em segundo plano (recomendado, espelha o comportamento atual) ou
   depender do `auto_watch` do CBM? O `auto_watch` só vigia enquanto uma
   sessão MCP dona estiver conectada — não é um substituto durável do
   post-commit. Recomendação do plano: post-commit com CLI, `auto_watch`
   deixado no padrão, sem depender dele.
5. **Mover o GitNexus para `_obsoleto`, sem desinstalar.** Ver §5. O binário,
   o wrapper e o registry ficam intactos e utilizáveis para o rollback e
   para o Passo 4 (comparação lado a lado). Só depois do Passo 4 verde e de
   confirmação expressa do José é que se cogita `gitnexus uninstall` /
   remoção do node 22 — fora deste plano.
6. **Reiniciar só o `pqbr-mcp`.** `systemctl --user restart pqbr-mcp` (unit
   de usuário, não gateway do Hermes), conferir `/saude` = 0.4.0 (ou a versão
   nova, se o Passo 3 subir a versão do pqbr-mcp — fora do escopo mínimo) e
   rodar `onboarding` + `buscar_memoria` + `codigo` pelo cliente
   `muse-mantenedor` antes de declarar o passo concluído.

## 5. `_obsoleto/` — o que vai para onde (nada apagado)

| Item que sai | Destino | Índice / observação |
|---|---|---|
| `src/pqbr/integrations/gitnexus.py` | `docs/_obsoleto/` não serve para código — mover para um diretório `_obsoleto/` fora do pacote, com índice, **ou** manter o arquivo no git history e registrar a remoção no DECISOES (decisão para o OK: o plano recomenda mover o arquivo para `scripts/_obsoleto/gitnexus.py` + índice em `docs/_obsoleto/INDICE-migracao-cbm.md`, porque `docs/_obsoleto/` é para documentos, não código) | Índice lista: arquivo, versão 1.6.12, motivo (licença), data, commit de origem |
| `scripts/gitnexus/verificar.sh` e `hook-post-commit.sh` | Mesmo `_obsoleto/` de scripts, com índice | O hook ativo em `.githooks/post-commit` é **trocado**, não duplicado: o arquivo antigo vai para `_obsoleto/` e o novo aponta para o script CBM |
| `~/.local/bin/gitnexus` (wrapper) + binário no prefixo node 22 | `~/.local/bin/_obsoleto/gitnexus` (wrapper) + registro no índice; o prefixo node 22 em si fica intacto até a desinstalação confirmada | **Não** rodar `gitnexus uninstall` no Passo 3 — ele removeria entradas MCP/skills/hooks de editores, fora do escopo e fora do controle deste plano |
| `.gitnexus/` do repo (215 MB, fora do git) | **Ponto em aberto para o OK (não decidir em silêncio):** mover para dentro de `docs/_obsoleto/` inflaria o git se alguém der `git add` ali; renomear no lugar para `.gitnexus-obsoleto-1.6.12` + entrada no `.gitignore` evita o git mas foge do padrão `_obsoleto/`; mover para fora do repo (ex.: `~/.local/share/_obsoleto/gitnexus-pqbr-1.6.12/`) preserva sem tocar no git. Recomendação: fora do repo, com índice apontando o caminho, e o registry global preservado (não apagar a entrada, para o rollback) | Índice deve registrar: tamanho, estatísticas (2.441 arquivos, 10.388 nós, 17.905 arestas), último commit `7f89cfa`, data da preservação |
| Docs antigas que citam GitNexus como vigente | Atualizadas no lugar (ARQUITETURA, ROADMAP, AGENTS, onboarding) + o texto antigo preservado no DECISOES-LOG (que é log, não se reescreve) | As seções superadas do Hindsight seguem o padrão t97u: memória nova supera, não apaga |

## 6. Passo 4 — verificação (mesmas consultas, lado a lado, antes de qualquer desinstalação)

Probes mínimos, rodados nas duas ferramentas, com o GitNexus ainda instalado.
"Passar" = mesmo símbolo/arquivo/caller/callee relevante, não string idêntica.
Qualquer probe vermelho ⇒ rollback (§7), sem avançar.

1. `query` / `search_graph` para: `gitnexus` (o próprio adaptador antigo),
   `VigiaAtualizacoesWorkflow`, `registrar_alteracao`. Comparar os 5 primeiros
   símbolos/arquivos de cada lado.
2. `context` para um símbolo não ambíguo (ex.: `VigiaAtualizacoesWorkflow`
   ou `consultar` com arquivo desambiguador) — chamadores + chamados.
3. `impact` para o mesmo símbolo, direção upstream, profundidade 3.
4. Probe ambíguo: `consultar` sem desambiguador — os dois lados devem
   devolver ambiguidade explícita, nunca um candidato arbitrário.
5. Probe negado: papel `auditor` sem a ferramenta, comando `cypher` /
   `query_graph`, papel desconhecido — os três devem negar nos dois lados
   (no lado novo, negar antes de qualquer chamada CBM).
6. `detect_changes`: um diff real pequeno (ex.: tocar um comentário num
   arquivo vigiado, sem commit de produção) — comparar símbolos afetados.
7. Suíte de testes: `PYTHONPATH=src .venv/bin/python -m pytest -q tests`
   (suíte inteira verde, como exige o protocolo de módulo novo; no mínimo
   `test_politica_papeis.py` + `test_vigia_atualizacoes.py` verdes antes de
   qualquer commit da migração).
8. Vigia: rodar `vigia_checar` para a entrada do CBM com a versão instalada
   fixada e a última release do GitHub. Critério: se a versão fixada for a
   última, `em_dia`; se houver release mais nova, a classificação deve ser
   `patch`/`minor`/`major` (nunca `em_dia` por engano) e o relatório deve
   listar a proposta sem aplicar nada. O Schedule de sexta 08:00 **não** é
   disparado manualmente para "provar" — o teste é da activity, e o próximo
   disparo real de sexta é o que valida em produção, com o relatório no
   Postgres conferido na segunda seguinte.
9. Frescor: commit de teste no post-commit novo deve atualizar o índice CBM
   (conferir em `index_status`: geração/data posterior ao commit), sem
   bloquear o commit.

## 7. Riscos e rollback

| # | Risco | Mitigação no plano |
|---|---|---|
| R1 | Versão fixada muda entre este plano e o Passo 3; README/API do CBM mudam | Pin só no Passo 3, com SHA-256 registrado; se a API de ferramentas diferir do README lido em 2026-10-29, parar e reapresentar o mapeamento ao José antes de adaptar no improviso |
| R2 | Daemon CBM com build/cache divergente (CLI vs MCP) falha por admission barrier | Uma única versão instalada, um único `CBM_CACHE_DIR`, todos os processos do mesmo build; verificar `daemon status`/logs em `~/.cache/codebase-memory-mcp/logs/` no Passo 3 |
| R3 | Saída do CBM não cobre `processes`/comunidades do GitNexus; consumidores de `codigo query` quebram por forma | Contrato do adaptador normaliza a saída; CHANGELOG/DECISOES avisam a mudança de forma; probes do Passo 4 cobrem os 3 usos reais, não todos os campos |
| R4 | Frescor: `auto_watch` some quando a sessão MCP fecha; índice fica velho entre commits | Post-commit com CLI em segundo plano (recomendado, §4.4), não dependência do `auto_watch`; probe de frescor (§6.9) |
| R5 | CBM indexa mais/menos que o GitNexus (`.gitignore` + `.cbmignore`, symlinks sempre ignorados, `.venv/` etc.) | Conferir `check_index_coverage` para os caminhos dos papéis (`src/`, `tests/`, `scripts/`, `config/`, `docs/`) no Passo 4; ajustar `.cbmignore` só com registro no DECISOES |
| R6 | Segunda entrada do registry (cópia `proposta-ferramentas-agentes`) é confundida com o projeto principal | Adaptador fixa nome/raiz do projeto principal; a cópia não é tocada nem listada como alvo |
| R7 | Instalador do CBM altera configs de clientes (Hermes/Cursor/Claude) ou abre a Lens | Setup de clientes desligado (§4.1); Lens desligada; nenhuma porta aberta; gateway do Hermes não reiniciado |
| R8 | Reinício do `pqbr-mcp` derruba o `codigo` durante a migração | Reinício só após adaptador + testes verdes; janela comunicada no resumo ao José; rollback é restaurar o adaptador antigo + reiniciar de novo (mesma unit) |
| R9 | Licença MIT do CBM tem terceiros vendored (grammars, etc.) | No Passo 3, guardar cópia do `LICENSE` + `THIRD_PARTY.md` da release fixada junto ao índice de `_obsoleto/`/documentação da migração e citar no DECISOES |

**Rollback (ordem, se qualquer probe do Passo 4 falhar ou o José mandar voltar):**

1. Parar de usar o adaptador CBM: restaurar `src/pqbr/integrations/gitnexus.py`
   (de `_obsoleto/` ou do git), `scripts/gitnexus/`, `.githooks/post-commit`
   apontando para o hook antigo e `config/politica_papeis.json` 1.5.0.
2. Restaurar o `.gitnexus/` do local de preservação (§5) e conferir
   `scripts/gitnexus/verificar.sh` verde + `gitnexus list` com o repo.
3. Reiniciar só o `pqbr-mcp` e rodar os probes do Passo 4 no lado GitNexus.
4. Manter o índice CBM (não apagar de imediato) até o José decidir se ele
   fica como experimento ou é removido com `delete_project`.
5. Registrar o rollback no DECISOES-LOG + CHANGELOG (versão nova, sem apagar
   o registro da tentativa) e avisar o José pelo mesmo canal do Passo 2b.
   **O rollback não desinstala o CBM nem reinstala o GitNexus** — ambos ficam
   instalados até decisão expressa, porque a desinstalação é o passo
   irreversível que o plano proíbe sem confirmação.

## 8. Passo 5 — registro (só após o Passo 4 verde)

- ADR nova em `docs/sdd/` (número seguinte aos existentes: 001, 003, 011 —
  confirmar o próximo número livre no momento do registro, não presumir).
- CHANGELOG (SemVer, nova versão) + DECISOES-LOG (mesmo commit) +
  `docs/ESTADO-ATUAL.md` (o pre-commit exige quando ROADMAP/DECISOES/CHANGELOG
  mudam) + `docs/ROADMAP.md` (item GitNexus → CBM, com portão).
- `docs/ARQUITETURA.md` §12 reescrita para o CBM (backend do `codigo`,
  pré-requisito fail-closed novo, licença MIT, stdio, sem Lens, sem HTTP).
- Mapa visual: `docs/mapa/13-memoria-mcp-handoff.mmd` (subgrafo GitNexus →
  CBM), `00-visao-geral.mmd` (nó K13), `05-vigia-atualizacoes.mmd` (entrada
  CBM), regenerar `docs/mapa/index.html` com `scripts/mapa/gerar_index.py`
  (nunca editar o HTML à mão).
- Memórias: `registrar_alteracao` (ou `registrar_memoria`, se não houver
  commit único) com o commit da migração, tags de decisão, citando arquivos —
  pelo cliente `muse-mantenedor`, sem exibir token.
- Reporte ao José: commit, o que mudou, o que ficou pendente (ex.: decisão
  do §5 sobre o `.gitnexus/`, decisão sobre renomear `gitnexus_consultar`,
  desinstalação do GitNexus — todas pendentes até ordem expressa).

## 9. Perguntas que só o OK do José resolve (não decidir em silêncio)

1. Aprova o desenho acima, em especial: backend do `codigo` trocado, pqbr-mcp
   mantido, `query_graph`/`cypher` continuando bloqueado, e instalador do CBM
   sem setup de clientes?
2. Aprova o reinício da unit `pqbr-mcp` (não do gateway do Hermes) no Passo 3?
3. Onde preservar o `.gitnexus/` de 215 MB (§5): fora do repo (recomendado) ou
   outro local?
4. Renomear a ferramenta da política `gitnexus_consultar` → `codigo_consultar`
   (com política 1.6.0 e testes atualizados) ou manter o nome antigo para
   minimizar o diff?
5. Post-commit novo: CLI CBM em segundo plano (recomendado) ou depender do
   `auto_watch`?
6. Após o Passo 4 verde, o GitNexus pode ser desinstalado, ou fica instalado
   em `_obsoleto/` até ordem posterior? (O plano assume: fica, até ordem
   expressa.)

**Resumo para o Telegram (Passo 2b):** ver a mensagem separada enviada ao José.
Sem o OK dele, o trabalho para aqui: plano escrito, nada instalado, nada
trocado, GitNexus 1.6.12 intacto e em uso.
