# Execution Plan

Selected slice: `010H2-interest-calculation-payment-and-replay-owner-closure`

## Permission and boundary check

- Product edits are limited to `sfpcl_credit/**`, which is allowed by `.ralph/permissions.json`.
- Evidence edits are limited to this run folder under `.ralph/runs/**`.
- No protected/source/frontend paths will be changed.
- Dependencies `010E4` and `010H` are complete; no owner veto for `010H2` was found.
- One migration is permitted. The 2,000-line/30-file slice limits remain binding.

## Public interface and module seam

Keep the existing invoice, accrual, issuance/SAP-posting, preview, and capitalisation owner
functions as the caller interface. Add one deep as-of accounting decision behind that interface,
returning immutable segment/payment evidence and totals. Callers do not learn rate-history,
principal-movement, payment-binding, or rounding implementation details.

## TDD tracer bullets

1. RED/green AC-INT-1: annual invoice uses daily principal/rate segments across FY/leap boundaries
   and only counts interest applications belonging to that obligation.
2. RED/green AC-INT-2: monthly accrual consumes the same segmented decision and persists one
   immutable loan/month result.
3. RED/green AC-INT-3/4: cutoff payments reduce interest once; tax/fees/charges never capitalise;
   principal, account interest/total, schedule, ledger, invoice evidence, email and hard-copy task
   agree atomically.
4. RED/green AC-INT-5: generation, issuance, SAP posting, and capitalisation persist response
   snapshots; exact replay stays byte-stable after mutable delivery/provider state changes and
   changed/cross-owner keys remain zero-write conflicts.
5. RED/green AC-INT-6: approved calculation configuration and terminal evidence reject instance,
   queryset, and bulk mutation; issuance uses the frozen owner/template decision.
6. AC-INT-7: add the declared five-test PostgreSQL acceptance class for exact/changed-key races,
   provider outcomes, and reverse-consumer coherence. Run it twice when PostgreSQL is available.

Each cycle adds one public behavioral test, captures a failing focused run under
`evidence/terminal-logs/`, implements only enough to pass, then captures the green run with an
explicit exit status.

## Expected impact map

- `sfpcl_credit/interest/modules/`: as-of decision and bounded owner integration.
- `sfpcl_credit/interest/models.py` plus one migration: immutable segment/payment/response and
  durable hard-copy evidence needed for retained financial truth.
- `sfpcl_credit/tests/`: permanent invoice/accrual/capitalisation owner and five-test PostgreSQL
  acceptance coverage.
- Existing loan repayment/schedule/ledger and rate-history models are read through their public
  retained evidence; their business rules are not changed.

## Verification and evidence

- Focused red/green Django labels with `/Users/amitkallapa/LMS/.ralph/venv/bin/python` only.
- Focused reverse-consumer suites for invoice, accrual, capitalisation, loan-account reads, and
  servicing PostgreSQL acceptance.
- `manage.py check` and `makemigrations --check`; do not run the complete backend suite/coverage.
- Save `review-closure-evidence.md`, `risk-assessment.md`, `review-packet.md`, and
  `final-summary.md`; finish the packet result with exactly `Ready for independent validation`.
