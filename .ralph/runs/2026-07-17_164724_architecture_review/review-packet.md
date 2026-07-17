# Review Packet: 2026-07-17_164724_architecture_review

## Result

Architecture review complete pending independent Ralph validation. No production code changed.

## Range and Scope

Reviewed 009E3, 009F2, 009G, and 009H across `f35e0fc7...dbccea9c`. The review covered production,
tests, migrations, slice contracts/run packets, Epic 009 digest/epic, cited source requirements,
module duplication/dependency direction, M08 requirement IDs, CONTEXT truth, and blocked slices.

## Standards

- High: successful transfer omits atomic register, pending-advice, and reachable checklist truth.
- High: advice provider idempotency is process-local and cannot survive acceptance plus rollback.
- High: source-bank changes retain no reviewable rationale and overstate request/single-actor approval.
- Medium: advice audit duplicates the full borrower email outside the protected communication row.

## Spec

- High: M08-FR-009 Loan Register and M08-FR-011 post-disbursement checklist paths are absent.
- High: advice grants CFC-only authority and omits source-authorised Credit Manager.
- High: transfer replay omits API §45.2's replay marker and original response.
- Medium: changed canonical email or rendered communication snapshot remains replayable as HTTP 200.

## Traceability

M08-FR-007/008 are substantively implemented by 009G's UTR, evidenced transfer, atomic funding, and
activation. M08-FR-009/011 are not implemented or deferred and are now owned by 009G2. M08-FR-010
has a real sent communication but remains partial until 009H2 closes authority, delivery idempotency,
current contact/rendered truth, and audit minimisation. CFG-001 rationale truth is owned by 009E4;
A-126 continues to leave the unnamed business provisioner unassigned.

## Evidence

- 14 retained public transfer/advice tests: PASS.
- Four review-only corrective probes: FAIL as expected and reproduce the four targeted contracts.
- Queue lint, first-grabbable selection, blocked-slice audit, and `git diff --check`: PASS.
- Full backend coverage/frontend gates are deliberately not duplicated for this documentation-only
  review; the orchestrator's specialized architecture-review lane remains authoritative.

## Corrective Queue

1. 009E4 — source-bank rationale and honest approval attribution.
2. 009G2 — atomic register/pending advice, §45.2 replay, and public checklist signature.
3. 009H2 — source role matrix, durable provider replay, current content/contact, masked audit.
4. 009I/009J — re-sharpened to consume 009H2/009G2.

Worst severity is High on both axes. Standards: 3 High, 1 Medium. Spec: 3 High, 1 Medium.
