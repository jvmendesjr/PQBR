"""Consolida somente evidências H3 e insere uma nota em F3-05, sem fechar gates."""
from pathlib import Path
import hashlib
import json
import re
ROOT=Path('/home/pc/Workspace/PQBR')
E=Path(__file__).resolve().parent
R=E/'runtime-A1'
log=(R/'candidate-test.log').read_text()
assert re.search(r'Ran 18 tests in [0-9.]+s\n\nOK\s*$',log), 'suíte runtime sem OK'
assert (R/'candidate-exit-code.txt').read_text().strip()=='0'
clean=json.loads((R/'final-verification.json').read_text())
assert clean['teste_exit_code']==0
assert not clean['processos_restantes_no_namespace_de_teste']
assert not clean['pids_de_containers_descartaveis_restantes']
assert all(not x['novos'] and not x['ausentes'] for x in clean['inventario'].values())
assert all(x['removed'] for x in clean['cleanup'])
assert json.loads((R/'protected-verification.json').read_text())['inalterados']
assert json.loads((R/'isolation-gate.json').read_text())['passed']
assert json.loads((R/'runtime/system-info.json').read_text())['serverVersion']=='1.32.1'
summaries=[json.loads(p.read_text()) for p in (R/'runtime').glob('*.summary.json')]
assert summaries and all(s['replay']=='ok' for s in summaries)
results=sorted((R/'runtime').glob('*.e2e.json'))
assert len(results)==18
h2=json.loads((E/'regressao-H2/resultado.json').read_text())
assert h2['testes']==104 and h2['sucesso'] and not any(h2[k] for k in ('falhas','erros','pulados'))
summary=dict(runtime_testes=18,runtime_falhas=0,runtime_erros=0,runtime_pulados=0,
             regressao_h2_testes=104,regressao_h2_sucesso=True,temporal_server='1.32.1',
             capturas_reproduzidas=len(summaries),runs_distintos=len({(s['workflow_id'],s['run_id']) for s in summaries}),
             isolamento_aprovado=True,gate_ausente_recusado='gate-negativo.log',limpeza_integral=True,
             cenarios=[p.name for p in results],G4='ABERTO',producao='NAO ATIVADA',
             autenticacao_real='NAO VALIDADA; identidades e decisões somente fakes',
             durabilidade='Histórico e replay Temporal no ciclo descartável; Paperclip/Discord somente memória',
             proximo_gate='Revisão e aceite explícito de José para uma etapa controlada de integração real do receptor/ponte, sem ativação: provar autoria humana canônica pela identidade já vinculada, persistência/releitura reais e recuperação idempotente do consumo/resume sob falha. Esta etapa exige nova autorização e plano; G4 permanece aberto até TS-11 e aceite operacional completos.')
(E/'resultado.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
N=summary['capturas_reproduzidas'];U=summary['runs_distintos']
note=f'''  - Composição E2E isolada H3, 2026-10-17: **18/18 testes runtime e regressão H2 104/104**, com **{N} capturas de {U} runs reproduzidas no replay**, conectando o adaptador canônico H2 inalterado a um novo supervisor por sessão somente na pasta de evidências. Temporal Server **1.32.1** descartável, rede `internal`/`isolated` sem egress/rota padrão/IPv6/porta publicada, `--pull=never`, gate obrigatório aprovado antes de banco/servidor e gate ausente recusado; limpeza integral comprovada. Duas operações já aceitas: primeira falha terminal, registro técnico falso e pausa; comando legado/decisão apenas enfileirada não libera; aprovação fake em interação única do ticket existente (`request_confirmation`, `human_only`, `continuationPolicy=none`) gravada e relida pelo adaptador e novamente pelo receptor antes do consumo em histórico Temporal; somente a segunda pendente executa uma vez. Painel/Discord fake convergem; negativa, identidade não autorizada, ticket/revisão/escopo stale, receipt incerto/forjado/ambíguo/expirado, falhas de persistência/registro, duplicata/replay/ACK perdido não repetem a terminal nem ampliam fila. [Código, resultados e limites](sdd/evidencias-f3-05-composicao-e2e-20261017-H3/README.md) · [resultado](sdd/evidencias-f3-05-composicao-e2e-20261017-H3/resultado.json). **Limites:** identidades, Paperclip/Discord e persistência canônica são fakes em memória; não prova autenticação real, durabilidade após crash desses fakes, transação distribuída, fencing ou exactly-once externo. Próximo gate: revisão/aceite explícito de José para etapa controlada de integração real do receptor/ponte, ainda sem ativação, com autoria humana canônica, persistência/releitura reais e recuperação idempotente comprovadas; **não é redefinir a identidade/integração já aprovadas**. G4 depende também do TS-11 e aceite operacional completos. 1.264 arquivos preexistentes protegidos e quatro Workers/units/PIDs/inícios/restarts preservados; candidata, supervisores anteriores e política de exceção intactos. **F3-05/G4 aberto; produção não ativada; F7-02/G7 e PQBR-114 pausados; F05-06 no-arm.** Sem ticket/aviso/HTTP real, credencial real, restart/deploy/commit/push ou documentos restritos.
'''
assert not (E/'nota-roadmap.txt').exists()
(E/'nota-roadmap.txt').write_text(note)
road=ROOT/'docs/ROADMAP.md';old=road.read_text()
assert old==(E/'roadmap-antes.txt').read_text(),'roadmap mudou durante execução; não sobrescrever'
marker='  - [ ] **Revisão futura da política de exceção técnica na intervenção'
assert old.count(marker)==1
road.write_text(old.replace(marker,note+marker,1))
print(json.dumps(summary,ensure_ascii=False,indent=2))
