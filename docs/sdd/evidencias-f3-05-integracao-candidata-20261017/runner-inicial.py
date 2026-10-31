"""Executa apenas o teste candidato em infraestrutura Docker descartavel e isolada."""
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback

ROOT = Path('/home/pc/Workspace/PQBR')
OUT = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else None
NAMESPACE = 'f3-05-candidate'
IMAGES = ('temporalio/server:1.32.1', 'postgres:17-alpine', 'temporalio/admin-tools:1.32.1')
created = []
network_id = None
network_name = None
container_pids = []
netns_ids = []
child = None
output_created = False
exit_code = 2


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def run(args, check=True, timeout=60):
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout)
    with (OUT / 'commands.jsonl').open('a') as f:
        f.write(json.dumps({'args': args, 'returncode': result.returncode,
                            'stdout': result.stdout, 'stderr': result.stderr},
                           ensure_ascii=False) + '\n')
    if check and result.returncode:
        raise RuntimeError(f'Falha {result.returncode}: {args}: {result.stderr} {result.stdout}')
    return result


def docker(*args, **kwargs):
    return run(['docker', *args], **kwargs)


def inspect(cid):
    return json.loads(docker('inspect', cid).stdout)[0]


def create(name, image, ip=None, extra=(), command=()):
    args = ['create', '--pull=never', '--name', PREFIX + '-' + name,
            '--label', LABEL, '--network', network_id, '--dns', '127.0.0.1',
            '--sysctl', 'net.ipv6.conf.all.disable_ipv6=1',
            '--sysctl', 'net.ipv6.conf.default.disable_ipv6=1',
            '--security-opt', 'no-new-privileges:true', '--restart', 'no',
            '--pids-limit', '512', '--memory', '2g', '--cpus', '2',
            '--cap-drop', 'ALL']
    if ip:
        args += ['--ip', ip]
    args += list(extra) + [image] + list(command)
    cid = docker(*args).stdout.strip()
    created.append(cid)
    save('created-resources.json', {'containers': created, 'network': network_id})
    return cid


def netcmd(pid, *args, check=True):
    return run(['sudo', '-n', 'nsenter', '-t', str(pid), '-n', *args], check=check)


def verify_network(cid, label, subnet, bridge):
    data = inspect(cid)
    assert data['State']['Running'], 'contêiner não está em execução'
    assert set(data['NetworkSettings']['Networks']) == {PREFIX + '-net'}
    assert not data['HostConfig']['Privileged']
    assert not data['HostConfig'].get('PortBindings')
    assert not data['HostConfig'].get('PublishAllPorts')
    assert data['HostConfig'].get('CapDrop') == ['ALL']
    pid = data['State']['Pid']
    container_pids.append(pid)
    netns = run(['sudo', '-n', '/usr/bin/readlink', f'/proc/{pid}/ns/net']).stdout.strip()
    netns_ids.append(netns)
    routes4 = json.loads(netcmd(pid, '/usr/bin/ip', '-j', '-4', 'route').stdout)
    routes6 = json.loads(netcmd(pid, '/usr/bin/ip', '-j', '-6', 'route').stdout)
    addresses = json.loads(netcmd(pid, '/usr/bin/ip', '-j', 'address').stdout)
    host_bridge = json.loads(run(['/usr/bin/ip', '-j', 'address', 'show', 'dev', bridge]).stdout)
    assert not any(x.get('addr_info') for x in host_bridge), host_bridge
    assert not any(r.get('dst') == 'default' for r in routes4 + routes6), (routes4, routes6)
    for interface in addresses:
        for address in interface.get('addr_info', []):
            value = ipaddress.ip_address(address['local'])
            if interface['ifname'] != 'lo':
                assert value.version == 4 and value in subnet, address
    # Consulta somente a tabela de rotas: não envia tráfego aos endereços de teste.
    neg4 = netcmd(pid, '/usr/bin/ip', '-4', 'route', 'get', '198.51.100.1', check=False)
    neg6 = netcmd(pid, '/usr/bin/ip', '-6', 'route', 'get', '2001:db8::1', check=False)
    assert neg4.returncode != 0 and 'unreachable' in neg4.stderr.lower(), neg4
    assert neg6.returncode != 0 and 'unreachable' in neg6.stderr.lower(), neg6
    save('network-' + label + '.json', {
        'pid': pid, 'netns': netns, 'inspect': data, 'routes_ipv4': routes4,
        'routes_ipv6': routes6, 'addresses': addresses, 'host_bridge': host_bridge,
        'route_get_ipv4': neg4.stderr, 'route_get_ipv6': neg6.stderr,
        'sem_rota_padrao': True, 'bridge_host_sem_endereco': True,
        'ipv6_desativado': True,
    })
    return pid, netns


