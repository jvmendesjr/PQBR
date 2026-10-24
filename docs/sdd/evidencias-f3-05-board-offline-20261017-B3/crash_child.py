"""Somente subprocesso do harness offline; caminhos fornecidos pelo teste."""
import os
from pathlib import Path
import signal
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

def guard(event, args):
    if event.startswith("socket.") or event in {"subprocess.Popen", "os.system", "os.posix_spawn"}:
        raise RuntimeError("OFFLINE_GUARD:" + event)
sys.addaudithook(guard)

from candidate import ReceiptStore, FakeTemporal, Denied, send_once
from fixtures import fixture, fake_cli, NOW


def main():
    action, store_path, target_path, rid = sys.argv[1:]
    m, _, _, _ = fixture()
    store = ReceiptStore(store_path)
    cli = fake_cli()
    snap = cli.snapshot(m)
    def kill(stage):
        if (action, stage) in {("consume-kill-cas", "after_cas"),
                               ("consume-kill-commit", "before_commit"),
                               ("send-kill-before", "before_send"),
                               ("send-kill-after", "after_ack")}:
            os.kill(os.getpid(), signal.SIGKILL)
    if action == "issue":
        print(store.issue(snap, m, NOW), flush=True)
    elif action.startswith("consume"):
        store.consume(rid, snap, m, NOW, fault=kill)
    elif action.startswith("send"):
        target = FakeTemporal(target_path, m)
        print(send_once(store, rid, cli, m, NOW, target, opt_in=True,
                        lose_ack=(action == "send-lose-ack"), fault=kill), flush=True)
    else:
        raise ValueError("UNKNOWN_ACTION")


if __name__ == "__main__":
    try:
        main()
    except Denied as e:
        print(str(e), flush=True)
        sys.exit(10)
    except TimeoutError:
        sys.exit(21)
