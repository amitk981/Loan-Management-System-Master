# Slice 012F: Security Privacy Regression Checks

## Status
Complete

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Create a deterministic production-hardening regression lane that proves implemented
authentication, authorisation, sensitive-data, web, audit, configuration, dependency, and log
controls fail closed before UAT.

## User Value
The owner gets one reproducible security-readiness result instead of relying on scattered tests or
assuming local functional success implies safe production configuration.

## Depends On
- 012E3
- 012EB

## Runtime Capabilities

- `none`

## Source References
- `docs/source/security-privacy.md` sections 10-18, 24-25, 29-30, 32, and 36-37
- `docs/source/test-plan.md` sections 18, 28.3, 33.2, and 34.2
- `docs/source/implementation-roadmap.md` sections 17.2, 17.5-17.6, and 24
- `docs/source/deployment-ops.md` sections 9-11 and 39
- `docs/source/technical-architecture.md` sections 17, 30, and 32
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` section 012F

## Prototype Reference
- sfpcl-lms/src/pages/reports/ReportsMIS.tsx
- sfpcl-lms/src/pages/registers/RegistersHub.tsx
- sfpcl-lms/src/pages/Dashboard.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
- Assemble a tagged, deterministic regression lane over existing public interfaces for
  authentication/session lifecycle, RBAC and object scope, maker-checker/conflict, masking and
  reason-gated reveal, restricted documents, exports, immutable audit, rate limits, and safe
  errors. Do not create a second security subsystem.
- Add production-settings assertions for DEBUG/allowed hosts, HTTPS/secure cookies/HSTS, CORS,
  trusted origins, secret presence/separation, and the tracer/key invariants from 012E2/012E3.
- Exercise injection/XSS sanitisation boundaries, unsafe upload/filename rejection, JWT/secret/PII
  absence from logs/URLs/errors, and public-object-storage denial using safe fixtures.
- Run repository-supported secret and dependency scans with pinned/reproducible configuration;
  produce a machine-readable pass/fail summary containing no secrets. An unavailable required
  scanner is a visible failure, not a silent skip.
- Record product defects as blocking findings/corrective slices under Ralph policy; do not bundle
  unrelated fixes into this test-focused slice.

## Database/Model Impact
None.

## API Contracts
No new business APIs. Update security/test documentation only where the executable lane exposes a
stable local command or clarifies existing safe error/config expectations.

## Permissions
Test backend authority independently of hidden buttons/routes, including cross-object/team access,
admin-without-business-role, conflicted approver, maker-checker, auditor read-only, and unknown
permission combinations. Unknown or disabled authority must deny.

## Audit Requirements
Verify critical success/denied events use the immutable recorder, include required actor/outcome/
request/reason context, and redact sensitive values. Audit edit/delete attempts must fail.

## Validation Rules
- The lane is non-destructive outside isolated test data, deterministic, runnable in CI/local, and
  fails on missing controls/scans or unexpected skips.
- Fixtures, output, logs, and evidence contain no live credentials or raw PAN/Aadhaar/bank data.
- Do not weaken an existing gate, coverage floor, or production fail-closed setting to make the
  lane green.

## Test Cases
- Map and execute `SEC-AUTH-001..010`, `SEC-AUTHZ-001..007`, `SEC-PII-001..012`,
  `SEC-WEB-001..010`, and `AUD-001..016`, reusing existing tests where they already prove the
  public behaviour instead of duplicating them.
- Production-config negatives for missing/malformed secrets, debug/demo/tracer exposure, insecure
  cookies/origins/hosts, and raw exception output.
- Reverse-consumer coverage across login/session, permissions, all sensitive field adapters,
  documents, exports, audit, production demo isolation, and field-key rotation.
- Test the summary command itself: one controlled failure produces non-zero status and an exact
  failing control; green emits counts, skips with approved reasons, scanner versions, and hash.

## Visual Acceptance Criteria
None.

## Evidence Required
Control-to-test matrix; focused and full-gate outputs; production-settings negatives; secret and
dependency scan reports/hashes; no-secret log scan; machine-readable summary and failure demo.

## Non-Goals
Broad product repair, a second auth/encryption system, live penetration tests, infrastructure
provisioning, or weakening/changing protected CI and Ralph scripts.

## Risk Level
High

## Acceptance Criteria
- Every required source security control maps to executable evidence or an explicit blocking
  finding; required scanners/config checks cannot silently skip.
- Production configuration, cross-scope permissions, masking/reveal/export, safe errors/logs, and
  immutable audit all fail closed under negative tests.
- The lane is reproducible, secret-free, and reports exact pass/fail/skip counts non-zero on any
  mandatory failure.
- Broad product repair, live penetration testing, infrastructure provisioning, and changing
  protected CI/scripts are out of scope.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Substantive unresolved risk or decision recorded only if needed
- [ ] Commit created only after passing gates
