# Review Packet: 2026-07-19_223154_normal_run

## Result
Ready for independent validation

## Slice
010B-direct-repayment-posting

## Implementation Review

- Public interface: direct capture and manual SAP posting only; allocation and all balance/ledger
  effects remain with 010C.
- Module seam: validation, idempotency, duplicate rules, authority, scope, locking, audit, task,
  obligation, and serialization are local to `direct_repayment_posting`; views only map HTTP.
- Database: one migration with global reference/key uniqueness, positive/bounded receipt constraints,
  complete pending/posted evidence, and singular task/audit relations.
- Reverse consumers: focused 009 activation and 010A schedule/ledger contracts remain green.

## Traceability

- Product §11.23, user-flow §27, BR-055/057, and M09-FR-001/003/005 require RTGS/NEFT bank facts
  and a next-working-day Credit Manager SAP duty. The code accepts only that direct shape and creates
  one pending obligation/task, verified by
  `test_valid_direct_receipt_and_exact_replay_create_one_pending_obligation`.
- API §§32.2/45 require idempotency and duplicate safety. Exact replay is retained and changed,
  cross-loan, or canonical-reference reuse conflicts, verified by
  `test_invalid_duplicate_and_changed_requests_are_zero_write` and both PostgreSQL races.
- Auth §§12.9/19.3/20.2/26.6 require source role, mutation permission, serviceable loan, and scope.
  The code enforces all four, verified by
  `test_capture_requires_effective_authority_and_serviceable_loan`.
- API §32.5 requires SAP reference/time/actor. The one-way audited manual transition is verified by
  `test_sap_posting_requires_permission_reference_and_records_safe_audit_truth`.

## Evidence

- RED/GREEN: `evidence/terminal-logs/direct-repayment-tracer-{red,green}.log` and
  `direct-repayment-behaviors-{red,green}.log`.
- Final focused gates: `evidence/terminal-logs/final-focused-gates.log`.
- Reverse consumers: `evidence/terminal-logs/focused-regression-green.log`.
- PostgreSQL twice-run: `evidence/terminal-logs/postgresql-acceptance-run-{1,2}.log`.
- API/database proof: `evidence/api-response-examples.md` and `evidence/database-proof.md`.

## Substantive Risks and Decisions

- High financial risk is controlled by transaction locks, service/database uniqueness, and real
  PostgreSQL races; see `risk-assessment.md`.
- A-138 records weekday-only next-working-day calculation because the source has no holiday calendar.
- The persisted enum includes the already source-defined subsidiary vocabulary so 010E can deepen
  the same owner later; this slice exposes and accepts only direct RTGS/NEFT behavior.

## Recommended Next Action
Run Ralph's independent complete gates, declared PostgreSQL acceptance twice, coverage, frontend
gates, migration/protected-path/diff checks, then let the orchestrator update state and commit.
