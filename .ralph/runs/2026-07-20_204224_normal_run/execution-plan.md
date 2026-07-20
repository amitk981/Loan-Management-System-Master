# Execution Plan

Selected slice: CR-014-rate-current-date-terminal-finalizer

## Boundary

Implement only the canonical effective-rate current-date owner and the backend read/interest seams
named by CR-014. No frontend, rate formula, scheduler-calendar policy, or retained financial history
rewrite is in scope.

## Public behaviors and TDD sequence

1. Add a public regression proving the obsolete caller-supplied future-date convergence seam cannot
   publish a successor early. Retain the failing RED log, then introduce a server-date-only account
   owner with immutable idempotency evidence and make the test GREEN.
2. Add a before/date/after public matrix proving the resolver, stored Loan Account projection,
   collection count/row, and detail projection agree; make stale-but-owner-valid accounts selectable
   before convergence so they cannot disappear from collection counts.
3. Add public reverse-consumer tests proving invoice, accrual, and capitalisation use the same
   effective version decision at the boundary without changing their arithmetic.
4. Add exact replay, changed-key, cross-account-key, repeated portfolio run, and competing successor
   tests. Implement only the durable decision/locking behavior needed by each test.
5. Add exactly five PostgreSQL acceptance tests under the slice-declared class, covering one-account
   and bounded-portfolio due-date races, stale projection visibility, replay, and competing versions.
6. Wire a bounded, server-date-only owner callable into the existing Celery task runtime and the
   list/detail selection path; do not invent a scheduler cadence.

## Expected implementation surface

- `sfpcl_credit/configurations/modules/interest_rate_configuration.py`: canonical current-date
  owner, bounded portfolio selection, replay/conflict rules, and coherent selector annotation.
- `sfpcl_credit/configurations/models.py` plus one migration: immutable projection-decision evidence
  with database uniqueness for idempotency/account-version races.
- `sfpcl_credit/processes/tasks.py`: production runtime entry without a new cadence.
- Loan-account list/detail composition: converge only the bounded selected window while preserving
  collection identity/count for stale projections.
- Focused permanent tests and public synthetic builders only where needed.

## Gates and retained evidence

- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for all backend commands.
- Save exact RED and GREEN selector logs in `evidence/terminal-logs/`, including command, output, and
  explicit exit code.
- Run focused reverse-consumer, permission, scheduler/task, and PostgreSQL-declared tests; run
  `manage.py check` and `makemigrations --check`. Do not run the complete backend suite locally.
- Complete `review-closure-evidence.md`, `risk-assessment.md`, `review-packet.md`, and
  `final-summary.md`, then run the exact review-closure validator until PASS.
