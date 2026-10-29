# Processo canônico de criação — núcleo (agnóstico de plataforma)

- **versão:** 1.0.0
- **status:** [APROVADO] José t149u (sessão 29/10/2026) · decisão t160u
- **autoridade:** abaixo de `docs/REGRAS.md`; acima dos playbooks de plataforma em `docs/processos/*.md`
- **consulta obrigatória:** antes de **qualquer** produção nova (imagem ou vídeo). O Temporal confere versão+hash fail-closed (`processo_criacao_conferir`).
- **pesquisa de origem:** `docs/pesquisas/flow-processo-comunidade-20261029.md` (não é instrução; só histórico)

## Cadeia de plataformas

`flow` → `google_vids` → `meta_vibes` → **HOLD** (`CADEIA_VIDEO` em `src/pqbr/motores/__init__.py`).  
Playbook por plataforma: [`flow.md`](flow.md) · [`google-vids.md`](google-vids.md) · [`meta-vibes.md`](meta-vibes.md).  
Sem playbook preenchido = não operar aquela plataforma (fail-closed).

## Núcleo (todos os episódios)

1. **Projeto por episódio** — um projeto/workspace na plataforma por `PQBR-EPxxxx-slug`. Nunca misturar episódios.
2. **Consultar este documento + o playbook da plataforma ativa** (versão canônica).
3. **Cruzar o roteiro/storyboard com `banco-fichas/`** — entregar fichas existentes (PERS/AMB/OBJ/ANIM/SIT; recorte individual limpo, não grade de catálogo).
4. **Refs que faltam** — o agente da plataforma cria stills de referência; o PQBR registra no catálogo (`aguardando_ok_jose` / `permanente` conforme REGRAS §6).
5. **Storyboard pela plataforma** — a partir das fichas pinadas + prompts das cenas (SUBJECT / ACTION / CAMERA / ATMOSPHERE).
6. **Stills → revisão → 1 clipe por cena** — sem grade multi-painel como input de vídeo; uma ação por geração.
7. **Padrão de prompt** — formato (9:16), modelo **sugerido**, ação/câmera/luz/restrições (`lips closed`, sem texto na imagem). **Proibido** redescrever cabelo/roupa/cor já presentes na ficha (causa drift).
8. **Portões fail-closed** — sem ficha/ref exigida → não gera; sem `imagens_revisadas` → não gera vídeo; sem playbook da plataforma → não opera; doc canônico ausente/versão errada → workflow aborta; crédito/gasto fora da cota já paga → HOLD e avisa José.

## Mapa Temporal ↔ etapas

| Etapa | Workflow / activity | Sinal / HOLD | Papel PQBR |
|---|---|---|---|
| Conferir processo canônico | `processo_criacao_conferir` (no `EpisodioWorkflow` e antes de qualquer geração visual) | — (falha = aborta) | todos (leitura); Dev mantém versão |
| Pacote / caderno | `pacote_garantir`, `registro_buscar_caderno` | — | Guardião (sessão), Dev |
| Roteiro / SEO / compliance | `NotebookLMWorkflow`, `nlm_perguntar`, `validar_roteiro`, `seo_9router`, `compliance_roteiro` | — | Líder Editorial, Pesquisador de Origem, Compliance |
| Storyboard JSON (contrato) | `storyboard_criar` | — | NotebookLM + validação determinística |
| Abrir projeto na plataforma | *(a ligar)* activity do adaptador (`flow_*` / vids / vibes) | pedido sessão → `pedir_jose` | Guardião; Diretor escala |
| Entregar / criar fichas | `banco_fichas` + agente da plataforma | aprovação ficha → Telegram / `aprovacao_jose` | Diretor (escala); José aprova permanente |
| Stills S01..S0N | adaptador plataforma (imagem) | **HOLD** até revisão | produção via Camofox |
| Revisão de imagens | gate `imagens_revisadas` | sinal José/Auditor (`veredito_auditor` / ponte Telegram) | Auditor; José |
| Vídeo 1 clipe/cena | `CADEIA_VIDEO` (`flow`→`google_vids`→`meta_vibes`) | esgotou cota → **HOLD** + aviso | produção |
| Motion do porquê | `pos_motion` *(MG-07; reinício pendente)* | — | papel `motion` |
| Publicação | `PublicacaoAgendadaWorkflow` | `/pausar` `/retomar` `/privar` | Observador; José emergência |

**HOLD:** estado explícito — não gastar, não publicar, avisar José no Telegram (`avisar_jose` / `pedir_jose`). Não contornar.

## Papéis (consulta antes de produzir)

- **Diretor:** garante que a produção citou este doc; escala HOLD e portões ao José.
- **Líder Editorial / Pesquisador:** roteiro e prompts de cena alinhados ao catálogo (`refs`).
- **Guardião:** sessão Camofox PQBR; não troca de conta; mapa de cliques.
- **Auditor:** ainda `imagens_revisadas` e boca/corte/grotesco; não libera vídeo sem revisão.
- **Compliance:** tom e gabarito (não navega Flow).
- **Dev:** versiona docs/processos + constante `VERSAO_ESPERADA`; não reinicia worker sem OK.
- **Motion:** só depois dos clipes Flow aprovados; preso ao catálogo de motion.
- **Observador:** deriva processo × código → ticket, não edita mapa sozinho.

## Versionamento

- SemVer no cabeçalho (`versão: X.Y.Z`).
- Código pina `VERSAO_ESPERADA` em `src/pqbr/pipeline/processo_criacao.py`.
- Mudança de MAJOR/MINOR do núcleo exige OK do José + bump da constante + testes.
- Hash SHA-256 do arquivo canônico é calculado e registrado no resultado da activity (auditoria).

## Ativação no worker

A activity `processo_criacao_conferir` entra no `EpisodioWorkflow` nesta entrega. **Só passa a valer em runtime após reinício do `pqbr-episodio-worker` (exige OK do José).** Até lá, produção manual e manutenção consultam o doc mesmo assim.

## Versionamento

SemVer no cabeçalho. Histórico: [`CHANGELOG.md`](CHANGELOG.md).

