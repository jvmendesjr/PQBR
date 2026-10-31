# Playbook — Google Flow

- **versão:** 1.2.0
- **status:** [APROVADO] José t149u · decisão t160u · ajuste upload t161u · **storyboard removido definitivamente por José em 29/10/2026**
- **núcleo:** [`CRIACAO-README.md`](CRIACAO-README.md) (consultar primeiro)
- **origem:** `docs/pesquisas/flow-processo-comunidade-20261029.md` + Help Google Flow Agent
- **conta / sessão:** só Camofox PQBR `127.0.0.1:9387` (REGRAS §11). Nunca outro browser.

## Navegação (resumo)

1. Abrir `https://flow.google.com/` (ou labs.google/fx/tools/flow) na sessão já logada.
2. **Novo projeto** nomeado `PQBR-EPxxxx-slug` (nunca o projeto de testes compartilhado).
3. No prompt box: ligar **Agente**.
4. **Configurações do agente:** Confirm before generating = **Sempre**; imagem `9:16` + x1 + `🍌 Nano Banana 2.1` (modelo atual registrado, 29/10/2026, ordem do José; procurar esse nome exato na UI, fail-closed se ausente, nunca substituir em silêncio); vídeo `9:16` + x1 + modelo barato padrão do projeto (hoje Omni Flash / o que a UI mostrar). O formato é parâmetro do projeto e tem de ser pedido explicitamente no prompt (9:16 para Shorts, 16:9 quando o projeto for horizontal) — consistência acima do formato.
5. **Instruções para o agente:** estilo cartoon 2D flat colorido stickman; lips closed; sem texto/marca; elenco do episódio; naming `S0N_…`; a protagonista é uma mulher jovem adulta (nunca escrever menina/girl no prompt, isso encolhe a personagem), proporções adultas, em pé no chão, balcão/mesas na altura da cintura, sem banquinho, sem braços ou mãos extras, todos os membros em traço fino preto de stickman (aprendizado 30/10/2026, ficha PERS-menina-rosa).
6. **Characters:** criar/anexar `@Nome` a partir das fichas do `banco-fichas/` (recorte individual, fundo limpo).
7. Collections: `Referencias` / `Cenas` / `Finais` (Storyboard removida 29/10/2026).

## Componentes que importam

| Componente | Uso PQBR |
|---|---|
| Agente | Orquestra fichas, cenas individuais, stills e clipes; sugere modelo |
| Characters / `@Nome` | Identidade pinada (obrigatório; nome no texto sem Character = drift) |
| Ingredients / Elements | ≤ **3** por geração; personagem + objeto/local + estilo |
| Cenas individuais | Uma cena por vez, sem board; **não** alimentar grade multi-painel no vídeo |
| Frames to Video | Start frame aprovado → motion |
| Ingredients to Video | Âncora de identidade no clipe |
| Scenebuilder | Montar clipes **já** aprovados; Extend/Jump com parcimônia |
| Nano Banana 2.1 | Modelo atual de still / ficha (conferir **0 créditos** antes de confirmar; se a UI mostrar custo, HOLD + avisar José) |

## Sequência operacional (Flow)

1. Conferir núcleo canônico (`processo_criacao_conferir` com plataforma `flow`).
2. Projeto novo `PQBR-EPxxxx-slug` (nunca o de testes `e2dacb70-…`); gravar id em `config/flow_projetos.json`.
3. Agente on + Confirm=Sempre + defaults acima.
4. Entregar fichas existentes do banco (Character/Element). Registrar em `config/flow_projetos.json` (`fichas_ok`). **Upload Angular (t161u, estável):** abrir `Adicionar elementos` → aba **Envios** → **clicar** `.sidebar-upload-btn` (instancia o `input[type=file]`) → `POST /tabs/{id}/upload` com `selector=input[type=file]` e caminho absoluto no host Camofox → esperar `Enviando <arquivo> Imagem` e o `group` na grade. O atalho `focus→click` no botão (pesquisa 2026-10-28) ficou intermitente após o 1º arquivo; preferir o clique direto + `direct_input`. Menu topo `Enviar arquivos` sem input prévio → timeout do filechooser.
5. Pedir ao Agente as refs faltantes (só stills Nano Banana 2.1). Registrar no catálogo PQBR.
6. **Direção vem do NotebookLM (`DirecaoCenas` 2.0.0), não do agente.** O Temporal já validou `direcao_cenas_nlm` (fail-closed). No Flow, o agente **só opera a UI**: aplica `prompt_imagem` / `prompt_animacao` e `refs` da direção, uma cena por vez. Sem board. Sem `storyboard_ok` — `flow_projeto.exigir_antes_cenas` exige só `fichas_ok`. Passo 2 (adaptador Temporal→Flow) ainda pendente; piloto manual não é o caminho oficial.
7. Gerar imagens de início de cena S01..S0N (formato do projeto); Collections; **parar** para revisão (`imagens_revisadas`) — no piloto, revisão do José; depois do piloto aprovado, revisão automática pelos agentes (juiz Gemini, Jev, checagens) e o José só monitora.
8. Só então 1 clipe contínuo por cena (`Single continuous shot, no cuts, lips closed`).
9. Baixar para repo/Drive; seguir motion (MG-05+).

## Checagem de 0 créditos (imagem)

Antes de confirmar geração de still/ficha: a UI deve indicar **0 créditos** para Nano Banana 2.1 no plano vigente. Se a UI mostrar gasto de crédito para still, **não confirmar** — HOLD + avisar José. Vídeo sempre gasta cota: só após revisão.

## Prompt (Flow)

Ver templates em `CRIACAO-README.md` § núcleo item 7 e pesquisa 2026-10-29 §6. Sempre: formato 9:16, modelo sugerido, uma ação, Character pinado, sem redescrever aparência da ficha.

## Fora de escopo neste playbook

- Google Vids / Meta Vibes → stubs respectivos.
- Reinício de worker / troca de combo → OK explícito do José.
