# Ralph Handoff

## Last Run

2026-07-16_093846_repair

## Current Status

Corrective slice 008M3 is complete. This bounded repair fixed the independent trusted-browser spec's
stale `termSheet` locator: after the scenario was moved to the pending Power of Attorney fixture,
the restricted-state assertion still referenced the removed locator and crashed with a JavaScript
`ReferenceError` after two screenshots. It now reuses the declared lazy Power of Attorney row
locator. No production, fixture, workflow, authority, API, or visual behavior changed.

The staff documentation workspace continues to project only actions
that their owner decision would permit from the same current locked facts. The public action
boundary accepts an HMAC-bound opaque action identity plus source-required user input, reconstructs
the current private command server-side, and returns nondisclosing 404 with zero writes for stale,
tampered, cross-user, and cross-application identities.

Every projected mutation is rendered in the checklist and Document Pack. Required-party signature,
stamp/notary, upload/re-upload, correction/return, ordered S35 approval/condition/return, generation,
bank, security, mismatch, verification, and completion actions dispatch through existing owners.
Success refetches once; rejected actions remain non-optimistic and visible.

## Validation

Repair evidence is in `.ralph/runs/2026-07-16_093846_repair/evidence/`. The exact undeclared-locator
TypeScript regression is green and Playwright collects the real-Django spec. Frontend validation
passed 321 tests, typecheck, lint, and build. Backend validation passed 944 tests with 51 expected
skips at 91% coverage, plus check and migration drift. Local Chromium was denied macOS bootstrap
services before page creation, so no screenshots were fabricated; the independent twice-run browser
gate must produce the four declared PNGs and is the remaining authoritative acceptance step.

## Important Continuation Notes

- 008M4 is sharpened to move the broad workspace dispatch/private-command construction behind deep
  owner decision/execute pairs without changing 008M3's opaque-ID, multipart, sibling-order, or
  rejected-action behavior.
- 009B2 retains A-124's conservative same-member reuse rule while adding exact payload replay. It
  must not invent outstanding-loan state or call real email/SAP services.
- 009C now depends on 009B2 and is owned by `loans.modules.loan_account_lifecycle`; A-121 still
  forbids a default Critical permission grant and A-122 still requires zero pre-disbursement balances.
- 009D remains read-only and is owned by `disbursements.modules.disbursement_readiness`; Finance
  initiation and CFC authorization remain downstream, not synthetic readiness checks.

## Next Run

Run 008M4, then 009B2. Continue with sharpened 009C and 009D only after those corrective dependencies
complete.
