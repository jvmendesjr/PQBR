# REF-MG-05 — Vovy (a palavra destacada e o número que conta)

- **Origem:** externa, só **gramática de movimento**. Vídeo entregue pelo José em t153u. Nada de conteúdo, marca, texto, música ou frame de terceiro entra no canal.
- **Link:** https://whatships.com/videos/vovy/ · **Consulta:** 28/10/2026.
- **Medida:** 1920×1080, 24 fps, 46,03 s.
- **Método:** folha de contato 5×5, um quadro a cada ~1,8 s. Não foi playback completo.
- **Estado:** `aguardando_ok_jose` (28/10/2026, t153u).
- **Prova renderizada:** `provas/mg10-pecas.png`, quadros 3–4 (`marca-texto`) e 5–6 (`numero-conta`).

## Gramática observada

1. **Recoloração de palavra:** dentro de uma frase, uma palavra muda de cor e vira o assunto; o resto do texto fica parado.
2. **Prompt pill que digita:** um campo de texto escreve sozinho, letra a letra, e o conteúdo aparece depois — a digitação é a ação.
3. **Abas que contam:** números sobem dentro de abas/rótulos até o valor final, com o rótulo fixo.
4. **Ícones que substituem palavras:** um ícone entra no lugar de uma palavra e assume o sentido dela.

## O que entra no motor

| Peça | O que veio daqui |
|---|---|
| `marca-texto` | O destaque de uma palavra dentro da frase (aqui, barra chapada atrás, com a palavra em branco para manter o contraste) e o cursor de leitura que corre até ela. |
| `numero-conta` | O contador com formatação pt-BR, sufixo, rótulo em cima e selo que carimba no fim — a ideia das abas que contam, sem a UI. |
| `frase-troca` | A palavra que muda no lugar enquanto o resto da frase fica. |

## O que fica de fora

- **A UI de produto:** prompt pill, abas, campos de texto e ícones de interface. No canal, o gráfico é desenho chapado, não tela de app.
- **A digitação como efeito.** Ela existe no catálogo v1 (`idioma_entrada: datilografar`) como variável sutil, mas não como cena inteira: o texto do bloco aparece por mola, não letra a letra.
- **Ícones substituindo palavras:** exigiria uma biblioteca de ícones e uma peça nova; só entra se o bloco de números pedir e depois de decisão registrada.
- **Textos e marca** da referência, e a paleta.

## O que acrescenta à REF-MG-00

Confirma duas gramáticas que o bloco usa muito: **destacar a palavra que importa** dentro da frase (em vez de reescrever a frase) e **contar o número** em vez de só mostrá-lo. As duas cabem no bloco de números travados sem inventar texto.
