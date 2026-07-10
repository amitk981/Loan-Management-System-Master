# Execution Plan

Selected slice: `006D2B-credit-loan-limit-calculator-and-appraisal-seam`

## Scope and constraints

- Work only in the active Ralph worktree and only on 006D2B.
- Preserve every existing 006A-006D HTTP payload, error, permission, object-access, calculation,
  rerun, immutable-read, audit, and workflow contract. Add no endpoint, database migration,
  dependency, frontend behavior, or business rule.
- Keep model/table ownership unchanged under ADR-0002. Preserve assessment UUIDs and one-to-one
  reruns. Keep the diff below 2,000 lines, targeting at most 1,500.
- Use only paths allowed by `.ralph/permissions.json`; do not alter protected or source files.

## Public module interfaces and seams

- Extract calculation/read orchestration behind
  `credit.modules.loan_limit_calculator.LoanLimitCalculatorModule`, with immutable module result,
  snapshot, and validation/error types as the caller/test interface.
- Make application views thin HTTP adapters. Remove loan-limit calculation, serialization, audit,
  and snapshot helper exposure from `applications.services`.
- Resolve effective policy only through
  `configurations.modules.configuration_resolver.resolve_effective_loan_policy(..., for_update=True)`;
  configuration-owned result/errors must not import `credit` or application result/error types.
- Add `credit.modules.appraisal_workflow` as the sole documented 006E entry seam, without adding
  appraisal behavior in this slice.
- Establish static AST/import regressions that reject direct/private/aliased credit-helper imports,
  direct policy-model queries outside the resolver, reverse `configurations -> credit` imports,
  and appraisal behavior added to `applications.services`.

## TDD tracer bullets

1. Confirm current characterization/API tests are green and save their output.
2. RED→GREEN: static dependency/import boundary and appraisal entry-seam behavior.
3. RED→GREEN: direct calculator module read/calculate result and canonical snapshot behavior,
   including public/audit shared financial-policy-acreage fields.
4. RED→GREEN: policy resolver invocation with `for_update=True`, no direct policy query, and
   translation of configuration-owned failures at the credit seam.
5. RED→GREEN: lower-of-two and below/equal/above boundaries, Decimal-equivalent acreage,
   two-value null-profile calculation, pending/rejected evidence, bad crop-plan linkage, and
   failed-rerun preservation.
6. RED→GREEN: transaction/locking coverage for the application, current assessment,
   shareholding, land holdings, crop plan, profile, and policy; forced evidence failure rolls back.
7. Refactor only while green; keep one canonical redacted immutable snapshot projection with
   request/audit metadata added at the relevant boundary.

## Verification and handoff

- Run focused module/API/static tests during implementation with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, saving red/green logs under
  `evidence/terminal-logs/`.
- Run backend check, migration sync, and the full suite under coverage; run frontend lint,
  typecheck, tests, and build even though no frontend change is expected. Run `git diff --check`
  and diff-budget checks.
- Perform separate standards and spec reviews, resolve material findings, and save an architecture
  map/traceability note in `review-packet.md`.
- Save `changed-files.txt`, `risk-assessment.md`, `final-summary.md`, validation evidence, and update
  the Epic 006 digest, state, progress, handoff, selected-slice status, and the next 1-2 eligible
  Not Started slice files using only source material already opened.
- Do not run git add, commit, or push; the Ralph orchestrator owns integration.
