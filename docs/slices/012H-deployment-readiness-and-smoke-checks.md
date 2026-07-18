# Slice 012H: Deployment Readiness and Smoke Checks

## Status
Not Started

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Make the platform verifiably deployable: implement the backend health endpoints from
deployment-ops.md section 20, and a runnable smoke-check command that executes the
post-deployment verification steps from deployment-ops.md section 13.1 (steps 10-14)
against any environment URL, so the staging branch deploy can be checked automatically
before the owner promotes to main.

## User Value
The owner can see, before every promotion to production, an objective pass/fail signal
that the deployed application is alive, ready, and passing its critical workflows —
instead of trusting that green unit tests imply a working deployment.

## Depends On
- 012G

## Source References
- docs/source/deployment-ops.md section 6 (environment strategy; staging is the
  production-like release candidate the smoke checks target)
- docs/source/deployment-ops.md section 11.5 (deployment gates that the smoke output
  provides evidence for)
- docs/source/deployment-ops.md section 13.1 steps 10-14 (post-deployment smoke tests,
  health checks, verify logs, confirm key business workflows)
- docs/source/deployment-ops.md sections 20.1-20.3 (health endpoints: /health/live/,
  /health/ready/; readiness verifies database connectivity, migrations applied, critical
  configuration present; deep checks must be cheap and never trigger business transactions)
- docs/source/deployment-ops.md section 15.2 (application rollback steps 7-8 reuse the
  same health checks and smoke tests after a rollback)
- docs/source/test-plan.md
- docs/source/security-privacy.md (health endpoints must not leak secrets, versions of
  vulnerable components, or personal data)
- docs/source/screen-spec.md section 12 (non-functional requirements: performance,
  accessibility, security)

## Prototype Reference
- sfpcl-lms/src/pages/Dashboard.tsx (smoke scenario target)

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
- `GET /health/live/`: returns 200 with a minimal body when the application process is up
  (deployment-ops.md section 20.1). No authentication, no database access.
- `GET /health/ready/`: returns 200 only when the application can serve traffic —
  database reachable, migrations applied, critical configuration present (section 20.2).
  Returns 503 with a terse machine-readable reason when not ready. Only check components
  that exist in this codebase; record components that do not exist yet (e.g. Redis,
  Celery, object storage) in `docs/working/ASSUMPTIONS.md` rather than stubbing them.
- A management command `python manage.py smoke_check --base-url <url>` that runs the
  section 13.1 post-deployment checks against a deployed environment: liveness, readiness,
  authentication round-trip with a designated smoke-test user, and one read-only critical
  workflow per module group (reuse the 012G smoke scenarios where they are API-driven).
  Exit code 0 on pass, non-zero on any failure, with a plain-English summary of what
  failed. Read-only: the command must never create, modify, or approve business records
  in the target environment (section 20.3: no actual business transactions).
- Health endpoints and smoke output must not expose secrets, stack traces, dependency
  versions, or personal data (security-privacy.md).

## Database/Model Impact
None. No migrations.

## API Contracts
Add the two health endpoints to `docs/working/API_CONTRACTS.md` with response shapes for
ready and not-ready states.

## Permissions
Health endpoints are unauthenticated by design (deployment infrastructure calls them);
they must therefore return no business data at all. The smoke-check command uses a
dedicated low-privilege smoke-test user, never an admin account.

## Audit Requirements
No audit events for health checks (they run continuously). The smoke_check command logs
its run summary to stdout only.

## Validation Rules
Enforce source-doc business rules and block invalid state transitions.
Verify screen-spec.md section 12 non-functional requirements as part of readiness: list
endpoints paginated per api-contracts section 8, no unbounded queries on large tables,
and performance smoke checks recorded in the run evidence.

## Out of Scope (owner decisions, not this slice)
- Backend hosting selection and any production deploy pipeline: the owner has deferred
  hosting; record this as an assumption. Do not create deployment workflows, do not touch
  `.github/` or `scripts/` (protected paths).
- Branch model: agent work integrates into `staging` only; the owner alone promotes to
  `main` per `docs/working/RELEASE_PROMOTION.md`. This slice changes nothing about that.

## Test Cases
- Liveness returns 200 without touching the database (assert zero queries).
- Readiness returns 200 when database is reachable and migrations are applied.
- Readiness returns 503 when a required component is unavailable (simulate database
  failure) and when unapplied migrations exist.
- Health responses contain no secret values, stack traces, or personal data.
- smoke_check exits non-zero when liveness, readiness, auth, or a workflow check fails,
  and zero when all pass (run against the local test server).
- smoke_check performs no writes: assert no business records are created in the target.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output; example responses for /health/live/ and /health/ready/ (ready and not-ready);
a full smoke_check run transcript against the local development server.

## Risk Level
Medium

## Acceptance Criteria
- Both health endpoints behave per deployment-ops.md sections 20.1-20.2 and are covered
  by the failure-path tests above.
- `manage.py smoke_check --base-url` runs green against a local server and fails loudly
  and legibly when the target is broken.
- Nothing in this slice writes to `.github/`, `scripts/`, or any protected path.
- Source-doc business rules are enforced or documented as assumptions.
- The implementation stays within one small Ralph slice.

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
