> ⛔ **ARQUIVO — não consultar sem aprovação do José.** Superado pelos docs canônicos (README).

> ⛔ **SUPERADO — ARQUIVO DE PRÉ-CONSTRUÇÃO. NÃO USAR PARA DECIDIR. AGENTES NÃO CONSULTAM SEM APROVAÇÃO EXPLÍCITA DO JOSÉ (t287).**
> Original: `box: testes/2026-10-08/auditor/v3/RUNBOOK.md`. Motivo: usa a tabela LEVE/GRAVE de identidade, superada por t264/t265. O gabarito (labels.json, decide.py) entra em tests/ na D4. As regras válidas estão em `docs/REGRAS.md`.

# Runbook: teste do auditor v3b (Gemini web, manual, sem API)

v3b = prompts com traços fechados por cena (revisão após a 1ª rodada real, decisão t232 do José). As respostas da v3a ficam em `answers/_v3a/` (A no 3.8 Flash) e `answers/_v3a_recusas/` (Flash Estendido recusou as pranchas).

Pasta: `/workspace/porquebr-production/testes/2026-10-08/auditor/v3/`
Conta: jvmendesjr (não é usada para publicar). Juiz visual: só o Gemini web.
O modelo responde só JSON de sim/nao. Veredito, gravidade e resumo saem do código (`decide.py`).

## Antes de começar
1. Abra https://gemini.google.com/app na conta jvmendesjr.
2. Escolha **3.8 Flash** no seletor, no modo normal. **Não** use "Raciocínio complexo" / "Flash Estendido": na v3a ele recusou as pranchas nos 4 vídeos. Use o mesmo modo em todos os chats e anote o nome que o seletor mostra hoje. Se o nome mudar, escolha pela função.
3. **Um chat novo para cada execução.** Nunca faça a rodada 2 no mesmo chat da rodada 1.
4. Para colar o prompt, abra o `.txt`, copie tudo e cole. A única edição é trocar `__RODADA__` (está só na linha do formato) por 1 ou 2. Se esquecer, o código usa a rodada do nome do arquivo.
5. Copie a resposta inteira do Gemini e salve exatamente no arquivo indicado em `answers/v3b/`. Uma cerca ```json``` em volta pode ficar: o `decide.py` tira.

## Execuções planejadas: 8 chats IDENT + 1 chat LOOP

## Chats IDENT (8 chats: 2 rodadas × 4 vídeos)
Anexe os arquivos nesta ordem, todos na mesma mensagem que o prompt (máx. 4 arquivos, abaixo do limite de 10):

| Chat | Anexos (pasta `sheets/`) | Prompt | `__RODADA__` = | Salvar em |
|---|---|---|---|---|
| 1 | `00_referencia_elenco.png`, `sheet_A_1.png`, `sheet_A_2.png`, `sheet_A_3.png` | `prompts/IDENT_A.txt` | 1 | `answers/v3b/A_ident_run1.json` |
| 2 | `00_referencia_elenco.png`, `sheet_B_1.png`, `sheet_B_2.png`, `sheet_B_3.png` | `prompts/IDENT_B.txt` | 1 | `answers/v3b/B_ident_run1.json` |
| 3 | `00_referencia_elenco.png`, `sheet_C_1.png`, `sheet_C_2.png` | `prompts/IDENT_C.txt` | 1 | `answers/v3b/C_ident_run1.json` |
| 4 | `00_referencia_elenco.png`, `sheet_D_1.png`, `sheet_D_2.png`, `sheet_D_3.png` | `prompts/IDENT_D.txt` | 1 | `answers/v3b/D_ident_run1.json` |
| 5 | igual ao chat 1 | `prompts/IDENT_A.txt` | 2 | `answers/v3b/A_ident_run2.json` |
| 6 | igual ao chat 2 | `prompts/IDENT_B.txt` | 2 | `answers/v3b/B_ident_run2.json` |
| 7 | igual ao chat 3 | `prompts/IDENT_C.txt` | 2 | `answers/v3b/C_ident_run2.json` |
| 8 | igual ao chat 4 | `prompts/IDENT_D.txt` | 2 | `answers/v3b/D_ident_run2.json` |

