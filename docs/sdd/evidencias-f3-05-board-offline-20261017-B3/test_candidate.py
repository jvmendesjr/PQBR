import copy
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from candidate import (Denied, ReceiptStore, FakeTemporal, FakeGetCLI, BoardContext,
                       Snapshot, parse_snapshot, validate, send_once, strict_json,
                       canonical, connect, INTERACTION_FIELDS, TICKET_FIELDS, WIRE_FIELDS)
from fixtures import NOW, fixture, fake_cli

BASE = Path(__file__).resolve().parent
NEGATIVE_CASES = []
CHILD_RESULTS = []


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.m, self.t, self.r, self.c = fixture()
        self.store = ReceiptStore(self.root / "receipt.sqlite")
        self.target = FakeTemporal(self.root / "target.sqlite", self.m)
        self.cli = fake_cli()

    def snap(self, t=None, r=None, c=None):
        return parse_snapshot(canonical(self.t if t is None else t),
                              canonical([self.r if r is None else r]), self.c if c is None else c)

    def issue(self):
        return self.store.issue(self.snap(), self.m, NOW)

    def ready(self):
        rid = self.issue()
        self.store.consume(rid, self.snap(), self.m, NOW)
        return rid

    def zero(self):
        self.assertEqual(self.target.counts(), dict(fake_effects=0, first_attempts=1,
                                                   second_attempts=0, external_effects=0))

    def denied_case(self, name, fn):
        with self.subTest(case=name):
            with self.assertRaises(Denied):
                fn()
            self.zero()
            NEGATIVE_CASES.append(name)

    def child(self, action, rid="unused", check=False):
        p = subprocess.run([sys.executable, "-I", "-B", str(BASE / "crash_child.py"), action,
                            str(self.root / "receipt.sqlite"), str(self.root / "target.sqlite"), rid],
                           capture_output=True, text=True, timeout=15)
        CHILD_RESULTS.append(dict(action=action, returncode=p.returncode,
                                  stdout=p.stdout.strip(), stderr=p.stderr.strip()))
        if check:
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        return p

    def test_positive_whitelist_binding_and_read_only(self):
        s = self.cli.snapshot(self.m)
        b = validate(s, self.m, NOW)
        self.assertEqual(set(b), {"snapshot", "manifest", "wire"})
        self.assertEqual(len(b["snapshot"]), 64)
        self.assertEqual(self.cli.calls, [("GET", ("issue", "get", self.m.issue_id, "--json")),
                                         ("GET", ("issue", "interactions", self.m.issue_id, "--json"))])
        self.assertEqual(set(strict_json(s.ticket_json)), set(TICKET_FIELDS))
        self.assertEqual(set(strict_json(s.interaction_json)), set(INTERACTION_FIELDS))
        self.zero()

    def test_positive_send_only_minimal_authorized_ids(self):
        rid = self.ready()
        captured = []
        original = FakeTemporal.send
        def capture(target, payload, **kw):
            captured.append(copy.deepcopy(payload))
            return original(target, payload, **kw)
        with patch.object(FakeTemporal, "send", capture):
            self.assertEqual(send_once(self.store, rid, self.cli, self.m, NOW, self.target, opt_in=True), "applied")
        self.assertEqual(captured, [self.m.wire()])
        self.assertEqual(set(captured[0]), set(WIRE_FIELDS))
        self.assertEqual(self.store.state(rid)[0], "ACKED")
        self.assertEqual(self.target.counts(), dict(fake_effects=1, first_attempts=1,
                                                   second_attempts=1, external_effects=0))

    def test_status_pending_rejected_stale_cancelled(self):
        for status in ["pending", "rejected", "stale", "cancelled", "superseded", "expired", "ACCEPTED"]:
            r = copy.deepcopy(self.r); r["status"] = status
            self.denied_case("status_" + status, lambda r=r: self.store.issue(self.snap(r=r), self.m, NOW))

    def test_actor_mismatch_all_author_fields(self):
        for where, keys in [("ticket", ["createdByUserId", "responsibleUserId"]),
                            ("interaction", ["createdByUserId", "addresseeUserId", "resolvedByUserId"])]:
            for key in keys:
                t, r = copy.deepcopy(self.t), copy.deepcopy(self.r)
                (t if where == "ticket" else r)[key] = "unauthorized-human"
                self.denied_case(where + "_" + key, lambda t=t, r=r: self.store.issue(self.snap(t, r), self.m, NOW))

    def test_agent_and_run_fields_rejected_in_both_sources(self):
        for where, fields in [("ticket", TICKET_FIELDS), ("interaction", INTERACTION_FIELDS)]:
            for key, typ in fields.items():
                if typ is type(None):
                    t, r = copy.deepcopy(self.t), copy.deepcopy(self.r)
                    (t if where == "ticket" else r)[key] = "fake-agent-or-run"
                    self.denied_case(where + "_nonnull_" + key,
                                     lambda t=t, r=r: self.store.issue(self.snap(t, r), self.m, NOW))

    def test_policies_and_implicit_sources_rejected(self):
        for key, val in dict(requestedResolverPolicy="agent", effectiveResolverPolicy="any",
                             resolverPolicy="any", resolverPolicyProvenance="default",
                             effectiveResolverPolicySource="fallback", continuationPolicy="resume").items():
            r = copy.deepcopy(self.r); r[key] = val
            self.denied_case("policy_" + key, lambda r=r: self.store.issue(self.snap(r=r), self.m, NOW))

    def test_board_profile_principal_and_identity_kind(self):
        for c in [replace(self.c, profile="other-profile"), replace(self.c, user_id="other-human"),
                  replace(self.c, identity_kind="agent"), replace(self.c, identity_kind="run"),
                  replace(self.c, identity_kind="Board")]:
            self.denied_case("board_" + canonical(c.__dict__), lambda c=c: self.store.issue(self.snap(c=c), self.m, NOW))

    def test_temporal_window_and_snapshot_freshness(self):
        for name, c, m, now in [
            ("old_observation", replace(self.c, observed_at=NOW-61), self.m, NOW),
            ("future_observation", replace(self.c, observed_at=NOW+1), self.m, NOW),
            ("inactive_scope", self.c, replace(self.m, valid_until=NOW), NOW),
            ("not_yet_active", self.c, replace(self.m, valid_from=NOW+1), NOW),
            ("expired_at_send", replace(self.c, observed_at=NOW+601), self.m, NOW+601),
            ("bool_clock", self.c, self.m, True),
            ("bad_age_policy", self.c, replace(self.m, max_snapshot_age=99999), NOW)]:
            self.denied_case(name, lambda c=c, m=m, now=now: self.store.issue(self.snap(c=c), m, now))
        for stamp in ["2026-10-16T21:59:00Z", "2026-10-17T22:01:00Z", "2026-10-17T21:59:00",
                      "bad", "2026-10-17T21:59:00+03:00"]:
            r = copy.deepcopy(self.r); r["resolvedAt"] = stamp
            self.denied_case("resolvedAt_" + stamp, lambda r=r: self.store.issue(self.snap(r=r), self.m, NOW))

    def test_missing_extra_and_wrong_types_every_top_field(self):
        for where, fields in [("ticket", TICKET_FIELDS), ("interaction", INTERACTION_FIELDS)]:
            for key, typ in fields.items():
                for mutation in ["missing", "wrong_type"]:
                    t, r = copy.deepcopy(self.t), copy.deepcopy(self.r)
                    obj = t if where == "ticket" else r
                    if mutation == "missing": del obj[key]
                    else: obj[key] = 7 if typ is not int else "7"
                    self.denied_case(where + "_" + mutation + "_" + key,
                                     lambda t=t, r=r: self.store.issue(self.snap(t, r), self.m, NOW))
            t, r = copy.deepcopy(self.t), copy.deepcopy(self.r)
            (t if where == "ticket" else r)["authToken"] = "not-a-credential-synthetic-injection"
            self.denied_case(where + "_extra", lambda t=t, r=r: self.store.issue(self.snap(t, r), self.m, NOW))

    def test_nested_payload_result_forgery(self):
        for name, update in [
            ("payload_extra", lambda r: r["payload"].update(command="shell")),
            ("payload_bool_version", lambda r: r["payload"].update(version=True)),
            ("payload_prompt", lambda r: r["payload"].update(prompt="do-anything")),
            ("payload_whitespace", lambda r: r["payload"].update(detailsMarkdown=r["payload"]["detailsMarkdown"]+" ")),
            ("payload_supersede", lambda r: r["payload"].update(supersedeOnUserComment=True)),
            ("result_extra", lambda r: r["result"].update(resolvedByUserId=self.m.board_user)),
            ("result_outcome", lambda r: r["result"].update(outcome="rejected")),
            ("result_bool_version", lambda r: r["result"].update(version=True)),
            ("result_version", lambda r: r["result"].update(version=2))]:
            r = copy.deepcopy(self.r); update(r)
            self.denied_case(name, lambda r=r: self.store.issue(self.snap(r=r), self.m, NOW))

    def test_id_scope_ticket_and_interaction_mismatch(self):
        for where, key in [("ticket", "id"), ("ticket", "companyId"), ("ticket", "identifier"),
                           ("ticket", "status"), ("ticket", "description"),
                           ("interaction", "id"), ("interaction", "issueId"), ("interaction", "companyId"),
                           ("interaction", "kind"), ("interaction", "idempotencyKey")]:
            t, r = copy.deepcopy(self.t), copy.deepcopy(self.r)
            (t if where == "ticket" else r)[key] = "different"
            self.denied_case("mismatch_" + where + "_" + key,
                             lambda t=t, r=r: self.store.issue(self.snap(t, r), self.m, NOW))
        for field in ["scope_id", "session_id", "operation_id"]:
            m = replace(self.m, **{field: "expanded-not-authorized"})
            self.denied_case("manifest_scope_" + field, lambda m=m: self.store.issue(self.snap(), m, NOW))

    def test_p119_never_eligible(self):
        for value in ["PQBR-119", "d3b2eb41-63e5-4e7e-8cb7-06672e3ddab9", "815e9e44-cf90-45b4-86a2-23aafd45d0fc"]:
            r = copy.deepcopy(self.r); r["id"] = value
            self.denied_case("P119_" + value, lambda r=r: self.store.issue(self.snap(r=r), self.m, NOW))

    def test_json_duplicate_nonfinite_and_envelopes(self):
        bad = ["", "{}", "null", "[", "[NaN]", "[Infinity]", "[]", canonical([self.r,self.r]),
               canonical({"items":[self.r]}), canonical([self.r]).replace('"status":"accepted"',
                         '"status":"pending","status":"accepted"'),
               canonical([self.r]).replace('"outcome":"accepted"',
                         '"outcome":"rejected","outcome":"accepted"'), "x"*65537]
        for i, raw in enumerate(bad):
            self.denied_case("json_"+str(i), lambda raw=raw: self.store.issue(
                parse_snapshot(canonical(self.t), raw, self.c), self.m, NOW))
        self.denied_case("context_from_json", lambda: parse_snapshot(canonical(self.t), canonical([self.r]), self.c.__dict__))

    def test_fake_get_port_cannot_mutate(self):
        for method, command in [("POST", ("issue","interactions", self.m.issue_id,"--json")),
                                ("GET", ("issue","create",self.m.issue_id,"--json")),
                                ("GET", ("issue","resolve",self.m.issue_id,"--json")),
                                ("GET", ("issue","get",self.m.issue_id,"--json","--approve"))]:
            self.denied_case("cli_"+str(command), lambda method=method, command=command: self.cli.request(method, command))
        self.assertEqual(self.cli.calls, [])

    def test_constructed_snapshot_is_reparsed(self):
        r = copy.deepcopy(self.r); r["extra"] = True
        forged = Snapshot(canonical(self.t), canonical(r), self.c)
        self.denied_case("constructed_snapshot_extra", lambda: self.store.issue(forged, self.m, NOW))

    def test_receipt_mismatch_binding_versions_and_snapshot(self):
        rid = self.issue()
        newer = copy.deepcopy(self.r); newer["resolvedAt"] = "2026-10-17T21:59:01Z"
        for name, fn in [
            ("receipt_unknown", lambda: self.store.consume("other", self.snap(), self.m, NOW)),
            ("receipt_version", lambda: self.store.consume(rid, self.snap(), self.m, NOW, expected_version=1)),
            ("receipt_snapshot", lambda: self.store.consume(rid, self.snap(r=newer), self.m, NOW)),
            ("receipt_manifest", lambda: self.store.consume(rid, self.snap(), replace(self.m, valid_until=NOW+700), NOW))]:
            self.denied_case(name, fn)
        self.assertIsNone(self.store.state(rid))

    def test_duplicate_issue_and_replay_consume(self):
        rid = self.ready()
        self.denied_case("duplicate_issue", self.issue)
        self.denied_case("replay_consume", lambda: self.store.consume(rid, self.snap(), self.m, NOW))
        self.assertEqual(self.store.state(rid)[0], "READY")
        db=connect(self.store.path)
        try:
            self.assertEqual(db.execute("SELECT count(*) FROM receipts").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT count(*) FROM outbox").fetchone()[0], 1)
        finally: db.close()

    def test_idempotency_collision_different_interaction(self):
        self.issue()
        m = replace(self.m, interaction_id="interaction-synthetic-different")
        t,r,c = copy.deepcopy(self.t),copy.deepcopy(self.r),self.c
        from candidate import scope_text
        r["id"]=m.interaction_id
        r["payload"]["detailsMarkdown"]=scope_text(m.wire())
        t["description"]=scope_text(m.wire())
        m=replace(m, description=t["description"], payload_json=canonical(r["payload"]))
        self.denied_case("idempotency_collision", lambda: self.store.issue(self.snap(t,r,c),m,NOW))

    def test_atomic_rollback_fault_between_cas_and_outbox(self):
        rid = self.issue()
        def fail(stage): raise RuntimeError("INJECTED_"+stage)
        with self.assertRaises(RuntimeError): self.store.consume(rid,self.snap(),self.m,NOW,fault=fail)
        self.assertIsNone(self.store.state(rid))
        self.store.consume(rid,self.snap(),self.m,NOW)
        self.assertEqual(self.store.state(rid)[0],"READY")
        self.zero()

    def test_atomic_rollback_sqlite_outbox_constraint(self):
        rid=self.issue(); db=connect(self.store.path)
        try:
            db.execute("CREATE TRIGGER reject_outbox BEFORE INSERT ON outbox BEGIN SELECT RAISE(ABORT,'INJECTED'); END")
        finally: db.close()
        with self.assertRaises(sqlite3.IntegrityError): self.store.consume(rid,self.snap(),self.m,NOW)
        self.assertIsNone(self.store.state(rid))
        db=connect(self.store.path)
        try:
            self.assertEqual(db.execute("SELECT state,version FROM receipts").fetchone(),("ISSUED",0))
        finally: db.close()
        self.zero()

    def test_parallel_consume_cas_one_winner_eight_processes(self):
        rid=self.issue()
        with ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(lambda _: self.child("consume",rid), range(8)))
        self.assertEqual(sorted(p.returncode for p in results),[0]+[10]*7)
        self.assertEqual(self.store.state(rid)[0],"READY")
        self.zero()

    def test_parallel_issue_one_winner(self):
        def attempt(_):
            try: return self.issue()
            except Denied: return None
        with ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(attempt,range(8)))
        self.assertEqual(sum(x is not None for x in results),1)
        self.zero()

    def test_parallel_claim_one_winner(self):
        rid=self.ready()
        def attempt(_):
            try: return self.store.claim(rid,self.snap(),self.m,NOW)
            except Denied: return None
        with ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(attempt,range(8)))
        self.assertEqual(sum(x is not None for x in results),1)
        self.zero()

    def test_opt_in_and_only_exact_fake_types(self):
        rid=self.ready()
        for name, cli, target, opt in [("not_opted",self.cli,self.target,False),
                                       ("truthy_opt",self.cli,self.target,1),
                                       ("real_cli_forbidden",object(),self.target,True),
                                       ("real_target_forbidden",self.cli,object(),True)]:
            self.denied_case(name,lambda cli=cli,target=target,opt=opt:send_once(
                self.store,rid,cli,self.m,NOW,target,opt_in=opt))
        self.assertEqual(self.store.state(rid)[0],"READY")

    def test_status_revoked_after_receipt_blocks_dispatch(self):
        rid=self.ready()
        r=copy.deepcopy(self.r); r["status"]="rejected"
        cli=fake_cli(r=r)
        self.denied_case("rejected_before_send",lambda:send_once(self.store,rid,cli,self.m,NOW,self.target,opt_in=True))
        self.assertEqual(self.store.state(rid)[0],"READY")

    def test_snapshot_changed_but_still_accepted_blocks_dispatch(self):
        rid=self.ready(); r=copy.deepcopy(self.r); r["resolvedAt"]="2026-10-17T21:59:01Z"
        self.denied_case("changed_accepted_binding",lambda:send_once(
            self.store,rid,fake_cli(r=r),self.m,NOW,self.target,opt_in=True))
        self.assertEqual(self.store.state(rid)[0],"READY")

    def test_outbox_tamper_blocks_dispatch(self):
        rid=self.ready(); db=connect(self.store.path)
        try: db.execute("UPDATE outbox SET wire='{}'")
        finally: db.close()
        self.denied_case("tampered_outbox",lambda:send_once(self.store,rid,self.cli,self.m,NOW,self.target,opt_in=True))

    def test_receipt_tamper_blocks_dispatch(self):
        rid=self.ready(); db=connect(self.store.path)
        try: db.execute("UPDATE receipts SET snapshot='forged'")
        finally: db.close()
        self.denied_case("tampered_receipt",lambda:send_once(self.store,rid,self.cli,self.m,NOW,self.target,opt_in=True))

    def test_wrong_owner_stale_ack_and_recovery_cas(self):
        rid=self.ready(); owner,v,wire=self.store.claim(rid,self.snap(),self.m,NOW)
        self.denied_case("wrong_ack_owner",lambda:self.store.ack(rid,"other",v))
        self.denied_case("stale_recovery",lambda:self.store.recover(rid,v+1))
        self.store.recover(rid,v)
        self.denied_case("old_fenced_ack",lambda:self.store.ack(rid,owner,v))
        self.denied_case("duplicate_recovery",lambda:self.store.recover(rid,v))
        self.assertEqual(self.store.state(rid)[0],"READY")

    def test_ack_lost_manual_recovery_duplicate_fake_no_extra_effect(self):
        rid=self.ready()
        with self.assertRaises(TimeoutError):send_once(self.store,rid,self.cli,self.m,NOW,self.target,opt_in=True,lose_ack=True)
        self.assertEqual(self.target.counts()["fake_effects"],1)
        state,v,owner=self.store.state(rid);self.assertEqual(state,"SENDING")
        with self.assertRaises(Denied):send_once(self.store,rid,self.cli,self.m,NOW,self.target,opt_in=True)
        self.store.recover(rid,v)
        self.assertEqual(send_once(self.store,rid,self.cli,self.m,NOW,self.target,opt_in=True),"duplicate")
        self.assertEqual(self.target.counts()["fake_effects"],1)
        with self.assertRaises(Denied):send_once(self.store,rid,self.cli,self.m,NOW,self.target,opt_in=True)
        self.assertEqual(self.target.counts()["fake_effects"],1)
        self.assertEqual(self.store.state(rid)[0],"ACKED")

    def test_sigkill_before_local_commit_rolls_back_both_stages(self):
        for action in ["consume-kill-cas","consume-kill-commit"]:
            with self.subTest(action=action):
                # Cada estágio usa uma autorização sintética nova em armazenamento isolado.
                with tempfile.TemporaryDirectory() as d:
                    old=self.root;self.root=Path(d)
                    try:
                        store=ReceiptStore(self.root/"receipt.sqlite")
                        rid=store.issue(self.snap(),self.m,NOW)
                        p=self.child(action,rid)
                        self.assertEqual(p.returncode,-signal.SIGKILL,p.stderr)
                        reopened=ReceiptStore(store.path)
                        self.assertIsNone(reopened.state(rid))
                        reopened.consume(rid,self.snap(),self.m,NOW)
                        self.assertEqual(reopened.state(rid)[0],"READY")
                    finally:self.root=old
        self.zero()

    def test_process_restart_after_issue_and_commit_before_dispatch(self):
        p=self.child("issue",check=True);rid=p.stdout.strip()
        self.assertTrue(rid.startswith("receipt-"))
        self.child("consume",rid,check=True)
        self.assertEqual(ReceiptStore(self.store.path).state(rid)[0],"READY")
        self.zero()
        self.child("send",rid,check=True)
        self.assertEqual(self.target.counts()["fake_effects"],1)

    def test_process_kill_before_send_restart_preserves_pending(self):
        rid=self.ready();p=self.child("send-kill-before",rid)
        self.assertEqual(p.returncode,-signal.SIGKILL,p.stderr);self.zero()
        store=ReceiptStore(self.store.path);state,v,_=store.state(rid)
        self.assertEqual(state,"SENDING");store.recover(rid,v)
        self.child("send",rid,check=True)
        self.assertEqual(self.target.counts()["fake_effects"],1)

    def test_process_kill_after_remote_ack_restart_dedupes(self):
        rid=self.ready();p=self.child("send-kill-after",rid)
        self.assertEqual(p.returncode,-signal.SIGKILL,p.stderr)
        self.assertEqual(self.target.counts()["fake_effects"],1)
        store=ReceiptStore(self.store.path);state,v,_=store.state(rid)
        self.assertEqual(state,"SENDING");store.recover(rid,v)
        p=self.child("send",rid,check=True);self.assertEqual(p.stdout.strip(),"duplicate")
        target=FakeTemporal(self.target.path,self.m)
        self.assertEqual(target.counts(),dict(fake_effects=1,first_attempts=1,second_attempts=1,external_effects=0))

    def test_process_ack_loss_then_restart_dedupes(self):
        rid=self.ready();p=self.child("send-lose-ack",rid)
        self.assertEqual(p.returncode,21,p.stderr)
        self.assertEqual(self.target.counts()["fake_effects"],1)
        state,v,_=self.store.state(rid);self.assertEqual(state,"SENDING")
        ReceiptStore(self.store.path).recover(rid,v)
        p=self.child("send",rid,check=True);self.assertEqual(p.stdout.strip(),"duplicate")
        self.assertEqual(self.target.counts()["fake_effects"],1)

    def test_fake_receiver_rejects_scope_expansion_and_nonpending(self):
        for key in WIRE_FIELDS:
            p=self.m.wire();p[key]="wrong-id"
            self.denied_case("target_wrong_"+key,lambda p=p:self.target.send(p))
        p=self.m.wire();p["command"]="execute"
        self.denied_case("target_extra",lambda:self.target.send(p))
        db=connect(self.target.path)
        try:db.execute("UPDATE target SET second_state='REJECTED'")
        finally:db.close()
        self.denied_case("target_not_pending",lambda:self.target.send(self.m.wire()))

    def test_first_failed_never_retried_or_reopened(self):
        db=connect(self.target.path)
        try:db.execute("UPDATE target SET first_state='RUNNING'")
        finally:db.close()
        rid=self.ready()
        self.denied_case("first_not_terminal",lambda:send_once(self.store,rid,self.cli,self.m,NOW,self.target,opt_in=True))

    def test_cas_does_not_claim_exactly_once_across_two_stores(self):
        # Dois bancos de receipt independentes NÃO são protegidos por CAS global.
        # O destino fake ainda deduplica pela mesma chave; esta premissa é explícita.
        a=self.ready();other=ReceiptStore(self.root/"other.sqlite")
        b=other.issue(self.snap(),self.m,NOW);other.consume(b,self.snap(),self.m,NOW)
        self.assertEqual(send_once(self.store,a,self.cli,self.m,NOW,self.target,opt_in=True),"applied")
        self.assertEqual(send_once(other,b,self.cli,self.m,NOW,self.target,opt_in=True),"duplicate")
        self.assertEqual(self.target.counts()["fake_effects"],1)

    def test_audit_guard_denies_network(self):
        # Evento simulado, sem sequer criar um socket; funciona também fora do runner.
        from run_offline import guard
        for event in ["socket.__new__", "socket.connect", "socket.getaddrinfo", "os.system"]:
            with self.assertRaisesRegex(RuntimeError,"OFFLINE_GUARD"):
                guard(event, (None,))
        with self.assertRaisesRegex(RuntimeError,"OFFLINE_GUARD"):
            guard("subprocess.Popen", ("paperclipai", ["paperclipai", "issue", "get"]))
        self.zero()

    def test_invalid_unicode_denied_uniformly(self):
        for raw in ['"\\ud800"', '"' + chr(0xd800) + '"']:
            self.denied_case("invalid_unicode_" + repr(raw), lambda raw=raw: strict_json(raw))

    def test_reclaimed_old_sender_is_not_remotely_fenced_but_fake_dedupes(self):
        # CAS protege ACK local; não impede transporte de um emissor antigo.
        rid=self.ready()
        old_owner,old_v,wire=self.store.claim(rid,self.snap(),self.m,NOW)
        self.store.recover(rid,old_v)
        new_owner,new_v,new_wire=self.store.claim(rid,self.snap(),self.m,NOW)
        self.assertEqual(self.target.send(wire),"applied")
        self.assertEqual(self.target.send(new_wire),"duplicate")
        with self.assertRaises(Denied):self.store.ack(rid,old_owner,old_v)
        self.store.ack(rid,new_owner,new_v)
        self.assertEqual(self.target.counts()["fake_effects"],1)
        self.assertEqual(self.store.state(rid)[0],"ACKED")
