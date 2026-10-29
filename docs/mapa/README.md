# Mapa do sistema PQBR (`docs/mapa/`)

Diagramas Mermaid **gerados a partir do código real** (workflows, activities, filas, config) em 24/10/2026. O que não está confirmado no código aparece com **⚠**. Página única para ver tudo: `index.html` (abre no navegador; mermaid.js por CDN).

| Arquivo | O que mostra | Fonte no código |
|---|---|---|
| `00-visao-geral.mmd` | Temporal no centro, filas/workers, Schedules, motores trocáveis, 8 papéis, contratos, Postgres, Telegram, sinais | `workflows/worker*.py`, `scripts/temporal/schedules.py`, `config/motores.json`, `agents/__init__.py` |
| `01-episodio.mmd` | EpisodioWorkflow (NotebookLM → pós → capa → sinal do Auditor → arquivo → publicação dry-run → reposição/apagar D+2) | `workflows/episodio.py` |
| `02-reposicao-temas.mmd` | ReposicaoTemasWorkflow (NotebookLM propõe, Líder Editorial valida) | `workflows/temas.py` |
| `03-acessos.mmd` | AcessosWorkflow (queda → restauro Camofox → registro → aviso/pedido ao José) | `workflows/acesso.py` |
| `04-descarte.mmd` | DescartarCadernoTeste + ApagarCaderno (3 cópias verificadas antes de apagar) | `workflows/descarte.py`, `workflows/pacote.py` |
| `05-vigia-atualizacoes.mmd` | Vigia semanal do Dev (só leitura, relatório, nunca aplica) | `workflows/atualizacoes.py` |
| `06-runs-presos.mmd` | Alerta de run preso (timer systemd) | `scripts/temporal/runs_presos.py` |
| `08-identidade-camofox.mmd` | Camofox hoje (global 9377 × PQBR 9387 duplicada) e alvo ADR-012 (instâncias por conta, NavegadorIdentidade) | diagnóstico do pc 24/10, `~/.pqbr/camofox/.env` (só nomes) |
| `09-agentes-responsabilidades.mmd` | Agente PQBR (dedicado, pc) × jr (generalista) × YT-LLM (descontinuação); migração planejada do YouTube; pré-requisito do logo; proposta da skill | DECISOES t532–t535, BRIEFING |
| `07-cadeia-video.mmd` | Processo canônico (`docs/processos/`) → Storyboard → Flow → Google Vids → Meta Vibes → HOLD | `motores/__init__.py` (`CADEIA_VIDEO`), `pipeline/processo_criacao.py` |
| `10-catalogo-erros.mmd` | Catálogo de erros (tabela `pqbr.catalogo_erros`, papéis que consultam, agente externo que alimenta) | `db/migrations/0019_*.sql`, `pipeline/catalogo_erros_leitura.py` |
| `11-publicacao.mmd` | Publicação automática (gate com LOOP → 11:40/18:35 → upload privado → público → registro; Telegram só avisa) + botão de emergência (/pausar, /retomar, /privar; flag global fail-closed; auditoria) | `workflows/publicacao.py`, `contratos/emergencia.py`, `db/migrations/0020_*.sql` |

## Regra
**Agentes nunca alteram o mapa sozinhos.** Mudança no mapa só por proposta aprovada pelo José (t517). Agente que perceber divergência entre código e mapa **sinaliza** (Observador/Dev) e propõe o diff; não edita.

## Verificação (sem virar gordura)
`scripts/mapa/verificar_mapa.py` compara o código com o mapa: todo `@workflow.defn` coberto aqui e todas as activities chamadas por esses workflows precisam aparecer pelo nome no `.mmd` correspondente. Roda nos testes (`tests/unit/test_mapa.py`): se o código mudou e o mapa não, o teste **falha e lista o que falta** — um humano (ou agente com OK do José) atualiza. Não gera diagrama automaticamente, de propósito: o mapa é decisão, não espelho.

## O mapa como meio de comunicação (proposta)
- **Níveis de detalhe:** nível 0 = `00-visao-geral` (para o José decidir: o que existe, o que está pausado, onde está o risco); nível 1 = um diagrama por workflow (para agentes e quem for corrigir: activity, fila, decisão); nível 2 = o código. Relatórios citam o nó pelo nome da activity (ex.: "falhou em `motor_consultar`"), não por descrição livre.
- **Para o José:** pedidos e relatórios (Telegram, vigia, Dev) trazem o link do diagrama e o nó afetado; ⚠ no mapa = decisão pendente.
- **Para agentes:** o mapa é contexto de leitura (o que chama o quê, em que fila); propostas de mudança de fluxo vêm como diff de `.mmd` + diff de código juntos.
- **Consistência:** um nome por coisa (activity = nó); ⚠ obrigatório onde há dúvida; a verificação só checa nomes, não layout — barato de manter.
- **Contra gordura:** 8 diagramas no máximo por camada; nada de mapa por papel ou por tela; diagrama que ninguém consulta em 3 meses vai para `docs/_obsoleto/` por proposta.

## Acesso
Página servida só na tailnet: http://<IP tailnet do pc>:8088/ (serviço de usuário `pqbr-mapa.service`, `python3 -m http.server` com bind no IP Tailscale; sem Funnel, sem 0.0.0.0 — t519).
| `12-storyboard-elenco.mmd` | Storyboard em série (FichaCena 1.3.0), stickman flat colorido, catálogo aberto de fichas, papel observa/participa, figurino, caras e bocas sem fala, elenco alternado com protagonistas definidos (t150u) | `contratos/storyboard.py`, `config/estilo_visual.json`, CONTRATO-EDITORIAL §18 e §19 |
Regenerar a página: `python scripts/mapa/gerar_index.py` (t78u).

**Aba Roadmap (t120u):** gerada de `docs/ROADMAP.md` + `docs/ESTADO-ATUAL.md` por `scripts/mapa/roadmap.py` a cada `gerar_index.py` (e no pre-commit). Só leitura; editar as fontes, nunca o HTML.
