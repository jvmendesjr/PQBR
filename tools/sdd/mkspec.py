import sys; sys.path.insert(0,'/workspace/sanit/gen'); from req import R,N
F={
'F01':('Grade e temas','Como José, quero que a grade do dia saia sozinha, correta e sem temas repetidos, para não precisar cobrar o sistema.',['A grade do dia D é gerada só a partir da data D e gravada antes do lote.','Nenhum tema publicado (ou variação próxima) entra na grade; o teste do incidente de 08/10 passa.','Tema acima de 75 de polêmica não entra sem o José; tema do bloqueio absoluto nunca entra.']),
'F02':('Roteiro e produção','Como José, quero roteiros no tom do canal e vídeos prontos de manhã, para publicar nas janelas sem intervenção.',['Roteiro validado pelo `RoteiroShort` (duração, CTA, sem nomes, sem pedido de comentário).','Produção sempre em caderno efêmero; nenhuma chamada ao caderno raiz.','Consumo do NotebookLM gravado antes e depois de cada geração.']),
'F03':('Auditor','Como José, quero que só vídeos dentro das travas sejam publicados, com motivo claro quando algo reprova.',['Veredito decidido pelo código com base em respostas sim/não e checagens de texto.','Falso aprovado e falso reprovado medidos no gabarito ampliado.','Estilo visual e imagem×fala nunca reprovam sozinhos.']),
'F04':('Publicação','Como José, quero os vídeos agendados nas janelas certas, sem duplicata e sem publicar reprovado.',['Upload interrompido não gera duplicata.','No máximo 4 por dia; reprovado nunca publicado; horário sem reserva cancelado.','Agendado confere com o aprovado (título, descrição, código).']),
'F05':('Correção pós-publicação (item 5)','Como José, quero que qualquer problema torne o vídeo privado na hora e me avise, sem republicação.',['Sinal de problema → privado e Telegram em minutos, com motivo.','Nenhum vídeo volta a público nem é excluído sem o José.']),
'F06':('Comunidade','Como José, quero que comentários comuns sejam respondidos com naturalidade e que só casos graves cheguem a mim.',['Respostas só do banco aprovado e dentro dos limites.','Casos graves (reclamação muito grave, direitos, situação visivelmente grave) desligam o automático e vão ao José, com tom formal.','Sombra e resposta real de teste antes de ligar.']),
'F07':('Conformidade','Como José, quero saber de avisos do YouTube e ter a fila parada em caso crítico.',['Crítico gera HOLD, privados os agendados, Telegram e ticket.','Recurso só enviado pelo José.']),
'F08':('Analista e relatórios','Como José, quero um relatório diário confiável, com custos e com aviso quando os números não significam nada.',['Relatório diário por template no Telegram.','Exceções sinalizadas; aviso de amostra sem significância estatística.','Custos levantados sem teto.']),
'F09':('Agentes, interação e manutenção','Como José, quero que os agentes só proponham e que eu aprove, pelo Telegram, tudo o que muda.',['Toda proposta é um objeto Pydantic v2 válido; nada se aplica sem aprovação.','Ordem só vale do ID autorizado.','Ticket chega pré-estruturado e tem 2 aprovações.','Item que falha em tudo vai para revisão, e a determinação é registrada.']),
'F10':('Sessão e resiliência','Como José, quero que quedas de sessão, rede ou banco não percam nada nem dupliquem nada.',['Cada degrau das escadas simulado.','Supabase fora não perde estado; na volta, outbox grava uma vez.']),
'F11':('Armazenamento','Como José, quero tudo guardado no Drive e o disco do servidor livre.',['Arquivo local só apagado após hash conferido.','Limpeza move duplicatas; nada excluído sem o José.']),
'F12':('Monitor de atualizações','Como José, quero saber de atualizações que importam e autorizar cada uma.',['Nenhuma atualização sem autorização.']),
'F13':('Painel','Como José, quero ver no Paperclip o estado de cada vídeo, as propostas e as verificações.',['Painel mostra estado vindo do Supabase/issues, nunca do Postgres do Temporal.']),
}
o=['# SPEC da PQBR (requisitos)','',
'> Autoridade: abaixo de `docs/REGRAS.md` (cuja §0–§3 é a constituição do projeto) e acima de `docs/ARQUITETURA.md`. Cada requisito aponta para a seção do REGRAS de onde vem; nenhum requisito cria regra nova.',
'> Fonte única: os IDs RF/RNF são usados em `docs/ARQUITETURA.md`, `docs/TESTES.md`, `docs/ROADMAP.md` e `docs/RASTREABILIDADE.md`. Para mudar um requisito, mude a regra no REGRAS primeiro.',
'> Não consultar material restrito (t287). Legenda: [PROPOSTA] · [HIPÓTESE] · EM CONSTRUÇÃO — aguardando José.','',
'## 1. Requisitos funcionais por funcionalidade','']
for fid,(nome,hist,ac) in F.items():
    o+=[f'### {fid}. {nome}','',f'**História:** {hist}','','**Critérios de aceite da funcionalidade:**']+[f'- {a}' for a in ac]+['','| ID | Requisito | REGRAS |','|---|---|---|']
    o+=[f'| {r[0]} | {r[2]} | {r[3]} |' for r in R if r[1]==fid]+['']
