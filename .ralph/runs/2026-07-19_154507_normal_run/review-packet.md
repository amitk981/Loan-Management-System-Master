# Review Packet: 2026-07-19_154507_normal_run

## Result
Ready for independent validation

## Slice
CR-012-epic-009-playwright-evidence-is-incomplete

## What changed

- Added a doubly guarded, idempotent Epic 009 E2E seed/advance command that composes current owner
  evidence for a completed SAP request, sanctioned account, named readiness blocker, real initiation,
  CFC, transfer, advice-action, and safe missing-account states.
- Replaced browser token injection and owned API fulfilment with real staff form logins and real
  Django reads/actions.
- Added `loan-account-list.png`, state-specific assertions before every capture, stale-file removal,
  nine-way SHA-256 uniqueness enforcement, and a sorted retained manifest.
- Kept production APIs, selectors, permissions, money/workflow rules, screens, and styling unchanged.

## Traceability

- The CR and 009J Visual Acceptance require separate real-Django Loan Account list, sanctioned,
  active/funded, and safe-error screenshots. The spec captures all four after visible heading/row,
  status/amount, and genuine Django 404 assertions.
- The CR and 009K acceptance require visible SAP, readiness blocker, initiation, CFC authorisation,
  and transfer/advice states. The spec proves Completed SAP, the named source-bank blocker with a
  disabled initiation action, the enabled initiation form, CFC action, and successful transfer plus
  advice action through the production screens.
- The CR prohibits browser fulfilment for auth, Loan Account, and workspace APIs. Static audit finds
  none, and `staffLogin` drives the real login form for each actor.
- The CR requires nine distinct screenshot hashes in each trusted run. `writeAndVerifyManifest`
  verifies all declared files, asserts a set size of nine, and writes the deterministic sorted
  `epic-009-screenshot-sha256.txt` manifest.
- Backend verification: the two new `SeedE2eUsersTests` methods prove both guards, idempotency,
  blocker/ready public projections, governed CFC identity, and immutable finance upload provenance.

## Validation reviewed

- Backend RED and GREEN evidence retained under `evidence/terminal-logs/`.
- Focused backend: 2 tests passed; Django check and migration sync passed.
- Focused frontend: 4 files / 15 tests passed; typecheck, lint, changed E2E lint, and build passed.
- Playwright collection passed. The local server migrated/seeded successfully; sandbox Chromium
  aborted before page creation, so the declared two independent trusted runs remain pending for the
  orchestrator as designed.

## Scope and review findings

- No protected path, source document, production UI, production API, or database migration changed.
- No auth token is injected and no owned response is stubbed.
- No new dependency was added.
- Changed-line volume remains within the configured slice limit.

## Recommended Next Action

Run Ralph's exact trusted browser contract twice, retain the nine fresh PNGs and manifest from each
run, then execute the independent configured gates.
