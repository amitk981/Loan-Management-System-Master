# Epic 012 Digest: Reports, Exports, Hardening, Regression, and UAT

Use this digest with the selected `012*` slice only. It is a bounded execution aid, not a
replacement for the cited source sections. `docs/source/` remains read-only.

## Delivery order and boundaries

- Main reporting chain: `012A -> 012B -> 012C -> 012D`; `012DA` wires its frontend.
- Hardening chain starts at `012E`; `012E2`, `012E3`, `012EA`, and `012F` retain their
  declared dependencies. `012EB` follows `012EA`; `012G -> 012H -> 012I` closes UAT.
- Reuse existing domain services/selectors. Reports are read models; they must not mutate
  loan, approval, finance, compliance, or audit records.
- Keep each implementation within its named capability. Do not absorb later frontend,
  security, UAT, deployment, or owner-only release work into an earlier slice.

## Shared source-backed invariants

1. Reports use system-of-record data, support filters/sorting, and reconcile to source
   records. The critical catalogue includes operational, financial, risk, compliance, and
   restricted audit reports. (`product-requirements.md` 11.31;
   `implementation-roadmap.md` 17.3; `test-plan.md` 22.1)
2. Report APIs are role/object scoped and paginated. A report selector owns each query;
   views do not duplicate cross-domain business logic. Heavy reports may use read-optimised
   or materialized views. (`api-contracts.md` 8, 40; `codebase-design.md` 33;
   `technical-architecture.md` 21)
3. Screen read permission never implies export permission. `reports.export` is required;
   sensitive exports also require separate authority and a reason. PAN, Aadhaar, bank,
   cheque, and BO-account values are masked by default and permitted columns only are
   emitted. (`security-privacy.md` 32.2; `product-requirements.md` 11.31;
   `auth-permissions.md` 11.1, 12.13, 33.3)
4. Export request and download are audited; links expire; large or >5-second exports are
   asynchronous and status tracked. Retries must not create duplicate jobs/files.
   (`test-plan.md` 22.2, 24.1; `api-contracts.md` 40.7-40.8;
   `codebase-design.md` 33.1, 33.3)
5. Audit logs are append-only, sanitised, long-retained, and non-editable. Audit reads and
   exports require explicit permission; the explorer is read-only and must not expose raw
   sensitive values. (`product-requirements.md` 11.32; `security-privacy.md` 24;
   `screen-spec.md` S74)
6. Dashboards are role-specific summaries of existing source records, never a second system
   of record. Links/filters must reach the corresponding scoped lists. (`api-contracts.md`
   43; `information-architecture.md` 9.1; `technical-architecture.md` 21.1-21.2)
7. Backend permissions remain authoritative even when the UI hides actions. Auditor and
   management access is read-only. (`api-contracts.md` 44; `auth-permissions.md` 19.1;
   `test-plan.md` 18.2)
8. Production readiness requires passing full regression, security/privacy, financial,
   audit, integration, operational, and UAT gates; exceptions need explicit acceptance.
   (`implementation-roadmap.md` 17.6; `test-plan.md` 27.3, 28, 33-34)

## 012A — Report API foundation

- Establish the `reports` boundary and report registry/selector contract. Implement the six
  source-contracted GET endpoints in `api-contracts.md` 40.1-40.6: application pipeline,
  documentation readiness, disbursement pending, loan portfolio, DPD, and compliance.
- Use the exact source filters (`from_date`, `to_date`, `status`, `stage`, `as_of_date`,
  `sop_bucket`, `financial_year`), standard pagination/envelope, deterministic ordering,
  and role/object scoping. Reject malformed dates/buckets; never silently ignore filters.
- Reconcile selector totals/rows against seeded source-domain records. No exports, files,
  report UI, new business calculations, or materialized-view optimisation in this slice.
- Reverse consumers: dashboard and domain selector tests; permissions; API pagination;
  empty/no-access cases. Evidence includes endpoint examples and reconciliation assertions.

## 012B — Register exports

- Implement the `POST /api/v1/reports/exports/` and
  `GET /api/v1/reports/exports/{id}/` contract plus persisted job lifecycle
  `queued/running/completed/failed`; support source formats required by the selected
  catalogue and fail unsupported report/format combinations explicitly.
