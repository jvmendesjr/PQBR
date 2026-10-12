# PQBR — Caderno mestre vs. efêmeros e papel da persona (pesquisa 12/10/2026)
Legenda: [OF]=oficial Google · [COM]=comunidade/blogs · [INF]=inferência

## Achados
1. [OF] O Video Overview tem personalização própria: formato (Cinematic/Explainer/Short), idioma, estilo visual (Classic, Whiteboard, Watercolor, Retro Print, Heritage, Paper-craft, Kawaii, Anime, auto ou Custom com descrição; **NÃO disponível para Cinematic e Short**) e um "steering prompt" de foco. O prompt usado fica visível em "View custom prompt". https://support.google.com/notebooklm/answer/16454555
2. [COM] Configure Chat tem um campo Custom de até 10.000 caracteres. Os guias divergem sobre o alcance: um diz que vale "para toda conversa e todos os outputs do Studio" (https://www.shareuhack.com/en/posts/notebooklm-advanced-guide-2026); outros tratam a persona como coisa do chat, com o steering do Studio separado (https://zaidalhuda.github.io/notebooklm-guide/NotebookLM_Comprehensive_Guide.pdf, https://aiarabai.com/en/notebooklm-video-overviews-updates/). A ajuda oficial do Video Overview não cita a persona. **Sem evidência oficial de que a persona afeta o Short.**
3. [COM] A persona é opaca e pode fazer o chat distorcer ou negar as fontes (https://www.xda-developers.com/notebooklm-personas-can-lie-about-sources/), o que é um risco de deriva num caderno mestre.
4. [COM] O padrão da comunidade para "caderno mestre" é um **índice ou corpus** (um mapa dos outros cadernos, ou o corpus bruto do qual saem cadernos focados), não uma central geradora de prompts. Não é possível conversar entre cadernos. Usam um caderno por pergunta/tema, porque a relevância importa mais que a quantidade de fontes. https://www.makeuseof.com/notebooklm-prompt-overview-all-sources/ · https://www.makeuseof.com/notebooklm-tips-tricks-improve-research/ · r/notebooklm: https://www.reddit.com/r/notebooklm/comments/1v9mob9/
5. [COM, citando páginas Google em 08/10/2026] Limites: free com 100 cadernos e 50 fontes; Plus com 200 e 100; Pro com 500 e 300. A cota é por computação, renova a cada 5 h e tem teto semanal; a geração de Overviews tem limite diário (Pro em torno de 20/dia). O Google não publica limite de caracteres do prompt do chat. https://masterprompting.net/blog/how-to-use-notebooklm-study-research · https://notebooklm-guide.com/notebooklm-system-limits-benchmarks/
6. [INF] Não encontrei relatos de faceless creators usando um caderno mestre como gerador de prompts. Automações (notebooklm-py e afins) criam cadernos por job.

## Avaliação técnica
**Q1 – Mestre como central de prompts: não recomendo como peça de produção.**
- Determinismo: o chat do NotebookLM não tem temperatura nem seed, não tem saída estruturada nativa, e o histórico de conversa influencia as respostas. Já o LLM via 9router aceita schema/Pydantic, temperatura baixa, retry e cache [INF].
- Operação: a geração passa por browser (Camofox), com mais latência, risco de sessão e risco de detecção, e consome a mesma cota usada nos vídeos [INF].
- Deriva e opacidade: veja o achado 3. A sincronia com o pacote por hash exige recriar o caderno a cada versão.
- Benefício real: as respostas saem ancoradas nas fontes canônicas, com citações. Isso dá para reproduzir pondo o pacote canônico no contexto do LLM, já que ele é pequeno.
- **Recomendação:** 100% cadernos efêmeros com o pacote canônico versionado mais as fontes do tema. Personas, steering prompts e os pedidos ao Gemini Web saem de **templates + LLM 9router (core-medio, revisão core-revisao)** com contrato Pydantic, cache por (tema, hash do pacote) e registro no Postgres. Se José quiser, o mestre pode existir como **caderno de consulta humana/índice**, somente leitura, fora do pipeline, protegido e recriável pelo hash.

**Q2 – Persona por caderno: manter, mas barata e gerada por template.**
- A alavanca comprovada do vídeo é o **steering prompt do Video Overview** mais a **seleção de fontes**. O estilo visual não se aplica ao Short, então o 2D precisa vir do texto do steering e das fontes de estilo [OF].
- O efeito da persona sobre o Short não está comprovado. Mesmo assim, ela custa pouco e ajuda no chat (capa, checagens). Mantenha a persona como texto fixo do pacote (≤10k caracteres), com a variação do tema só nos campos do template.

## Cuidados
- O Short não aceita estilo visual, então o bloco §16.7 precisa ir no steering e nas fontes.
- Registrar sempre o "View custom prompt" de cada artefato para auditoria.
- Garantir que só as fontes do episódio estejam selecionadas antes de gerar.
- Respeitar o limite de cadernos do plano, porque os cadernos acumulados até a exclusão em 48 h ocupam esse limite. Monitorar a cota diária de Overviews.

## Testes para confirmar
1. A/B da persona: no mesmo caderno, mesmas fontes e mesmo steering, gerar 2 Shorts com persona default e 2 com a persona PQBR. Comparar tom, gancho, PT-BR e 2D, e ler o "View custom prompt" para ver se a persona aparece.
2. Steering sozinho: com persona default, um steering com o §16.7 resumido. Medir a aderência ao 2D.
3. Limite do steering: aumentar o tamanho até truncar ou dar erro.
4. Repetibilidade: gerar 3 vezes com as mesmas entradas e medir a variância.
5. Prompts via 9router vs. via caderno mestre (um caderno de teste temporário, apagado depois): mesma tarefa, comparar a qualidade e o custo de cota.
