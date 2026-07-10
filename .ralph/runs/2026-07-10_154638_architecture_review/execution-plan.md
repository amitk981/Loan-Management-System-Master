# Execution Plan

Selected slice: architecture-review

## Scope

Review the four product slices merged after architecture-review commit `c25fcfc` and through
`HEAD` (`005I3`, `005I4`, `006C2`, and `006D2A`) without modifying production code. Treat
intervening owner/configuration and E2E-baseline commits as context only.

## Steps

1. Pin the comparison range and inventory each in-scope commit, changed file, run packet, slice
   requirement, parent epic, digest, and cited source section.
2. Run independent Standards and Spec reviews in parallel. Standards covers test quality,
   duplication, module boundaries, architecture drift, and documented repository rules. Spec
   covers requirement/source fidelity, missing or partial behavior, scope creep, and functional
   requirement-ID disposition.
3. Reproduce and verify candidate findings against the actual code, tests, source extracts, and
   run evidence. Record the review window and self-contained supporting evidence.
4. Append the newest review entry to `docs/working/REVIEW_FINDINGS.md`. Create or sharpen
   corrective slices for significant confirmed issues, record an ADR only if a new durable
   architectural decision is needed, and sharpen the next one or two Not Started slices using
   source material already opened.
5. Run all configured backend and frontend quality gates plus integrity/protected-path checks.
6. Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, evidence,
   and update Ralph state, progress, and handoff to complete this architecture-review run.

## Guardrails

- No production-code, dependency, migration, source-document, or protected-file edits.
- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.
- Findings must cite concrete files/tests/source requirements and distinguish confirmed defects
  from watch items or judgment calls.
