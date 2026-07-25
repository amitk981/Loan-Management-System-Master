# Execution Plan

Selected slice: 012DAC-audit-explorer-and-observation-frontend-wiring

Repair boundary: trusted-browser acceptance only. Preserve the current product candidate and
correct only the demonstrated strict-locator collision in
`sfpcl-lms/e2e/reports-exports-audit-explorer.e2e.spec.ts`.

1. Reproduce the authoritative failure with the exact trusted-browser command recorded in
   `trusted-browser-acceptance-1.log`, saving the repair RED output.
2. Confirm whether the app has one exact `Action` control and the collision is caused by
   Playwright's injected `Block page interactions` checkbox.
3. Make the minimal semantic-locator correction in the existing E2E spec without changing product
   behavior, styling, source documents, protected files, or the selected slice contract.
4. Rerun the exact trusted-browser command twice with the declared repair evidence directories so
   both complete five-test runs pass and both screenshot sets are generated.
5. Run the impacted frontend checks for the changed test surface, inspect the bounded diff, and save
   repair test evidence, risk assessment, and a review packet whose result is exactly
   `Ready for independent validation`.

Permissions checked: the intended edit is the already-selected candidate's existing
`sfpcl-lms/e2e/` acceptance spec, explicitly bounded by this trusted-browser repair. The path is
not protected or forbidden; repair artifacts are under
`.ralph/runs/2026-07-25_072622_repair/`. No protected or forbidden path will be edited.

Ranked hypotheses:

1. `getByLabel('Action')` performs a substring accessible-name match and therefore also matches
   Playwright's injected `Block page interactions` checkbox. Prediction: the exact-name locator
   resolves one app input and makes the failing step pass.
2. The application renders two `Action`-labelled controls. Prediction: an exact-name count will be
   greater than one even without considering the injected checkbox.
3. A transient application overlay duplicates the control. Prediction: the duplicate will vary
   between otherwise identical runs or disappear after the overlay settles.

## Completion Status

- [x] Authoritative post-launch failure and exact validator command inspected.
- [x] Exact browser command rerun before repair; local Chrome failed before page creation and did
      not supersede the authoritative application assertion.
- [x] Hypothesis 1 confirmed by the authoritative strict-mode diagnostic and repository search.
- [x] Minimal exact-name locator correction applied.
- [x] Complete trusted spec rerun after repair; local Chrome again failed before page creation.
- [x] Targeted S74 browser rerun after repair; local Chrome failed at launch before the page fixture.
- [x] Five-test Playwright contract discovery, 13 impacted frontend tests, typecheck, lint,
      targeted E2E lint, build, diff check, and debug-marker cleanup check passed.
- [x] Browser infrastructure limitation and missing local screenshots recorded without fabrication.
- [x] Risk assessment, test evidence, and review packet prepared for independent validation.

The planned second local full browser run was not repeated after two consecutive full-spec
pre-page launcher failures (one before and one after the repair) plus one targeted S74 pre-page
launcher failure. Per the trusted-browser rule, only independent validation can decide browser
acceptance and produce the required two screenshot sets.
