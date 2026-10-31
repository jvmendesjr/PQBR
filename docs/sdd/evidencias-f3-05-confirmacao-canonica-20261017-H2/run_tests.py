"""Runner OFFLINE stdlib. Saída nova, sem importar pqbr/Temporal ou ler ambiente/segredos."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
import unittest
from dataclasses import asdict


def bloquear(evento, args):
    if (evento.startswith('socket.') or evento.startswith('subprocess.')
            or evento in ('os.system', 'os.posix_spawn', 'os.posix_spawnp', 'os.exec', 'os.fork', 'os.forkpty')):
        raise RuntimeError('Runner H2 bloqueou rede/subprocesso: ' + evento)


sys.addaudithook(bloquear)
raiz = Path(__file__).resolve().parent
sys.path.insert(0, str(raiz))
exigir_saida = len(sys.argv) == 2
if not exigir_saida:
    raise SystemExit('Uso: python3 -I -S run_tests.py DIRETORIO_NOVO')
saida = Path(sys.argv[1]).resolve()
saida.mkdir(parents=True, exist_ok=False)

import test_confirmacao
from fakes import cenario
from modelos import EventoVinculado


class ResultadoDetalhado(unittest.TextTestResult):
    def startTest(self, test):
        self.ids.append(test.id())
        super().startTest(test)

    def __init__(self, *args, **kwargs):
        self.ids = []
        super().__init__(*args, **kwargs)


suite = unittest.defaultTestLoader.loadTestsFromModule(test_confirmacao)
with (saida / 'testes.log').open('w') as log:
    resultado = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=ResultadoDetalhado).run(suite)

resumo = {
    'portas': 'TODAS FAKES EM MEMORIA; sem transporte real',
    'testes': resultado.testsRun, 'falhas': len(resultado.failures),
    'erros': len(resultado.errors), 'pulados': len(resultado.skipped),
    'sucesso': resultado.wasSuccessful(), 'ids': resultado.ids,
    'pqbr_ou_temporal_importado': any(m == 'pqbr' or m.startswith('pqbr.') or m == 'temporalio'
                                     or m.startswith('temporalio.') for m in sys.modules),
    'rede_subprocesso': 'bloqueados por audit hook Python (não sandbox de kernel)',
    'crash_safety_durabilidade_real': 'NAO PROVADAS',
}
(saida / 'resultado.json').write_text(json.dumps(resumo, indent=2, ensure_ascii=False) + '\n')


def demo(canal):
    ctx, relogio, vinculo, pc, sup, ad, trilha = cenario()
    iid = ad.abrir(ctx)
    antes = {'ticket_existente': ctx.issue_id, 'interacao': pc.registros[iid].copy(),
             'pendentes': list(ctx.escopo.pendentes), 'operacao_terminal': ctx.escopo.falha_id}
    # Cópia profunda JSON para preservar estado anterior.
    antes = json.loads(json.dumps(antes))
    if canal == 'paperclip':
        pc.painel_decidir_fixture(iid)
        primeiro = ad.pelo_painel(ctx, iid)
    else:
        evento = EventoVinculado(vinculo.usuario, 'discord', ctx.issue_id, iid,
                                  ctx.escopo.revisao, ctx.escopo, 'accepted', relogio.agora())
        vinculo.registrar_fixture('FAKE-decisao', evento)
        primeiro = ad.pelo_discord(ctx, iid, 'FAKE-decisao')
    duplicata = ad.pelo_painel(ctx, iid)
    dados = {'aviso': 'SINTETICO: todas as portas são fakes; não enviado a serviço algum',
             'canal': canal, 'antes': antes, 'registro_canonico_fake': pc.registros[iid],
             'receipt_local_fake_consumido': asdict(next(iter(sup.receipts.values()))),
             'primeiro': primeiro, 'duplicata': duplicata, 'executados_fake': sup.executados,
             'terminal_nao_reexecutado': ctx.escopo.falha_id not in sup.executados,
             'total_interacoes': len(pc.registros), 'trilha': trilha,
             'limite': 'locks/CAS/dedup apenas memória, sem crash safety ou durabilidade real'}
    (saida / ('demo-' + canal + '.json')).write_text(json.dumps(dados, indent=2, ensure_ascii=False) + '\n')


if resultado.wasSuccessful():
    demo('paperclip')
    demo('discord')
print(json.dumps({k: v for k, v in resumo.items() if k != 'ids'}, ensure_ascii=False))
raise SystemExit(0 if resultado.wasSuccessful() and not resumo['pqbr_ou_temporal_importado'] else 1)
