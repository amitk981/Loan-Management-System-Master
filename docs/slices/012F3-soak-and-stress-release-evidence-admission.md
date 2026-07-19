# Slice 012F3: Soak and Stress Release Evidence Admission

## Status
Not Started

## Runtime Capabilities
- `none`

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Origin
The final queue review found that 012F2 could finish after defining bounded probes while the mandatory
section-24.3 environment runs remained pending. This terminal admission prevents that false green.

## Goal
Admit a fresh, commit-bound, tamper-evident environment bundle proving every source-required soak and
stress scenario after deployment smoke, or fail closed before the final UAT packet.

## User Value
The owner cannot receive a release-ready result based only on fast functional tests or local probe
definitions when sustained load, restart recovery, storage, queue, audit, and connection pressure are
still unproven.

## Depends On
- 012H

## Source References
- `docs/source/test-plan.md` §24.3 Soak and Stress Tests
- `docs/source/test-plan.md` §24.1–24.2 performance targets and PERF-001–010
- `docs/source/implementation-roadmap.md` R8-E5 and R8-AC-004
- `docs/source/deployment-ops.md` release evidence, monitoring, worker, Redis, database, and rollback
- `docs/slices/012F2-performance-readiness-evidence.md` trusted command and evidence schema
- `docs/slices/012H-deployment-readiness-and-smoke-checks.md` candidate environment/commit identity

## Screens Involved
None. This is an evidence-admission gate, not a dashboard or replacement visual proof.

## Frontend Scope
None.

## Backend/API Scope
- Implement/reuse a non-mutating admission command for the 012F2 evidence schema. It reads bounded
  result summaries and raw-result hashes; it does not create a test-only production endpoint or
  reinterpret a failed scenario.
- Require all seven §24.3 results: four-hour sustained workflow usage, large document volume, large
  audit table, heavy export queue, worker restart during task, Redis restart with no system-of-record
  data loss, and database connection pressure with controlled degradation.
- Bind the bundle to the exact release-candidate commit/environment produced after 012H, with tool
  versions, dataset/load manifest, start/end times, actual elapsed duration, thresholds, counts,
  percentiles/throughput where applicable, result, and SHA-256 hashes.
- Reconcile the bundle with all §24.1 targets and PERF-001–010 results from 012F2. A local smoke,
  synthetic elapsed time, copied older result, environment mismatch, or success-only excerpt cannot
  substitute for the source-required run.

## Validation Rules
- Every required entry is exactly once, passed, fresh, hash-valid, and tied to the candidate commit;
  unknown entries do not compensate for missing ones.
- The sustained-workflow entry proves at least four real elapsed hours. Clock reversal, overlapping
  fragments, or caller-supplied duration without trusted timestamps fails.
- Missing infrastructure, pending execution, approved skip/deferral, partial pass, threshold breach,
  restart data loss, uncontrolled degradation, stale commit, or tampering produces non-zero status.
- Evidence contains no credentials, tokens, live PII, unrestricted URLs, or raw sensitive fields.

## Test Cases
- Admission rejects each missing scenario, four-hour duration shortfall, stale/wrong commit, wrong
  environment, changed hash, duplicate/unknown-only entry, skip/deferral, failed threshold, worker or
  Redis recovery loss, uncontrolled database pressure, and sensitive evidence.
- A complete synthetic fixture tests parser/validation behavior only and is visibly non-admissible as
  release evidence; the green admission uses the real environment bundle.
- Reverse-consumer checks keep 012F2 commands/schema and 012H candidate identity unchanged.

## Evidence Required
The admitted environment summary; raw-result hash manifest; exact candidate commit/environment;
dataset/load/tool manifest; start/end/duration proof; scenario/threshold reconciliation; admission
negative tests; redaction scan; configured full gates.

## Non-Goals
Running a shortened substitute, altering thresholds, approving a deferral, product repair, live-data
load generation, deployment, owner signoff, or promotion to `main`.

## Risk Level
High

## Acceptance Criteria
- All seven section-24.3 scenarios have fresh, passing, hash-valid environment evidence for the exact
  release candidate, including four real sustained hours and restart/data-integrity outcomes.
- Missing, pending, skipped, stale, partial, synthetic, failed, or tampered evidence blocks 012I.
- No threshold, security, correctness, or source requirement is weakened to obtain admission.

## Done Checklist
- [ ] Admission validator tests written first
- [ ] Exact environment/candidate identity verified
- [ ] Seven section-24.3 results and 012F2 reconciliation admitted
- [ ] Hash, duration, failure, and redaction negatives passed
- [ ] Full gates and risk review passed
- [ ] Commit delegated to the orchestrator after gates
