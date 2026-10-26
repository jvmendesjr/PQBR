# ESTADO ATUAL da PQBR — continue daqui

Fonte única de "onde estamos". Não repete o ROADMAP: aponta os itens por id. **Atualize este arquivo a cada correção ou pendência resolvida.** O hook pre-commit exige isso quando o commit toca ROADMAP, LACUNAS, DECISOES-LOG ou CHANGELOG, e o `registrar_alteracao` exige isso para `tipo` correcao ou pendencia_resolvida.

Atualizado: 26/10/2026 (t101u: mapa 13 das inovações; publicação fica para depois da análise do José) · versão 0.12.0

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
| P2 | Publicação: (a) José ativa a verificação em 2 etapas na conta juniormoedavirtual → (b) criar o OAuth do YouTube via Camofox (projeto `pqbr-publicacao`, chaves em `episodio.env`) → (c) aplicar a migração 0020 e reiniciar o worker → (d) upload pelo `PublicacaoAgendadaWorkflow` | F8-01 · Estado 26/10 · Próximo 1 | José (a); agente (b–d) | (a) José; (c) exige OK do José |
| P3 | Teste: LOOP por cena vs o atual | Estado 26/10 · Testes pendentes | agente | depois do fluxo de publicação |
| P4 | Teste: 4 Argon com raciocínio baixo vs 3.8 Flash | Estado 26/10 · Testes pendentes; LACUNAS | agente | depois do fluxo de publicação |
| P5 | Imagens de referência do elenco (`ASSET_personagem_{masculino,feminino}-v1`) | Estado 26/10 · Próximo 4 | agente | geração paga: OK do José (postergado) |
| P6 | Activity do Storyboard no Temporal (bloqueia a geração sem ele) | Estado 26/10 · Próximo 2; R2 | agente | postergado |
| P7 | Gate VISUAL: 3 critérios novos (lábios, enquadramento cortado, grotesco) | Estado 26/10 · Próximo 3 | agente | postergado |
| P8 | 7 memórias `obsoleto_candidato` para revisão | `docs/operacao/hindsight-descarte-candidatos.md` | José | apagar exige OK |
| P9 | `PQBR_KIT_PAPEL` nos configs do opencode | Fase Conhecimento | agente | — |
| P10 | Reconsolidação do Hindsight em andamento (observações sendo refeitas) | Fase Conhecimento | Hindsight (automático) | só conferir |
| P11 | Merge da branch `feat/f8-01-publicacao-automatica` (já no GitHub) na main | — | José | merge/PR exige OK |
| P12 | ERR-01: revisar os erros aceitáveis | ERR-01 | agente | depois dos primeiros dias de produção |

## Como atualizar
Resolveu ou corrigiu algo: tire a linha da tabela (ou mude o bloqueio), ajuste "Próximo passo" e a data acima, faça o commit junto com o DECISOES-LOG/CHANGELOG e chame `registrar_alteracao` com `tipo` igual a `pendencia_resolvida` ou `correcao`.
