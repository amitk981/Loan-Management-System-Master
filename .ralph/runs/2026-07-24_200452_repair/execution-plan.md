# Execution Plan

Selected slice: 012F2-performance-readiness-evidence

## Repair boundary and permissions

- Preserve the uncommitted candidate from run `2026-07-24_191534_normal_run`.
- Repair only the demonstrated trusted-browser validator domain recorded in that run's
  `failure-summary.md`: the first browser execution and its two required screenshots/manifests.
- `.ralph/permissions.json` permits writes under this run folder and `sfpcl-lms/e2e/**`. Do not
  modify protected configuration, scripts, source documents, production UI, backend product code,
  mechanical state/progress/handoff facts, or the selected slice status.
- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command. Do not install
  dependencies, run the complete backend suite, or commit/add/push.

## Diagnosis and feedback loop

1. Re-run the exact trusted slice-specific browser command with this repair run's evidence folder.
   Treat it as the red-capable feedback loop because it launches the real configured browser,
   backend, frontend, authentication path, populated dashboard route, assertions, and screenshots.
2. If it fails, compare the browser-infrastructure probe, launch executable selection, server
   lifecycle, and the exact Playwright failure. Rank and test only hypotheses that distinguish a
   transient infrastructure launch from a defect in the slice-owned browser spec.
3. Make the smallest change in the trusted-browser domain only if the failure is reproducible and
   attributable to the candidate. Do not weaken latency, populated-state, role, route-count,
   screenshot-size, or two-repetition assertions.
4. Re-run the exact named browser validator until it passes and correct every newly exposed error
   from that validator. Retain the command output and both screenshots in this repair run.

## Completion evidence

- Record the diagnosis, exact command, validator output, screenshot hashes, and candidate diff
  inspection in this repair run.
- Update `risk-assessment.md`, `review-packet.md`, and `final-summary.md` with the bounded repair
  outcome. Set the review Result exactly to `Ready for independent validation`.
- Leave full independent revalidation, changed-files bookkeeping, status/state/progress updates,
  commit, merge, and push to the orchestrator.