- Key idempotency by actor + report code + canonical filters + format + idempotency key.
  A retry returns the existing job. Files contain the applied filters, generator, and
  generation time; download grants expire and storage retention is explicit.
- Cover the high-priority registers in the existing report catalogue without rebuilding
  their domain queries. No sensitive unmasking—that is owned by `012C`.
- Reverse consumers: report selectors, job/task restart, storage/signed URL, audit adapter,
  and frontend status contract. Prove worker retry cannot duplicate jobs/files.

## 012C — Export masking and permission checks

- Enforce `reports.export` separately from report read. Require the source-defined
  `reports.export_sensitive` permission plus a mandatory nonblank reason for unmasked permitted
  columns; otherwise mask PAN/Aadhaar/bank/cheque/BO account and exclude forbidden columns.
- Classify each exported report per `security-privacy.md` 32.3. Audit request, denial,
  sensitive grant, and download without placing raw secrets in audit/log fields. Expired or
  cross-user/cross-scope grants fail closed.
- Cover `EXP-001` through `EXP-010` and sensitive-data regressions `SEC-PII-009`,
  `SEC-WEB-009`, and audit-export restriction. No UI work or unrelated reveal redesign.
- Reverse consumers: ordinary report reads remain unchanged; audit export is restricted;
  signed URLs cannot bypass actor scope; masked API/display contracts do not regress.

## 012D — Audit explorer

- Add filterable, paginated, deterministic read endpoints for audit logs, workflow events,
  and version history per `api-contracts.md` 42 and S74 filters: date, actor/user, role,
  entity/reference, action/module, exception/approval, and linked record where supported.
- Project sanitised before/after values and actor role/team snapshot; never expose secrets or
  unrestricted raw payloads. Enforce audit permissions and object scope; do not add update or
  delete paths. Reuse the existing immutable audit model/recorder.
- Reverse consumers: existing audit creation tests, auditor read-only views, sensitive reveal,
  restricted download, and export events. Prove mutation methods are 405/403 and query/export
  access cannot reveal a record outside scope.

## 012DA — Reports/exports/audit frontend

- Follow the already concrete slice: wire S69/S74 and register export actions to `012A-012D`,
  remove owned mocks, display job and permission states, and save browser evidence.
  (`screen-spec.md` S69, S74; `information-architecture.md` 16, 18)

## 012E — Operational dashboard hardening

- Complete role-backed `GET /api/v1/dashboard/` plus sanction committee, compliance, and
  treasury variants in `api-contracts.md` 43. Cards derive from existing selectors and carry
  stable code/label/count/link values; role context cannot be supplied by the caller.
- Wire `Dashboard.tsx` to real APIs and preserve source role cards for Credit, Compliance,
  CFO, Treasury, Accounts, and CS. Include loading, empty, error, forbidden, and refresh states.
- Measure query count/latency and avoid unbounded per-card queries; target dashboard <3 seconds
  under the test-plan fixture/load profile. Tasks remain the `012EA/012EB` responsibility.
- Reverse consumers: navigation link filters, report/compliance/finance selectors, role switch,
  cross-role leakage, frontend dashboard tests, and current empty `tasks[]` compatibility.

## 012E2 / 012E3 — Production isolation and encryption

- Follow the concrete slice files. Preserve development tracer evidence while proving all
  demo/tracer surfaces absent in production (`012E2`). Then separate and version field keys,
  rotate with reconciliation, and preserve existing reveal/CDSL seams (`012E3`).
  (`security-privacy.md` 15, 30; `deployment-ops.md` 6, 9-10)

## 012EA / 012EB — Task engine and inbox

- Follow the concrete slice files. `012EA` owns persisted, idempotent workflow tasks and APIs;
  `012EB` owns S03 wiring and final staff mock removal. Do not merge compliance tasks into the
  workflow task resource. (`screen-spec.md` S03; `api-contracts.md` 8, 43.1)

## 012F — Security/privacy regression checks

