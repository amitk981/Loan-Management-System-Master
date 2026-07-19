# Execution Plan

Selected slice: 009L6-epic-009-owner-selector-equivalence-and-matrix-closure

## Boundary and permissions

- Edit only the Epic 009 owner modules, collection coordinators, focused backend tests/migration,
  working API contract if its public description changes, and this run's evidence artifacts.
- The permitted paths are `sfpcl_credit/**`, `docs/working/**`, and
  `.ralph/runs/2026-07-19_135000_normal_run/**`; no protected file, `docs/source/**`, frontend
  styling/component, Epic 010 behavior, or hosted browser evidence is in scope.
- Keep account/application/member/customer-code edges and role/object/maker-checker/mutation
  authority behind their existing owners. Do not add SAP-posting confirmation authority.

## Deep-module interface and public behaviors

1. Give Loan Account creation/SAP completion, S36, S37, combined Senior Finance, and pending-CFC
   collections one owner-level eligibility interface each. The interface owns exact queryable
   identities, deterministic ordering, count, and bounded windows; public scalar/projector paths
   consume the same decision rather than re-checking a stricter private Python copy.
2. Make selection total: any selected identity projects exactly one row in the same transaction.
   Lifecycle, SAP send/completion, initiation, task, audit/workflow, actor/team, readiness,
   transfer, file-integrity, and aggregate drift is excluded before count/offset/limit.
3. Preserve database pagination and portfolio-independent query ceilings for 1/21/101 mixed
   portfolios and first/middle/last/out-of-range pages. Do not restore overscan or scan a complete
   portfolio in Python.
4. Prove row/count/action/mutation/nondisclosure parity through public HTTP or public owner-module
   interfaces, including independent 400/403/409 responses. Replace the private portal-helper test
   with an HTTP assertion and remove duplicate PostgreSQL discovery inheritance.
5. Make `pgcrypto` setup ownership-safe: record whether this app created the extension, reverse
   only app-owned setup, and prove exact SHA-256 selector execution in the declared four-test
   PostgreSQL acceptance label while retaining SQLite compatibility.

## RED -> GREEN tracer bullets

1. Productize the four architecture-review probes, one public behavior at a time, and save the
   failing HTTP outputs. Deepen the corresponding owner selector/scalar interface until each probe
   is green without projection-time filtering.
2. Add table-driven public regressions for the remaining scalar evidence fields and adjacent drift
   runs, then make each owner interface exact before adding the next behavior.
3. Add bounded 1/21/101 page/order/query-ceiling cases and combined-branch boundaries; make every
   count/window pair consume one owner interface.
4. Add action/mutation, denial/nondisclosure, consumer, and 400/403/409 matrix assertions only where
   existing public tests do not already execute the contract; keep each tracer green before moving
   on.
5. Add PostgreSQL extension-ownership/SHA-256 acceptance tests and migration changes last, retaining
   a secondary SQLite-focused green run.

## Verification and evidence

- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command and retain focused
  RED/GREEN output in `evidence/terminal-logs/`.
- Run impacted backend labels, reverse-consumer labels, Django `check`, and
  `makemigrations --check`; do not run the complete backend suite or coverage.
- Run `git diff --check`, inspect stats/targeted hunks, then complete `risk-assessment.md`,
  `review-packet.md`, and `final-summary.md`. Ralph alone owns changed-files/state/progress/status,
  commit, merge, and push.
