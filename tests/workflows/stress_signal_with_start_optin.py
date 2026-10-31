"""Experimento opt-in F3-05: nenhum import operacional, somente Activities falsas.
Executar exclusivamente pelo runner de isolamento acompanhante. Não é teste de produção.
"""
import argparse
import asyncio
import base64
from collections import Counter
from contextlib import AsyncExitStack
from datetime import timedelta
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import time
import traceback
import uuid

import temporalio
from temporalio import activity
from temporalio.api.common.v1 import WorkflowType
from temporalio.api.taskqueue.v1 import TaskQueue
from temporalio.api.workflowservice.v1 import SignalWithStartWorkflowExecutionRequest
from temporalio.client import Client
from temporalio.common import WorkflowIDConflictPolicy, WorkflowIDReusePolicy
from temporalio.runtime import Runtime, TelemetryConfig
from temporalio.service import RPCError, RetryConfig
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from tests.workflows.prototipo_signal_with_start import (
    AtorSignalSintetico as Ator, ator_id, configuracao, enviar_signal_with_start,
)

SERVER = '/tmp/temporal-test-server-sdk-python-1.34.0'


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def exception_data(exc):
    chain = []
    seen = set()
    current = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        item = dict(type=f'{type(current).__module__}.{type(current).__name__}',
                    message=str(current), repr=repr(current))
        if isinstance(current, RPCError):
            item.update(code=int(current.status), status=current.status.name,
                        raw_grpc_status_base64=base64.b64encode(current.raw_grpc_status).decode(),
                        grpc_details=[dict(type_url=x.type_url,
                            value_base64=base64.b64encode(x.value).decode()) for x in current.grpc_status.details])
        for attr in ('workflow_id', 'run_id', 'first_run_id'):
            if hasattr(current, attr):
                item[attr] = getattr(current, attr)
        chain.append(item)
        current = current.__cause__ or current.__context__
    return dict(chain=chain, traceback=''.join(traceback.format_exception(exc)))


class Fake:
    def __init__(self):
        self.gate = asyncio.Event()
        self.calls = []
        self.active = Counter()
        self.maximum = Counter()

    @activity.defn(name='efeito_signal_sintetico_v1')
    async def effect(self, pedido: dict) -> dict:
        session = pedido['sessao']
        self.active[session] += 1
        self.maximum[session] = max(self.maximum[session], self.active[session])
        item = dict(pedido=pedido, attempt=activity.info().attempt,
                    start=time.monotonic(), end=None)
        self.calls.append(item)
        try:
            await self.gate.wait()
            return {'sintetico': True}
        finally:
            item['end'] = time.monotonic()
            self.active[session] -= 1