- Build a deterministic release-hardening lane over implemented controls, not a second auth or
  encryption subsystem. Cover `test-plan.md` 18 and `security-privacy.md` 37: authentication,
  object/role authorisation, maker-checker/conflict, masking/reveal, restricted download,
  export, injection/XSS/upload/CORS/error/log leakage, immutable audit, and rate limits.
- Add production-settings assertions for secure cookies/HTTPS/HSTS/hosts/CORS/debug, secret and
  dependency scans using repository-supported tools, and a machine-readable pass/fail summary.
  Tests must use safe fixtures and redact findings.
- Reverse consumers: login/session/permission suites, every sensitive field adapter, document
  download, export, audit, production demo isolation, and field-key checks. Do not fix unrelated
  product defects silently; record a blocking finding/corrective slice under Ralph policy.

## 012G — Critical E2E/UAT smoke scenarios

- Automate the smallest cross-module tracer set proving the critical UAT paths: standard loan
  through disbursement; approval threshold/exception; direct and subsidiary repayment plus
  interest/DPD; default/recovery/closure; compliance; reports/exports/audit; and RBAC/masking
  negative journey. Map each to `UAT-001..026` rather than duplicating every unit test.
- Use seeded deterministic data and public UI/API boundaries. Assert business state, ledger or
  evidence, permissions, and audit—not merely HTTP 200 or visible text. Keep retry-safe cleanup.
- Produce a scenario-to-source/test/evidence matrix and runtime. No hosting, live provider calls,
  owner signoff, or broad defect repair in this slice.

## 012H — Deployment readiness

- Follow the concrete slice: liveness/readiness plus read-only `smoke_check`; no protected-path
  pipeline or hosting work. (`deployment-ops.md` 13.1, 20; `test-plan.md` 25.1)

## 012I — Final UAT review packet

- Assemble, do not manufacture, release evidence: `UAT-001..026` status and actor; regression,
  security, financial, audit, integration and ops results; report reconciliation; known defects
  with acceptance/workaround; assumptions/open decisions; rollback/backup/monitoring/support;
  and named signoff slots from `test-plan.md` 27, 33-34 and `implementation-roadmap.md` 17.5.
- Verify evidence hashes/paths and exact candidate commit. Missing or stale mandatory evidence is
  a visible `NOT READY`, never a checked box. Separate engineering readiness from owner/business
  go/no-go approval; Ralph cannot grant that approval.
- Documentation/review only. No product fixes, deployment, production migration, synthetic
  signoffs, or promotion to `main`.

## Open decisions Ralph must not invent

- `product-requirements.md` 11.31 and `implementation-roadmap.md` 17.3 require a broader report
  catalogue than the six read endpoints defined by `api-contracts.md` 40.1-40.6. `012A` owns the
  six contracted endpoints and `012B` may export already implemented register/report selectors;
  any still-unimplemented catalogue entry is a visible contract/backlog gap, not an invented route
  or a false `R8-AC-001` completion.
- `auth-permissions.md` names read permissions for application pipeline, portfolio, DPD, and
  compliance reports, but not dedicated codes for documentation-readiness or disbursement-pending
  reports. `012A` must use a bounded owning-resource read mapping and default deny; do not grant a
  generic role broader report access.
- `security-privacy.md` 32.2 and `auth-permissions.md` 33.3 define the separate permission code
  `reports.export_sensitive`, but do not assign its role grants. `012C` must use that exact code;
  unresolved role mappings default deny and must not broaden `reports.export`.
- The source requires XLSX/PDF/CSV/JSON across different descriptions but does not map every
  report to every format. `012B` must publish an explicit supported matrix and reject the rest.
- S69 names “schedule email” and “save report view”, but API contracts 40 define neither.
  Keep them out of `012A-012DA` unless separately approved; do not fake them client-side.
- `api-contracts.md` 43 gives a concrete card shape only for the Credit Manager example; the other
  role card names are descriptive in `information-architecture.md` 9.1. `012E` must publish a
  stable bounded code/link mapping and reconcile it to existing selectors without adding scope.
- Hosting, live backup/restore infrastructure, providers, migration scope, training completion,
  and business/UAT signatories remain owner/environment decisions. `012I` reports their status.
