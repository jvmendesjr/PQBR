> ⛔ **SUPERADO — ARQUIVO DE PRÉ-CONSTRUÇÃO. NÃO USAR PARA DECIDIR. AGENTES NÃO CONSULTAM SEM APROVAÇÃO EXPLÍCITA DO JOSÉ (t287).**
> Original: `docs/99-historico/RESULTADO-gemini.md`. Motivo: rodadas do auditor superadas por t232 e t264/t265. As regras válidas estão em `docs/REGRAS.md`.

# Rubrica real no Gemini (08/10/2026, 20:36 PT) — modelo "3.8 Flash" (sem toggle de pensamento visível), conta jvmendesjr, 1 chat por vídeo
| Vídeo | Real | Esperado | Gemini | Acerto |
|---|---|---|---|---|
| A | ref toalha v1 | aprova_com_ressalva (drift leve 0:51–0:54) | reprova (identidade: "camisa/jaleco/corpo preenchido" 0:03, 0:40, 0:48); CTA, loop, tom ok | FALSO REPROVA (severidade) |
| B | syn_c personagem errado enxertado | reprova identidade | reprova: pegou enxerto 0:20–0:23, nome "Seu Valdemar", 3 personagens, quebra texto-imagem e corte | ACERTO |
| C | v2r2 genéricos | reprova identidade genérica | reprova: pele colorida, roupas | ACERTO |
| D | syn_f2 loop semântico | reprova loop | reprova: loop quebrado e corte em 0:57 (+ mesma "roupa" de A) | ACERTO |
Conclusão: detecção 3/3 dos defeitos; não diferencia desvio leve de grave (reprovou a referência). Ajustes: anexar imagem de referência do personagem ao prompt; escala de severidade com exemplos (contorno duplo/traço = leve); regra de proporção (identidade grave em > X s ou em cena-chave = reprova; leve = ressalva); validar com José o limite de tolerância.
Chats: A fbac5ccab365d015, B d4d89265e3cc7955, C bc8091e1cb574fce, D e7dc630635c610a5.

## Decisão do José (t222) — tolerância de identidade
- Vídeo A (toalha v1) APROVADO: "três erros aceitáveis"; exigir o máximo do modelo no prompt, mas imperfeição leve do personagem não reprova.
- LEVE (passa com ressalva): corpo contornado/com volume, contorno duplo, traço diferente, cabelo só contornado.
- GRAVE (reprova): pele colorida, roupa real (camisa/terno/suéter), 3D, realista, boneco genérico, personagem trocado/novo, > 2 personagens.
- Cena sem personagem é válida quando a imagem acompanha o texto (ex.: ácaros na toalha).
- Observação editorial: em 0:03 (jogar na cama) a explicação podia ser um pouco melhor, mas passa.
- Próximo: rubrica v2 com imagem de referência do personagem + escala leve/grave com exemplos; o código decide pelo nível de gravidade, não pelo "reprova" do Gemini; re-testar A–D.

## Rodada 2 — rubrica v2 (escala leve/grave + imagem do elenco), 3.8 Flash, 08/10 ~20:54 PT
Não foi encontrado toggle "raciocínio completo" no 3.8 Flash. O seletor oferece 3.5 Flash Lite, 3.8 Flash, 3.1 Pro e "Raciocínio complexo".
| Vídeo | Esperado | Veredito | Motivo correto? |
|---|---|---|---|
| A toalha v1 | aprova_com_ressalva | aprova_com_ressalva | Sim (4 desvios leves) |
| B syn_c (trecho do EP2 inserido em 20–24 s) | reprova | reprova | Parcial: pegou o trecho estranho; diz que o nome "Seu Valdemar" é falado, mas o áudio é da v1 (provavelmente vem da legenda do quadro ou é alucinação) |
| C v2r2 (genérico) | reprova | reprova | Sim (grave: pele e roupa colorida) |
| D syn_f2 (loop semântico) | reprova | reprova | NÃO: diz que o loop está ok e cita a ponte que foi removida; reprova por identidade grave em 0:03/0:40, os mesmos quadros que no A foram leves |
Veredito 4/4, motivo 2,5/4. Achados: gravidade instável entre execuções com quadros idênticos; o loop semântico não é confiável no Gemini e deve ser checado por transcrição (Whisper) contra a ponte do roteiro.
Chats: A 72d52fe120fb82d4, B fc24f595973d6e2d, C 0ad406c776f2ed8f, D 482e45daadbb0744

## Rodada 3 — rubrica v2, modo "Raciocínio complexo" (botão do seletor: "Flash Estendido"), 08/10 ~21:04 PT
| Vídeo | Esperado | Veredito | Motivo correto? |
|---|---|---|---|
| A toalha v1 | aprova_com_ressalva | reprova (FALSO REPROVA) | NÃO: diz que tem roupa grave em 0:40, mas a cena é dos ácaros, sem personagem (conferido em chk/A_chk.png); legibilidade exagerada (0:06 está ok; 0:25 só uma leve ondulação em "Colchão e Lençol") |
| D syn_f2 | reprova | reprova | SIM no áudio: pegou a ponte cortada e o trecho vazado em 0:57–0:58 e reprovou o loop; repetiu a falsa roupa grave em 0:40 |
Chats: A fa1e6a3de9050a9b, D 9e2501fb9d800e07
Conclusão: o modo estendido melhora o áudio e o loop, mas piora o falso reprova visual (timestamps inventados). Nenhum modo sozinho é confiável. Proposta: toda alegação GRAVE com timestamp tem de ser confirmada por código, extraindo o quadro citado (±1 s) e fazendo uma pergunta de imagem só sobre ele; se não confirmar, cai para ressalva. Loop e corte de fala vão primeiro pela transcrição contra o roteiro.

## t232 (08/10 ~21:50 PT) — decisão de José
Roupa insinuada só por contorno (linha no peito, golinha), toda branca, sem cor, sem botão visível nem estampa = LEVE (passa com ressalva). GRAVE continua sendo roupa com cor, botões, estampa, pele colorida, 3D/realista, personagem genérico/trocado/novo, > 2 personagens.
Achado v3: o modo "Raciocínio complexo"/"Flash Estendido" recusa pranchas de imagem ("sou só um modelo de linguagem"); o 3.8 Flash normal responde.

## v3b — quadros por cena + transcrição, sim/não por traço, código decide (08/10 ~22:02 PT)
Modo 3.8 Flash, 2 rodadas IDENT por vídeo + 1 LOOP só texto (chats na v3/RUNBOOK e no relatório). Saída bruta: veredito 3/4. O A reprovou porque a regra do código exigia o tufo para reconhecer o Zé, e o Gemini descreveu certo o Zé de cabelo volumoso com relógio teal (S15/S16/S18).
Ajuste no código (decide.py; original em decide_v3b_original.py): Zé = cabeça quadrada + (tufo OU cabelo preto volumoso OU relógio teal); cabelo volumoso deixou de ser sinal de grave (tolerância t222). As respostas do Gemini não mudaram.
Resultado: 4/4, motivos certos:
- A: aprova com ressalva (só leves).
- B: reprova exatamente nas cenas enxertadas S09/S10 (roupa com cor + imagem não bate com a fala).
- C: reprova (pele e roupa coloridas, cabeça não branca).
- D: reprova pelo loop e pela fala final cortada (LOOP só texto); a identidade sai igual à do A.
Ressalva: a regra foi ajustada depois de ver o resultado. Validar na fase de desenvolvimento com os outros vídeos rotulados (labels.json) e com vídeos novos antes de confiar.