def interrupted(signum, frame):
    raise KeyboardInterrupt(f'sinal {signum}')


def snapshot_resources():
    data = {}
    for kind, args in {
        'containers': ['ps', '-aq', '--no-trunc'],
        'networks': ['network', 'ls', '-q', '--no-trunc'],
        'volumes': ['volume', 'ls', '-q'],
    }.items():
        data[kind] = sorted(docker(*args).stdout.splitlines())
    return data


if OUT is None:
    print('Uso: run_candidate_container.py <diretorio-novo-de-evidencias>', file=sys.stderr)
    sys.exit(2)

try:
    OUT.mkdir(mode=0o700)
    output_created = True
    TOKEN = OUT.name.rsplit('-', 1)[-1]
    assert TOKEN and TOKEN.isalnum(), 'o nome do diretório precisa terminar em token alfanumérico'
    EXPERIMENT_ID = 'f305-candidate-' + TOKEN
    BRIDGE = 'pqbrfc' + TOKEN.lower()
    PREFIX = 'pqbr-f305-' + TOKEN
    LABEL = 'pqbr.candidate.run=' + EXPERIMENT_ID
    PYTHON = str(ROOT / '.venv/bin/python')
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)

    save('run-metadata.json', {'root': str(ROOT), 'namespace': NAMESPACE,
                               'labels': {LABEL.split('=')[0]: EXPERIMENT_ID},
                               'images': IMAGES, 'test_timeout_seconds': 300})
    before = snapshot_resources()
    save('resources-before.json', before)
    # Usar somente imagens locais; qualquer imagem ausente encerra o gate sem pull.
    for image in IMAGES:
        docker('image', 'inspect', image)
    # Rede dedicada internal + gateway isolado; sem IPv6 e sem publicação de portas.
    network_id = docker('network', 'create', '--driver', 'bridge', '--internal',
                        '--ipv6=false', '--label', LABEL,
                        '--opt', 'com.docker.network.bridge.gateway_mode_ipv4=isolated',
                        '--opt', 'com.docker.network.bridge.gateway_mode_ipv6=isolated',
                        '--opt', 'com.docker.network.bridge.name=' + BRIDGE,
                        PREFIX + '-net').stdout.strip()
    network_name = PREFIX + '-net'
    save('created-resources.json', {'containers': [], 'network': network_id})
    net = json.loads(docker('network', 'inspect', network_id).stdout)[0]
    save('network-initial.json', net)
    assert net['Internal'] is True and net['Driver'] == 'bridge' and net['EnableIPv6'] is False
    assert net['Options']['com.docker.network.bridge.gateway_mode_ipv4'] == 'isolated'
    subnet = ipaddress.ip_network(net['IPAM']['Config'][0]['Subnet'])
    assert subnet.version == 4
    dbip, serverip, adminip = [str(subnet.network_address + i) for i in (2, 3, 4)]
    # Sysctl aplicado somente à bridge dedicada; nunca altera valores globais.
    run(['sudo', '-n', '/usr/sbin/sysctl', '-w', f'net.ipv6.conf.{BRIDGE}.disable_ipv6=1'])
    admin = create('admin', 'temporalio/admin-tools:1.32.1', ip=adminip,
                   extra=['--read-only', '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m',
                          '--entrypoint', '/bin/sh'],
                   command=['-c', 'trap exit TERM INT; sleep 3600 & wait'])
    docker('start', admin)
    verify_network(admin, 'gate', subnet, BRIDGE)
    save('isolation-gate.json', {'passed': True,
         'message': 'Internal/isolated IPv4-only, sem IPv6, sem rota padrao/external, bridge host sem IP'})
    print('GATE DE ISOLAMENTO APROVADO; iniciando somente recursos descartáveis.', flush=True)

    # Nenhum banco ou servidor candidato é iniciado antes da aprovação do gate.
    postgres = create('postgres', 'postgres:17-alpine', ip=dbip,
        extra=['--user', 'postgres', '--read-only',
               '--tmpfs', '/var/lib/postgresql/data:rw,nosuid,nodev,size=768m,uid=70,gid=70,mode=0700',
               '--tmpfs', '/var/run/postgresql:rw,nosuid,nodev,size=16m,uid=70,gid=70,mode=0775',
               '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m',
               '-e', 'POSTGRES_USER=temporal', '-e', 'POSTGRES_PASSWORD=candidate_fake_only',
               '-e', 'POSTGRES_DB=temporal'])
    docker('start', postgres)
    verify_network(postgres, 'postgres', subnet, BRIDGE)
    deadline = time.monotonic() + 60
    while True:
        ready = docker('exec', postgres, 'pg_isready', '-U', 'temporal', '-d', 'temporal', check=False)
        if ready.returncode == 0:
            break
        if time.monotonic() > deadline:
            raise TimeoutError('Postgres não ficou pronto em 60 segundos')
        time.sleep(1)
    docker('exec', postgres, 'psql', '-U', 'temporal', '-d', 'temporal', '-v', 'ON_ERROR_STOP=1',
           '-c', 'CREATE DATABASE temporal_visibility;')
    for database, schema in [('temporal', 'temporal'), ('temporal_visibility', 'visibility')]:
        base = ['exec', '-e', 'SQL_HOST=' + dbip, '-e', 'SQL_PORT=5432', '-e', 'SQL_USER=temporal',
                '-e', 'SQL_PASSWORD=candidate_fake_only', '-e', 'SQL_PLUGIN=postgres12',
                '-e', 'SQL_DATABASE=' + database, admin, 'temporal-sql-tool']
        docker(*(base + ['setup-schema', '--version', '0.0']))
        docker(*(base + ['update-schema', '--schema-dir',
                          f'/etc/temporal/schema/postgresql/v12/{schema}/versioned']))

    config = OUT / 'config'
    config.mkdir()
    (config / 'dynamic.yaml').write_text('{}\n')
    server_yaml = f'''log:
  stdout: true
  level: warn
persistence:
  defaultStore: default
  visibilityStore: visibility
  numHistoryShards: 4
  datastores:
    default:
      sql:
        pluginName: postgres12
        databaseName: temporal
        connectAddr: {dbip}:5432
        connectProtocol: tcp
        user: temporal
        password: candidate_fake_only
        maxConns: 20
        maxIdleConns: 20
        maxConnLifetime: 1h
    visibility:
      sql:
        pluginName: postgres12
        databaseName: temporal_visibility
        connectAddr: {dbip}:5432
        connectProtocol: tcp
        user: temporal
        password: candidate_fake_only
        maxConns: 10
        maxIdleConns: 10
        maxConnLifetime: 1h
global:
  membership:
    maxJoinDuration: 30s
    broadcastAddress: {serverip}
services:
  frontend:
    rpc:
      grpcPort: 7233
      membershipPort: 6933
      bindOnIP: 0.0.0.0
  history:
    rpc:
      grpcPort: 7234
      membershipPort: 6934
      bindOnIP: 0.0.0.0
  matching:
    rpc:
      grpcPort: 7235
      membershipPort: 6935
      bindOnIP: 0.0.0.0
  worker:
    rpc:
      grpcPort: 7239
      membershipPort: 6939
      bindOnIP: 0.0.0.0
clusterMetadata:
  enableGlobalNamespace: false
  failoverVersionIncrement: 10
  masterClusterName: active
  currentClusterName: active
  clusterInformation:
    active:
      enabled: true
      initialFailoverVersion: 1
      rpcAddress: {serverip}:7233
dcRedirectionPolicy:
  policy: noop
archival:
  history:
    state: disabled
  visibility:
    state: disabled
publicClient:
  hostPort: 127.0.0.1:7233
dynamicConfigClient:
  filepath: /etc/temporal/experiment/dynamic.yaml
  pollInterval: 10s
'''
    (config / 'server.yaml').write_text(server_yaml)
    server = create('server', 'temporalio/server:1.32.1', ip=serverip,
        extra=['--read-only', '--tmpfs', '/tmp:rw,nosuid,nodev,size=128m',
               '--mount', f'type=bind,src={config},dst=/etc/temporal/experiment,readonly',
               '--entrypoint', '/usr/local/bin/temporal-server'],
        command=['--config-file', '/etc/temporal/experiment/server.yaml', '--allow-no-auth', 'start'])
    docker('start', server)
    pid, netns = verify_network(server, 'server', subnet, BRIDGE)
    candidate_out = OUT / 'runtime'
    candidate_out.mkdir(mode=0o700)
    bootstrap_cmd = [
        'sudo', '-n', 'nsenter', '-t', str(pid), '-n',
        '/usr/bin/setpriv', '--reuid=1000', '--regid=1000', '--clear-groups',
        '/usr/bin/env', '-i',
        f'PYTHONPATH={ROOT / "src"}:{ROOT}',
        'PYTHONDONTWRITEBYTECODE=1',
        f'PQBR_CANDIDATE_OUT={candidate_out}',
        PYTHON, str(Path(__file__).with_name('f3_05_candidate_bootstrap.py')),
    ]
    with (OUT / 'candidate-bootstrap.log').open('w') as log:
        bootstrap = subprocess.run(bootstrap_cmd, stdout=log, stderr=subprocess.STDOUT,
                                   timeout=210, env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'})
    if bootstrap.returncode:
        raise RuntimeError(f'Bootstrap candidato terminou com código {bootstrap.returncode}')
    # Python do checkout executado apenas no namespace do servidor, com ambiente integralmente limpo.
    run_tests = [
        'sudo', '-n', 'nsenter', '-t', str(pid), '-n',
        '/usr/bin/setpriv', '--reuid=1000', '--regid=1000', '--clear-groups',
        '/usr/bin/env', '-i',
        f'PYTHONPATH={ROOT / "src"}:{ROOT}',
        'PYTHONDONTWRITEBYTECODE=1', 'PQBR_CANDIDATE_ISOLATED=1',
        f'PQBR_CANDIDATE_OUT={OUT / "runtime"}',
        PYTHON, '-m', 'unittest', '-v', 'tests.workflows.test_f3_05_candidate_runtime',
    ]
    with (OUT / 'candidate-test.log').open('w') as log:
        child = subprocess.Popen(run_tests, stdout=log, stderr=subprocess.STDOUT,
                                 start_new_session=True, env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'})
        save('candidate-process.json', {'pid': child.pid, 'args': run_tests,
                                       'expected_netns': netns})
        try:
            exit_code = child.wait(timeout=300)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=8)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait(timeout=8)
            raise TimeoutError('Teste candidato excedeu o limite de 300 segundos')
        (OUT / 'candidate-exit-code.txt').write_text(str(exit_code) + '\n')
    if exit_code:
        raise RuntimeError(f'Teste candidato terminou com código {exit_code}')
except BaseException as exc:
    if output_created:
        try:
            save('orchestrator-error.json', {'type': type(exc).__name__, 'message': str(exc),
                 'traceback': traceback.format_exc()})
        except Exception:
            pass
    traceback.print_exc()
    exit_code = 2
finally:
    if output_created:
        if child is not None and child.poll() is None:
            try:
                os.killpg(child.pid, signal.SIGTERM)
                child.wait(timeout=8)
            except Exception:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=8)
                except Exception:
                    exit_code = 2
        cleanup = []
        for cid in reversed(created):
            try:
                data = inspect(cid)
                assert data['Config'].get('Labels', {}).get('pqbr.candidate.run') == EXPERIMENT_ID
                save('inspect-final-' + data['Name'].lstrip('/') + '.json', data)
                logs = docker('logs', '--timestamps', cid, check=False)
                (OUT / ('logs-' + data['Name'].lstrip('/') + '.txt')).write_text(logs.stdout + logs.stderr)
                docker('stop', '--time', '8', cid, check=False, timeout=20)
                docker('rm', cid, timeout=30)
                cleanup.append({'container': cid, 'removed': True})
            except Exception as exc:
                cleanup.append({'container': cid, 'removed': False, 'error': str(exc)})
                exit_code = 2
        if network_id is not None:
            try:
                net = json.loads(docker('network', 'inspect', network_id).stdout)[0]
                assert net.get('Labels', {}).get('pqbr.candidate.run') == EXPERIMENT_ID
                assert not net.get('Containers')
                docker('network', 'rm', network_id)
                cleanup.append({'network': network_id, 'removed': True})
            except Exception as exc:
                cleanup.append({'network': network_id, 'removed': False, 'error': str(exc)})
                exit_code = 2
        leftovers = []
        for proc in Path('/proc').glob('[0-9]*'):
            try:
                ns = os.readlink(proc / 'ns/net')
                if ns in netns_ids:
                    leftovers.append({'pid': int(proc.name), 'netns': ns})
            except OSError:
                pass
        after = {}
        # Inspeção privilegiada restrita aos namespaces criados, inclusive UID postgres.
        scan = run(['sudo', '-n', '/usr/bin/python3', '-c',
                    'import os,pathlib,json,sys; ns=set(json.loads(sys.argv[1])); left=[]\n'
                    'for p in pathlib.Path("/proc").glob("[0-9]*"):\n'
                    ' try:\n'
                    '  n=os.readlink(p/"ns/net")\n'
                    '  if n in ns: left.append(dict(pid=int(p.name),netns=n))\n'
                    ' except OSError: pass\n'
                    'print(json.dumps(left))', json.dumps(netns_ids)])
        leftovers = json.loads(scan.stdout)
        try:
            for kind, args in {
                'containers': ['ps', '-aq', '--no-trunc'],
                'networks': ['network', 'ls', '-q', '--no-trunc'],
                'volumes': ['volume', 'ls', '-q'],
            }.items():
                after[kind] = sorted(docker(*args).stdout.splitlines())
        except Exception as exc:
            after['inventory_error'] = str(exc)
            exit_code = 2
        original = {}
        if (OUT / 'resources-before.json').exists():
            original = json.loads((OUT / 'resources-before.json').read_text())
        compare = {k: {'novos': sorted(set(after.get(k, [])) - set(original.get(k, []))),
                       'ausentes': sorted(set(original.get(k, [])) - set(after.get(k, [])))}
                   for k in ('containers', 'networks', 'volumes') if k in after}
        remaining_pids = [pid for pid in container_pids if Path(f'/proc/{pid}').exists()]
        save('final-verification.json', {'cleanup': cleanup,
             'processos_restantes_no_namespace_de_teste': leftovers,
             'pids_de_containers_descartaveis_restantes': remaining_pids,
             'inventario': compare, 'teste_exit_code': exit_code})
        if leftovers or remaining_pids or any(x['novos'] or x['ausentes'] for x in compare.values()):
            exit_code = 2
        print('Inventário e verificação final:', json.dumps(compare, ensure_ascii=False), flush=True)

sys.exit(exit_code)
