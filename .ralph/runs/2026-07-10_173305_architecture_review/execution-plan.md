# Execution Plan

Selected slice: architecture-review

## Scope

Review the four product slices merged after architecture-review commit `18d403e` and through
`HEAD` (`005I5`, `006D2B`, `006D3`, and `006E`) without modifying production code. Treat the
review boundary as `git diff 18d403e...HEAD` and assess each product commit against its slice,
epic digest, cited source requirements, and run evidence.

## Steps

1. Inventory the four commits, their slice specifications, run packets, changed files, tests,
   migrations, and relevant functional-requirement IDs.
2. Run the review skill's independent Standards and Spec reviews in parallel. Standards covers
   documented conventions, substantive tests and edge cases, duplication, deep-module seams, and
   architecture drift. Spec covers missing or partial requirements, scope creep, incorrect
   behavior, source fidelity, and explicit deferrals.
3. Reproduce every candidate finding against the actual implementation, tests, source excerpts,
   and saved evidence. Separate confirmed issues from watch items and judgment calls.
4. Append the newest-first entry to `docs/working/REVIEW_FINDINGS.md`; create or sharpen a
   corrective slice for each significant confirmed issue; add an ADR only if this review makes a
   new durable architectural decision.
5. Sharpen the next one or two Not Started slices from source material already opened, then run
   all configured backend/frontend gates and integrity checks without changing production code.
6. Save self-contained review evidence, `changed-files.txt`, `risk-assessment.md`,
   `review-packet.md`, and `final-summary.md`; update Ralph state, progress, handoff, digest, and
   applicable slice statuses.

## Guardrails

- Do not edit production code, dependencies, migrations, `docs/source/`, or protected files.
- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.
- Do not stage, commit, merge, or push; the orchestrator owns those actions.
- Cite concrete requirements and tests for findings; do not invent business rules.
