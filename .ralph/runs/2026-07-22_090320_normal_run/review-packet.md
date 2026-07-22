# Review Packet: 2026-07-22_090320_normal_run

## Result
Ready for independent validation

## Slice
011A-default-case-opening

## Delivered

- Added the `defaults` owner, `DefaultCase` model, one migration, and the deep
  `DefaultWorkflow.open_if_missed_repayment` interface.
- Added POST open plus scoped GET detail/list endpoints with standard envelopes, exact filters,
  bounded pagination, and server-derived `available_actions`.
- Added exact Credit Manager opening authority, scoped reads for Credit/CS/persisted required
  approvers/Auditor, safe audit evidence, canonical workflow evidence, replay convergence, and
  database uniqueness for one missed obligation.
- Updated the durable API contract and permission catalogue; no frontend or unrelated epic work was
  touched.

## Traceability

- The source doc says a missed scheduled principal repayment opens a case and the three-month grace
  starts on its due date (`product-requirements.md` §11.26; `api-contracts.md` §§35.1–35.3). The code
  derives the missed state from locked loan-owned schedule/allocation facts and performs calendar
  month arithmetic, verified by
  `test_missed_scheduled_principal_opens_one_audited_case` and
  `test_allocated_principal_obligation_does_not_open_a_case`.
- The source doc says the defaults owner exposes `DefaultWorkflow.open_if_missed_repayment` and hides
  missed-principal detection/audit (`codebase-design.md` §18.3). The code keeps HTTP views thin over
  that interface, verified through the public HTTP behavior tests.
- The source doc says `defaults.case.open` belongs to Credit Manager and default stage changes are
  audited (`auth-permissions.md` §§12.10, 20.3, 25.8). The code requires permission plus role and
  atomically writes `default.case_opened` plus one workflow event, verified by the success,
  permission, replay, Auditor, and PostgreSQL race tests.
- The source data model retains loan/member/trigger/due/grace/status facts (`data-model.md` §21.1).
  The migration stores those facts with indexes and bounded/unique constraints; migration sync and
  isolated forward/reverse/reapply evidence are green.

## Validation evidence

- RED: `evidence/terminal-logs/red-01-missed-principal-open.log` fails at the missing defaults owner.
- GREEN focused API: `evidence/terminal-logs/focused-default-api-final2.log` — 6/6 passed.
- GREEN PostgreSQL acceptance: `evidence/terminal-logs/postgres-race-final2.log` — exact declared
  class, 1/1 passed against PostgreSQL.
- GREEN reverse consumers: `evidence/terminal-logs/reverse-consumers.log` — DPD, repayment allocation,
  and schedule/ledger, 26/26 passed.
- GREEN permission catalogue regression: `evidence/terminal-logs/catalogue-seed-regression.log` —
  18/18 passed and repeated seeding remained stable.
- GREEN system/migrations: `django-check-final.log`, `migration-sync-final2.log`, and
  `migration-forward-reverse-reapply.log`.
- Response examples: `evidence/api-response-examples.md`.

## Self-review

- One migration, no dependencies, no protected/source/frontend edits, and no changes outside the
  selected vertical slice/API contract.
- The open response follows source §35.1 exactly plus required `available_actions`; richer retained
  facts are exposed only by detail/list.
- No unresolved correctness, security, financial-integrity, or scope finding remains from focused
  review. Independent validation remains authoritative.

## Recommended Next Action
Run Ralph's independent schema/routing classification, backend gate, and review; commit only if all
independent checks pass.
