# Execution Plan

Selected slice: `009I2-portal-disbursement-stage-and-visual-closure`

## Boundaries and permissions

- Work only in the active Ralph worktree and only on MP14's explicit application selection,
  owner-stage projection, portal composition, tests, browser contract, and run evidence.
- Product edits are permitted under `sfpcl_credit/**` and `sfpcl-lms/src/**`; browser specs are
  permitted under the existing frontend tree. Run artifacts are permitted under this run folder.
- Do not edit protected paths, source documents, orchestrator-owned state/progress/status facts, or
  unrelated future slices. No migration or dependency change is expected.
- High risk proceeds under standing approval; no matching owner revocation exists.

## Behavior-first implementation

1. Inspect the retained MP14 projection, portal container, frontend API/component/tests, owner
   decision facades, review probe, and the minimal cited source sections needed to resolve stage
   semantics.
2. Add one focused backend public-interface regression at a time for current SAP completion,
   distinct owner timestamps/nulls, exact CFC/advice states, stale/mixed evidence, masking, and a
   no-write status GET. Save the first failing output under `evidence/terminal-logs/`, then implement
   only the projection changes needed for green and save the green output.
3. Add frontend interaction regressions proving that `BorrowerPortal` passes its explicit selected
   application id, opposite application order cannot change the requested id, and no selection
   renders the established navigation/empty pattern. Then update MP14 to accept the id and compose
   existing `AlertBanner`/portal patterns without new styling or components.
4. Add the declared real-Django Playwright spec for processing, disbursed/advice, and safe-error
   screenshots without blanket interception. Use collection/non-browser checks locally if Chromium
   is unavailable; leave the actual twice-run screenshot contract to the orchestrator.
5. Run focused backend and frontend tests during development, followed by Django check and migration
   sync plus frontend typecheck, lint, tests, and build. Do not run the complete backend suite or
   full coverage locally.
6. Review targeted diffs against the slice/source contract, run debug/protected-path checks, and
   finish self-contained red/green, test, risk, review, and final-summary evidence. Record only a
   genuinely source-silent decision in assumptions and update bounded contract/digest/inventory
   documentation only if the implementation changes their durable truth.

## Acceptance evidence

- Backend: public API/service assertions for six exact stages, honest timestamps/nulls, stale/mixed
  blocking, corrected accepted-advice capability, masking/session/download/error behavior, and
  zero database writes on GET.
- Frontend: container/application-selection and MP14 state/action tests; static guard against local
  selection and bespoke portal message styling.
- Browser: `sfpcl-lms/e2e/portal-disbursement-status.spec.ts` collected successfully and configured
  to save the three exact screenshot names declared by the slice.
- Gates and traceability: command logs plus source-to-code-to-test mapping in `review-packet.md`.
