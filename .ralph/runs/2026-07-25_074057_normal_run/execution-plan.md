# Execution Plan

Selected slice: 012G-critical-e2e-uat-smoke-scenarios

## Boundaries

- Add only deterministic test fixtures/builders, public-boundary assertions, and the declared
  `e2e/critical-uat-smoke.e2e.spec.ts` browser suite.
- Reuse existing public APIs, UI routes, roles, and fake/manual provider adapters. Do not add
  production endpoints, bypass permissions, mutate database state directly from scenarios, or
  repair broad product defects.
- Map every `UAT-001..026` to automated scenario evidence or an explicit manual UAT step.
- Retain the exact screenshots `critical-uat-standard-loan.png` and
  `critical-uat-permission-negative.png`.

## Behavior Sequence

1. Inventory the existing E2E harness, deterministic seed commands/builders, authenticated role
   helpers, public workflow APIs, audit/report/export paths, and prior screenshot conventions.
2. Add the first bounded standard-loan tracer assertion through the public browser/API interfaces;
   run it once to capture RED, then add the minimum deterministic support needed for GREEN.
3. Add one scenario at a time for approval threshold/exception boundaries; direct and subsidiary
   repayment plus interest/DPD; default/recovery/closure; compliance; reports/export/audit; and the
   RBAC/object-scope/masking negative. Each scenario must assert canonical state plus the applicable
   ledger, evidence, denial, and actor/outcome/reason audit fields.
4. Add the scenario-to-UAT/E2E/source matrix and seed manifest as self-contained run evidence,
   including any source-defined manual UAT steps.
5. Run the declared suite twice from fresh deterministic seeds and retain exact counts, skips,
   runtimes, screenshots, and traces. Results and counts must agree with no cross-scenario leakage.
6. Run focused frontend tests, typecheck, lint, and build, plus focused backend checks only if
   deterministic backend test support changes. Leave the authoritative full/reverse-consumer and
   security lane to the orchestrator.
7. Review the candidate against the selected slice and source traceability, then complete the risk
   assessment, review packet, and final summary.

## Test Design

- Public interface: Playwright browser actions and existing authenticated HTTP APIs exposed by the
  application; no direct ORM/database transitions.
- System boundaries faked: existing SAP, bank, communications, and storage fake/manual adapters
  only.
- Isolation: each scenario creates or selects a namespaced deterministic seed and must be safe to
  rerun in any order.
- Assertions: workflow state, immutable approval/document evidence, loan/ledger/allocation values,
  compliance calculations, report reconciliation, permission denial/masking, and critical audit
  actor/outcome/reason fields.

## Permissions Check

Planned edits are limited to `sfpcl-lms/**`, `sfpcl_credit/**` if deterministic test support is
strictly required, and this run's `.ralph/runs/2026-07-25_074057_normal_run/**` evidence. These paths
are allowed by `.ralph/permissions.json`; protected and forbidden paths will not be edited.

## Completion Notes

- The deterministic fixture and its production guard were developed test-first with retained
  red/green logs.
- Fixture setup runs before the browser journey. No management command or direct database
  transition runs from the Playwright scenario.
- Focused backend tests, fixture-selection tests, typecheck, lint, build, Django system check, and
  migration drift check pass.
- Local Chromium closed during launch before a page existed. No screenshot or successful browser
  result was fabricated; the declared trusted-browser contract remains for independent validation.
