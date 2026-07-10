# Review Packet: 2026-07-10_154638_architecture_review

## Result
Success

## Slice
architecture-review

## Review Window

Pinned comparison: `git diff c25fcfc...HEAD`

Reviewed product commits:
- `261641c` — 005I3 application nominee selection contract
- `c20b72f` — 005I4 application detail backend-state hardening
- `7023475` — 006C2 cultivated-acreage source hardening
- `5c6866a` — 006D2A credit eligibility/configuration seam

Intervening owner E2E/configuration/map commits were context-only. Full inventory:
`evidence/review-window.md`.

## Standards

- Hard: staff/portal forms duplicate current-date adult/minor decisions in React instead of
  rendering backend validation.
- Hard: invalid staff PATCH and portal nominee mutation paths lack required no-side-effect tests.
- Hard: backend derives `assigned_owner` from receiver/creator, neither of which is assignment.
- Hard: Application Detail tests split mocked HTTP loading from injected view success/error and do
  not exercise the production async action controller.
- Owned hard debt: 006C2 financial behavior remains in `applications.services`; 006D2B is the
  immediately queued extraction.
- Judgment: 006D2A still has application-service reach-back; ADR-0002 intentionally stages model
  ownership. The resolver's narrow function shape is acceptable, but reverse dependency and weak
  boundary enforcement require correction.

Full independent report: `evidence/standards-review.md`.

## Spec

- High: `received_by_user or created_by_user` is presented as assigned owner. Portal intake can
  therefore show the borrower as the staff-side internal owner.
- Medium: portal MP10 omits safe nominee ID and minor/adult status required by 005I3.
- Watch: 006D2A's eligibility-path resolver wording is not demonstrated because eligibility does
  not query policy; adding such a query would violate behavior preservation. 006D2B must prove the
  real calculator path instead.
- No additional scope creep or 006C2 formula/snapshot regression was confirmed.

Full independent report: `evidence/spec-review.md`.

## Corrective Work

- Created `005I5-application-ownership-and-nominee-authority-hardening` for neutral owner
  projection, complete portal nominee facts, backend-only minority authority, missing invalid
  mutation tests, and production-component coverage.
- Sharpened 006D2B with static AST/import boundaries, no `configurations -> credit` dependency,
  no direct policy query, and explicit financial-source locks.
- Added 005I5 as an explicit prerequisite for 006D2B/006E and warned 006E not to revive
  receiver/creator ownership inference.
- No ADR was required.

## Test Quality And Requirement IDs

006C2 mismatch/verification/Decimal/null-profile/failed-rerun assertions and 006D2A direct
eligible/ineligible/pending/rollback assertions are substantive. Neither Epic 005 nor Epic 006 is
Complete; incomplete M03/M04 IDs remain explicitly queued or assumed. Full traceability:
`evidence/source-fidelity-and-test-quality.md`.

## Validation

- Backend check/migration sync: pass.
- Backend suite: 308 tests passed under coverage.
- Backend coverage: 95%, above 85% floor.
- Frontend lint/typecheck: pass.
- Frontend tests: 106 passed across 16 files.
- Frontend build: pass; existing non-blocking chunk-size warning only.
- Diff whitespace, production boundary, protected paths, and diff limits: pass.

## Recommended Next Action
Run `005I5-application-ownership-and-nominee-authority-hardening`, then 006D2B and 006E.

Summary: Standards has 5 hard/owned findings (worst: synthesized owner and duplicated frontend
authority); Spec has 2 confirmed findings plus 1 watch (worst: portal user can appear as staff owner).
