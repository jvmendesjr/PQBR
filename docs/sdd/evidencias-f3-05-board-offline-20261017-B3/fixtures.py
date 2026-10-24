"""Fixtures sintéticas explícitas; nenhum ID/credencial/autorização real."""
from datetime import datetime, timezone
from dataclasses import replace
from candidate import (Manifest, BoardContext, FakeGetCLI, canonical, scope_text,
                       AUTH_PROMPT, PAYLOAD_FIELDS, TICKET_FIELDS, INTERACTION_FIELDS)

NOW = int(datetime(2026, 10, 17, 22, 0, 0, tzinfo=timezone.utc).timestamp())


def fixture():
    m = Manifest(issue_id="issue-synthetic-B3", interaction_id="interaction-synthetic-B3",
                 company_id="company-synthetic", ticket="SYNTHETIC-B3",
                 board_user="human-synthetic-tutibom", board_profile="board-synthetic-authorized",
                 scope_id="scope-synthetic-B3-once", session_id="session-synthetic-B3",
                 operation_id="second-synthetic-accepted", idempotency_key="idempotency-synthetic-B3-once",
                 description="", payload_json="{}", valid_from=NOW-120, valid_until=NOW+600)
    details = scope_text(m.wire())
    payload = dict(version=1, prompt=AUTH_PROMPT, acceptLabel="Autorizar execução única",
                   rejectLabel="Não autorizar", allowDeclineReason=True,
                   detailsMarkdown=details, supersedeOnUserComment=False)
    m = replace(m, description=details, payload_json=canonical(payload))
    t = {k: None for k in TICKET_FIELDS}
    t.update(id=m.issue_id, companyId=m.company_id, identifier=m.ticket, status="backlog",
             createdByUserId=m.board_user, responsibleUserId=m.board_user, description=details)
    r = {k: None for k in INTERACTION_FIELDS}
    r.update(id=m.interaction_id, issueId=m.issue_id, companyId=m.company_id,
             kind="request_confirmation", status="accepted", createdByUserId=m.board_user,
             addresseeUserId=m.board_user, resolvedByUserId=m.board_user,
             requestedResolverPolicy="human_only", effectiveResolverPolicy="human_only",
             resolverPolicy="human_only", resolverPolicyProvenance="explicit",
             effectiveResolverPolicySource="requested", continuationPolicy="none",
             idempotencyKey=m.idempotency_key, resolvedAt="2026-10-17T21:59:00Z",
             payload=payload, result=dict(version=1, outcome="accepted"))
    c = BoardContext(m.board_profile, m.board_user, "board", NOW)
    return m, t, r, c


def fake_cli(m=None, t=None, r=None, c=None):
    fm, ft, fr, fc = fixture()
    return FakeGetCLI(canonical(ft if t is None else t), canonical([fr if r is None else r]), fc if c is None else c)
