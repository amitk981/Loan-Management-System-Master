# Review Packet: 2026-07-15_181520_architecture_review

## Result
Complete — findings recorded; no production code changed.

## Slice
architecture-review

## Fixed Point and Scope

`git diff 8dbefb17...fad70f95` covering 008K4, CR-005, 008L3, CR-006, and CR-007.

## Standards

- 1 Critical: bank decisions lack application object and Stage-4 scope.
- 3 High: borrower-safe conditional precedence, cross-app migration ownership, browser tests that
  replace all backend behavior.
- 2 Medium: incomplete action/race evidence and unlocked GET versus locked POST authority.

Worst Standards issue: immutable bank evidence is writable for a draft or unrelated application by
any globally authorized Compliance/CS actor.

## Spec

- 3 High: browser acceptance never reaches Django, changed retained completion evidence still
  projects complete, and the every-role real-instrument reader matrix remains partial.
- 1 Medium: source portal audit actions and response submitted-state projection are inconsistent.

Worst Spec issue: the required real-session browser acceptance is entirely fixture-driven.

## Traceability

- Source says application access is role-and-object scoped and documentation starts only after
  sanction (`auth-permissions.md` §§19.2/20.1); code checks only global role/permission; probe
  `test_bank_decision_rejects_non_documentation_application_state` receives HTTP 200 in draft.
- K4 says any changed action/audit/workflow/version/current evidence blocks borrower-safe truth;
  code's inline conditional skips later predicates; probe
  `test_borrower_projection_rejects_changed_completion_version_body` remains complete.
- L3 says trusted browser acceptance uses a real portal session; both specs route every
  `/api/v1/**` call; static review plus the route definitions prove Django is bypassed.
- CR-005 says Complete and Download coexist; rendered tests prove both with no upload controls.
- CR-006 says Asia/Kolkata display is host-independent; formatter fixes the zone and the full
  frontend suite passes.
- CR-007 says CI must provision the existing Noto font; the reviewed workflow does so without
  changing renderer validation, and remote run 29414744868 is green.

## Corrective Slices

- `008K5-final-evidence-authority-and-migration-closure`
- `008L4-portal-production-boundary-and-browser-proof`
- `008M-documentation-hub-frontend-wiring` now depends on 008L4.

## Validation

Frontend: 304 tests, lint, typecheck, build PASS. Backend: 887 tests PASS, 92% coverage, Django
check and migration drift PASS. Queue lint, JSON, diff, protected-path, and production-code checks
PASS. Review probes are intentionally RED evidence and are not production gates.

## Recommended Next Action
Run 008K5, then 008L4, then 008M.
