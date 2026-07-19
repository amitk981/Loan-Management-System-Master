# Review Packet: 2026-07-19_165226_repair

## Result
Ready for independent validation

## Slice
CR-012-epic-009-playwright-evidence-is-incomplete

## Demonstrated failure and repair

The retained browser run proved CFC authorisation succeeded through real Django, after which the
pending-only CFC workspace became empty. The spec incorrectly waited for a success alert nested
inside a selected-row container that no longer existed. It now asserts the exact genuine response
and the truthful empty CFC queue.

The same selector made CFC an invalid actor for the next UI transfer step. Test-first fixture proof
showed Senior Finance lacked the required transfer grant. The isolated guarded fixture now assigns
that existing production capability and its synthetic evidence to the initiating Senior Finance
actor. The real browser sequence uses Credit Manager for Loan Account reads, Senior Finance for
initiation/transfer, and CFC for independent authorisation, all through the login form.

## Traceability

- The CR requires real Django, no browser fulfilment of owned APIs, immediate state assertions,
  nine distinct screenshots, and a deterministic SHA-256 manifest. The code performs genuine
  authorisation and transfer POSTs, asserts their server states, clears stale evidence, and rejects
  any duplicate screenshot hash.
- The Epic 009 contract assigns initiation to Senior Manager Finance and independent approval to
  CFC. The browser uses those exact actors, while transfer is executed by the initiating Senior
  Finance actor through the existing owner-authorized action.
- `docs/working/FRONTEND_DESIGN_RULES.md` forbids redesign during wiring. No production frontend
  component or styling changed; the only frontend production-adjacent addition is a regression test
  for the existing empty-state behavior.

## Verification reviewed

- Guarded fixture red/green regression: PASS after one expected red.
- Impacted frontend tests: PASS (four files, sixteen tests).
- Exact Playwright collection and static real-boundary scan: PASS.
- Typecheck, lint, build, Django check, and diff hygiene: PASS.
- Local exact browser attempt: Chrome closed during sandbox launch before the test body; no
  screenshot claim is made.

## Independent acceptance still required

Ralph must execute the declared Playwright contract twice outside the sandbox, retaining two fresh
sets of nine structurally valid, pairwise-distinct PNGs plus deterministic manifests. Ralph also
owns the authoritative complete backend suite under coverage and all remaining gates.

## Recommended Next Action
Run full independent validation; commit only after both trusted browser runs and every configured
gate pass.
