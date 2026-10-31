# Biblioteca do motion: faça e não faça (REGRAS §26, t145u)

A biblioteca é o lugar das peças aprovadas. O papel `motion` só usa o que está no catálogo
(`../catalogo/indice.json` + um `.js` por modelo). Peça nova entra aqui antes de ir ao vídeo:
um HTML de prova, um vídeo curto, um quadro de referência e a linha no índice.

## Faça
- Uma ideia por tela. Texto grande, alinhado à esquerda, dentro da zona segura (topo 14%, base 20%, direita 12%).
- Entrada por mola fechada (passa um pouco do alvo e assenta). Saída por corte ou pela cortina padrão.
- Cores só do elenco e da marca (`catalogo.PALETA`, padrão flat colorido de t150u: masculino azul-aço, feminino rosa). Letra colorida sobre fundo claro usa o tom `texto` do elenco, nunca o rosa ou o azul chapado (2,3:1 e 3,6:1 no creme). Fundo neutro claro `#f6f1e7`. Cartões brancos.
- Personagem presente (t150u): `personagem-moldura` põe uma ficha `PERS-*` do catálogo num quadradinho num canto do layout do bloco, com uma pose (nome do recorte da ficha: `giro-*`, `exp-*`). Troque a pose em peças seguidas; use o coadjuvante quando a cena pede outro ponto de vista; `espelhar` faz o personagem olhar para o conteúdo.
- Varie o lado e o eixo entre blocos: centralizar tudo é o vício de motion feito por IA.
- Peças de t153u no catálogo (1.2.0): `frase-troca` (2–4 frases no mesmo lugar, troca seca), `marca-texto` (o `destaque` é **trecho de `texto`**; o contrato confere), `numero-conta` (contador pt-BR), `leque` (2–4 satélites), `elo-causa` (causa → conector → efeito) e `transicao-pincelada` (`cobre`/`revela`). A pincelada é uso **interno** do bloco; a entrada e a saída continuam na cortina padrão. Use os parâmetros travados do `indice.json`.
- Quem escolhe o movimento é a regra determinística (tipo de conteúdo + semente do código, MG-04), não o José movimento a movimento (t153u). Registre a razão na `justificativa` da peça.
- Texto na tela só do bloco de números travados do roteiro/cenas individuais (storyboard removido 29/10/2026). O que não está no bloco não aparece.
- Teste a 360 px de largura antes de aprovar: se não se lê no celular, aumenta a letra ou tira texto.
- Folha de contato (1 quadro/s), nota de 1 a 10, corrigir os três piores pontos, repetir até ≥ 8.
- Quadro = função pura do tempo. Nada de `setTimeout`, `requestAnimationFrame`, transição CSS ou `Math.random`.

## Não faça
- Título centralizado em gradiente, fade puro, brilho, partículas, glitch, crossfade, rótulos de canto.
- Música. SFX só por ação, indicado no roteiro.
- Pedir clique, curtida, inscrição ou comentário (t263). "Interatividade passiva": movimento, não pedido.
- Mapa geográfico "de cabeça": o modelo `origem-pino` usa cartão e pino, não contorno de país.
- Bloco de tela cheia como última cena (o loop volta ao vídeo) ou cobrindo o gancho e o CTA falado.
- Personagem em cima de texto ou de cartão: o render reprova (`personagem … cobre …`). Mude o canto, o tamanho ou o momento. Personagem na tela o bloco inteiro também é ruído: entre quando tem algo a dizer.
- Cobrir marca ou proveniência do provedor de vídeo.
- Copiar código de kit sem licença. O motor é próprio; ideia é livre, código não.

## Como provar uma peça nova
1. Escreva `catalogo/<slug>.js` registrando no `PQBRMotion` e a entrada em `indice.json`.
2. Rode `tests/unit/test_motion_motor.py` (slug, parâmetros e zona segura) e `test_motion_contrato.py`.
3. Renderize um plano mínimo com `render.py` e gere a folha de contato com `compor.folha_contato`.
4. Guarde aqui `<slug>.png` (quadro de referência) e a nota da autocrítica no `historico.md`.
