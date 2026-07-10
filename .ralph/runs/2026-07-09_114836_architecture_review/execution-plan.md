# Execution Plan

Selected slice: architecture-review

## Permissions Check
- Allowed run artifacts: `.ralph/runs/2026-07-09_114836_architecture_review/**`.
- Allowed workflow docs for review output: `docs/working/**`, excluding protected decision/risk/design rule files.
- Allowed corrective planning edits: `docs/slices/**`.
- Allowed Ralph bookkeeping: `.ralph/progress.md`, `.ralph/state.json`.
- Forbidden/protected for this run: production code, `docs/source/**`, `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, and `docs/working/FRONTEND_DESIGN_RULES.md`.

## Review Scope
- Review the four slices completed since the last architecture review:
  - `004A-member-directory-api-and-ui`
  - `004B-member-profile-api-and-ui`
  - `004C-individual-farmer-and-fpc-profile-details`
  - `004D-nominee-validation-and-ui`
- Use their slice files, Epic 004, and the Epic 004 digest as the spec baseline.
- Inspect run evidence and diffs for test quality, source fidelity, duplication, architecture drift, frontend rule adherence, and requirement-ID handling.

## Steps
1. Identify the last architecture-review commit/run and collect the diff/log window for 004A-004D.
2. Read only the relevant completed slice files, run summaries, changed-file lists, review packets, and evidence indexes.
3. Spot-check implementation files touched by the reviewed slices where findings require code evidence.
4. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`; record no finding if the review is clean.
5. Create or sharpen corrective slices only for significant issues; otherwise sharpen the next one or two `Not Started` slices using already-opened Epic 004 digest/source extracts.
6. Run available gates appropriate for a docs/review-only run and save terminal logs.
7. Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; update progress, handoff, state, and slice status/bookkeeping.
