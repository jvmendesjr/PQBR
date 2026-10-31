# Pesquisa e validação empírica — Agente do Google Flow, fichas permanentes em Nano Banana Pro e upload de referências (28/10/2026, t146u)

> **Contexto do pedido (José, 28/10/2026):**
> 1. Estabelecer como **regra canônica** que, para **personagens, objetos e locais permanentes** (`banco-fichas/`), as fichas são **permanentes** e geradas a partir do **modelo mais potente de geração de imagens (atualmente `🍌 Nano Banana Pro`)**, padronizadas a partir das 5 imagens reais tiradas de vídeos do próprio canal Porquê BR (`banco-fichas/referencias-canal/`).
> 2. Pesquisar e validar no próprio Google Flow se é melhor usar o **Agente do Google Flow** entregando essas imagens de referência (fichas permanentes), os storyboards como referência e os prompts para que ele entregue o que precisamos na produção do vídeo.

---

## 1. Padronização visual real do canal Porquê BR (extraída dos 5 frames enviados)

Os 5 recortes reais enviados pelo José foram preservados em `banco-fichas/referencias-canal/`:
- `ref-01-close-expressao-picole.jpeg` (410×567) — close de expressão (olhos arregalados, boca em O, gotas de suor, mão branca estilo luva segurando picolé).
- `ref-02-duplo-susto-calmo.png` (338×305) — contracena de dois stickmen (esquerda em pânico com mãos na cabeça e gotas de suor; direita calmo piscando).
- `ref-03-apontando-mapa-brasil.png` (365×486) — stickman apontando para quadro com mapa do Brasil e lupa.
- `ref-04-corpo-inteiro-hachura-escudo.png` (347×492) — stickman de corpo inteiro na rua com hachura na bochecha, mãos brancas estilo luva, tronco e membros em traço preto grosso, pés pretos ovais e sombra hachurada no chão.
- `ref-05-corpo-inteiro-olhos-fechados.png` (250×277) — stickman de corpo inteiro com olhos fechados em arco feliz e sombra hachurada.
- `ref-canal-composta-sem-texto.png` — folha composta limpa (sem qualquer texto) usada como âncora visual (`Elemento`) no Google Flow.

### Traços invariantes do canal:
1. **Fundo:** papel creme/off-white texturizado (`#f5f0e4`).
2. **Cabeça e rosto:** círculo branco grande com contorno preto orgânico de nanquim e **hachura sutil (cross-hatching)** na lateral da bochecha; **DOIS OLHOS expressivos sempre visíveis** (proibido ciclope / 1 olho só); sobrancelhas expressivas; boca fechada ou em reação estática (`lips closed, no lip-sync`).
3. **Corpo, mãos e pés:** tronco e membros em traço preto sólido grosso de caneta (sem camiseta/bermuda colorida que descaracterize o stickman clássico do canal); mãos brancas estilo luva cartum com contorno preto; pés pretos ovais preenchidos sobre sombra oval hachurada no chão.
4. **Diferenciação do elenco permanente:**
   - `PERS-M`: óculos redondos vermelhos finos (`#e23b2f`).
   - `PERS-F`: coque preto no topo da cabeça e brinco de argola dourada/amarela (`#e6b325`) à esquerda.
   - `PERS-M-classico`: stickman clássico do canal sem óculos (fiel aos 5 frames enviados).

---

## 2. Achado técnico de automação: como anexar imagens de referência no Google Flow via Camofox

O Google Flow utiliza Angular Material (`flow-media-upload`) dentro do menu `Adicionar elementos à caixa de comando`. O botão de envio (`button.sidebar-upload-btn`, rótulo `"Fazer upload de imagem"`) **só instancia o `<input type="file">` no DOM quando recebe um evento `.click()`**.

Como o endpoint `/tabs/:id/upload` do Camofox tenta primeiro `locator.focus()` + `press('Enter')` e só procura `input[type="file"]` depois, chamar `/upload` diretamente em `.sidebar-upload-btn` falhava com `File chooser did not open and no file input found`.

