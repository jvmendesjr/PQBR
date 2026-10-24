"""Executar explicitamente: python3 -I -B run_offline.py --run-offline --output <nova-pasta>."""
import argparse
from pathlib import Path
import json
import sys
import unittest

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
ALLOWED_CHILD = str(BASE / "crash_child.py")
EVENTS = []


def guard(event, args):
    if event.startswith("socket.") or event in {"os.system", "os.posix_spawnp"}:
        EVENTS.append(dict(event=event, disposition="blocked"))
        raise RuntimeError("OFFLINE_GUARD:" + event)
    if event in {"subprocess.Popen", "os.posix_spawn"}:
        command = args[1]
        if not (type(command) is list and len(command) == 8 and
                command[:4] == [sys.executable, "-I", "-B", ALLOWED_CHILD] and
                command[4] in {"issue", "consume", "consume-kill-cas", "consume-kill-commit",
                               "send", "send-kill-before", "send-kill-after", "send-lose-ack"}):
            raise RuntimeError("OFFLINE_GUARD:only_crash_child")
        EVENTS.append(dict(event=event, disposition="allowed_python_harness", action=command[4]))


class Result(unittest.TextTestResult):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.subtests = 0
        self.subtest_failures = 0

    def addSubTest(self, test, subtest, err):
        self.subtests += 1
        if err is not None:
            self.subtest_failures += 1
        super().addSubTest(test, subtest, err)


def main():
    parser = argparse.ArgumentParser(description="Harness B3 somente offline; nunca chama CLI/API real.")
    parser.add_argument("--run-offline", action="store_true", required=True)
    parser.add_argument("--output", type=Path, required=True)
    opts = parser.parse_args()
    if opts.output.exists():
        parser.error("A pasta de saída deve ser nova, para não sobrescrever evidência")
    opts.output.mkdir(parents=True)
    sys.addaudithook(guard)
    try:
        sys.audit("socket.connect", None, ("synthetic.invalid", 443))
    except RuntimeError as e:
        if str(e) != "OFFLINE_GUARD:socket.connect":
            raise
    else:
        raise RuntimeError("AUDIT_HOOK_NOT_INSTALLED")
    import test_candidate
    from fixtures import fixture, NOW
    from candidate import canonical
    m,t,r,c=fixture()
    # Não são snapshots reais, tokens, nem autorização reutilizável em produção.
    for name,value in {"synthetic-ticket.json":t,"synthetic-interactions.json":[r],
                       "synthetic-manifest.json":m.__dict__,"synthetic-board-context.json":c.__dict__,
                       "synthetic-wire-payload.json":m.wire()}.items():
        (opts.output/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n")
    with (opts.output/"tests.log").open("w") as stream:
        runner=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result)
        result=runner.run(unittest.defaultTestLoader.loadTestsFromModule(test_candidate))
    report=dict(status="PASSED" if result.wasSuccessful() else "FAILED",
                offline_only=True, tests_run=result.testsRun, subtests=result.subtests,
                failures=len(result.failures), errors=len(result.errors),
                subtest_failures=result.subtest_failures,
                negative_cases_with_zero_effects=len(test_candidate.NEGATIVE_CASES),
                negative_cases=test_candidate.NEGATIVE_CASES,
                child_results=test_candidate.CHILD_RESULTS,
                subprocesses=sum(e["event"]=="subprocess.Popen" for e in EVENTS),
                sigkill_injection_processes=sum(e["event"] == "subprocess.Popen" and
                                               "kill" in e.get("action", "") for e in EVENTS),
                events=EVENTS, actual_paperclip_calls=0, actual_discord_calls=0,
                actual_temporal_server_starts=0, actual_external_effects=0,
                runtime="Python stdlib; fake Temporal backed by disposable SQLite",
                guarantees="CAS local + outbox atomic + at-least-once fake delivery with durable fake dedupe; NOT real exactly-once",
                gates=dict(F3_05_G4="OPEN",F05_06="NO_ARM",F7_02_G7="PAUSED",PQBR_114="PAUSED"))
    (opts.output/"result.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in {"events","negative_cases","child_results"}},ensure_ascii=False,indent=2))
    if not result.wasSuccessful():
        print((opts.output/"tests.log").read_text())
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
