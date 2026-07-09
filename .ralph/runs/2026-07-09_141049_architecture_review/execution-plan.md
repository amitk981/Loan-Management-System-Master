# Execution Plan

Selected slice: architecture-review

Mode: architecture_review

## Scope

Review only the slices merged since the previous architecture review. Do not modify
production code, generated migrations, source documents, scripts, Ralph guardrails, or
frontend styling.

## Read Order Completed Before Review

- AGENTS.md
- docs/working/TOKEN_RULES.md
- docs/working/CONTEXT.md
- docs/working/AFK_RUNBOOK.md
- .ralph/config.yaml
- .ralph/permissions.json
- .ralph/state.json
- docs/working/HANDOFF.md
- docs/working/DECISION_POLICY.md
- docs/working/FRONTEND_DESIGN_RULES.md
- docs/slices/ index
- docs/working/digests/epic-004-member-kyc-master.md

## Review Steps

1. Identify the previous architecture-review run and the four completed slices
   since then.
2. Inspect each slice file, run evidence, relevant diffs, and targeted source
   fidelity material from the Epic 004 digest.
3. Critique test quality, doc fidelity, duplication, architecture drift, and
   implementation/deferral traceability.
4. Append findings, newest first, to docs/working/REVIEW_FINDINGS.md.
5. Create or sharpen corrective/future slices only if significant issues are
   found; otherwise sharpen the next one or two Not Started slices using
   already-opened Epic 004 digest requirements.
6. Run quality gates where applicable to this docs-only review and save logs.
7. Save required Ralph artifacts: changed-files.txt, risk-assessment.md,
   review-packet.md, final-summary.md, and update state/progress/handoff/slice
   status.

## Permission Check

Allowed edit targets for this run: .ralph/runs/**, docs/working/**,
docs/slices/**, and .ralph/state.json. Protected and forbidden paths remain
untouched.
