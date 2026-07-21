# Execution Plan

Selected slice: `010MA-servicing-account-and-repayment-frontend-wiring`

## Scope and seams

- Work only on the staff S43-S46 account, schedule, ledger, direct-repayment, bank-statement
  exception, and subsidiary-reconciliation surfaces assigned to 010MA.
- Put transport/envelope, pagination, Money projection, authenticated-error, and idempotency handling
  behind one shared servicing module interface. Pages consume retained backend projections and do not
  calculate balances, allocation, matching, or permission decisions.
- Reuse the existing Loan Account 360, Repayments Hub, RepaymentLedger, alert, tabs, modal, table, and
  pagination patterns without introducing styling or visual-system changes.
- Add a narrow backend read projection only if repository inspection proves S45 cannot be rendered
  from existing canonical endpoints. Any backend/business change follows strict RED -> GREEN TDD.

## Permissions and protected scope

- `.ralph/permissions.json` permits edits under `sfpcl-lms/src/**`, `sfpcl-lms/e2e/**` through the
  project tree, `sfpcl_credit/**`, `docs/working/**`, and this run's `.ralph/runs/**` artifacts.
- Do not edit protected orchestrator/configuration/source paths, mechanical state/progress/HANDOFF,
  or the selected slice status. Do not run git add/commit/push.

## TDD sequence

1. Inspect existing authenticated transport, canonical servicing routes/serializers, reverse
   consumers, current page routing, and retained failed-run requirements evidence. Confirm whether a
   backend projection is actually missing and map exact public interfaces.
2. RED -> GREEN: add focused servicing transport tests for standard envelopes, deterministic
   pagination, Money strings, validation/401/403 propagation, and one stable Idempotency-Key reused
   only for the same attempted mutation/replay.
3. RED -> GREEN: add Loan Account 360/RepaymentLedger behavior tests, then wire schedule and ledger
   tabs to canonical paginated backend values and backend totals, including loading, empty, error,
   unauthorized, and page controls.
4. RED -> GREEN: add Repayments Hub behavior tests, then replace all mocks and client money logic
   with canonical account, posting/allocation, statement-exception, and subsidiary-reconciliation
   projections. Prove validation/duplicate/replay behavior, backend allocation explanation, success,
   refresh, and permission-gated mutation visibility.
5. If S45 needs a backend read addition, write and save an exact failing backend test first, add the
   smallest owner-aligned projection, update API_CONTRACTS, and save focused GREEN/reverse-consumer
   evidence using `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
6. Add the declared real-auth Playwright contract and screenshot assertions for
   `servicing-ledger.png` and `direct-repayment-posting.png`; collect/execute locally as sandbox
   capabilities allow, without fabricating screenshots.

## Verification and evidence

- Save every focused RED and GREEN command with explicit exit status under
  `evidence/terminal-logs/`, plus static mock/auth audits and any backend reverse-consumer result.
- Run impacted frontend tests throughout, then frontend typecheck, lint, build, and the relevant
  Playwright collection/non-browser feedback. Run Django check/migration consistency and only focused
  backend labels if backend code changes; do not run the complete backend suite or full coverage.
- Inspect diff stats and targeted hunks before handoff; remain below the 1,450-line resplit warning
  and the configured 2,000-line hard limit.
- Complete `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; set the review-packet
  Result exactly to `Ready for independent validation` only after all locally available gates pass.
