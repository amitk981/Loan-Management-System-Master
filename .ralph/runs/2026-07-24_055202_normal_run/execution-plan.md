# Execution Plan

Selected slice: 012C-export-masking-and-permission-checks

## Scope

Implement only the backend export-authorisation hardening selected by slice 012C. Preserve the
012B request/status contracts and existing report selectors and formats. Do not add frontend work,
new report definitions, role grants, or general sensitive-reveal changes.

## Permissions and Safety

- Product edits are limited to `sfpcl_credit/**`.
- Contract/assumption documentation, if required, is limited to `docs/working/**`.
- Run evidence is limited to `.ralph/runs/2026-07-24_055202_normal_run/**`.
- `docs/source/**`, protected workflow/configuration files, orchestrator-owned state/progress,
  slice status, and mechanical handoff facts will not be edited.
- No dependency installation, git staging, commit, or push will be attempted.

## Public Interface and Deep Module Seam

Retain the 012B export request, job-status, generation, retry, and download interfaces. Concentrate
report read authority, `reports.export`, object/team scope, requested/permitted columns,
classification, sensitive authority/reason, masking, expiry, and download re-authorisation behind
one central export-policy interface used at request, file generation, and access time. Tests will
exercise observable API/job/file/audit behaviour rather than policy implementation details.

## TDD Behaviour Sequence

1. Inspect the 012B export module, models, permissions, audit recorder, masking helpers, and focused
   tests; map existing public interfaces and supported report/format matrix.
2. RED/GREEN tracer: an actor without `reports.export` cannot queue an export and receives a
   sanitised denial audit.
3. RED/GREEN incrementally: report-read and object/team scope are independent prerequisites;
   requested columns are server-allowlisted, forbidden columns omitted, and unknown policy denies.
4. RED/GREEN incrementally: PAN, Aadhaar, bank account, cheque, and BO-account families are masked
   in every supported format by default.
5. RED/GREEN incrementally: unmasked permitted columns require exact
   `reports.export_sensitive` authority plus a nonblank reason; bulk KYC and audit export retain
   their stricter permissions; no new role receives a grant.
6. RED/GREEN incrementally: generation, status, and download re-check requesting actor/scope,
   permission revocation, expiry, guessed/cross-user/cross-team access, and signed-link possession.
7. RED/GREEN incrementally: request, denial, sensitive grant, generation outcome, download,
   expired/revoked access, and unusual attempt rate are immutable and sanitised; jobs, URLs, logs,
   and audit payloads contain no raw sensitive values.
8. Add reverse-consumer coverage for filter equivalence, async/idempotent retry, generated-by/time,
   retention, ordinary report reads, existing reveal/download audit, and audit sanitisation.

Each backend behaviour follows one failing focused test, captured RED output, minimal implementation,
and captured GREEN output before the next behaviour. Existing helpers and infrastructure will be
reused.

## Verification and Evidence

- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.
- Run focused export tests throughout; do not run the complete backend suite or coverage lane.
- Run Django `check` and `makemigrations --check`; run any directly impacted focused regressions.
- Save RED/GREEN logs, permission/classification matrix, parsed masked/authorised format evidence,
  denial/expiry examples, sanitised audit evidence, and a no-secret scan under this run folder.
- Inspect changed-file/line limits and targeted diffs, then complete `risk-assessment.md`,
  `review-packet.md`, and `final-summary.md`. Set the review result exactly to
  `Ready for independent validation`.
