"""B3: candidato estritamente offline. Importar não executa nada.
Não contém CLI real, HTTP, SDK Temporal, credenciais nem registro de Worker.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
import sqlite3
import uuid


class Denied(ValueError):
    pass


def require(ok, code):
    if not ok:
        raise Denied(code)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def strict_json(raw):
    require(type(raw) is str, "JSON_SIZE_TYPE")
    def pairs(items):
        out = {}
        for k, v in items:
            require(k not in out, "DUPLICATE_KEY")
            out[k] = v
        return out
    try:
        require(len(raw.encode("utf-8")) <= 65536, "JSON_SIZE_TYPE")
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(Denied("NONFINITE")))
        def unicode_check(item):
            if type(item) is str:
                item.encode("utf-8")
            elif type(item) is dict:
                for key, val in item.items():
                    unicode_check(key)
                    unicode_check(val)
            elif type(item) is list:
                for val in item:
                    unicode_check(val)
        unicode_check(value)
        return value
    except (ValueError, RecursionError, UnicodeError) as e:
        raise Denied("INVALID_JSON") from e


def shape(obj, fields):
    require(type(obj) is dict and set(obj) == set(fields), "SCHEMA_FIELDS")
    for k, t in fields.items():
        require(type(obj[k]) is t, "SCHEMA_TYPE_" + k)


def ident(x):
    require(type(x) is str and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}", x) is not None, "ID")
    # Bloqueio explícito da autorização já consumida; não é um registro global.
    require(x not in {"PQBR-119", "d3b2eb41-63e5-4e7e-8cb7-06672e3ddab9",
                      "815e9e44-cf90-45b4-86a2-23aafd45d0fc"}, "P119_CONSUMED")


def instant(s):
    require(type(s) is str and len(s) < 50, "TIMESTAMP")
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        require(d.tzinfo is not None and d.utcoffset().total_seconds() == 0, "TIMESTAMP_UTC")
        return d.timestamp()
    except (ValueError, OverflowError) as e:
        raise Denied("TIMESTAMP") from e


PAYLOAD_FIELDS = dict(version=int, prompt=str, acceptLabel=str, rejectLabel=str,
                      allowDeclineReason=bool, detailsMarkdown=str, supersedeOnUserComment=bool)
TICKET_FIELDS = dict(id=str, companyId=str, identifier=str, status=str,
                     createdByUserId=str, responsibleUserId=str, description=str,
                     createdByAgentId=type(None), executionRunId=type(None),
                     checkoutRunId=type(None), executionLockedAt=type(None),
                     completedAt=type(None), cancelledAt=type(None))
INTERACTION_FIELDS = dict(id=str, issueId=str, companyId=str, kind=str, status=str,
                         createdByUserId=str, addresseeUserId=str, resolvedByUserId=str,
                         requestedResolverPolicy=str, effectiveResolverPolicy=str,
                         resolverPolicy=str, resolverPolicyProvenance=str,
                         effectiveResolverPolicySource=str, continuationPolicy=str,
                         idempotencyKey=str, resolvedAt=str, payload=dict, result=dict,
                         createdByAgentId=type(None), addresseeAgentId=type(None),
                         resolvedByAgentId=type(None), resolvedByRunId=type(None), sourceRunId=type(None))
WIRE_FIELDS = dict(issueId=str, interactionId=str, scopeId=str, sessionId=str,
                   operationId=str, idempotencyKey=str)


AUTH_PROMPT = "Autoriza uma única prova sintética deste escopo exato, sem efeitos externos?"


def scope_text(wire):
    scope_ids = {k: wire[k] for k in ("scopeId", "sessionId", "operationId", "idempotencyKey")}
    return ("Uma única rodada sintética. Primeira já FAILED, uma tentativa, sem retry ou reexecução. "
            "Somente a segunda já aceita e pendente pode retomar uma vez. "
            "Temporal Server 1.32.1 descartável somente após autorização específica, rede interna isolada, "
            "Activities falsas e armazenamento descartável. Sem Workers persistentes, integrações reais, "
            "Discord, produção, publicação, deploy ou mudança da política de falha técnica. "
            "issueId e interactionId devem ser exclusivamente os IDs do ticket e da própria confirmação aceita, "
            "fixados no manifesto ativo e vinculados integralmente ao snapshot e receipt, nunca IDs de outra autorização. "
            "IDs de escopo exatos autorizados: " + canonical(scope_ids))


@dataclass(frozen=True)
class Manifest:
    """Entradas confiáveis do harness; nunca derivadas de campos não confiáveis."""
    issue_id: str
    interaction_id: str
    company_id: str
    ticket: str
    board_user: str
    board_profile: str
    scope_id: str
    session_id: str
    operation_id: str
    idempotency_key: str
    description: str
    payload_json: str
    valid_from: int
    valid_until: int
    max_snapshot_age: int = 60

    def wire(self):
        return dict(issueId=self.issue_id, interactionId=self.interaction_id,
                    scopeId=self.scope_id, sessionId=self.session_id,
                    operationId=self.operation_id, idempotencyKey=self.idempotency_key)

    def binding(self):
        # Todos os atributos, inclusive janela temporal e perfil Board.
        return canonical(self.__dict__)


@dataclass(frozen=True)
class BoardContext:
    """Metadado out-of-band do fake; NÃO afirma autenticação real."""
    profile: str
    user_id: str
    identity_kind: str
    observed_at: int


@dataclass(frozen=True)
class Snapshot:
    ticket_json: str
    interaction_json: str
    context: BoardContext

    def binding(self):
        return canonical(dict(ticket=strict_json(self.ticket_json),
                              interaction=strict_json(self.interaction_json),
                              board=dict(profile=self.context.profile, userId=self.context.user_id,
                                         identityKind=self.context.identity_kind)))


def parse_snapshot(ticket_raw, interactions_raw, context):
    require(type(context) is BoardContext, "TRUSTED_CONTEXT_REQUIRED")
    t, rows = strict_json(ticket_raw), strict_json(interactions_raw)
    shape(t, TICKET_FIELDS)
    require(type(rows) is list and len(rows) == 1, "ONE_ACTIVE_INTERACTION_REQUIRED")
    r = rows[0]
    shape(r, INTERACTION_FIELDS)
    shape(r["payload"], PAYLOAD_FIELDS)
    shape(r["result"], dict(version=int, outcome=str))
    for value in [t["id"], t["companyId"], t["identifier"], t["createdByUserId"],
                  t["responsibleUserId"], r["id"], r["issueId"], r["companyId"],
                  r["createdByUserId"], r["addresseeUserId"], r["resolvedByUserId"], r["idempotencyKey"]]:
        ident(value)
    for text in [t["description"], r["payload"]["prompt"], r["payload"]["detailsMarkdown"]]:
        require(0 < len(text) <= 16000 and "\x00" not in text, "TEXT")
    instant(r["resolvedAt"])
    # Somente whitelist, sem manter raw/envelope ou campos arbitrários.
    return Snapshot(canonical(t), canonical(r), context)


def validate(snapshot, manifest, now):
    require(type(manifest) is Manifest and type(snapshot) is Snapshot, "BOUND_TYPES")
    require(type(now) is int, "CLOCK")
    require(type(manifest.valid_from) is int and type(manifest.valid_until) is int
            and manifest.valid_from <= now < manifest.valid_until, "INACTIVE_SCOPE")
    require(type(manifest.max_snapshot_age) is int and 0 < manifest.max_snapshot_age <= 300, "AGE_POLICY")
    c = snapshot.context
    require(type(c.observed_at) is int and 0 <= now - c.observed_at <= manifest.max_snapshot_age, "STALE_SNAPSHOT")
    require(c.identity_kind == "board" and c.profile == manifest.board_profile
            and c.user_id == manifest.board_user, "UNAUTHORIZED_BOARD")
    for x in [manifest.issue_id, manifest.interaction_id, manifest.company_id, manifest.ticket,
              manifest.board_user, manifest.board_profile, manifest.scope_id, manifest.session_id,
              manifest.operation_id, manifest.idempotency_key]:
        ident(x)
    # Repassar o parser também impede Snapshot construído manualmente com esquema forjado.
    parsed = parse_snapshot(snapshot.ticket_json, "[" + snapshot.interaction_json + "]", c)
    t, r = strict_json(parsed.ticket_json), strict_json(parsed.interaction_json)
    expected_t = dict(id=manifest.issue_id, companyId=manifest.company_id, identifier=manifest.ticket,
                      status="backlog", createdByUserId=manifest.board_user,
                      responsibleUserId=manifest.board_user, description=manifest.description)
    require(all(t[k] == v for k, v in expected_t.items()), "TICKET_SCOPE_ACTOR")
    expected_r = dict(id=manifest.interaction_id, issueId=manifest.issue_id, companyId=manifest.company_id,
                      kind="request_confirmation", status="accepted", createdByUserId=manifest.board_user,
                      addresseeUserId=manifest.board_user, resolvedByUserId=manifest.board_user,
                      requestedResolverPolicy="human_only", effectiveResolverPolicy="human_only",
                      resolverPolicy="human_only", resolverPolicyProvenance="explicit",
                      effectiveResolverPolicySource="requested", continuationPolicy="none",
                      idempotencyKey=manifest.idempotency_key)
    require(all(r[k] == v for k, v in expected_r.items()), "INTERACTION_SCOPE_ACTOR_POLICY")
    require(r["result"] == {"version": 1, "outcome": "accepted"}, "ACCEPTED_RESULT_REQUIRED")
    p = strict_json(manifest.payload_json)
    shape(p, PAYLOAD_FIELDS)
    require(type(p["version"]) is int and p["version"] == 1, "PAYLOAD_VERSION")
    require(canonical(r["payload"]) == canonical(p), "EXACT_PAYLOAD_REQUIRED")
    require(manifest.valid_from <= instant(r["resolvedAt"]) <= now, "STALE_ACCEPTANCE")
    require(p["supersedeOnUserComment"] is False, "SUPERSEDE_POLICY")
    require(p["detailsMarkdown"] == scope_text(manifest.wire())
            and manifest.description == scope_text(manifest.wire())
            and p["prompt"] == AUTH_PROMPT, "WIRE_SCOPE_TEXT")
    return dict(snapshot=digest(parsed.binding()), manifest=digest(manifest.binding()),
                wire=canonical(manifest.wire()))


class FakeGetCLI:
    """Porta fake explícita. Não executa nem resolve caminho de CLI real."""
    def __init__(self, ticket_raw, interactions_raw, context):
        self.ticket_raw, self.interactions_raw, self.context = ticket_raw, interactions_raw, context
        self.calls = []

    def request(self, method, command):
        require(method == "GET", "GET_ONLY")
        require(type(command) is tuple and len(command) == 4
                and command[0] == "issue" and command[1] in {"get", "interactions"}
                and command[3] == "--json", "READ_ONLY_COMMAND")
        self.calls.append((method, command))
        return self.ticket_raw if command[1] == "get" else self.interactions_raw

    def snapshot(self, manifest):
        t = self.request("GET", ("issue", "get", manifest.issue_id, "--json"))
        r = self.request("GET", ("issue", "interactions", manifest.issue_id, "--json"))
        return parse_snapshot(t, r, self.context)


def connect(path):
    db = sqlite3.connect(str(path), timeout=3, isolation_level=None)
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA journal_mode=DELETE")
    db.execute("PRAGMA synchronous=FULL")
    return db


class ReceiptStore:
    def __init__(self, path):
        self.path = str(path)
        db = connect(path)
        try:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS receipts(
                id TEXT PRIMARY KEY, interaction TEXT UNIQUE NOT NULL,
                idem TEXT UNIQUE NOT NULL, snapshot TEXT NOT NULL, manifest TEXT NOT NULL,
                wire TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('ISSUED','CONSUMED')),
                version INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS outbox(
                receipt TEXT PRIMARY KEY REFERENCES receipts(id), wire TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('READY','SENDING','ACKED')),
                version INTEGER NOT NULL, owner TEXT);
            """)
        finally:
            db.close()

    def issue(self, snapshot, manifest, now):
        b = validate(snapshot, manifest, now)
        rid = "receipt-" + uuid.uuid4().hex
        db = connect(self.path)
        try:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT INTO receipts VALUES(?,?,?,?,?,?, 'ISSUED',0)",
                       (rid, manifest.interaction_id, manifest.idempotency_key, b["snapshot"], b["manifest"], b["wire"]))
            db.commit()
            return rid
        except sqlite3.IntegrityError as e:
            db.rollback()
            raise Denied("DUPLICATE_AUTHORIZATION") from e
        finally:
            db.close()

    def consume(self, rid, snapshot, manifest, now, expected_version=0, fault=None):
        b = validate(snapshot, manifest, now)
        db = connect(self.path)
        try:
            db.execute("BEGIN IMMEDIATE")
            count = db.execute("""UPDATE receipts SET state='CONSUMED',version=version+1
              WHERE id=? AND snapshot=? AND manifest=? AND wire=? AND state='ISSUED' AND version=?""",
              (rid, b["snapshot"], b["manifest"], b["wire"], expected_version)).rowcount
            require(count == 1, "RECEIPT_BINDING_CAS")
            if fault:
                fault("after_cas")
            db.execute("INSERT INTO outbox VALUES(?,?,'READY',0,NULL)", (rid, b["wire"]))
            if fault:
                fault("before_commit")
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def claim(self, rid, snapshot, manifest, now):
        b = validate(snapshot, manifest, now)
        owner = uuid.uuid4().hex
        db = connect(self.path)
        try:
            db.execute("BEGIN IMMEDIATE")
            r = db.execute("SELECT snapshot,manifest,wire,state FROM receipts WHERE id=?", (rid,)).fetchone()
            require(r == (b["snapshot"], b["manifest"], b["wire"], "CONSUMED"), "RECEIPT_MISMATCH")
            n = db.execute("""UPDATE outbox SET state='SENDING',version=version+1,owner=?
              WHERE receipt=? AND wire=? AND state='READY'""", (owner, rid, b["wire"])).rowcount
            require(n == 1, "OUTBOX_CAS")
            v = db.execute("SELECT version FROM outbox WHERE receipt=?", (rid,)).fetchone()[0]
            db.commit()
            return owner, v, strict_json(b["wire"])
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def recover(self, rid, expected_version):
        """Somente chamada manual do harness; nenhum timer/loop/retry automático."""
        db = connect(self.path)
        try:
            n = db.execute("""UPDATE outbox SET state='READY',version=version+1,owner=NULL
              WHERE receipt=? AND state='SENDING' AND version=?""", (rid, expected_version)).rowcount
            require(n == 1, "RECOVERY_CAS")
        finally:
            db.close()

    def ack(self, rid, owner, version):
        db = connect(self.path)
        try:
            n = db.execute("""UPDATE outbox SET state='ACKED',version=version+1,owner=NULL
              WHERE receipt=? AND state='SENDING' AND owner=? AND version=?""", (rid, owner, version)).rowcount
            require(n == 1, "ACK_FENCED")
        finally:
            db.close()

    def state(self, rid):
        db = connect(self.path)
        try:
            return db.execute("SELECT state,version,owner FROM outbox WHERE receipt=?", (rid,)).fetchone()
        finally:
            db.close()


