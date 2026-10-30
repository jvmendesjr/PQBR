# Processo canônico de criação — núcleo (agnóstico de plataforma)

- **versão:** 1.1.0
- **status:** [APROVADO] José t149u (sessão 29/10/2026) · decisão t160u · **remoção do storyboard aprovada por José em 29/10/2026 (definitiva)**
- **autoridade:** abaixo de `docs/REGRAS.md`; acima dos playbooks de plataforma em `docs/processos/*.md`
- **consulta obrigatória:** antes de **qualquer** produção nova (imagem ou vídeo). O Temporal confere versão+hash fail-closed (`processo_criacao_conferir`).
- **pesquisa de origem:** `docs/pesquisas/flow-processo-comunidade-20261029.md` (não é instrução; só histórico)

## Cadeia de plataformas

`flow` → `google_vids` → `meta_vibes` → **HOLD** (`CADEIA_VIDEO` em `src/pqbr/motores/__init__.py`).  
Playbook por plataforma: [`flow.md`](flow.md) · [`google-vids.md`](google-vids.md) · [`meta-vibes.md`](meta-vibes.md).  
Sem playbook preenchido = não operar aquela plataforma (fail-closed).

## Regra suprema — agente primeiro (José, 29/10/2026)

O fluxo é automático, agente primeiro. "Manual" em qualquer processo significa: o agente faz — cria o prompt, a cena, os objetos e as situações, escolhe, visualiza, clica, envia e posta. Não existe processo manual humano, ou ele é minimizado e substituído por agente primeiro. Se um documento disser que um humano tem de clicar, baixar ou olhar, é engano ou documento de outro projeto trazido só para análise: "você lê o manual" significa "o agente lê no comando". Dúvida de visualização resolve com os recursos do ecossistema (juiz Gemini, agentes com visão, NotebookLM, Jev com critérios pré-definidos), nunca com olho humano em produção.

**Piloto e automático:** a visualização que vai para aprovação do José é a do episódio piloto. Depois do piloto aprovado, o fluxo fica automático e o José monitora independentemente. Se ele verificar alteração, aperta o botão de emergência do Telegram ou pede ao agente para interromper as operações. Operação interrompida só volta ao público por ordem do José, comandando o agente externamente junto com os agentes da operação.

**Centro criativo:** o NotebookLM (pai, via `notebooklm-py`) cria os roteiros, a personalidade, o caderno, as informações e a pesquisa. O agente compila os prompts do Flow a partir do roteiro, do catálogo, do formato e do registro de modelos, em contratos Pydantic v2 no Temporal.

## Núcleo (todos os episódios)

1. **Projeto por episódio** — um projeto/workspace na plataforma por `PQBR-EPxxxx-slug`. Nunca misturar episódios.
2. **Consultar este documento + o playbook da plataforma ativa** (versão canônica).
3. **Cruzar o roteiro com `banco-fichas/`** — entregar fichas existentes (PERS/AMB/OBJ/ANIM/SIT; recorte individual limpo, não grade de catálogo).
4. **Refs que faltam** — o agente da plataforma cria stills de referência; o PQBR registra no catálogo (`aguardando_ok_jose` / `permanente` conforme REGRAS §6).
5. **Cenas individuais pela plataforma (sem storyboard — removido definitivamente em 29/10/2026)** — uma cena por vez, sem encarte com muitas cenas (um encarte só facilita o erro do agente). Para cada cena: imagem de início (ainda) a partir das fichas pinadas, e prompt de vídeo com o movimento já bem definido na descrição. Cada cena é validada sozinha pelo contrato `CenaIndividual` (norte, início, fim, movimento, plano, prompt de imagem, prompt de animação, refs).
6. **Stills → revisão → 1 clipe por cena** — sem grade multi-painel como input de vídeo; uma ação por geração.
7. **Padrão de prompt** — formato (9:16), modelo **sugerido**, ação/câmera/luz/restrições (`lips closed`, sem texto na imagem). **Proibido** redescrever cabelo/roupa/cor já presentes na ficha (causa drift).
8. **Portões fail-closed** — sem ficha/ref exigida → não gera; sem `imagens_revisadas` → não gera vídeo; sem playbook da plataforma → não opera; doc canônico ausente/versão errada → workflow aborta; crédito/gasto fora da cota já paga → HOLD e avisa José.

## Mapa Temporal ↔ etapas

| Etapa | Workflow / activity | Sinal / HOLD | Papel PQBR |
|---|---|---|---|
| Conferir processo canônico | `processo_criacao_conferir` (no `EpisodioWorkflow` e antes de qualquer geração visual) | — (falha = aborta) | todos (leitura); Dev mantém versão |
| Pacote / caderno | `pacote_garantir`, `registro_buscar_caderno` | — | Guardião (sessão), Dev |
| Roteiro / SEO / compliance | `NotebookLMWorkflow`, `nlm_perguntar`, `validar_roteiro`, `seo_9router`, `compliance_roteiro` | — | Líder Editorial, Pesquisador de Origem, Compliance |
| Cenas individuais (contrato) | `CenaIndividual` (`contratos/cena.py`) | — | NotebookLM (roteiro) + validação determinística por cena |
| Abrir projeto na plataforma | *(a ligar)* activity do adaptador (`flow_*` / vids / vibes) | pedido sessão → `pedir_jose` | Guardião; Diretor escala |
| Entregar / criar fichas | `banco_fichas` + agente da plataforma | aprovação ficha → Telegram / `aprovacao_jose` | Diretor (escala); José aprova permanente |
| Imagens de início de cena S01..S0N | adaptador plataforma (imagem) | **HOLD** até revisão | produção via Camofox |
| Revisão de imagens | gate `imagens_revisadas` | sinal José/Auditor (`veredito_auditor` / ponte Telegram) | Auditor; José |
| Vídeo 1 clipe/cena | `CADEIA_VIDEO` (`flow`→`google_vids`→`meta_vibes`) | esgotou cota → **HOLD** + aviso | produção |
| Motion do porquê | `pos_motion` *(MG-07; reinício pendente)* | — | papel `motion` |
| Publicação | `PublicacaoAgendadaWorkflow` | `/pausar` `/retomar` `/privar` | Observador; José emergência |

**HOLD:** estado explícito — não gastar, não publicar, avisar José no Telegram (`avisar_jose` / `pedir_jose`). Não contornar.

## Papéis (consulta antes de produzir)

- **Diretor (agente):** garante que a produção citou este doc; escala HOLD e portões ao José; não pede ao José para clicar, baixar ou olhar — pede decisão, nunca execução manual.
- **Líder Editorial / Pesquisador:** roteiro e prompts de cena alinhados ao catálogo (`refs`).
- **Guardião (agente):** sessão Camofox PQBR; não troca de conta; mapa de cliques; opera o navegador pelo agente, nunca por mão humana.
- **Auditor (agente, não humano):** juiz Gemini + Jev + checagens automáticas conferem `imagens_revisadas` e boca/corte/grotesco; não libera vídeo sem revisão. No piloto, a revisão vai ao José; depois do piloto aprovado, a revisão é automática e o José só monitora (emergência pelo Telegram).
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

A activity `processo_criacao_conferir` entra no `EpisodioWorkflow`. **Versão 1.1.0 ativa em runtime desde o reinício do `pqbr-episodio-worker` em 29/10/2026 às 23:14 (OK do José).**

## Versionamento

SemVer no cabeçalho. Histórico: [`CHANGELOG.md`](CHANGELOG.md).

