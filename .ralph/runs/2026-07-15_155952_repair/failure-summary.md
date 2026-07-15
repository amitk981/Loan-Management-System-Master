# Validation Failure Summary

The independent validation runner was intentionally stopped before repeating the full gates because
the trusted, outside-sandbox Playwright feedback loop exposed two deterministic selector failures
after Chromium build 1148 was installed successfully.

## Demonstrated browser failures

1. `member-portal-deficiency-response.e2e.spec.ts:79`
   - `getByText('Portal Contract Member').first()` resolves to an element hidden in the collapsed
     mobile navigation and times out waiting for visibility.
   - Fix the login-ready assertion to target a visible, stable portal surface at the 390x844 viewport.
2. `member-portal-documentation-actions.e2e.spec.ts:44`
   - `getByRole('button', { name: 'My Documents', exact: true })` resolves to both the sidebar button
     and the dashboard quick-action button, causing Playwright strict-mode failure.
   - Scope the click to the intended navigation or main-region control.

The exact two-spec command is the required tight feedback loop. Run it outside the coding sandbox
after the selector repair; do not reinterpret these as missing-browser or product/backend failures.
