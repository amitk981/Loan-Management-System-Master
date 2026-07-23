# Risk Assessment

Risk level: Medium (inherited slice); Low repair delta.

## Repair scope

- Selected slice: `011O-auditor-read-only-views`
- Mode: same-worktree repair
- Changed validation domain: trusted Playwright acceptance only
- Product/backend/schema/dependency changes in this repair: none

## Demonstrated failure and mitigation

The first trusted browser run reached the product and exposed two false assumptions in the E2E spec:

1. A global substring action matcher counted the existing `Audit & Archive` navigation and
   `Close details` UI as operational mutation controls.
2. The shared navigation helper required the success heading even when a `403` correctly replaces
   the content with the explicit unauthorised card.

The repair now checks exact operational labels (`Approve`, `Review evidence`, `Update`, `Close loan`,
`Issue NOC`, `Return security`, and `Archive file`) and requires the success heading only in the
populated and empty success scenarios. The mutation-request listener remains unchanged, so any
POST/PATCH/DELETE request still fails the populated acceptance test.

## Residual risks

- The agent sandbox cannot launch system Chrome: the exact Playwright reruns and a minimal Chrome
  `--dump-dom about:blank` probe abort before page creation. The orchestrator-owned probe for this
  repair passed, so independent trusted validation remains the authoritative browser run and must
  generate all three screenshot manifests. No screenshot was fabricated.
- Exact action labels deliberately avoid false positives from read-only navigation/dismiss controls.
  If future operational controls use different labels, their owning slice must extend the acceptance
  vocabulary.

## Verification

- Focused auditor frontend tests: 4 passed.
- Playwright discovery: 3 required scenarios found.
- Frontend typecheck: passed.
- Frontend lint: passed.
- Frontend production build: passed.
- Independent trusted Playwright and screenshot validation: required before commit.
