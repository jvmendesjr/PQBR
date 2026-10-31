# REF-MG-07 — Valendata (o dado explicado)

- **Origem:** externa, só **gramática de movimento**. Vídeo entregue pelo José em t153u. Nada de conteúdo, marca, texto, música ou frame de terceiro entra no canal.
- **Link:** https://whatships.com/videos/valendata/ · **Consulta:** 28/10/2026.
- **Medida:** 1920×1080, 30 fps, 90,09 s.
- **Método:** folha de contato 5×5, um quadro a cada ~3,6 s. Não foi playback completo.
- **Estado:** `aprovada` (29/10/2026, t131u — José aprovou a regra e as fichas).
- **Prova renderizada:** `provas/mg10-pecas.png`, quadros 3–4 (`marca-texto`), 5–6 (`numero-conta`), 7–8 (`leque`) e 9–10 (`elo-causa`).

## Gramática observada

1. **Destaque de palavra + riscado:** uma palavra é destacada e outra é riscada e substituída — o texto mostra a correção, não só o resultado.
2. **Cursor de leitura:** um cursor percorre a frase e para na palavra que importa, como um dedo apontando.
3. **Contador:** o número sobe até o valor (100%) e o mesmo acontece dentro de abas, com o rótulo fixo.
4. **Grafo radial:** um nó central e satélites ligados por linhas, um a um.
5. **Grafo de 2 nós:** causa e efeito ligados por um conector rotulado.

## O que entra no motor

| Peça | O que veio daqui |
|---|---|
| `marca-texto` | O destaque chapado atrás da palavra e o cursor de leitura que corre até ela e sai quando o destaque assenta. |
| `numero-conta` | O contador com sufixo, rótulo e selo (o "100%" com a fonte do dado). |
| `leque` | O grafo radial adaptado ao 9:16: nó central e 2–4 satélites abertos na diagonal, com as linhas crescendo uma a uma. |
| `elo-causa` | O grafo de 2 nós: causa em cima, conector rotulado (o "porque") e efeito embaixo. |

## O que fica de fora

- **O riscado** (palavra riscada e substituída): ainda não é peça. É o candidato mais forte para o próximo lote, porque explica "o que se pensava × o que é" sem inventar texto.
- **A UI de dashboard** (abas, painéis, tabelas) e a paleta escura.
- **Textos e marca** da referência.
- **Muitos nós no grafo:** no 9:16 cabem 2–4 satélites; mais que isso vira teia ilegível.

## O que acrescenta à REF-MG-00

É a referência que mais rendeu peças: mostra como **explicar um dado** com destaque, cursor, contador e grafo, tudo com texto curto. Quatro das seis peças novas vêm daqui.