async def run(args):
    assert os.environ.get('PQBR_TEMPORAL_ISOLADO') == '1', 'exige runner opt-in'
    assert os.readlink('/proc/self/ns/net') != os.environ['PQBR_HOST_NETNS']
    assert [name for _, name in socket.if_nameindex()] == ['lo']
    assert len(Path('/proc/net/route').read_text().splitlines()) == 1
    out = Path(os.environ['PQBR_TEMPORAL_EVIDENCIAS'])
    assert out.is_dir()
    dump(out / 'environment.json', dict(sdk=temporalio.__version__, python=sys.version,
        server=SERVER, server_sha256=hashlib.sha256(Path(SERVER).read_bytes()).hexdigest(),
        netns=os.readlink('/proc/self/ns/net'), pidns=os.readlink('/proc/self/ns/pid'),
        interfaces=socket.if_nameindex(), routes=Path('/proc/net/route').read_text(),
        args=vars(args), transport_retry=False, application_retry=False,
        workflow_retry_maximum_attempts=1, activity_retry_maximum_attempts=1))
    rpc_log = (out / 'rpc.jsonl').open('x', buffering=1)
    rounds_log = (out / 'rounds.jsonl').open('x', buffering=1)
    errors_log = (out / 'errors.jsonl').open('x', buffering=1)
    errors = 0
    invariant_errors = 0
    harness_errors = 0
    rounds = []
    clients = []
    runtimes = []
    fake = Fake()
    pending = set()
    env = None
    shutdown_ok = False
    try:
        env = await WorkflowEnvironment.start_time_skipping(
            test_server_existing_path=SERVER, retry_config=RetryConfig(max_retries=0))
        endpoint = env.client.service_client.config.target_host
        assert endpoint.split(':')[0] in ('127.0.0.1', 'localhost', '[::1]'), endpoint
        dump(out / 'endpoint.json', dict(endpoint=endpoint))
        max_c = max(args.concurrency)
        for slot in range(max_c):
            runtime = Runtime(telemetry=TelemetryConfig())
            runtimes.append(runtime)
            client = await Client.connect(endpoint, runtime=runtime,
                identity=f'isolado-stress-client-{slot:03d}', retry_config=RetryConfig(max_retries=0))
            original = client.workflow_service.signal_with_start_workflow_execution
            async def observe(req, *, retry=False, metadata={}, timeout=None,
                              original=original, slot=slot):
                row = dict(slot=slot, workflow_id=req.workflow_id, request_id=req.request_id,
                    identity=req.identity, reuse=req.workflow_id_reuse_policy,
                    conflict=req.workflow_id_conflict_policy, retry_requested=retry,
                    retry_effective=False, start=time.monotonic(),
                    request_base64=base64.b64encode(req.SerializeToString()).decode())
                try:
                    response = await original(req, retry=False, metadata=metadata, timeout=timeout)
                    row.update(ok=True, run_id=response.run_id, started=response.started)
                    return response
                except Exception as exc:
                    row.update(ok=False, error=exception_data(exc))
                    raise
                finally:
                    row['end'] = time.monotonic()
                    rpc_log.write(json.dumps(row, ensure_ascii=False) + '\n')
            client.workflow_service.signal_with_start_workflow_execution = observe
            clients.append(client)
        dump(out / 'clients.json', dict(count=len(clients), independent_runtimes=len(runtimes),
            independent_service_clients=len({id(c.service_client) for c in clients}),
            identities=[c.identity for c in clients]))
        async with AsyncExitStack() as stack:
            wq = 'teste-sws-wf-stress-optin-v1'
            aq = 'teste-sws-act-stress-optin-v1'
            await stack.enter_async_context(Worker(clients[0], task_queue=wq, workflows=[Ator],
                max_cached_workflows=0, graceful_shutdown_timeout=timedelta(seconds=2)))
            await stack.enter_async_context(Worker(clients[1 if len(clients) > 1 else 0],
                task_queue=wq, workflows=[Ator], max_cached_workflows=0,
                graceful_shutdown_timeout=timedelta(seconds=2)))
            await stack.enter_async_context(Worker(clients[0], task_queue=aq,
                activities=[fake.effect], max_concurrent_activities=32,
                graceful_shutdown_timeout=timedelta(seconds=2)))
            try:
                for mode in args.modes:
                    for condition in ('cold', 'warm'):
                        for concurrency in args.concurrency:
                            block_errors = 0
                            for iteration in range(args.iterations):
                                # Mesmos IDs determinísticos em todas as repetições completas do script.
                                session = f'stress-v1-{mode}-{condition}-c{concurrency:02d}-i{iteration:04d}'
                                wf_id = ator_id(session)
                                queue = wq if mode == 'prototype-workers' else wq + '-sem-worker'
                                config = configuracao(session, queue, aq, prazo_s=30)
                                handle = clients[0].get_workflow_handle(wf_id)
                                pending.add(wf_id)
                                fake.gate.clear()
                                barrier = asyncio.Event()

                                async def invoke(index, wait=True):
                                    client = clients[index % len(clients)]
                                    pedido = dict(id=f'p{index:04d}', sessao=session, falhar=False)
                                    if wait:
                                        await barrier.wait()
                                    if mode.startswith('prototype'):
                                        return await enviar_signal_with_start(client, session, queue, aq,
                                            pedido, prazo_s=30)
                                    req = SignalWithStartWorkflowExecutionRequest(
                                        namespace=client.namespace, workflow_id=wf_id,
                                        workflow_type=WorkflowType(name='AtorSignalSintetico'),
                                        task_queue=TaskQueue(name=queue), identity=client.identity,
                                        request_id=str(uuid.uuid4()),
                                        workflow_id_reuse_policy=int(WorkflowIDReusePolicy.REJECT_DUPLICATE),
                                        workflow_id_conflict_policy=int(WorkflowIDConflictPolicy.USE_EXISTING),
                                        signal_name='solicitar')
                                    req.input.payloads.extend(await client.data_converter.encode([dict(config=config)]))
                                    req.signal_input.payloads.extend(await client.data_converter.encode([
                                        dict(config=config, pedido=pedido)]))
                                    req.workflow_execution_timeout.FromTimedelta(timedelta(minutes=2))
                                    req.retry_policy.maximum_attempts = 1
                                    return await client.workflow_service.signal_with_start_workflow_execution(
                                        req, retry=False, timeout=timedelta(seconds=10))

                                seed_error = None
                                if condition == 'warm':
                                    try:
                                        await invoke(-1, wait=False)
                                    except Exception as exc:
                                        seed_error = exception_data(exc)
                                        harness_errors += 1
                                        errors_log.write(json.dumps(dict(session=session, phase='warm-seed',
                                            error=seed_error), ensure_ascii=False) + '\n')
                                tasks = [asyncio.create_task(invoke(i)) for i in range(concurrency)]
                                await asyncio.sleep(0)
                                barrier.set()
                                results = await asyncio.gather(*tasks, return_exceptions=True)
                                failures = []
                                success = []
                                for i, result in enumerate(results):
                                    if isinstance(result, BaseException):
                                        item = dict(session=session, mode=mode, condition=condition,
                                            concurrency=concurrency, iteration=iteration, index=i,
                                            error=exception_data(result))
                                        failures.append(item)
                                        errors_log.write(json.dumps(item, ensure_ascii=False) + '\n')
                                    else:
                                        success.append(f'p{i:04d}')
                                errors += len(failures)
                                block_errors += len(failures)
                                row = dict(session=session, workflow_id=wf_id, mode=mode, condition=condition,
                                    concurrency=concurrency, iteration=iteration, success=len(success),
                                    failed=len(failures), seed_error=seed_error)
                                expected = success + (['p-001'] if condition == 'warm' and seed_error is None else [])
                                try:
                                    hist = await handle.fetch_history()
                                    starts = [e for e in hist.events if e.HasField('workflow_execution_started_event_attributes')]
                                    signals = [e for e in hist.events if e.HasField('workflow_execution_signaled_event_attributes')]
                                    payloads = [client.data_converter for client in clients[:1]][0]
                                    received = [p['pedido']['id'] for event in signals
                                        for p in await payloads.decode(event.workflow_execution_signaled_event_attributes.input.payloads)]
                                    row.update(run_id=(await handle.describe()).run_id, starts=len(starts),
                                        signal_count=len(signals), signal_ids=received)
                                    assert len(starts) == 1, row
                                    if mode == 'prototype-workers':
                                        # Signals podem estar buffered durante Workflow Task aberta.
                                        # Polling de observação, não retry/reenvio de Signal-With-Start.
                                        deadline = time.monotonic() + 12
                                        observations = []
                                        while True:
                                            state = await handle.query(Ator.estado,
                                                rpc_timeout=timedelta(seconds=3))
                                            observations.append(dict(at=time.monotonic(),
                                                accepted=state['aceitos']))
                                            if Counter(state['aceitos']) == Counter(expected):
                                                break
                                            if time.monotonic() >= deadline:
                                                raise AssertionError(('aceitos nao observados', state, expected))
                                            await asyncio.sleep(0.01)
                                        row['observation_polls'] = observations
                                        # Signal de fechamento é enviado após todas as RPCs, sem retry de pedidos.
                                        await handle.signal(Ator.fechar)
                                        fake.gate.set()
                                        result = await asyncio.wait_for(handle.result(), 30)
                                        calls = [x for x in fake.calls if x['pedido']['sessao'] == session]
                                        row.update(completed=result['concluidos'], accepted=result['aceitos'],
                                            fake_calls=len(calls), max_session=fake.maximum[session],
                                            attempts=[x['attempt'] for x in calls])
                                        assert Counter(result['concluidos']) == Counter(expected), row
                                        assert len(calls) == len(expected), row
                                        assert fake.maximum[session] == 1, row
                                        assert all(x['attempt'] == 1 for x in calls), row
                                        assert all(a['end'] <= b['start'] for a, b in zip(calls, calls[1:])), row
                                        hist = await handle.fetch_history()
                                        signals = [e for e in hist.events
                                            if e.HasField('workflow_execution_signaled_event_attributes')
                                            and e.workflow_execution_signaled_event_attributes.signal_name == 'solicitar']
                                        received = [p['pedido']['id'] for event in signals
                                            for p in await payloads.decode(event.workflow_execution_signaled_event_attributes.input.payloads)]
                                        row.update(final_signal_count=len(signals), final_signal_ids=received)
                                        assert Counter(received) == Counter(expected), (received, expected)
                                    else:
                                        assert Counter(received) == Counter(expected), (received, expected)
                                        assert not any(e.HasField('activity_task_scheduled_event_attributes') for e in hist.events)
                                        await handle.terminate('cleanup experimento sem worker')
                                    desc = await handle.describe()
                                    assert desc.status.name != 'RUNNING', desc.status
                                    assert not desc.raw_description.pending_activities
                                    row['final_status'] = desc.status.name
                                    if failures or iteration == 0:
                                        final_hist = await handle.fetch_history()
                                        (out / (session + '.history.json')).write_text(final_hist.to_json() + '\n')
                                    pending.discard(wf_id)
                                    row['invariants_ok'] = True
                                except Exception as exc:
                                    invariant_errors += 1
                                    row.update(invariants_ok=False, invariant_error=exception_data(exc))
                                    errors_log.write(json.dumps(dict(session=session, phase='invariant',
                                        error=exception_data(exc)), ensure_ascii=False) + '\n')
                                    fake.gate.set()
                                    # Somente cleanup, nunca reenvio de solicitação falhada.
                                    if (await handle.describe()).status.name == 'RUNNING':
                                        await handle.terminate('cleanup apos falha experimental')
                                    pending.discard(wf_id)
                                rounds.append(row)
                                rounds_log.write(json.dumps(row, ensure_ascii=False) + '\n')
                            print(json.dumps(dict(progress=mode, condition=condition, concurrency=concurrency,
                                iterations=args.iterations, rpc_errors=block_errors,
                                total_rpc_errors=errors, invariant_errors=invariant_errors)), flush=True)
            finally:
                fake.gate.set()
                for wf_id in list(pending):
                    try:
                        h = clients[0].get_workflow_handle(wf_id)
                        if (await h.describe()).status.name == 'RUNNING':
                            await h.terminate('cleanup final stress')
                        pending.discard(wf_id)
                    except Exception as exc:
                        errors_log.write(json.dumps(dict(phase='cleanup', workflow_id=wf_id,
                            error=exception_data(exc)), ensure_ascii=False) + '\n')
                        harness_errors += 1
        dump(out / 'fake-calls.json', fake.calls)
    except Exception as exc:
        harness_errors += 1
        errors_log.write(json.dumps(dict(phase='harness', error=exception_data(exc)), ensure_ascii=False) + '\n')
        traceback.print_exc()
    finally:
        if env is not None:
            try:
                await env.shutdown()
                shutdown_ok = True
            except Exception as exc:
                harness_errors += 1
                errors_log.write(json.dumps(dict(phase='shutdown', error=exception_data(exc)), ensure_ascii=False) + '\n')
        summary = dict(rounds=len(rounds), burst_calls=sum(x['concurrency'] for x in rounds),
            burst_rpc_errors=errors, invariant_errors=invariant_errors, harness_errors=harness_errors,
            failed_rounds=sum(x['failed'] > 0 for x in rounds), pending_cleanup=list(pending),
            shutdown_ok=shutdown_ok, robustez_comprovada=False,
            by_block=[dict(mode=m, condition=cond, concurrency=c,
                rounds=sum(x['mode']==m and x['condition']==cond and x['concurrency']==c for x in rounds),
                failed=sum(x['failed'] for x in rounds if x['mode']==m and x['condition']==cond and x['concurrency']==c))
                for m in args.modes for cond in ('cold','warm') for c in args.concurrency])
        dump(out / 'summary.json', summary)
        rpc_log.close()
        rounds_log.close()
        errors_log.close()
        print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 1 if errors or invariant_errors or harness_errors or not shutdown_ok else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iterations', type=int, default=20)
    parser.add_argument('--concurrency', type=int, nargs='+', default=[1,2,4,12,32])
    parser.add_argument('--modes', nargs='+', choices=['prototype-workers','prototype-no-worker','raw-no-worker'],
        default=['prototype-workers','prototype-no-worker','raw-no-worker'])
    args = parser.parse_args()
    if not 1 <= args.iterations <= 100 or any(not 1 <= c <= 64 for c in args.concurrency):
        parser.error('limites experimentais: 1..100 iteracoes; concorrencias 1..64')
    sys.exit(asyncio.run(run(args)))
