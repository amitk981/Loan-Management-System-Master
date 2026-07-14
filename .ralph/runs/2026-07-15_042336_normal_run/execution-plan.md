# Execution Plan

Selected slice: 008K2-sensitive-security-contract-closure

1. Inspect the current encryption, CDSL, blank-cheque, security-package read, coordinator, migration,
   and architecture-regression seams, plus the focused review regressions that reproduce the gaps.
2. TDD confidentiality first: add a public encryption-token regression proving no plaintext suffix or
   metadata is recoverable; save RED output, implement a versioned opaque token, then save GREEN output.
3. TDD retained-data migration reconciliation: add/extend migration tests for CDSL and blank-cheque
   `field:v1` rows, then add one frozen migration that preserves row identity and lookup hashes while
   re-encrypting to the corrected version without plaintext evidence.
4. TDD blank-cheque PATCH semantics one behavior at a time through the public API: single/multi-field
   partial updates, omitted/null/unknown/immutable/empty/stale/cross-object/terminal/concurrent cases;
   merge each request into the locked current row and validate the complete candidate.
5. TDD finance-reader object scope and boundary proof: exercise documented state transitions and
   permission-only/inactive/unrelated/missing/stale denials across package, PoA, SH-4, CDSL, cheque,
   and checklist public reads; add both-direction executable import guards, forged-access rejection,
   duplicate-hash, masking, and reveal-owner regressions.
6. Run focused backend tests throughout, then Django check, migration sync, full backend coverage,
   frontend lint/typecheck/tests/build, and the declared PostgreSQL race suite twice. Save all command
   output under `evidence/terminal-logs/` and run plaintext scans over repository/database/evidence.
7. Perform the required standards/spec review, update API contracts and durable working docs where
   behavior changed, sharpen the next one or two eligible Not Started slices from already-opened
   sources, and finish changed-files, risk, review, summary, progress, handoff, state, and slice status.

Constraints: backend commands use `/Users/amitkallapa/LMS/.ralph/venv/bin/python`; no frontend design
or production UI changes are planned; no protected/source files, dependencies, git metadata, commits,
merges, or pushes will be modified by the agent.
