# Execution Plan

Selected slice: `011F-recovery-action-execution-shell`

## Repair boundary and permissions

- Preserve the quarantined 011F candidate and repair only the failed trusted-browser validation
  domain reported by the prior run's `failure-summary.md`.
- `.ralph/permissions.json` allows the slice-owned `sfpcl-lms/e2e/**` acceptance spec and this
  run's `.ralph/runs/**` evidence. Product source will not be changed unless the exact browser
  repro demonstrates a product defect. Protected files, `docs/source/**`, orchestrator-owned
  state/progress/status facts, and the prior run's mechanical artifacts remain untouched.
- The candidate is already at the 1,997-line product limit. Any repair edit must be minimal and
  must not broaden the slice or add a dependency, migration, styling pattern, or business rule.

## Feedback loop and diagnosis

1. Reproduce the reported spec failure with the exact validator environment and slice command:
   `RALPH_EVIDENCE_DIR=<run screenshots> E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/recovery-action-execution.e2e.spec.ts`
   from `sfpcl-lms/`.
2. If launch still fails, compare the slice run with the already-green central browser probe and
   the repository's Playwright configuration/working slice specs. Rank and test only hypotheses
   that distinguish the failed validator domain.
3. If the command reaches the page, treat its assertions and screenshot contract as the tight
   red/green loop. Change only the smallest slice-owned acceptance or product seam demonstrated
   by that loop.

## Repair verification and evidence

- Run the exact declared Playwright spec until it passes, then run it a second time because trusted
  browser acceptance requires two green runs with both declared screenshots.
- Retain both command outputs and screenshot manifests under this repair run's evidence directory;
  never fabricate browser evidence.
- Refresh `risk-assessment.md`, `review-packet.md`, and `final-summary.md`. Set the review packet
  Result to exactly `Ready for independent validation` only after the bounded browser domain is
  green. Independent Ralph validation remains responsible for the full authoritative revalidation.

## Diagnosis outcome

- The full prior validator log, rather than the agent-authored browser recovery log, is authoritative:
  trusted Chrome launched and both tests reached application behavior.
- The blocked fixture supplied an invalid empty pagination envelope (`total_pages: 0`), producing an
  error state instead of `Security Invocation Locked`.
- The approved fixture supplied only canonical recovery-action permissions, but those permissions
  were absent from the existing canonical-to-prototype navigation bridge, so the Company Secretary
  could not see `Default & Recovery`.
- The minimal repair corrects those two seams. Focused tests, typecheck, lint, build, and Playwright
  test collection pass. Actual browser launch is unavailable inside the agent sandbox; the trusted
  post-agent validator owns the required two green runs and screenshot manifests.
