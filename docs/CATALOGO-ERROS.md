# Catálogo de erros de produção (`pqbr.catalogo_erros`)

Decisão do José em 25/10/2026, às 14:09 BRT. Migração `0019_pqbr_catalogo_erros.sql` (rollback em `rollback/0019_down.sql`). Mapa: `docs/mapa/10-catalogo-erros.mmd`.

## Para que serve
Guarda os erros já vistos na produção de Shorts, cada um com a instrução que o evita (`prevencao`). Os agentes internos consultam o catálogo **antes de gerar** e anexam as prevenções ao prompt ou à checagem.

## Quem escreve, quem lê
- **Escreve:** só o **agente externo** (t538-P), com OK do José, pelo papel `pqbr_app` ou por um seed versionado em `db/seeds/`. Não existe delete: um erro superado recebe `ativo=false`.
- **Lê:** os agentes internos, pela função `pqbr.pipeline.catalogo_erros_leitura.catalogo_erros_para_papel(papel)` ou pela activity `catalogo_erros_consultar`.
  - A leitura usa `pqbr_leitura` quando `PQBR_LEITURA_PASSWORD` está no ambiente.
  - Sem essa senha, usa `pqbr_app` em transação `READ ONLY`.
  - `prevencoes_para_prompt()` formata as prevenções em linhas como `- [codigo/severidade] instrução`.
- **RLS:** ligado e forçado.
  - `pqbr_app`: select, insert, update.
  - `pqbr_leitura`: select.

## Campos
| Campo | Conteúdo |
|---|---|
| `codigo` | Código estável `ERR-XXX-NN` (PER personagem, ROT roteiro, EST estilo, MON montagem, TXT texto na imagem, CMP compliance, CUS custo) |
| `categoria` | estilo, personagem, roteiro, montagem, texto_na_imagem, compliance, custo |
| `descricao` / `exemplo` | O erro e onde ele apareceu (`{"tema", "caminho"}`) |
| `prevencao` | Instrução para o prompt ou para a checagem |
| `severidade` | baixa, media, alta, bloqueante |
| `papeis_interessados` | Papéis do `REGISTRO` (lider-editorial, auditor, lider-compliance, dev…) |

Contrato Pydantic: `pqbr.contratos.catalogo_erros.ErroCatalogo`, versão `CATALOGO_ERROS_VERSAO = "1.0.0"`.

## Carga inicial (lote-2510)
| Código | Erro | Severidade |
|---|---|---|
| ERR-PER-01 | Personagem inconsistente (barba, cabelo, camiseta) | alta |
| ERR-ROT-01 | Café escuro em "café fraco" (detalhe do roteiro ignorado) | alta |
| ERR-EST-01 | Cenário repetitivo | média |
| ERR-EST-02 | Cena fora do cenário | média |
| ERR-MON-01 | Último quadro congelado (clipe mais curto que a fala) | alta |
| ERR-MON-02 | CTA personalizado substituído por genérico (seed `db/seeds/seed_catalogo_erros_err_mon_02.sql`, 25/10) | alta |
| ERR-EST-03 | Mistura de modelos com traços diferentes | média |
| ERR-TXT-01 | Texto inventado na imagem (Runway Kling/Seedance) | alta |
| ERR-CMP-01 | CTA fora do padrão | média |
| ERR-CMP-02 | Pessoa real nomeada | bloqueante |
| ERR-CMP-03 | Marca real | bloqueante |
| ERR-CMP-04 | Pedido de comentário na fala | alta |

## Pendente
A activity está pronta, mas ainda não foi registrada em nenhum worker nem é chamada pelos workflows. Ligar a consulta às etapas de geração exige proposta aprovada.
