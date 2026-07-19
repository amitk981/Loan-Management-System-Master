# Execution Plan

Selected slice: `010D-bank-statement-matching-unmatched-receipts`

## Boundary

- Implement the backend-only statement-import, statement-line, automatic evidence-match,
  reconciliation-list, and authorised manual-match capability owned by 010D.
- Reuse the existing `loans` servicing owner, document metadata/storage seam, standard API
  envelopes, role/permission catalogue, audit model, and loan-object scope rules.
- Do not create or allocate repayments, change account/schedule/ledger balances, mark SAP posted,
  add a bank feed/OCR/fuzzy matcher, introduce split matching, or change frontend code.

## Permission and Safety Check

- Intended edits are limited to allowed `sfpcl_credit/**`, `docs/working/**`, and this run's
  `.ralph/runs/2026-07-19_233905_normal_run/**` evidence paths.
- Protected configuration, orchestration scripts, git metadata, `docs/source/**`, and mechanical
  state/progress/status files remain unchanged.
- The slice has standing High-risk approval and no matching `[revoked]` entry.

## Behavior-First TDD Sequence

1. Add one public API tracer test for a deterministic synthetic CSV upload and singular exact
   reference/amount/date/account match. Save the expected initial route/model failure as RED, then
   add the minimum models, migration, parser/service, permission catalogue entries, URL/view, and
   serialization needed for GREEN.
2. Add public API cases incrementally for idempotent upload replay, deterministic line ordering,
   malformed/forbidden files, unmatched and exception reason codes, ambiguous candidates,
   permission denial, and loan-object scope nondisclosure; complete the bounded validation and list
   behavior one RED→GREEN step at a time.
3. Add public API behavior for authorised manual match: mandatory chosen receipt and reason,
   immutable actor/audit evidence, one-to-one line/receipt ownership, safe response projection, and
   explicit exception allocation state without moving money. Add match-conflict and retained-link
   receipt projection coverage.
4. Add reverse-consumer assertions proving receipt/allocation/account/schedule/ledger state is
   unchanged by evidence-only operations, plus the declared PostgreSQL concurrent double-match test
   proving one winner/one retained counterpart.

## Contract and Data Shape

- Add bounded statement import/line provenance, source file identity, SFPCL bank-account label,
  transaction/value dates, amount, bounded narration/reference, parse/match status and safe reason
  codes, timestamps, and database uniqueness/one-to-one constraints.
- Document upload/list/match API routes, exact request fields, response/error behavior,
  idempotency, permissions, scope, and non-financial guarantees in
  `docs/working/API_CONTRACTS.md`.
- Use synthetic, non-sensitive CSV fixtures only; never expose raw statement content in audits,
  errors, or ordinary logs.

## Focused Validation and Evidence

- Run focused tests with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, saving exact RED and GREEN
  output (including explicit exit codes) under `evidence/terminal-logs/`.
- Run the declared PostgreSQL test locally if the configured test database is reachable; otherwise
  retain the exact test and report the sandbox limitation for orchestrator acceptance.
- Run impacted 010A–010C reverse-consumer tests, `manage.py check`, and
  `manage.py makemigrations --check`; do not run the complete backend suite or coverage.
- Run frontend lint/typecheck/tests/build only if a backend contract unexpectedly requires a
  frontend edit; none is planned for this backend-only slice.
- Finish `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; set the review result
  exactly to `Ready for independent validation` only after focused evidence is green.
