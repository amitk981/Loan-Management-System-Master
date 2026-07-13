# Execution Plan

Selected slice: architecture-review

1. Pin the review window at `git diff cea56b2...HEAD` and isolate the four product slices from
   intervening Ralph-orchestrator commits.
2. Review standards and specification fidelity independently against each slice contract, run
   packet, epic digest, cited source sections, implementation, and tests.
3. Inspect test assertion quality, edge cases, duplication, module boundaries, functional-ID
   coverage, repository context accuracy, and stale Blocked slices.
4. Append evidence-backed findings to `docs/working/REVIEW_FINDINGS.md`; create or sharpen
   corrective slices only for significant unresolved issues, and update digests/ADRs only when
   review conclusions require durable documentation.
5. Run the configured backend/frontend and Ralph documentation gates, save terminal evidence,
   changed-files, risk assessment, review packet, final summary, progress, handoff, and state.

Production code and protected files will not be modified.
