# Execution Plan

Selected slice: 012G-critical-e2e-uat-smoke-scenarios

## Repair boundary

- Preserve the existing candidate and repair only the trusted-browser validation domain reported
  by `.ralph/runs/2026-07-25_085034_repair/failure-summary.md`.
- Treat the first post-launch failure as authoritative: the DPD assertion expected
  `300000.00` on `2026-07-01`, while the public API returned `400000.00`.
- Do not change business logic, protected workflow files, source documents, or unrelated slices.

## Feedback loop

1. Confirm from the retained public scenario that the two `2026-07-25` repayments occur after the
   DPD calculation date and therefore cannot reduce principal paid as of `2026-07-01`.
2. Run the exact trusted browser command named in the validator log:
   `RALPH_EVIDENCE_DIR=... E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/critical-uat-smoke.e2e.spec.ts`.
3. Save the complete current-run output under `evidence/terminal-logs/`.

## Minimal repair and verification

- Retain the corrected assertion at the existing public E2E seam: `400000.00` overdue and
  `0.00` paid as of `2026-07-01`, while separately asserting the later direct allocation reduces
  current principal to `300000.00`.
- If the browser reaches the application and reveals another assertion in the same spec, fix only
  that bounded validation-domain error and rerun the same command.
- Run the focused backend seed test plus frontend typecheck, lint, and build only if the repair
  changes their respective files; the orchestrator remains responsible for authoritative
  independent validation.
- Save diagnosis, terminal evidence, risk assessment, and review packet. End with the review
  packet result exactly `Ready for independent validation`.
