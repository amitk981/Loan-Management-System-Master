# Execution Plan

Selected slice: `010E4-rate-effective-date-and-write-boundary-closure`

## Boundary and impact map

- Rate owner: harden `configurations.models.InterestRateConfig` and
  `configurations.modules.interest_rate_configuration` so ordinary ORM/service/API writes cannot
  manufacture or mutate an approved row, while the canonical activation transaction retains one
  narrow internal transition.
- Database: add one configurations migration for coherent active/proposed approval evidence. No
  historical business values will be rewritten.
- Loan projection: expose explicit-date rate/current-projection decisions through the public rate
  facade; activation records future history/notices without publishing a future rate early, and a
  separately callable due-date convergence operation updates the mutable projection idempotently
  with audit evidence.
- Reverse consumers: replace changed loan/interest imports of private configuration models with the
  public decision/facade where this slice's rate-to-loan boundary requires it.
- Permanent tests: add the exact four-test
  `RateEffectiveDatePostgreSQLAcceptanceTests` contract and public builders. Preserve existing
  010E3 replay, consumption, overlap/gap, history, and consumer behavior.
- API/frontend: no new endpoint or frontend scope. Existing create/activate API remains the public
  mutation surface and must retain standard error/replay envelopes.

## TDD tracer bullets

1. RED then GREEN: ordinary create/bulk-create/bulk-update/queryset/model/delete paths cannot create
   or mutate active rate truth, and database constraints reject incoherent active evidence.
2. RED then GREEN: future activation leaves today's loan projection unchanged; explicit-date
   resolution selects the correct rate on each side of the boundary.
3. RED then GREEN: the public due-date convergence operation updates only when due, is idempotent,
   and retains audit/history coherence without changing frozen activation replay bytes.
4. RED then GREEN: exact/changed-key and competing-successor PostgreSQL races preserve a single
   immutable contiguous decision using public fixture builders/facades.

Each RED and GREEN command will use
`/Users/amitkallapa/LMS/.ralph/venv/bin/python` and be retained under
`evidence/terminal-logs/`, with the exact permanent test selector and explicit exit status.

## Verification and evidence

- Run focused configurations/servicing-owner tests and the exact PostgreSQL acceptance class twice
  when the configured database is available.
- Run reverse-consumer tests for loan-account reads plus invoice/accrual behavior, then backend
  `manage.py check` and `makemigrations --check`. Do not run the complete backend suite/coverage;
  the orchestrator owns that authoritative gate.
- Run frontend lint, tests, typecheck, and build only if a frontend file is affected (none planned).
- Produce `review-closure-evidence.md`, `risk-assessment.md`, `review-packet.md`, and
  `final-summary.md`; set the packet result exactly to `Ready for independent validation`.
