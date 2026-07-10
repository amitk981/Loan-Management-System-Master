# Execution Plan

Run ID: `2026-07-10_041851_architecture_review`
Selected slice: `architecture-review`
Mode: architecture review

## Scope
- Review only the four completed product slices since the prior architecture-review commit
  `353c6df`: `005G2`, `005H`, `005I`, and `006A`.
- Do not modify production code.
- Use committed slice specs, run evidence, digests, API contracts, targeted source references
  already distilled into digests, and the product diff from `353c6df...HEAD`.
- Append findings to `docs/working/REVIEW_FINDINGS.md` newest-first.
- Create or sharpen corrective / next not-started slices only if the review finds significant
  issues or clearer requirements from already-opened source/digest material.

## Review Steps
1. Confirm diff window and changed files with `git log 353c6df..HEAD` and
   `git diff --name-status 353c6df...HEAD`.
2. Inspect backend/frontend diffs and run evidence for:
   - test quality and red/green evidence;
   - source/spec fidelity against slice files and digests;
   - permission, audit, object-access, and side-effect guarantees;
   - duplication or architecture drift;
   - frontend design-rule fidelity for the 005I UI wiring.
3. Spot-check relevant implementation files and tests rather than reading broad source documents.
4. Run available quality gates as a non-production review check and save terminal logs.
5. Write required Ralph artifacts:
   - `changed-files.txt`
   - `risk-assessment.md`
   - `review-packet.md`
   - `final-summary.md`
   - evidence logs under `evidence/terminal-logs/`
6. Update Ralph working state:
   - `docs/working/REVIEW_FINDINGS.md`
   - `docs/working/HANDOFF.md`
   - `.ralph/progress.md`
   - `.ralph/state.json`
   - current/next slice status files as appropriate.

## Permission Check Before Edits
Planned editable paths are allowed by `.ralph/permissions.json`: `.ralph/runs/**`,
`docs/working/**`, `docs/slices/**`, and `.ralph/state.json`. Protected paths and
`docs/source/**` will not be modified.