### Receita determinística validada em produção (Camofox PQBR, `127.0.0.1:9387`):
1. Clicar em `button "Adicionar elementos à caixa de comando"` via `clicar(tab, ref=...)`;
2. Registrar um listener one-shot no botão via `/evaluate`:
   ```js
   const b = document.querySelector(".sidebar-upload-btn");
   if (b) { b.addEventListener("focus", () => b.click(), { once: true }); }
   ```
3. Chamar `POST /tabs/{tab}/upload` com `{"userId": "pqbr", "selector": ".sidebar-upload-btn", "path": ["/caminho/absoluto/ficha.png"]}`.
4. Quando o Camofox executa `locator.focus()`, o listener dispara `b.click()`, o Angular cria o `<input type="file">` instantaneamente e o Camofox injeta o arquivo via `panel_input`, gerando o chip `button "Elemento"` na caixa de comando.

---

## 3. Avaliação técnica: vale a pena usar o Agente do Google Flow na produção do vídeo?

Inspecionamos e testamos ao vivo o **Agente do Google Flow** no projeto ativo (`https://flow.google.com/project/e2dacb70-b9d0-4dc7-8b93-e6ac1688a454`, aba `745303b5-4d3b-4012-8538-e2227d7d6bf3`).

### O que o Agente do Google Flow possui na interface real:
- **Botão `Agente`** na barra de comando: ativa o assistente conversacional do projeto ("Seu agente está ativo! Peça para ele discutir ideias, gerar variações de imagens, renomear recursos ou responder a perguntas sobre o Flow").
- **`Configurações do agente` (já travadas no projeto):**
  - `Confirmar antes de gerar`: **`Sempre`** ("O agente vai pedir confirmação antes de gerar mídia") vs. `Nunca`.
  - `Padrão da geração de imagens`: **`9:16`**, **`x1`**, modelo padrão **`🍌 Nano Banana Pro`** (**0 créditos** no plano Google AI Pro).
  - `Padrão para geração de vídeo`: **`9:16`**, **`x1`**, modelo padrão **`Omni 1.1 Flash`**.
- **`Instruções para o agente` (já gravadas no projeto):** permite cadastrar diretrizes permanentes por projeto com chave `Ativar/desativar instrução`, `Título da instrução`, botão `Referência` e `Descrição da instrução`.

### Veredito técnico: **SIM, em arquitetura híbrida (Agente para consistência + Fichas Permanentes em Nano Banana Pro + 1 clipe por cena)**

| Aspecto | Entregar tudo solto sem Agente/Fichas | Arquitetura Híbrida com Agente do Flow + Fichas Permanentes (Recomendada) |
|---|---|---|
| **Padronização de personagens, objetos e locais** | Deriva entre cenas (muda traço, perde um olho, vira pessoa 3D ou muda roupa). | **Alta fidelidade:** as fichas permanentes geradas em `🍌 Nano Banana Pro` entram como `Elemento` (imagem anexada) + `Instruções para o agente` fixas no projeto. |
| **Geração dos quadros-chave (start frames das cenas S01..S0N)** | Cada prompt precisa repetir tudo do zero e ainda pode errar proporção. | O Agente + `🍌 Nano Banana Pro` (0 créditos) compõem o start frame `9:16` de cada cena combinando a ficha permanente do personagem (`PERS-*`), do local (`AMB-*`) e do objeto (`OBJ-*`). |
| **Uso do Storyboard como referência** | Pedir um vídeo único a partir de uma folha inteira de storyboard gera cortes malucos ou anima os quadros da grade na tela. | O **JSON do Storyboard** (vindo do NotebookLM) guia cena a cena (`S01..S0N`). O Agente do Flow usa as fichas permanentes + descrição da cena para preparar os frames iniciais `S01..S0N` com `Confirmar antes de gerar = Sempre`, e a animação gera **1 clipe contínuo por cena** (`Single continuous shot, no cuts`). |
| **Controle de créditos** | Risco de gerar vídeo antes de aprovar o desenho. | Com `Confirmar antes de gerar = Sempre`, todas as fichas e frames iniciais saem em `🍌 Nano Banana Pro` a **0 créditos**, e o vídeo (`Omni 1.1 Flash` / `Veo 3.1`) só roda após validação visual do frame inicial. |