Fazer A, B, C, D na rodada 1 e só depois a rodada 2 evita que a ordem dos vídeos se repita colada.

Se a resposta vier cortada, sem alguma cena ou com texto fora do JSON: salve assim mesmo. O `decide.py` marca o vídeo como `revisao_jose` e lista o problema. Não peça para o Gemini "corrigir" no mesmo chat. Se quiser refazer, abra chat novo e salve como `run3`.

## LOOP (só texto, sem anexo)
Opção recomendada, 1 chat para os 4 vídeos:
- Chat 9: cole `prompts/LOOP_todos.txt`, sem anexo. Salve em `answers/v3b/loop_todos_run1.json`.

Alternativa, 1 chat por vídeo: `prompts/LOOP_A.txt` … `LOOP_D.txt`, salvando em `answers/v3b/<V>_loop_run1.json`.
O formato é o mesmo JSON fechado que o Jev vai responder depois, então troca de juiz sem mudar o prompt.

Opcional: rodar LOOP uma segunda vez (chat novo, `loop_todos_run2.json`). Com 2 rodadas, o código aplica a mesma regra de concordância.

## Depois dos chats (no box)
```
cd /workspace/porquebr-production/testes/2026-10-08/auditor/v3
/workspace/.venv-whisper/bin/python det_checks.py    # já rodado; repetir não faz mal
python3 decide.py                                    # ou: python3 decide.py A D
```
Saída em `resultados/`:
- `<V>.json`: veredito, falhas, revisões, ressalvas, votos por cena.
- `<V>_resumo.md` e `RESUMO.md`: texto em pt-BR montado por template, sem texto do modelo.

## Regras que o código aplica
O modelo responde só traços. A identidade e a gravidade são decididas no `decide.py`.
- Identidade inferida: Zé = cabeça quadrada + tufo preto espetado (relógio opcional); Lia = rabo de cavalo ou óculos; Seu Valdemar = cabeça redonda careca, ou chapéu + bigode.
- "Fora do elenco" só é GRAVE se nenhum conjunto bate E há sinal de outro personagem: cabeça não branca, cabelo volumoso cobrindo a cabeça, pele colorida ou 3D. Palito branco sem traço do elenco é LEVE.
- GRAVE (reprova): pele colorida, roupa com cor, roupa com botão ou estampa, 3D/realista, cabeça não branca, mais de 2 personagens, fora do elenco pela regra acima.
- LEVE (ressalva): corpo contornado ou volumétrico, contorno de roupa branca (linha no peito, golinha, tudo branco; t232), olhos que não são de ponto, acessório da ficha ausente, palito branco sem traço do elenco.
- Imagem que não corresponde à fala: falha. Cena sem personagem que corresponde à fala: válida.
- LOOP: `ultima_continua_na_primeira = nao` ou `fala_final_cortada_no_meio = sim` é falha.
- Determinístico (Whisper): nome falado, CTA incompleto ou ausente, corte de fala no fim. Ponte diferente do roteiro é só indício.
- 2 rodadas: falha só se as duas concordam. Divergência vira `revisao_jose`. Uma rodada só: a falha vale, com aviso de "rodada única".
- Ordem: reprova > revisao_jose > aprova_com_ressalva > aprova.

## Gabarito (não mostrar ao Gemini)
| Vídeo | Esperado | Onde está o defeito |
|---|---|---|
| A | aprova_com_ressalva | desvio leve de traço; S12 são os ácaros, sem personagem, e é válido |
| B | reprova | S09 (Seu Valdemar de camisa azul e calça, pote de arroz) e S10 (cubo 3D com pote): identidade e texto–imagem |
| C | reprova | todas as cenas: avatares genéricos, pele colorida, suéter |
| D | reprova | LOOP: a ponte "porque amanhã é a mesma coisa" foi trocada por "amontoada, a toalha não pega vento" |
