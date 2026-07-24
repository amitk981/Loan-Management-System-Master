# 011PE Trusted-Browser Repair Diagnosis

## Authoritative symptom

The prior validator's first complete browser run reached the S58-S61 application flow and failed
because:

`getByRole('button', { name: 'Archive' })`

matched both the sidebar button named `Closure & Archive` and the intended tab named exactly
`Archive`.

The same authoritative log showed the other three tests passing. The later prior-run failures were
all Chrome launch aborts before page creation.

## Hypotheses tested

1. **Confirmed:** Playwright's substring accessible-name matching made the locator ambiguous.
   Prediction: selecting the already-reported exact accessible name removes the strict-mode
   ambiguity without changing application code.
2. **Rejected by the diagnostic:** the application did not lack or disable the intended tab; the
   strict-mode error explicitly identified it as an available exact match.
3. **Not implicated:** stale page state was not required to produce the error because the
   authoritative DOM contained both matching controls in the same deterministic run.

## Repair

Changed the test locator to:

`getByRole('button', { name: 'Archive', exact: true })`

No application, backend, styling, dependency, schema, protected, or workflow file was changed by
the repair.

## Verification

- TypeScript typecheck: passed.
- ESLint on the repaired spec: passed.
- Playwright discovery/compilation: passed; four declared tests were listed from the spec.
- Two complete post-repair spec attempts: inconclusive because Chrome aborted during
  `browserType.launch` before any page or application assertion.
- Post-repair one-page infrastructure probe: failed at the same `browserType.launch` boundary,
  confirming the current local failure is browser infrastructure rather than an application
  assertion.

No screenshots were created or fabricated. The orchestrator's independent trusted-browser lane
must run the complete contract twice and retain the five declared screenshots.
