> ⛔ **SUPERADO — ARQUIVO DE PRÉ-CONSTRUÇÃO. NÃO USAR PARA DECIDIR. AGENTES NÃO CONSULTAM SEM APROVAÇÃO EXPLÍCITA DO JOSÉ (t287).**
> Original: `box: testes/2026-10-08/final-round/v2-r3/RELATORIO-v2-r3.md`. Motivo: avaliação anterior às regras t264/t265 (a3 foi reavaliada como aprovada pelo critério novo). As regras válidas estão em `docs/REGRAS.md`.

# V2-r3: "o último pedaço" (2 personagens), 09/10/2026

**Veredito: NÃO publicável.** As 3 tentativas falharam na identidade. Narração, CTA e loop de texto ficaram certos nas 3.

## Caderno
- `pqbr-20261009-ep2-ultimo-pedaco-r3` = e5345e55-54fc-4cf5-8397-5087dc56e102.
  - Perfil `-p jv`; o caderno raiz não foi tocado.
- Fontes:
  - novas: `BRIEFING_PQBR_V2r3`, `ROTEIRO_V2r3`;
  - `ELENCO_V2r3_moca_e_senhor_fundo_creme.png`: o elenco sem nomes, em fundo creme #FDFBF7;
  - `QUADRO0_modelo_moca_e_senhor_a_mesa.png`: um quadro 0 montado com os dois à mesa;
  - os 2 links (RFM e Stanford).
- Formato: **Short**, vertical, pt_BR. É o equivalente por função; o Short não aceita estilo próprio.

## O que mudou nos prompts e nas fontes
- **Narração:**
  - abre com o gancho "Por que a gente nunca pega o último pedaço?";
  - fecha em "A gente é assim mesmo: prefere passar vontade a passar vergonha. E com muito orgulho.";
  - a última fala é **só "Segue o Porquê BR."**;
  - o loop fecha no eco "Porquê… / Por que a gente…";
  - nenhum pedido de comentário (174 palavras).
- **Briefing:**
  - fundo creme;
  - cabeças brancas;
  - descrição explícita de cada personagem;
  - os dois juntos em todo plano com gente;
  - proibidos: plano só de infográfico, avatar genérico e texto de chamada na tela.
- **a1:** prompt abrindo com "ESTILO OBRIGATÓRIO" e as duas imagens de referência.
- **a2:** os personagens como "bonecos palito", com uma lista de planos por tempo.
- **a3:** a estrutura do prompt que funcionou na V1, com "vistos de frente, sem ícones, sem vista de cima". A geração ficou limitada a briefing, roteiro e as 2 imagens (`-s`).

## Resultado por tentativa (final = pós com `post_final.py`; end card de 3,1 s detectado e cortado nas 3)
| Tentativa | Final | Identidade (minha checagem dos quadros) |
|---|---|---|
| a1 | `final/ep2-ultimo-pedaco_v2-r3-a1_post.mp4` (63,0 s) | **Nenhum personagem** em nenhuma cena: só mesa, pizza e gráficos (1/2, setas). Repete a falha da v2. |
| a2 | `final/ep2-ultimo-pedaco_v2-r3-a2_post.mp4` (61,9 s) | GRAVE: vista de cima com **4 a 8 ícones** de cabeças da moça clonadas, ou seja, mais de 2 personagens e personagem genérico (0:04–0:20, 0:50–1:00). Entre 0:36 e 0:48, só infográfico. |
| a3 | `final/ep2-ultimo-pedaco_v2-r3-a3_post.mp4` (62,6 s) | GRAVE em **todas** as cenas (S01–S11): **pele colorida**, **suéter cinza ou verde e jeans** (roupa com cor), e um **rapaz no lugar do senhor** (personagem trocado). Em S07–S09 há ícones de pessoas (mais de 2). Os dois aparecem pequenos, o que é o mesmo padrão de avatar da v2-r2. |

## CTA e loop (Whisper + checagens determinísticas, regra nova)
- Nomes falados: nenhum nas 3.
- Pedido de comentário: nenhum nas 3.
- Corte de fala: não houve.
- "Segue o Porquê BR" é a última fala nas 3:

| Tentativa | Fala do CTA | Fim do vídeo |
|---|---|---|
| a1 | 61,4–62,5 s | 63,0 s |
| a2 | 60,3–61,4 s | 61,9 s |
| a3 | 61,1–62,0 s | 62,6 s |

- O Whisper ouve "Porquê BR" como "por KBR". A checagem aceita essas variantes, e corrigi a grafia nos prompts LOOP.
- **Loop do texto:** ok ("…E com muito orgulho. Segue o Porquê BR." → "Por que a gente nunca pega o último pedaço?").
- **Loop visual:** na a3, o último plano repete o primeiro (os dois à mesa com o pedaço).
- **Ressalva da a3:** o título "Segue o Porquê BR." aparece escrito no topo entre 56 e 62 s. Não é pedido de comentário, mas é texto de chamada na tela.

## Auditor v3
- **Feito** em `audit/<a1|a2|a3>/`:
  - cenas;
  - quadros-chave;
  - pranchas `sheets/sheet_R3_*.png` + `00_referencia_elenco.png`;
  - transcrição;
  - `resultados/det.json`;
  - prompts `IDENT_R3.txt` e `LOOP_R3.txt`.
- **Pendente:** a etapa visual no Gemini web (3.8 Flash normal, 2 rodadas, conforme o RUNBOOK).
  - Salve as respostas em `audit/<tag>/answers/`.
  - Depois rode `python3 audit/decide_r3.py <tag>`.
  - Pela minha checagem, a2 e a3 dão **reprova**.

## Conclusão
- Com a V2 em dois personagens, o Short do NotebookLM ignora as imagens de elenco: são 5 gerações com falha (v2, v2-r2, a1, a2, a3).
- O acerto da V1 (um personagem só) não se repetiu aqui.
- Sugestão para decidir: manter a V1 como referência de tolerância e tratar a V2 fora do NotebookLM Short. Uma opção é usar a narração do NotebookLM com quadros gerados a partir do elenco por outra ferramenta e montados em código, a validar.
