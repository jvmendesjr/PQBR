# PQBR (Porquê BR)

Aplicação de produção do canal Porquê BR: Shorts de sátira leve, em stickman, sobre manias e rotinas dos brasileiros.

## Ordem de autoridade e de leitura (em conflito, vale o primeiro)

1. `docs/REGRAS.md`: todas as regras aprovadas pelo José; §0–§3 são a constituição.
2. `docs/SPEC.md`: requisitos funcionais e não funcionais, histórias e critérios de aceite.
3. `docs/ARQUITETURA.md`: ADRs, modelo de dados, workflows do Temporal, integração com o Paperclip, contratos Pydantic v2.
4. `docs/TESTES.md`: plano de testes, teste de 1 dia do Temporal e os 7 itens da validação.
5. `docs/ROADMAP.md`: tarefas, estado e próximo passo. **Qualquer agente retoma daqui.**
6. `docs/PLANO.md`: fases, portões do José, rollback e riscos.

`docs/RASTREABILIDADE.md` liga requisito → desenho → tarefa → teste.

## ⛔ Proibido consultar sem aprovação explícita do José (t287)

Arquivos de pré-construção **nunca** são consultados por agentes; ler qualquer um exige aprovação explícita do José, porque podem ser mal interpretados e aplicados em produção:

- `docs/CONTRATO-EDITORIAL.md` (rascunho; o que vale está no REGRAS §5)
- `docs/DECISOES-LOG.md` (registro histórico de decisões)
- `docs/pesquisas/` (pesquisas e referências)
- `docs/arquivo/` (material superado e legado)
- qualquer rascunho ou material legado, dentro ou fora do repositório

## Regras do repositório

- Dúvida ou conflito sem certeza: não adivinhar; marcar "EM CONSTRUÇÃO — aguardando José" (t323).
- Decisão nova entra no `DECISOES-LOG.md` e no `REGRAS.md` no mesmo commit; requisitos, desenho, testes e tarefas afetados são atualizados junto.
- Nada de senhas, tokens, cookies, dados pessoais, IPs ou IDs internos neste repositório.
