# ESTADO ATUAL da PQBR — continue daqui

Fonte única de "onde estamos". Não repete o ROADMAP: aponta os itens por id. **Atualize este arquivo a cada correção ou pendência resolvida.** O hook pre-commit exige isso quando o commit toca ROADMAP, LACUNAS, DECISOES-LOG ou CHANGELOG, e o `registrar_alteracao` exige isso para `tipo` correcao ou pendencia_resolvida.

Atualizado: 26/10/2026 (t121u: checkboxes só leitura na aba Roadmap) · versão 0.16.2

## Onde estamos
- **Produção:** o lote do saldo está em `runtime/lote-saldo/` (um diretório por tema). O EP1002 olhos-da-cara foi reprovado e descartado (`runtime/lote-saldo/_descartado/`), e o tema voltou a `proposto`.
- **Publicação (ROADMAP F8-01):** o fluxo pelo Temporal está pronto (`PublicacaoAgendadaWorkflow` no `worker_episodio`). O upload real está bloqueado por falta das credenciais OAuth do YouTube.
- **Agente externo:** o servidor MCP 0.2+ só funciona pela tailnet. A memória escrita leva o autor (o cliente) e o commit. O protocolo obrigatório está no AGENTS.md. Hindsight: bank `pqbr` reclassificado, com as obsoletas apagadas.

## Próximo passo
José assiste o EP1003 cafe-fraco (`runtime/lote-saldo/cafe-fraco/cafe-fraco-final.mp4`). Só depois disso roda o LOOP do Gemini nesse episódio.

## Pendências abertas
| # | Pendência | Ref. ROADMAP | Dono | Bloqueio |
|---|---|---|---|---|
| P1 | EP1003 cafe-fraco: José assiste antes do LOOP do Gemini | Estado 26/10 · Próximo 5 | José | aguardando José |
| P2 | Publicação: (a) verificar qual perfil/conta do Camofox PQBR (127.0.0.1:9387) foi usado na tentativa bloqueada do Cloud Console (t107u) → (b) criar o OAuth do YouTube pelo Camofox (projeto `pqbr-publicacao`, chaves em `episodio.env`; se o Google pedir confirmação, José confirma na tela) → (c) upload pelo `PublicacaoAgendadaWorkflow`. Já feito: 2 etapas de juniormoedavirtual ativa (t106u); migração 0020 aplicada 26/10 16:56 e worker reiniciado 16:57 (t109u) | F8-01 · Estado 26/10 · Próximo 1 | agente | (b) confirmação do Google pelo José, se pedir |
| P3 | Teste: LOOP por cena vs o atual | Estado 26/10 · Testes pendentes | agente | depois do fluxo de publicação |
| P4 | **Feito (t108u/t109u).** Juiz por etapa (`gemini_juiz` v1.0.0): pré-produção usa 3.8 Flash; produção (VISUAL e LOOP) usa 4 Argon Baixo. O worker `pqbr-episodio-worker` foi reiniciado com OK do José às 16:57 (-03), e o poller está ativo na fila `episodio-pqbr`, ns `pqbr` | Estado 26/10 · DECISOES-LOG t109u | agente | concluído |
| P5 | Imagens de referência do elenco (`ASSET_personagem_{masculino,feminino}-v1`) | Estado 26/10 · Próximo 4 | agente | geração paga: OK do José (postergado) |
| P6 | Activity do Storyboard no Temporal (bloqueia a geração sem ele) | Estado 26/10 · Próximo 2; R2 | agente | postergado |
| P7 | **Feito (t108u).** O gate VISUAL agora tem `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco` (FichaCena/REGRAS §25), e cada um reprova sozinho. Validado no EP1002 (`loop-gemini-4argon-v2.json`): reprova, com S01 corte+grotesco, S04 corte e S02/S05/S09 boca | Estado 26/10 · CHANGELOG 0.14.0 | agente | concluído |
| P8 | 7 memórias `obsoleto_candidato` para revisão | `docs/operacao/hindsight-descarte-candidatos.md` | José | apagar exige OK |
| P9 | **Feito (t112u–t116u).** Papel `mantenedor` (política 1.4.0) lê todas as tags e o repo todo; pqbr-mcp 0.4.0 exclusivo do mantenedor; onboarding em `docs/operacao/onboarding-agente-externo.md`. Falta só entregar token por cliente novo (`scripts/mcp/novo_cliente.py <nome> mantenedor`) | Fase Conhecimento | agente | concluído |
| P10 | Reconsolidação do Hindsight em andamento (observações sendo refeitas) | Fase Conhecimento | Hindsight (automático) | só conferir |
| P11 | Merge da branch `feat/f8-01-publicacao-automatica` (já no GitHub) na main | — | José | merge/PR exige OK |
| P12 | ERR-01: revisar os erros aceitáveis | ERR-01 | agente | depois dos primeiros dias de produção |

## Painel
Aba **Roadmap** no painel (:8088): Próximos passos, Falta e Feito gerados deste arquivo e do ROADMAP por `scripts/mapa/roadmap.py` (via `gerar_index.py`; o pre-commit regenera quando ROADMAP/ESTADO-ATUAL/mapa mudam). Itens com ☑ (feito) e ☐ (falta/próximos), só símbolo, nada clicável. Só leitura.

## Operacional e persistência (verificado 26/10/2026 18:21 -03)
pqbr-mcp 0.4.0 (user unit, enabled, Restart=on-failure, linger=yes), hindsight-api (enabled, Restart=always), Docker DB/Temporal (`unless-stopped`), worker enabled. Comando de checagem e detalhes: `docs/operacao/onboarding-agente-externo.md` § Operacional e persistência.

## Como atualizar
Resolveu ou corrigiu algo: tire a linha da tabela (ou mude o bloqueio), ajuste "Próximo passo" e a data acima, faça o commit junto com o DECISOES-LOG/CHANGELOG e chame `registrar_alteracao` com `tipo` igual a `pendencia_resolvida` ou `correcao`.
