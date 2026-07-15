# Risk Assessment

Risk level: High (inherited slice); Medium repair delta

- Selected slice: 008L4-portal-production-boundary-and-browser-proof
- Mode: repair
- Standing approval applies; no protected/source file was modified.

## Demonstrated risk and repair

- The trusted browser reached real portal login and `/auth/me`, but the seeded catalogue kept the
  borrower role inactive. The response therefore omitted roles, the frontend selected its neutral
  staff shell, and both specs failed before MP07/MP11.
- The canonical catalogue now makes only `borrower_portal_user` active among external roles. This is
  the source-required live portal identity, not a new authority. Nominee, bank, subsidiary, and
  external-auditor roles stay inactive.
- No staff permission link was granted. Portal authentication continues to replace effective
  permissions with the fixed own-member allowlist, and existing staff-endpoint denial tests pass.

## Controls and residual risk

- TDD evidence freezes both catalogue status and the exact real `/auth/me` borrower role response.
- Twenty-five affected identity/portal tests and the full 897-test suite pass; no migration,
  dependency, styling, external call, or document-policy change was introduced by the repair.
- Residual risk is browser-only until Ralph reruns both declared specs twice outside this sandbox
  and verifies the four genuine screenshots. Local Chromium was denied before execution and the
  in-app browser runtime exposed no browser backend; no screenshot was fabricated.
