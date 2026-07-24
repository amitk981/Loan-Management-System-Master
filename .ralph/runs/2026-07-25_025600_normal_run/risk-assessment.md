# Risk Assessment

Risk level: Medium

- Selected slice: `011PD-compliance-frontend-wiring`
- Product scope is frontend-only: one established Epic 011 API seam, its focused tests, the
  Compliance Dashboard owner, and the declared trusted-browser spec.
- Authorization risk is contained by rendering only backend `available_actions`; the frontend does
  not infer mutation authority from roles. The backend remains the enforcement owner.
- Financial/compliance risk is contained by displaying backend-calculated Section 186 and NBFC
  values without recalculating money, ratios, state, or statutory Board requirements in React.
- Canonical-state risk is covered: every successful review action refetches all seven tracker reads.
- Auditor mutation risk is covered by a sanitized backend projection, UI assertions, zero browser
  mutations in the declared contract, and existing 011O reverse-consumer tests.
- Regression risk is bounded by 32 passing impacted tests across the shared Epic 011 seam and its
  default, closure, compliance, and auditor consumers; typecheck, lint, build, Django check, and
  migration sync are green.
- Browser infrastructure risk remains: the exact Playwright contract started healthy servers but
  system Chrome aborted before test execution; the immediate central browser probe reproduced the
  same launch failure. No screenshot was fabricated. Trusted validation must execute the spec twice
  and save `compliance-trackers.png`.
- Source-screen completeness risk remains bounded by existing backend projections: the 011M KYC
  projection does not expose Aadhaar/last-KYC/open-loan fields, and the 008D report intentionally
  omits custody/CS-verifier/notary-date details. The UI renders every available canonical field and
  does not invent these facts.
- No dependency, backend model, migration, protected-path, or source-document changes were made.

Manual review required: yes, for trusted-browser execution and the explicitly bounded projection
field gap.
