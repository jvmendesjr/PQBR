# Testes t460 (capa) e t461 (persona) — 12/10/2026

Arquivo completo (verificado): Drive `00_Biblia_Visual/pesquisas/` (bff9409b_t460-capa, c753867a_t461-persona-com, ce30c1e2_t461-persona-sem), repo `docs/pesquisas/arquivo-cadernos/`, `pqbr.arquivo_caderno`. Os vídeos ficam no Drive, no Postgres (só metadados e hash) e no disco, não no git. Os cadernos foram apagados depois da verificação. Cota: 2 vídeos e 1 infográfico.

## Capa (t460)
- **Comando:** `notebooklm generate infographic -n <id> --orientation portrait --detail concise --language pt_BR --wait "<pedido: UMA ilustração 2D da cena, sem texto>"` e depois `download infographic`.
- **Saída:** PNG **1536×2752** (≈9:16; para 1080×1920, escalar para 1080×1935 e recortar 15 px). É uma ilustração só, sem texto, com o estilo e o personagem da fonte. A ação pedida (trono de moedas) não foi seguida.
- **Marca d'água:** nenhuma visível. Tem metadado **C2PA assinado pela Google** e provavelmente SynthID invisível; re-encodar remove o C2PA, o SynthID não.
- **Chat:** `ask "gere uma imagem…"` cria um artefato **File (.jpg)** no Studio, mas a CLI 0.8.4 não baixa esse tipo.

## Persona (t461), mesma fonte e mesmo steering
- O "View custom prompt" (`artifact get-prompt`) mostra **só o steering** nos dois casos: a persona do chat não entra no prompt do vídeo.
- **2D:** mantido nos dois, só com o steering e o bloco [ESTILO] da fonte. Short em 720×1280, 60–63 s.
- **Com persona:** o personagem fica consistente nas primeiras cenas. **Sem persona:** o personagem some depois da 1ª cena.
- Nos dois aparece título escrito dentro da imagem e, no "sem", texto ilegível; isso vai para `erros_aceitaveis` ou para o Auditor.
- **Risco:** o personagem grisalho de barba pode lembrar pessoa real; o Auditor precisa checar semelhança.
- **Conclusão:** persona como texto fixo do pacote é suficiente; o que segura o 2D e o personagem é o steering mais a fonte com [ESTILO]/[PERSONAGEM]. Reforçar no steering: "sem títulos nem texto na imagem" e "o mesmo personagem em TODAS as cenas".
