# Execution Plan

Selected slice: 005I2-application-detail-api-state-hardening

## Scope
- Harden the existing staff `GET /api/v1/loan-applications/{id}/` detail response with nullable,
  metadata-only `rejection_note` data when a `RejectionNote` exists.
- Preserve current staff permission ordering: unauthenticated/session denial, missing global read
  permission, 404 lookup, then object access denial.
- Keep borrower portal application routes unchanged and without staff rejection-note metadata.
- Remove frontend-only `LO00000035` overrides, hardcoded witness rows, and hardcoded nominee
  sensitive identifiers from `ApplicationDetail.tsx`.
- Render rejection-note metadata on the existing detail screen using existing cards/badges/text
  classes only.

## TDD Plan
1. Backend RED: add focused staff detail tests for `rejection_note = null`, `rejection_note`
   populated, object-access denial hiding detail metadata, and portal detail route omission.
2. Backend GREEN: extend existing serializer/service code without adding a new endpoint or model.
3. Frontend RED: add Application Detail render regressions for API-backed `LO00000035` and returned
   rejection-note metadata.
4. Frontend GREEN: adjust types/data mapping/rendering and remove mock override branches.

## Verification Plan
- Save red/green logs under `.ralph/runs/2026-07-10_044114_normal_run/evidence/terminal-logs/`.
- Run focused backend and frontend tests first, then full Ralph gates:
  backend `manage.py check`, backend tests, `makemigrations --check --dry-run`, coverage; frontend
  lint, typecheck, tests, build; `git diff --check`.
- Save visual evidence for detail-without-rejection-note and detail-with-rejection-note states.
- Update API contracts, run artifacts, progress, handoff, state, and selected/next slice files.
