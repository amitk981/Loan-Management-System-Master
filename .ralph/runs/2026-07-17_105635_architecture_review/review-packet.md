# Review Packet: 2026-07-17_105635_architecture_review

## Result

Architecture review complete pending independent Ralph validation. No production code changed.

## Range and Scope

Reviewed 008M7, 009D4, 009E2, and 009F across `24bfc4f4...277f6c8f`. The review covered production,
tests, migrations, slice contracts, run packets, Epic 008/009 digests, cited source requirements,
module duplication/dependency direction, requirement IDs, CONTEXT truth, and queue blockers.

## Standards

- High: authorisation/transfer aggregate constraints admit incomplete or impossible tuples.
- High: active source-bank governance can persist without version/audit proof and its permission is
  absent from the production catalogue.
- High: source-bank replacement does not append/close effective historical evidence.
- Medium: a long-lived test asserts private source shape.
- Medium: CFC scope and authorisation duplicate a drifting initiation predicate.

## Spec

- High: S38/S39 positive lesser amounts are rejected as over-sanction.
- High: CFC authorisation does not consume the current borrower-bank decision.
- High: UTR/disbursed/register truth can pre-exist CFC approval.
- Medium: the claimed genuine composed fixture inserts raw loan account/terms rows.
- Medium: governed rejection/inactive authority and CFC-scope lifecycle proof is partial.

## Traceability

The source says S39 permits an amount editable within sanction limits; code requires equality;
probe `test_positive_lesser_amount_within_sanction_can_be_initiated` fails and 009E3 owns it.

The source/slice says CFC acts only on exact current bank evidence with no transfer-success truth;
code checks labels/copies and omits later-state fields; two 009F probes fail and 009F2 owns them.

M06-FR-018/019 current-tail/signature behavior remains substantive in 008M7/009D4. M07-FR-010 and
M08-FR-001-006 are partial only where 009E3/009F2 now explicitly own the gaps. A-126 is reopened on
mechanism completeness while the unnamed business provisioner remains intentionally unassigned.

## Evidence

- Four retained focused tests: PASS.
- Four review-only corrective probes: FAIL as expected.
- Queue lint/capabilities/JSON/diff/protected paths: PASS.
- Full backend coverage/frontend gates were not duplicated; the orchestrator runs authoritative
  validation after this docs-only review.

## Corrective Queue

1. 009E3 — amount, loan-owner, permission catalogue, source-bank lifecycle/races.
2. 009F2 — current bank evidence, aggregate constraints, scope/action parity, CFC matrix/races.
3. 009G — transfer success after 009F2.

Worst severity is High on both axes. Standards: 3 High, 2 Medium. Spec: 3 High, 2 Medium.
