# Execution Plan

Selected slice: 011M2-member-portal-kyc-correction-request

## Demonstrated failure

The preserved candidate passed the trusted browser infrastructure probe, but the exact declared
Playwright spec failed because the configured Chrome process closed immediately during launch.
Neither trusted run completed, so neither required screenshot manifest was produced.

## Permission and scope check

- Allowed repair paths: `sfpcl-lms/**` and this run's `.ralph/runs/2026-07-23_104026_repair/**`.
- Preserve all existing product, backend, migration, documentation, test, and prior-run evidence.
- Do not edit protected workflow/configuration files or `docs/source/**`.
- Repair only the trusted browser-acceptance domain and every error subsequently exposed by that
  same validator.

## Bounded repair

1. Inspect the declared Playwright spec, shared E2E configuration, browser selection, seed/server
   lifecycle, and prior browser evidence without changing the candidate.
2. Reproduce the exact slice-specific E2E command as the red-capable feedback loop and retain its
   output in `evidence/terminal-logs/`.
3. Rank and test launch/lifecycle hypotheses one at a time; change only the smallest slice-owned
   browser test or frontend behavior required by the demonstrated validator.
4. Rerun the exact declared spec until it passes twice and writes the required
   `portal-kyc-correction-decision.png` evidence for both trusted runs.
5. Run the impacted frontend test/typecheck/lint/build checks only if product or test code changes.
   Do not rerun the complete backend suite.
6. Save browser evidence, risk assessment, review packet, and final summary. Set the review packet
   Result exactly to `Ready for independent validation`.
7. Leave full independent revalidation, mechanical bookkeeping, and commit handling to Ralph.
