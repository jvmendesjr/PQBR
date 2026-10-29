# Playbook — Google Flow

- **versão:** 1.0.0
- **status:** [APROVADO] José t149u · decisão t160u
- **núcleo:** [`CRIACAO-README.md`](CRIACAO-README.md) (consultar primeiro)
- **origem:** `docs/pesquisas/flow-processo-comunidade-20261029.md` + Help Google Flow Agent
- **conta / sessão:** só Camofox PQBR `127.0.0.1:9387` (REGRAS §11). Nunca outro browser.

## Navegação (resumo)

1. Abrir `https://flow.google.com/` (ou labs.google/fx/tools/flow) na sessão já logada.
2. **Novo projeto** nomeado `PQBR-EPxxxx-slug` (nunca o projeto de testes compartilhado).
3. No prompt box: ligar **Agente**.
4. **Configurações do agente:** Confirm before generating = **Sempre**; imagem `9:16` + x1 + `🍌 Nano Banana Pro`; vídeo `9:16` + x1 + modelo barato padrão do projeto (hoje Omni Flash / o que a UI mostrar).
5. **Instruções para o agente:** estilo cartoon 2D flat colorido stickman; lips closed; sem texto/marca; elenco do episódio; naming `S0N_…`.
6. **Characters:** criar/anexar `@Nome` a partir das fichas do `banco-fichas/` (recorte individual, fundo limpo).
7. Collections: `Referencias` / `Storyboard` / `Cenas` / `Finais`.

## Componentes que importam

| Componente | Uso PQBR |
|---|---|
| Agente | Orquestra fichas, storyboard, stills e clipes; sugere modelo |
| Characters / `@Nome` | Identidade pinada (obrigatório; nome no texto sem Character = drift) |
| Ingredients / Elements | ≤ **3** por geração; personagem + objeto/local + estilo |
| Storyboard Studio / grade | Planejamento; **não** alimentar grade multi-painel no vídeo |
| Frames to Video | Start frame aprovado → motion |
| Ingredients to Video | Âncora de identidade no clipe |
| Scenebuilder | Montar clipes **já** aprovados; Extend/Jump com parcimônia |
| Nano Banana Pro | Default de still / ficha (conferir **0 créditos** antes de confirmar) |

## Sequência operacional (Flow)

1. Conferir núcleo canônico (`processo_criacao_conferir` com plataforma `flow`).
2. Projeto novo `PQBR-EPxxxx-slug`.
3. Agente on + Confirm=Sempre + defaults acima.
4. Entregar fichas existentes do banco (Character/Element). Upload Angular: ver receita em `docs/pesquisas/flow-agente-e-nano-banana-pro-20261028.md` (`.sidebar-upload-btn`).
5. Pedir ao Agente as refs faltantes (só stills Nano Banana Pro). Registrar no catálogo PQBR.
6. Pedir storyboard com refs pinadas + prompts SUBJECT/ACTION/CAMERA/ATMOSPHERE.
7. Gerar stills S01..S0N (9:16); Collections; **parar** para revisão (`imagens_revisadas`).
8. Só então 1 clipe contínuo por cena (`Single continuous shot, no cuts, lips closed`).
9. Baixar para repo/Drive; seguir motion (MG-05+).

## Checagem de 0 créditos (imagem)

Antes de confirmar geração de still/ficha: a UI deve indicar **0 créditos** para Nano Banana Pro no plano vigente. Se a UI mostrar gasto de crédito para still, **não confirmar** — HOLD + avisar José. Vídeo sempre gasta cota: só após revisão.

## Prompt (Flow)

Ver templates em `CRIACAO-README.md` § núcleo item 7 e pesquisa 2026-10-29 §6. Sempre: formato 9:16, modelo sugerido, uma ação, Character pinado, sem redescrever aparência da ficha.

## Fora de escopo neste playbook

- Google Vids / Meta Vibes → stubs respectivos.
- Reinício de worker / troca de combo → OK explícito do José.
