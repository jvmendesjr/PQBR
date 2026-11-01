# PROPOSTA — Regras e contratos mais permissivos para o estilo do canal (2026-11-01)

STATUS: PROPOSTA em branch, NAO vigente em producao. Mudanca de regra
canonica exige OK do Jose (aprovador do PQBR); ate la, workers continuam
rodando a regra antiga, sem reinicio, sem merge em main e sem push desta
branch. Ordem: Junior, no chat, em 2026-11-01 08:43 e 08:45 -03 (nao
atribuida ao Jose nesta conversa).

## Motivacao

O canal Porquê BR é ironico e hiperbólico por essencia: sátira leve de
costumes brasileiros, exagero comico e origem histórica contada como a
"fofoca" que explica a piada (CONTRATO-EDITORIAL §17). A regra antiga da
compliance reprovava em bloco "pessoa real/celebridade" e
"política/religião/tragédia", sem distinguir pessoa viva de figura
histórica, política atual de história do passado, nem hipótese com
incerteza de afirmação falsa como certa. Com essa leitura, um episodio
sobre um café aguado cuja origem passa por um senador do inicio do
século XX vira automaticamente reprovado — o estilo fica inviável no
processo. O caso concreto: EP1003, workflow `ep1003-redo-20261101d`,
reprovado pela compliance antiga (ver `docs/EP1003-REFAZER-20261101.md`
§5).

## O que muda (nesta branch)

1. `src/pqbr/workflows/criativo.py` — prompt da activity
   `compliance_roteiro` extraido para a constante `PROMPT_COMPLIANCE`.
   PERMITIDO: personagem histórico do passado (sobretudo figura pública
   falecida) em stickman, sem difamação; história política do passado,
   sem política atual, partidarismo, eleição ou propaganda; suposição
   ou hipótese sobre possível origem, baseada em pesquisa e com
   linguagem de incerteza ("versão mais aceita", "tem quem diga",
   "possível origem"); hipérbole coloquial como exagero comico.
   REPROVA continua para: pessoa real viva ou celebridade atual,
   difamação, marca real, estereótipo ofensivo contra grupo protegido,
   política atual ou partidária, religião como alvo, tragédia,
   afirmação falsa como certa sem atenuador, pedido de comentário e
   conselho especializado.
2. `src/pqbr/workflows/temas.py` — `PEDIDO` da grade: de "Sem política,
   religião, tragédia, marca ou pessoa real" para "Sem política atual
   ou partidária, religião como alvo, tragédia, marca real ou pessoa
   real viva; personagem histórico do passado e história política do
   passado são permitidos". Afeta temas FUTUROS, nao o tema 5 do EP1003
   (já em produção).
3. `src/pqbr/pipeline/grade.py` — `BLOQUEIO.politica_partidaria`:
   saem os títulos de cargo sozinhos ("senador", "deputado",
   "presidente da república"), que tambem aparecem em história do
   passado. Ficam: nomes de políticos atuais, partido, eleição e STF.
   Defesa em camadas: a compliance a jusante continua reprovando
   política atual/partidária, mesmo que um tema passe na grade.
4. `src/pqbr/contratos/catalogo_visual.py` — `PROIBIDO_PADRAO`:
   "rosto de pessoa real ou celebridade" vira "rosto realista
   identificável de pessoa real ou celebridade (um stickman que
   representa figura histórica não é rosto real)". Mantidos, sem
   alteração: texto na imagem, marca real, pessoa realista ou
   fotorrealismo, volume 3D, um olho só, cabeça cortada e nome de
   personagem escrito ou falado.

## Conflitos explicitados (leitura proposta, nao canonica ainda)

- REGRAS §5 diz "satiriza o comportamento, nunca a pessoa ou o grupo"
  e "Sem nomes de personagem falados ou escritos", e o visual reprova
  "semelhança com pessoa real". Leitura proposta: "nunca a pessoa"
  significa nunca difamar e nunca ter pessoa viva como alvo; satirizar
  o COMPORTAMENTO ao redor de uma figura histórica (os bajuladores
  disputando a chaleira) é o próprio objeto da sátira de origem, nao
  ataque à pessoa. "Sem nomes" vale para os personagens do canal
  (elenco stickman), nao para o nome histórico que É o assunto da
  origem. "Semelhança com pessoa real" no visual vale para semelhança
  fotorrealista ou rosto identificável, nao para stickman de cabeça
  redonda branca que representa a figura.
- Se o Jose entender diferente em qualquer um desses pontos, a leitura
  dele prevalece e a proposta volta para ajuste — nao se aplica
  silenciosamente.

## O que NAO foi afrouxado (travas de segurança mantidas)

Pessoa viva/celebridade, difamação, marca real, estereótipo ofensivo,
grupos protegidos, tragédia, religião como alvo, política atual ou
partidária, conselho de saúde/finanças/jurídico, incentivo a ato
ilegal ou perigoso, pedido de comentário e afirmação falsa como certa
sem atenuador. Nada disso vira permitido por esta proposta.

## Avaliacao: compliance refeita do roteiro do EP1003 (regra nova)

Execucao fora do Temporal (chamada direta da activity com o prompt
novo, sobre o markdown do roteiro do workflow d, sem reiniciar worker
e sem alterar o veredito registrado da corrida d):

- Veredito novo: `aprovado: true`.
- Motivos: Pinheiro Machado, figura histórica pública falecida,
  contexto irônico sem difamação — permitido; hipérbole "todo
  brasileiro odeia", exagero comico coloquial — permitido; origens
  apresentadas com atenuadores ("versão mais aceita", "tem quem
  diga") — permitido; sem pessoa viva, marca real, estereótipo
  ofensivo, política atual, religião ou afirmação falsa sem atenuador;
  bloco visual proíbe rosto realista e logo real — conforme o contrato.
- Ressalvas: fala 6 cita "governador" de Sergipe sem nome — sem risco,
  mas nenhuma versão futura pode nomear governador vivo ou recente;
  fontes (blogs, nao acadêmicas) — os atenuadores já cobrem isso, mas
  a pesquisa deve manter o registro caso a origem seja questionada.
- Este veredito é AVALIACAO, nao o veredito de producao: a corrida d
  continua registrada como reprovada pela regra antiga. O veredito de
  producao só muda com worker reiniciado (regra nova) + nova corrida.

## Testes

`tests/unit/test_compliance_prompt.py` (2) e
`tests/unit/test_essencia_canal.py` (novos, 3) + suites afetadas
(`test_grade`, `test_temas_t465`, `test_catalogo_visual`,
`test_auditor_visual`, `test_briefing_mestre`): 54 passed.

## Para virar regra vigente (apos OK do Jose)

1. Jose aprova esta proposta (merge em main fica para decisão dele;
   esta branch nao foi mergeada nem enviada ao origin).
2. Reiniciar `pqbr-notebooklm-worker` e `pqbr-episodio-worker` para
   carregar a regra nova.
3. Nova corrida do `EpisodioWorkflow` (id novo; reutiliza o efemero
   `ca7b16f9`, vivo no NotebookLM) → roteiro → compliance nova → SEO
   → `direcao_cenas_nlm` → `flow_cenas_individuais_pendente` → Flow
   em projeto limpo.