o+=['## 2. Requisitos não funcionais','','| ID | Requisito | REGRAS |','|---|---|---|']+[f'| {n[0]} | {n[1]} | {n[2]} |' for n in N]
o+=['','## 3. Lacunas (não inventar; levar ao José)','',
'- **EM CONSTRUÇÃO — aguardando José:** regras de roteiro R1–R6, R8 e R9 (contrato v2, F7-01). Afetam RF-07.',
'- **EM CONSTRUÇÃO — aguardando José:** metas do piloto (definidas depois, t327). Afetam V1–V7 e F12-01.',
'- **EM CONSTRUÇÃO — aguardando José:** limite de RAM aceitável para o motor (RNF-09); combinar antes de F05-01.',
'- [PROPOSTA] local dedicado da revisão humana (RF-36): registro no Supabase + `04_Privados_Revisao` no Drive.',
'- [PROPOSTA, validar na Fase 0.5] ponte Temporal ↔ Paperclip (RF-33, RF-43).',
'- [HIPÓTESE] H1–H16, H-ORQ1–3, H-SDD1–3 (ARQUITETURA §7) condicionam RF-10, RF-15, RF-22, RF-24, RF-25, RF-34, RF-43.','']
open('/workspace/sanit/out/docs/SPEC.md','w').write('\n'.join(o))
# matriz
m=['# Matriz de rastreabilidade','',
'> Requisito → regra → desenho → tarefa → teste. Gerada a partir da mesma lista de `docs/SPEC.md`; ao mudar um ID, atualize os cinco documentos no mesmo commit.','',
'| Requisito | REGRAS | ARQUITETURA | ROADMAP | TESTES |','|---|---|---|---|---|']
m+=[f'| {r[0]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} |' for r in R]
m+=[f'| {n[0]} | {n[2]} | {n[3]} | {n[4]} | {n[5]} |' for n in N]
m+=['','Validação (REGRAS §14): V1 contrato editorial · V2 consistência visual · V3 auditor · V4 publicação sem duplicidade · V5 correção pós-publicação · V6 procedência · V7 premissas técnicas. Detalhe em `docs/TESTES.md` §3.','']
open('/workspace/sanit/out/docs/RASTREABILIDADE.md','w').write('\n'.join(m))
# ids used
import re
ts=set();tk=set()
for r in R+N:
    for x in re.split(r',\s*',r[-1]): ts.add(x)
    for x in re.split(r',\s*',r[-2]): tk.add(x)
print(sorted(ts)); print(sorted(tk))