### Regra de ouro sobre folhas (`*-folha.png`) e storyboards na animação de vídeo:
- **Folhas multi-pose (`PERS-M-folha.png`, `PERS-F-folha.png`) e grades de storyboard** servem para **validação humana do José e referência de expressões**.
- Na hora de gerar a cena `S01..S0N` no Flow (imagem inicial + vídeo), **anexa-se o recorte individual `9:16` (`PERS-M.png` ou `PERS-F.png`) + a ficha do ambiente (`AMB-*.png`) + a ficha do objeto (`OBJ-*.png`)**, nunca uma grade com vários bonecos, evitando que o modelo de vídeo desenhe bonecos duplicados ou divida a tela.

---

## 4. Fichas permanentes geradas no Google Flow com `🍌 Nano Banana Pro` (28/10/2026)

Todas as 12 fichas permanentes foram geradas ao vivo no Google Flow usando **`🍌 Nano Banana Pro`** (0 créditos), ancoradas nas referências do canal (`banco-fichas/referencias-canal/`), com manifesto prévio em `~/.pqbr/episodios/flow-teste/` e inspeção visual individual:

1. `banco-fichas/personagens/PERS-M.png` (`768×1376`, 9:16) — protagonista masculino de corpo inteiro (óculos redondos vermelhos finos, 2 olhos visíveis, hachura na bochecha, tronco/membros em nanquim preto grosso, luvas brancas, pés pretos ovais).
2. `banco-fichas/personagens/PERS-M-folha.png` (`1376×768`, 16:9) — folha com 3 poses/expressões de corpo inteiro de `PERS-M` (calmo, assustado com gotas de suor, curioso apontando).
3. `banco-fichas/personagens/PERS-F.png` (`768×1376`, 9:16) — protagonista feminina de corpo inteiro (coque preto no topo, brinco de argola amarela à esquerda, 2 olhos visíveis com cílios, hachura na bochecha, tronco/membros em nanquim preto grosso, luvas brancas, pés pretos ovais).
4. `banco-fichas/personagens/PERS-F-folha.png` (`1376×768`, 16:9) — folha com 3 poses/expressões de corpo inteiro de `PERS-F` (calma, surpresa com mãos no rosto, confiante de olhos fechados em arco).
5. `banco-fichas/personagens/PERS-M-classico.png` (`768×1376`, 9:16) — stickman clássico do canal sem óculos (corpo inteiro frontal).
6. `banco-fichas/personagens/PERS-M-classico-folha.png` (`1376×768`, 16:9) — folha com 3 poses/expressões do stickman clássico sem óculos.
7. `banco-fichas/ambientes/AMB-cozinha.png` (`768×1376`, 9:16) — cozinha brasileira aconchegante em nanquim + hachura sobre papel creme (`#f5f0e4`).
8. `banco-fichas/ambientes/AMB-sala.png` (`768×1376`, 9:16) — sala de estar brasileira em nanquim + hachura sobre papel creme (`#f5f0e4`).
9. `banco-fichas/objetos/OBJ-chaleira.png` (`1024×1024`, 1:1) — chaleira clássica em nanquim + hachura sobre papel creme.
10. `banco-fichas/objetos/OBJ-xicara.png` (`1024×1024`, 1:1) — xícara de café com pires em nanquim + hachura sobre papel creme.
11. `banco-fichas/objetos/OBJ-filtro-pano.png` (`1024×1024`, 1:1) — coador de pano brasileiro no suporte em nanquim + hachura sobre papel creme.
12. `banco-fichas/objetos/OBJ-controle-remoto.png` (`1024×1024`, 1:1) — controle remoto sem texto em nanquim + hachura sobre papel creme.
