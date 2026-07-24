# Slice 012F2: Performance Readiness Evidence

## Status
Complete

## Runtime Capabilities
- `localhost-e2e-server`

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Origin
Owner-chat source-coverage audit on 2026-07-19 found PERF-001 through PERF-010 and the applicable
soak/stress scenarios had no complete executable owner before UAT.

## Goal
Provide a repeatable, environment-bound performance lane that measures every source scenario against
recorded thresholds and fails visibly when a mandatory scenario is absent or regresses.

## User Value
The owner receives measured readiness evidence for interactive, batch, export, and recovery behavior
instead of treating functional green tests as proof of capacity.

## Depends On
- 012F

## Source References
- `docs/source/test-plan.md` sections 24.1 through 24.3, PERF-001 through PERF-010
- `docs/source/implementation-roadmap.md` R8-E5 and R8-AC-004
- `docs/source/screen-spec.md` non-functional response-time requirements
- `docs/source/deployment-ops.md` monitoring, worker, database, and release-evidence requirements
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md`

## Prototype Reference
- Existing dashboard, search, Loan Account 360, approval, disbursement, reports, and audit routes.

## Screens Involved
Existing critical screens only; no visual redesign.

## Frontend Scope
Add only stable selectors/fixtures required to measure existing paths. Do not change production UI to
hide or relax a performance failure.

## Backend/API Scope
- Add one documented performance command/lane mapping PERF-001 through PERF-010 to exact scenarios,
  dataset size, load, warm-up, repetitions, percentile/throughput/batch measure, threshold source,
  and pass/fail result.
- Measure every section-24.1 target explicitly: login, dashboard, member search, Application Detail,
  Loan Account 360, approval action, Disbursement Readiness, document upload, report export, DPD
  batch, monthly accrual, and Capitalisation Dry Run. A PERF-001–010 load mapping does not silently
  stand in for these target-specific route/batch measurements.
- Cover login, dashboard, member search, application creation, document upload, approval, report
  export, DPD batch, monthly accrual, and audit query. Exercise async jobs through their public seams.
- Implement bounded worker-restart, Redis-restart, database-pressure, export-queue,
  large-document/audit, and sustained-workflow probe definitions and local failure tests. The Redis
  restart contract must prove no system-of-record data loss. Environment-bound section-24.3 results
  remain explicitly `release-evidence-required`; they cannot be converted to a pass or approved skip
  here and are admitted only by terminal slice 012F3 after deployment smoke.
- Emit a machine-readable summary with versions, commit, environment facts, counts, percentiles,
  failures, approved skips, and hashes. Never include credentials or PII.

## Database/Model Impact
None. Performance fixtures are isolated and disposable; no production benchmark table.

## API Contracts
No business contract changes. Document only the stable local command and evidence schema.

## Permissions
Use realistic least-privilege source roles and object scopes. No admin shortcut or test-only
production endpoint may be introduced.

## Audit Requirements
Load fixtures and output contain no live data; expected access/audit events may be counted but not
disabled to improve results.

## Validation Rules
- Thresholds are sourced or explicitly environment-bound; the agent cannot invent or relax them.
- Mandatory missing/failed scenarios and unapproved skips produce non-zero status; a bounded local
  probe result is distinct from the terminal environment result consumed by 012F3.
- Runs are seed-deterministic and report warm/cold behavior without mixing measurements.

## Trusted Browser Acceptance
- Spec: `e2e/performance-readiness.e2e.spec.ts`
- Screenshot: `performance-readiness-dashboard.png`

## Test Cases
- The lane detects a controlled latency/throughput failure, missing scenario, unsupported skip,
  malformed threshold, and stale/wrong-commit evidence.
- A representative local run exercises all ten mappings with deterministic fixtures; two browser
  repetitions retain equivalent scenario counts and successful critical-route screenshots.
- Contract tests fail when any section-24.1 target (including Application Detail, Loan Account 360,
  Disbursement Readiness, or Capitalisation Dry Run) or any section-24.3 probe definition is absent.
- Security, permission, financial correctness, and full-suite gates remain unchanged.

## Visual Acceptance Criteria
The retained critical dashboard route is populated, role-correct, and visibly usable during the
trusted performance smoke; no new styling or performance-only production state is introduced.

## Evidence Required
Scenario/threshold matrix; exact commands; environment and dataset manifest; raw bounded results and
machine summary; controlled failure; two trusted browser runs; section-24.3 command/evidence schema
and explicit 012F3 handoff; full functional/security gates.

## Risk Level
Medium

## Acceptance Criteria
- PERF-001 through PERF-010 each have exact repeatable evidence and an unambiguous pass/fail status.
- The lane and schema cannot mark R8-AC-004 release-ready; 012F3 remains mandatory for fresh,
  complete section-24.3 environment evidence.
- Performance tooling does not weaken correctness, security, audit, or production interfaces.

## Done Checklist
- [ ] Execution plan written
- [ ] Performance-lane failure tests written first
- [ ] Scenario mappings and command implemented
- [ ] Local and trusted-browser evidence saved
- [ ] Missing/failed/skip behavior proven fail-closed
- [ ] Full functional/security gates passed
- [ ] Risk and review evidence completed
- [ ] Commit delegated to the orchestrator after gates
