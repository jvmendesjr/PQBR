# AGENTES da PQBR

Vigente desde a ADR-011 (t474/t512): agentes PydanticAI dentro de activities do Temporal. Canal do José: bot próprio do Telegram (t538) e sinais do Temporal. Painel: Temporal UI e o mapa em `docs/mapa/`.

O texto que ainda descrevia contratação, issues e rotinas do Paperclip está em `docs/_obsoleto/AGENTES-operacao-paperclip-20261011.md`. A equipe de 14 agentes está em `docs/_obsoleto/agentes-equipe-14-t395.md`. Esses arquivos não são instrução.

## Equipe (9 papéis)

| Papel | Onde a persona está | No fluxo |
|---|---|---|
| Diretor | `company/agents/` | orquestra; não aplica efeito externo |
| Líder Editorial | idem | já entra em `ReposicaoTemasWorkflow` (valida a resposta do motor e grava temas) |
| Pesquisador de Origem | idem | agente |
| Auditor | idem | activity `auditor_gemini` existe; o `EpisodioWorkflow` ainda não a chama |
| Compliance (`lider-compliance`) | idem | conformidade da conta |
| Guardião de Segurança | idem | segurança da conta; não corrige produção |
| Observador | idem | mede; não corrige |
| Dev | idem | fusão de Corretor e Revisor; indica e propõe, não aplica |
| Motion (`motion`, t145u) | idem | monta o bloco de motion graphics do porquê a partir do catálogo (`src/pqbr/pos/motion/catalogo/`); texto só do bloco de números travados; não julga o próprio resultado (Auditor julga); ainda sem activity no worker |

Roteirista, SEO e Caçador Sazonal são etapas de workflow que chamam o NotebookLM. Comunidade está adiada. Diretor de Arte 2D está aposentado. Personas aposentadas: `docs/_obsoleto/company/agents/`.

## O que continua valendo da divisão

- Compliance lê política, monetização e avisos da conta. Observador lê saúde da sessão. Guardião lê sinal de comprometimento. Nenhum dos três abre o Studio por conta própria: a leitura sai do Temporal pelo Camofox.
- Efeito externo (render, upload, privacidade, apagar) só pelo Temporal.
- Quem mede não corrige. Autor não é o auditor. Quem monta o motion não julga o motion (t145u).

## O que não é operação

Não abrir organização, issue ou agente no Paperclip. Não tratar login da CLI do Paperclip como pendência. O código antigo dessa ponte permanece no repositório até o corte do F05-09 e não se altera sem OK do José.
