# PQBR (Porquê BR)

Aplicação de produção do canal Porquê BR: Shorts de sátira leve, em stickman, sobre manias e rotinas dos brasileiros.

## Ordem de autoridade (em conflito, vale o primeiro)

1. `docs/REGRAS.md`: **todas as regras aprovadas pelo José**. Agentes leem este primeiro.
2. `docs/ARQUITETURA.md`: como as regras são executadas (ADRs, componentes, papéis, hipóteses).
3. `docs/PLANO.md`: fases, tarefas D1–D15, portões do José, pendências e riscos.

## ⛔ Proibido consultar sem aprovação explícita do José (t287)

Arquivos de pré-construção **nunca** são consultados por agentes. Ler qualquer um deles exige aprovação explícita do José, porque podem ser mal interpretados e aplicados em produção:

- `docs/CONTRATO-EDITORIAL.md` (rascunho; o que vale está no REGRAS §5)
- `docs/DECISOES-LOG.md` (registro histórico de decisões)
- `docs/pesquisas/` (pesquisas e referências)
- `docs/arquivo/` (material superado e legado)
- qualquer rascunho ou material legado, dentro ou fora do repositório

## Regras do repositório

- Dúvida ou conflito sem certeza: não adivinhar; marcar "EM CONSTRUÇÃO — aguardando José" (t323).
- Decisão nova entra no `DECISOES-LOG.md` e no `REGRAS.md` no mesmo commit.
- Nada de senhas, tokens, cookies, dados pessoais, IPs ou IDs internos neste repositório. Segredos só no `.env`/cofre do servidor.
