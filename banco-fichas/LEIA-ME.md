# Banco de fichas — catálogo visual do canal

Estilo (José, t150u): **cartoon 2D, flat, colorido, com personagens stickman**. Não é pessoa realista, não é 3D e não é o nanquim de t146u.

**Catálogo aberto (José, t150u):** tudo aqui é referência e sugestão, não lista fechada. O agente pode inserir personagens, figuras, animais, objetos, ambientes e situações novos, e deve variar o elenco em vez de repetir sempre os mesmos. Antes de criar, busca; reaproveitar vem antes.

A semente é o padrão definitivo do canal (t148u): o conjunto entregue pelo José no Drive (`Fontes/Imagens`, id `1ziYivEewPQIvlgt6Z7v7R8wXPerPLvLd`) em 28/10/2026. As fichas em nanquim geradas no Flow em t146u foram descartadas a pedido dele (preservadas no histórico do git, commit `ad1b689`).

## O que entra

| Tipo | Pasta | Id | O que é |
|---|---|---|---|
| Personagem | `personagens/` | `PERS-*` | stickman do elenco, com acento (peça ou cor chapada); folha individual multi-pose ou recorte da grade `ELENCO-catalogo.png` (13 no catálogo) |
| Figura | `figuras/` | `FIG-*` | ente de apoio fora do elenco e dos animais (robô, fantasma, criatura, mascote); a pasta nasce com a primeira ficha |
| Animal | `animais/` | `ANIM-*` | animal no mesmo traço flat (grade `ANIM-catalogo.png` e uma ficha por bicho) |
| Objeto | `objetos/` | `OBJ-*` | objeto do cotidiano ou do tema, sem marca e sem texto (grade `OBJ-catalogo.png` e uma ficha por objeto) |
| Ambiente | `ambientes/` | `AMB-*` | lugar em 16:9; 3 incluem personagens do elenco em cena (prova de escala) |
| Situação | `situacoes/` | `SIT-*` | pose ou movimento corriqueiro de um personagem (acenar, pensar, digitar, correr); imagem e vídeo curto |

Modelos de ficha em `modelos/`. Índice legível por máquina: `indice.json` (3.0.0). Contrato: `src/pqbr/contratos/catalogo_visual.py` (`FichaCatalogo` 1.0.0). Código: `src/pqbr/pipeline/banco_fichas.py`.

## Como o agente insere e usa

CLI: `PYTHONPATH=src python -m pqbr.pipeline.banco_fichas listar|obter|buscar|registrar <json>|aprovar|descartar|resumo`.

1. **Buscar** (`buscar`): se existe ficha parecida, reaproveitar. O registro recusa título repetido no mesmo tipo e devolve os `similares`.
2. **Registrar** (`registrar`): id `PREFIXO-slug`, título, trava (frase curta repetida igual), tags; para situação, `acao`; para personagem, `acento`. Nunca sobrescreve outra ficha.
3. **Estados:** `sugestao` (ideia sem mídia), `aguardando_ok_jose` (com imagem ou vídeo, já usável) e `permanente` (o José aprovou). Só o José aprova (`aprovar`) ou manda descartar (`descartar`); ficha permanente só muda por ordem dele.
4. **Anexar mídia** (`anexar_midia`): a ficha `sugestao` vira `aguardando_ok_jose`. Recortes nomeados (`adicionar_recorte`) guardam poses da folha como retângulos normalizados.
5. **Prompt do storyboard:** `resumo_para_prompt()` lista os ids que podem ir em `refs`.

O contrato recusa 3D, realismo, texto na imagem, marca, pessoa real e nome de personagem escrito ou falado.

## Mídia (política do repositório)

- **Imagem nova:** até 2 MB no repositório (png, jpg ou webp). Acima disso, vai para o Drive (`integrations/drive.py`) e a ficha guarda o `imagem_drive_id`.
- **Vídeo:** sempre no Drive (`videos[].drive_id`, até 30 s, no máximo 6 por ficha). Nunca no git.
- As imagens da semente (t148u) têm de 2,5 a 6 MB e ficam como estão. O que entra de novo segue a regra acima.

## Protagonistas

A alternância do storyboard segue por gênero (par = masculino, ímpar = feminino). Definidos pelo José em t150u: **masculino = `PERS-menino-azul`** (nº 1) e **feminino = `PERS-menina-rosa`** (nº 2). Os demais entram como coadjuvantes e para variar o elenco. `PERS-bob-oculos` entrou no catálogo como 13º.

## Como o Flow usa

A folha ou o recorte do personagem entra como referência (`Elemento`), citada pelo id curto. O recorte individual para a cena é gerado a partir da folha quando a produção pedir; a folha inteira nunca vai como imagem única para animar vídeo (t146u). O prompt da cena muda pose, expressão, objeto e lugar; não redesenha cabeça nem roupa. A situação (`SIT-*`) dá a pose ou o movimento; o personagem vem do catálogo.

## Como o motion usa

O bloco do porquê em motion pode ter um personagem do catálogo presente (num quadro do layout, explicando ou participando), com recorte da folha ou vídeo de situação. Ver `docs/fases/motion-graphics.md` e `PlanoMotion.personagem`. A coletânea de referências de motion fica em `referencias-motion/`.

## O que não volta

- As fichas em nanquim de t146u (descartadas pelo José em t148u).
- A bíblia de 08/10 (Zé, Lia, Valdemar, Sandra) fica histórica. Nome não entra no vídeo.
- Os frames antigos do canal (`referencias-canal/`), descartados em t149u por ordem do José.
