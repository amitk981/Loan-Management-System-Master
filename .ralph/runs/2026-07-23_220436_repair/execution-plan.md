# Execution Plan

Selected slice: 011O-auditor-read-only-views

## Repair boundary

Repair only the demonstrated backend coverage failure in the compliance global-search permission
domain. Preserve the existing 011O candidate and do not change frontend, schema, routing, source
documents, protected files, or unrelated Epic 011 behavior.

## Permission check

- Allowed: `sfpcl_credit/**` and this run's `.ralph/runs/2026-07-23_220436_repair/**` artifacts.
- Forbidden/protected: `docs/source/**`, `scripts/**`, `.ralph/config.yaml`,
  `.ralph/permissions.json`, `.codex/config.toml`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`,
  `docs/working/HIGH_RISK_APPROVALS.md`, and `docs/working/DECISION_POLICY.md`.
- No git add/commit/push.

## Feedback loop and repair steps

1. Reproduce the exact failing behavior with the focused Django test
   `sfpcl_credit.tests.test_global_search_compliance.GlobalSearchComplianceTests.test_compliance_cfo_cs_and_auditor_permission_matrix`
   using the mandated Ralph Python interpreter; retain RED output.
2. Inspect only the implicated compliance search facade, scope guard, actor construction, and
   neighboring tests. Rank falsifiable hypotheses before editing.
3. Add or tighten the smallest regression assertion at the existing global-search seam if the
   current test does not fully express the required auditor scope contract.
4. Apply the minimum permission/scope fix and retain GREEN output from the focused regression.
5. Run the directly impacted 011O backend permission tests, then rerun the exact authoritative
   validator from the failure report:
   `/Users/amitkallapa/LMS/scripts/ralph-parallel-backend-coverage.sh
   /Users/amitkallapa/LMS/.ralph/venv/bin/python
   /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run
   sfpcl_credit 6 85`.
6. Save the exact validator output, inspect targeted diff/stat, confirm no debug instrumentation or
   forbidden changes, and complete `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
   Set the review-packet Result exactly to `Ready for independent validation`.
