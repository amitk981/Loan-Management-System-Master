# Slice 006X3: Credit Visual and Real-Browser Closure

## Status
Complete

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Replace 006H3's zero-test visual contract and 006X's fully mocked tracer with deterministic trusted-
browser proof of the restored state matrix and one real-backend, two-role Epic 006 path.

## Depends On
- 006X2

## Runtime Capabilities
- `localhost-e2e-server`

## Trusted Browser Acceptance
- Spec: `e2e/epic-006-closure.e2e.spec.ts`
- Screenshot: `appraisal-loading.png`
- Screenshot: `appraisal-queue.png`
- Screenshot: `appraisal-eligible.png`
- Screenshot: `appraisal-ineligible.png`
- Screenshot: `appraisal-pending.png`
- Screenshot: `appraisal-below.png`
- Screenshot: `appraisal-equal.png`
- Screenshot: `appraisal-above.png`
- Screenshot: `appraisal-draft.png`
- Screenshot: `appraisal-returned.png`
- Screenshot: `appraisal-review-pending.png`
- Screenshot: `appraisal-reviewed.png`
- Screenshot: `appraisal-rejected.png`
- Screenshot: `appraisal-submitted.png`
- Screenshot: `appraisal-empty.png`
- Screenshot: `appraisal-denied.png`
- Screenshot: `appraisal-validation.png`
- Screenshot: `appraisal-api-error.png`
- Screenshot: `epic-006-reviewed.png`
- Screenshot: `epic-006-pending-sanction.png`

## Source / Review References
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/working/VISUAL_ACCEPTANCE.md`
- `docs/source/implementation-roadmap.md` §11
- `docs/source/api-contracts.md` §22-§24 and §44
- `docs/source/functional-spec.md` M04-FR-004 through M04-FR-011
- `docs/source/test-plan.md`
- `docs/slices/006H3-appraisal-workbench-prototype-fidelity-restoration.md`
- `docs/slices/006X-mvp-end-to-end-happy-path-tracer-bullet.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-11_230238_architecture_review`

## Scope

- Add one collectable focused Playwright contract and committed Chromium baselines for the exact
  loading/queue/eligibility/limit/appraisal/empty/denied/validation/API-error matrix above. Remove
  the temporal-dead-zone failure in the 006H3 spec and do not accept zero collected tests.
- Preserve the approved pre-006H queue/header/three-stage/checklist/calculator composition and use
  only stored API facts. Counting/displaying stored checks must not become local eligibility or
  workflow authority; action visibility continues to consume 006X2's backend actions.
- Add a second test in the same declared spec that uses the real Django server, deterministic
  synthetic seed/setup, and real Deputy Manager Finance/Credit Manager login sessions. Through the
  default routed workbench, run eligibility and limit, create/update/submit the appraisal, record
  independent review, submit sanction once, and reload the pending case.
- Before each cross-role mutation, assert the exact six-field enabled/disabled resource action and
  prove a global permission cannot expose an absent/disabled control. Assert the exact writable
  appraisal PATCH keys, canonical four-read refresh counts, shared assessment/decision/case/event
  IDs, repeat-submit `409` cardinality, and metadata-only evidence.
- Retire or narrow the fully mocked 006X browser test so it cannot be presented as real-backend
  evidence. Preserve the backend integration tracer as an independent authoritative API check.

## Test Cases

- Playwright collection finds both visual-matrix and real-backend tracer tests before launch.
- The visual test produces all eighteen `appraisal-*` screenshots and matching committed baselines.
- The real tracer uses two authenticated roles, captures reviewed/pending-case screenshots, proves
  denied/missing actions and exact server IDs, and stops at one pending case with no committee action.
- Run the declared contract twice outside the sandbox plus all frontend/backend gates.

## Evidence Required

Collection log showing non-zero tests, two green trusted-browser runs, all twenty screenshots,
committed baselines, real HTTP/action/ID transcript with synthetic data, prototype-fidelity
checklist, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- The full restored visual matrix has deterministic self-contained screenshot/baseline evidence.
- One real-browser, real-backend, two-role path reaches exactly one pending sanction case without
  mock credit facts or client-owned workflow decisions.

## Run-Ahead Sharpening Review (006X2, 2026-07-11)

- Consume the exact authenticated-container mutation matrix established by 006X2: eligibility,
  limit, create/update/revalidate/submit, reviewed/returned/rejected, and sanction each issue one
  write and exactly one four-resource refresh; 400/403/409 paths issue no refresh.
- The trusted-browser tracer must begin from the server-projected loan-limit action now returned
  with stored eligibility, and must prove absent/disabled actions remain non-invokable before each
  cross-role mutation. Do not replace these assertions with global permission or stage heuristics.
