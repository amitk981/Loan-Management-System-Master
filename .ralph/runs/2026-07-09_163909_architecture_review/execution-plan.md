# Execution Plan

Selected slice: architecture-review

Mode: architecture_review

## Permissions Check
- Allowed review/run artifacts: `.ralph/runs/2026-07-09_163909_architecture_review/**`.
- Allowed documentation updates: `docs/working/**`, `docs/slices/**`, `.ralph/progress.md`, `.ralph/state.json`.
- Forbidden/protected paths for this run: production code, `docs/source/**`, `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`, `.git/**`.

## Review Window
- Previous architecture-review commit: `fef0026`.
- Product slice commits to review:
  - `1544e88` - `004H2-kyc-profile-duplicate-create-contract-hardening`
  - `06d8655` - `004I-sensitive-masking-and-reveal-audit`
  - `127bf9d` - `004J-bank-account-and-cancelled-cheque-profile-foundation`
  - `9327696` - `004K-borrower-360-kyc-panel-and-masking-ui-wiring`

## Steps
1. Capture the review-window commit list, name-status diff, and focused diffs in `evidence/terminal-logs/`.
2. Read only the reviewed slice specs and the Epic 004 digest/source extracts already referenced by those slices.
3. Critique the merged diffs for test quality, doc fidelity, duplication, architecture drift, and functional-spec traceability.
4. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`.
5. Create or sharpen corrective slices for significant issues; otherwise sharpen the next 1-2 `Not Started` slices (`005A`, `005B`) using already opened digest/source requirements.
6. Run the required quality gates without changing production code.
7. Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, and terminal-log evidence.
8. Update `.ralph/state.json`, `.ralph/progress.md`, `docs/working/HANDOFF.md`, and the architecture-review run status.
