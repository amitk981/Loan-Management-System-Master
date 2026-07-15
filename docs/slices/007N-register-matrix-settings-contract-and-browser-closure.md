# Slice 007N: Register, Matrix, and Settings Contract and Browser Closure

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007L
- 007M

## Runtime Capabilities
- `localhost-e2e-server`

## Goal

Remove the remaining frontend transport and approval-rule calculations, preserve the approved
Settings composition, and retain trusted browser proof for S23/S25/S70/S71.

## Source / Review References

- `docs/source/screen-spec.md` S23, S25, S70, and S71
- `docs/source/api-contracts.md` §§6-8, 25.1, 25.9, and 25.10
- `docs/source/codebase-design.md` §§23.3-23.6, 24.4, 26.3, 28.3, and 42.3
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/007J-registers-and-approval-matrix-frontend-wiring.md`
- `docs/slices/007J2-settings-hub-panels-wiring-or-lockdown.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_010536_architecture_review`

## Concrete Requirements

1. Extend the shared authenticated API client with typed pagination-envelope support and migrate
   the register/matrix feature service to it. JWT/header loading, request ids, JSON/envelope/error
   parsing, and auth failure behavior must have one owner; feature services retain only paths,
   filters, payloads, and DTOs.
2. The approval-matrix API must project display-ready authority summary and minimum approver count
   from the configuration owner. React must not reimplement Director-count/role composition rules;
   it renders the server fields and the complete retained version/proposal facts.
3. Keep S23 and S25 on independent scoped endpoints. Every filter/page response atomically replaces
   rows and pagination; permission loss clears data; ids remain metadata and create no action,
   decision, evidence-reference, or download authority.
4. Restore the closest pre-007J2 SettingsHub policy card/form composition using existing patterns.
   Do not retain a new ten-column policy table/header-card treatment where the approved screen used
   cards/fields. Preserve API truth, read-only/manager authority, complete create-only successor,
   honest draft labels, and inert 008A/012EA panels without reintroducing fixtures.
5. Use one navigation manifest for both Sidebar visibility and direct route guards so resource-
   specific register/matrix/settings permissions cannot drift. Navigation remains usability only;
   each panel enforces its canonical permission.

## Trusted Browser Acceptance

- Spec: `e2e/approval-register-settings.e2e.spec.ts`
- Screenshot: `credit-sanction-register-scoped.png`
- Screenshot: `exception-register-scoped.png`
- Screenshot: `approval-matrix-read-only.png`
- Screenshot: `approval-matrix-successor-pending.png`
- Screenshot: `loan-policy-read-only.png`
- Screenshot: `settings-deferred-panels.png`

## Trusted Browser Scenario

- Open routed Registers and Settings through production app-shell navigation using deterministic
  authenticated contracts. Exercise scoped/filtered register pages, matrix reader/manager proposal
  states, policy reader state, and inert template/TAT panels; never mount components directly or
  bless self-generated baselines.

## Test Cases

- Shared-client pagination/error/auth behavior and feature-service exact filters/payloads.
- Server-projected matrix authority is rendered verbatim; raw-source regression rejects client
  Director-count/minimum-approval calculation and duplicate transport implementations.
- Permission loss, empty/denied/error/normalized-page states, create-only policy proposal, and one
  shared navigation-manifest parity matrix.
- All six screenshots are produced in both independent orchestrator runs.

## Risk Level
High

## Acceptance Criteria

- Register/matrix/settings clients use one auth/envelope transport and no React approval calculation.
- The approved Settings composition is preserved without mock/live-looking fixtures.
- Trusted browser evidence and all configured gates pass.

## Done Checklist

- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated
- [x] Database rules followed (no schema change required)
- [x] Permissions tested
- [x] Audit behavior retained by the governed successor boundary
- [x] Browser contract collected; local Chromium sandbox denial retained honestly
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [x] Commit left to the orchestrator after independent gates