class FakeTemporal:
    """Destino fake persistente descartável: não é Temporal Server/SDK.
    A dedupe e o efeito fake são uma transação SQLite; isso não prova efeito real.
    """
    def __init__(self, path, manifest):
        self.path = str(path)
        db = connect(path)
        try:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS target(id INTEGER PRIMARY KEY CHECK(id=1), wire TEXT NOT NULL,
              first_state TEXT NOT NULL, first_attempts INTEGER NOT NULL,
              second_state TEXT NOT NULL, second_attempts INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS effects(idem TEXT PRIMARY KEY, wire TEXT NOT NULL);
            """)
            db.execute("INSERT OR IGNORE INTO target VALUES(1,?,'FAILED',1,'ACCEPTED_PENDING',0)",
                       (canonical(manifest.wire()),))
            require(db.execute("SELECT wire FROM target").fetchone()[0] == canonical(manifest.wire()), "TARGET_SCOPE")
        finally:
            db.close()

    def send(self, payload, lose_ack=False):
        shape(payload, WIRE_FIELDS)
        for v in payload.values():
            ident(v)
        wire = canonical(payload)
        db = connect(self.path)
        try:
            db.execute("BEGIN IMMEDIATE")
            t = db.execute("SELECT wire,first_state,first_attempts,second_state,second_attempts FROM target").fetchone()
            require(t[0] == wire and t[1:3] == ("FAILED", 1), "TARGET_BINDING_OR_FIRST")
            prev = db.execute("SELECT wire FROM effects WHERE idem=?", (payload["idempotencyKey"],)).fetchone()
            if prev:
                require(prev[0] == wire, "DEDUPE_COLLISION")
                result = "duplicate"
            else:
                require(t[3:] == ("ACCEPTED_PENDING", 0), "TARGET_NOT_PENDING")
                db.execute("INSERT INTO effects VALUES(?,?)", (payload["idempotencyKey"], wire))
                db.execute("UPDATE target SET second_state='DONE',second_attempts=1 WHERE id=1")
                result = "applied"
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()
        if lose_ack:
            raise TimeoutError("FAKE_ACK_LOST_AFTER_COMMIT")
        return result

    def counts(self):
        db = connect(self.path)
        try:
            return dict(fake_effects=db.execute("SELECT count(*) FROM effects").fetchone()[0],
                        first_attempts=db.execute("SELECT first_attempts FROM target").fetchone()[0],
                        second_attempts=db.execute("SELECT second_attempts FROM target").fetchone()[0],
                        external_effects=0)
        finally:
            db.close()


def send_once(store, rid, cli, manifest, now, temporal, *, opt_in=False, lose_ack=False, fault=None):
    """Não dispara sem opt-in explícito; uma chamada = uma tentativa de transporte fake."""
    require(opt_in is True, "OPT_IN_REQUIRED")
    require(type(cli) is FakeGetCLI and type(temporal) is FakeTemporal, "OFFLINE_FAKES_ONLY")
    snapshot = cli.snapshot(manifest)  # releitura fake imediatamente antes do consumo/claim
    owner, version, wire = store.claim(rid, snapshot, manifest, now)
    if fault:
        fault("before_send")
    result = temporal.send(wire, lose_ack=lose_ack)
    if fault:
        fault("after_ack")
    store.ack(rid, owner, version)
    return result
