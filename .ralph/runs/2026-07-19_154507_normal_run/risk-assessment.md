# Risk Assessment

Risk level: High

- Selected slice: `CR-012-epic-009-playwright-evidence-is-incomplete`
- Mode: `normal_run`
- Standing approval: applicable; no revoked entry was found in the mandated workflow context.

## Principal risks and controls

- False browser proof: removed every owned-route fulfilment and token injection from the declared
  spec. Login, Loan Account reads, workspaces, notifications, and financial actions use Django.
- Unsafe fixture availability: the new command refuses unless both `SFPCL_DEBUG=true` and
  `SFPCL_ALLOW_E2E_SEED=true`; Playwright also uses its fresh isolated SQLite path and storage root.
- State fabrication or business-rule weakening: no production model, endpoint, permission, money,
  workflow, selector, component, or styling code changed. The fixture composes retained owner
  contract setup and advances only isolated source-bank/document facts.
- Stale/duplicate screenshots: the spec removes all nine declared files and the old manifest before
  each run, then requires all files to exist and all nine SHA-256 values to differ.
- Shared Playwright seed collision: the config selects the Epic 009 isolated seed only for the exact
  declared spec; existing general/MP14 specs retain their established seed sequence.
- Transfer evidence timing: the restricted finance upload is prepared only after CFC approval, then
  consumed immediately by the real transfer endpoint. This avoids presenting an unconsumed upload
  as completed transfer evidence.
- Browser infrastructure: local Chromium aborted with `SIGABRT` before page creation. Per the slice
  workflow, no screenshots were fabricated and outside-sandbox trusted-browser validation decides
  acceptance twice.

## Residual risk

The only remaining acceptance risk is browser-selector/runtime behavior that cannot be exercised in
the coding sandbox. Playwright collection, server migration/seed startup, focused regressions, and
all non-browser gates are green; the exact trusted contract is ready for independent execution.
