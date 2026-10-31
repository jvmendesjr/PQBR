# Índice — storyboard removido (29/10/2026, ordem do José)

O storyboard foi removido definitivamente do fluxo PQBR. Motivo do José: um encarte só com muitas cenas facilita o erro do agente; cenas individuais, com o movimento já bem definido no prompt, são mais determinísticas.

## O que saiu do fluxo ativo
- Board geral (Storyboard 1.3.0, coleção de FichaCena em um único JSON).
- Activity `storyboard_criar` e o prompt `PROMPT_STORYBOARD` (um insert só com todas as cenas).
- Gate `storyboard_ok` / `exigir_storyboard` em `flow_projeto.py`.
- Etapa de storyboard no `EpisodioWorkflow` e nos playbooks (`CRIACAO-README.md`, `flow.md`).
- Collection `Storyboard` nos projetos Flow e o campo `storyboard_ok` em `config/flow_projetos.json`.

## O que ficou, no lugar
- `CenaIndividual` (`src/pqbr/contratos/cena.py`, 1.0.0): a mesma validação por cena (norte, início, fim, movimento, plano, prompt de imagem, prompt de animação, refs), agora sem board. Cada cena é criada, validada e animada sozinha, uma por vez.
- Gate novo: `flow_projeto.exigir_antes_cenas` exige só `fichas_ok`.
- Regra suprema agente-primeiro, piloto e emergência: ver `docs/processos/CRIACAO-README.md` (versão 1.1.0).

## Preservado, não apagado (histórico)
- `scripts/_obsoleto/storyboard.py` (activity antiga) e `scripts/_obsoleto/storyboard_criar_arquivado.py`.
- O contrato antigo vive na história do git via `src/pqbr/contratos/cena.py` (renomeado de `storyboard.py`).
- O storyboard de 8 painéis do EP1003 v2 (t163u) fica só como histórico; não é etapa nem gate.
- Validadores de coleção que morreram com o board (ordem das cenas, alternância e protagonista único entre cenas): agora são regra de prompt (protagonista pinado por episódio) + verificador automático por cena, não mais validador de board.

## Não mudou nesta alteração
- Motion graphic (MG-05 / `pos_motion`): segurado, definição pendente, fora deste commit.
- Google Vids / Meta Vibes: continuam fallback, stubs, teste só no segundo momento.
- Publicação: continua dry-run, nada a público; item 5 das REGRAS (privado automático / voltar a público só por ordem do José) não foi alterado.
