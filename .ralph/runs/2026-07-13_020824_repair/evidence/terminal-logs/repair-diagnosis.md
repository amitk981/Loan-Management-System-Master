# Repair Diagnosis Evidence

Prior trusted command:

`RALPH_EVIDENCE_DIR=... E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/portal-application-limit-authority.e2e.spec.ts`

Observed twice in `2026-07-13_015523_repair`: all four tests timed out at
`getByRole('button', { name: 'New Application' }).click()` after 30 seconds. The sidebar action is
unconditional for a mounted borrower portal. Existing `portal-auth-interaction.e2e.spec.ts` proves
the real MP00 login path; the repaired fixture now uses that path.
