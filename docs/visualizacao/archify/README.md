# Visualização Archify da PQBR — proposta em branch

> **Status: PROPOSTA, não aprovada pelo José, não mergeada na main.**
> Branch: `feat/archify-visualizacao` · Worktree: `~/.pqbr/archify-visualizacao`
> Base: commit `82a5529` (v0.31.1, t169u). Painel ao vivo só na tailnet,
> porta 8899 (`pqbr-arquitetura.html`).
> Serviço no `pc`: `pqbr-archify-panel.service` (usuário, enabled), servindo
> `~/pqbr-archify-panel/` na porta 8899, amarrado ao IP Tailscale — sem Funnel,
> sem 0.0.0.0, sem exposição pública.

## O que é

Um diagrama interativo de arquitetura gerado com
[Archify](https://github.com/tt-a1i/archify) 3.2.0, a partir do próprio
repositório, com fontes pinadas no commit da base. Ele cobre, em um só painel:

- fluxo canônico: Mestre NotebookLM → `BriefingEfemerico` → efêmero →
  `DirecaoCenas` 2.0.0 → Flow (adapter pendente), com o Temporal orquestrando;
- contratos Pydantic v2 em `src/pqbr/contratos/` (SemVer em `VERSOES`) e os
  gates de aprovação do José (sinal do Temporal, fail-closed);
- infra no servidor `pc`: Temporal, workers, Camofox, 9router, os dois
  Postgres separados, Hindsight, pqbr-mcp e o painel Temporal UI / mapa :8088;
- piloto EP1003 v3 e as pendências registradas no `ESTADO-ATUAL`.

O HTML é autossuficiente: dá para baixar e abrir sem o Archify instalado.
O `candidate.json` é a fonte do diagrama; o HTML é o artefato gerado.

## O que NÃO é

- Não substitui `docs/mapa/` (Mermaid, gerado do código, servido em :8088).
  **Agentes nunca alteram o mapa sozinhos; mudança no mapa só por proposta
  aprovada pelo José (t517).** Este painel é uma visualização complementar,
  em branch de proposta, e não altera nenhum `.mmd` nem o `index.html` do mapa
  por decisão própria — se o hook pre-commit regenerar o `index.html` ao
  tocar o `ESTADO-ATUAL`, isso vai no commit como efeito do hook e deve ser
  conferido na revisão, não tratado como decisão de mapa.
- Não é decisão do José, não entra em `docs/REGRAS.md` nem em
  `docs/DECISOES-LOG.md` nesta branch. Virar processo canônico, entrar no
  REGRAS e mergear na main exigem OK explícito do José.
- Não é revisão visual: os gates automáticos do Archify passaram
  (validate, deliver, check, browser-check), mas há cruzamentos nas linhas
  longas de retorno (16 apontados pelo Archify). Leia seguindo os caminhos
  clicáveis do painel, não só pelas linhas.

## Regra de atualização (item para os agentes)

**Toda vez que arquitetura, fluxos, contratos ou infra mudarem de verdade
(novo workflow/activity, novo contrato ou versão, novo serviço, mudança de
cadeia Flow/Vids/Vibes, mudança de Postgres/filas), o agente que fez a
mudança deve, no mesmo trabalho:**

1. Atualizar `candidate.json` (nós, relações e fontes pinadas no commit novo)
   e regenerar o HTML com o Archify, sem inventar nó, relação ou fonte;
2. Atualizar este README e o `docs/ESTADO-ATUAL.md` com o que mudou no painel;
3. Registrar a alteração no MCP (`registrar_alteracao`, tipo `alteracao`,
   com o commit), citando os arquivos do painel;
4. Conferir o painel servido na tailnet (:8899) depois de regenerar.

Mudança só de texto, de roteiro ou de ficha visual não obriga regenerar o
painel, salvo se mudar a arquitetura que ele mostra. Se o painel divergir do
código, sinalizar a divergência em vez de corrigir o painel por palpite.

## Como regenerar

No worktree da branch, com o Archify clonado em `~/archify` no `pc`:

```bash
cd docs/visualizacao/archify
node ~/archify/archify/bin/archify.mjs finalize architecture \
  candidate.json pqbr-arquitetura.html \
  --repo-root <raiz-do-worktree> --quality showcase --json
```

Depois, copiar o HTML gerado para `~/pqbr-archify-panel/` no `pc` e conferir o painel na tailnet, porta 8899 (o serviço já serve esse
diretório; não é preciso reiniciar nada para um arquivo novo, só copiar).

Para uma revisão visual nova, o Archify pede `--out-dir` próprio a cada
execução após o primeiro `browser-check`; não reutilizar o diretório de
evidência de um HTML anterior.

## Por que o HTML não está commitado nesta branch

O HTML gerado pelo Archify contém, no JavaScript do visualizador, atribuições
com o nome de variável `token` (ex.: o código do próprio visualizador, não
um segredo do projeto). A barreira de segredos do PQBR
(`scripts/seguranca/verificar_segredos.py`, pre-commit) sinaliza essas linhas
como possível segredo e bloqueia o commit. Adicionar uma exceção em
`.segredos-permitidos` exige OK explícito do José — e esta branch não o tem.
Por isso, **nesta branch o HTML não é commitado**: o que vai ao repo é a
fonte (`candidate.json`) e o processo, e o HTML continua sendo gerado e
servido a partir dela. Quando o José aprovar a exceção (ou outra forma de
publicar o artefato), o HTML gerado pode entrar no commit seguinte sem mudar
o diagrama.

## Arquivos nesta pasta (commitados)

- `candidate.json` — fonte do diagrama (editar esta, nunca o HTML à mão).
- `pqbr-arquitetura.finalize-summary.json` — resumo da última entrega
  aprovada nos gates automáticos.
- `README.md` — este processo.

O `pqbr-arquitetura.html` gerado fica fora do commit, em
`~/pqbr-archify-panel/` no `pc`, servido só na tailnet, porta 8899.
