"""Reprodução: env -i PATH=/usr/bin:/bin python3 -I -S run_tests.py DIRETORIO_NOVO.

-I -S não carrega site-packages, projeto operacional ou ambiente de credenciais.
O bloqueio Python de rede/subprocesso é uma defesa do harness, não uma sandbox
contra código hostil. Nenhum serviço, Worker, container ou SDK é iniciado.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
import json
import socket
import subprocess
import time
import unittest
from unittest.mock import patch
from dataclasses import asdict


def proibido(*args, **kwargs):
    raise RuntimeError('Efeito externo proibido no harness offline')


class Resultado(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.casos = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.casos.append({'teste': test.id(), 'estado': 'passou'})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.casos.append({'teste': test.id(), 'estado': 'falhou'})

    def addError(self, test, err):
        super().addError(test, err)
        self.casos.append({'teste': test.id(), 'estado': 'erro'})


def demo(canal):
    from test_autorizacao import ambiente
    from contratos import PedidoDecisao
    f, t, p, d, s, r, trilha = ambiente()
    ticket, notificado = f.abrir_pedido()
    antes = {'bloqueado': s.bloqueado, 'pendentes': s.pendentes,
             'falhas': sorted(s.falhas), 'aceitos': sorted(s.aceitos)}
    pedido = PedidoDecisao(ticket.ticket_id, ticket.revisao, ticket.escopo, 'aprovar', 'SYN-DEC-demo')
    port = p if canal == 'paperclip' else d
    ator = 'SYN-HUMANO-painel' if canal == 'paperclip' else 'SYN-HUMANO-discord'
    port.autenticar_fixture('SYN-EVENT-demo', ator, pedido)
    call = f.pelo_painel if canal == 'paperclip' else f.pelo_discord
    resposta, duplicata = call('SYN-EVENT-demo'), call('SYN-EVENT-demo')
    return {'canal': canal, 'somente_fakes': True, 'antes': antes,
            'ticket_canonico': asdict(t.ler(ticket.ticket_id)),
            'comando': asdict(next(iter(s.consumidos.values()))),
            'resposta': resposta, 'duplicata': duplicata, 'trilha': trilha,
            'depois': {'bloqueado': s.bloqueado, 'executados': s.executados,
                       'falhas': sorted(s.falhas), 'admissao_fechada': s.admissao_fechada}}


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Informe diretório de resultado NOVO')
    output = Path(sys.argv[1]).resolve()
    output.mkdir(exist_ok=False, parents=True)
    patches = [(socket, 'socket'), (socket, 'create_connection'), (socket, 'getaddrinfo'),
               (subprocess, 'Popen')]
    from contextlib import ExitStack
    inicio = time.monotonic()
    with ExitStack() as stack:
        for obj, name in patches:
            stack.enter_context(patch.object(obj, name, proibido))
        # Autoteste do bloqueio: nunca tenta conectar, resolve DNS ou cria processo.
        for obj, name in patches:
            try:
                getattr(obj, name)()
            except RuntimeError:
                pass
            else:
                raise AssertionError('bloqueio offline falhou')
        suite = unittest.defaultTestLoader.discover(str(BASE), pattern='test_*.py')
        with (output / 'testes.log').open('x') as stream:
            result = unittest.TextTestRunner(stream=stream, verbosity=2,
                                            resultclass=Resultado).run(suite)
        report = {'testes': result.testsRun, 'falhas': len(result.failures),
                  'erros': len(result.errors), 'pulados': len(result.skipped),
                  'sucesso': result.wasSuccessful(), 'segundos': time.monotonic() - inicio,
                  'somente_fakes': True, 'bloqueio_python_rede_e_subprocessos': True,
                  'sdk_temporal_importado': any(x.startswith('temporalio') for x in sys.modules),
                  'modulo_operacional_pqbr_importado': any(x == 'pqbr' or x.startswith('pqbr.') for x in sys.modules),
                  'casos': result.casos}
        (output / 'resultado.json').write_text(json.dumps(report, indent=2) + '\n')
        if result.wasSuccessful():
            for canal in ('paperclip', 'discord'):
                (output / ('demo-' + canal + '.json')).write_text(
                    json.dumps(demo(canal), indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'casos'}, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
