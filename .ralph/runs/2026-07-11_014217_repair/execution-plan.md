# Execution Plan

Selected slice: `006G2-sanction-handoff-module-and-read-contract`

1. Diagnose the newest failed run and inspect its leftover worktree. Reproduce the static
   dependency-test failure with a focused Django test and retain the red output.
2. Reapply the slice through the current clean repair worktree: add the approvals-owned sanction
   handoff create/get/serialization interface, remove the concrete approvals-model import from
   credit, add the reload-safe read adapter, and preserve the existing transaction/lock order.
3. Add or restore focused contract tests first, including a repository-location-independent AST
   dependency assertion, canonical submit/read parity, malformed JSON, access/missing/repeat
   behavior, and atomic rollback failures. Save red and green logs.
4. Run the exact 006F4 PostgreSQL five-race acceptance command twice with zero skips, then run all
   configured backend and frontend gates using the mandated interpreter/tooling.
5. Update the API contract, epic digest, selected/next slice status and requirements, Ralph state,
   progress, and handoff. Produce self-contained API/dependency evidence plus changed-files, risk,
   review, and final-summary artifacts.

No frontend production change or database migration is planned. All edits are within paths allowed
by `.ralph/permissions.json`; protected and source-document paths remain untouched.
