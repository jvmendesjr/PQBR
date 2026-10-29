# REF-MG-04 — OmaPhoto (a pincelada que revela)

- **Origem:** externa, só **gramática de movimento**. Vídeo entregue pelo José em t153u. Nada de conteúdo, marca, texto, música ou frame de terceiro entra no canal.
- **Link:** https://whatships.com/videos/omaphoto/ · **Consulta:** 28/10/2026.
- **Medida:** 1920×1080, 60 fps, 30,06 s.
- **Método:** folha de contato 5×5, um quadro a cada ~1,2 s. Não foi playback completo.
- **Estado:** `aguardando_ok_jose` (28/10/2026, t153u).
- **Prova renderizada:** `provas/mg10-pecas.png`, quadros 11–12 (`transicao-pincelada`, fases cobre e revela).

## Gramática observada

1. **A pincelada abre a cena:** uma forma pintada cobre a tela e depois se afasta, revelando o conteúdo atrás — a transição é um gesto, não um fade.
2. **Íris e luz radial:** o conteúdo aparece dentro de um círculo que abre, como uma lente; a luz guia o olho para o centro.
3. **Sobreposição:** a forma pintada não é um retângulo; a borda é irregular, com sobras e farpas, como pincel de verdade.

## O que entra no motor

| Peça | O que veio daqui |
|---|---|
| `transicao-pincelada` | A transição em duas fases (`cobre` / `revela`), com borda ondulada e diagonal, farpas finas e traço de acento na borda. É a passagem entre assuntos do bloco; a cortina padrão continua na entrada e na saída do bloco. |

## O que fica de fora

- **A íris de câmera** (círculo que abre e fecha como lente): é efeito de lente, clichê de motion, e não foi implementada. Se um dia entrar, entra como peça própria e com decisão registrada.
- **A interface de produto** que a pincelada revela (painéis, mockups) e a paleta escura.
- **Textos e marca** da referência.
- **A pincelada como transição padrão.** Ela é uso interno do bloco; a entrada e a saída do bloco continuam na cortina padrão (REGRAS §26).

## O que acrescenta à REF-MG-00

Dá **gesto** à passagem entre ideias. A cortina padrão abre e fecha o bloco; a pincelada move o bloco por dentro, sem que o espectador sinta um corte de software.
