# Execution Plan

Selected slice: 008I-cdsl-pledge-workflow

1. Preserve the `security_instruments` ownership boundary and extend the existing locked
   `SecurityPackage` aggregate with one protected CDSL pledge, bounded database constraints,
   masked BO-account serialization, and immutable terminal acceptance evidence.
2. Drive the implementation through public-interface TDD tracer bullets: first the demat
   create/read/replay path, then maker/checker acceptance and evidence projection, then strict
   validation/permission/reveal/rollback behavior, and finally the declared PostgreSQL five-worker
   create and changed-acceptance races. Save every red and green command output in
   `evidence/terminal-logs/`.
3. Add the exact §28.5 POST/GET/PATCH routes with authority-first parsing. Compliance owns current
   PRF preparation; a distinct Company Secretary owns terminal accepted/created verification.
   Reject invocation, unpledge, terminal downgrade, cross-application evidence, over-pledging, and
   all non-demat or non-canonical package use without success evidence.
4. Reuse repository protected-identity hashing/masking and legal-document provenance selectors.
   Add an audited, reason-bearing BO-account reveal action guarded by an explicit CDSL reveal
   permission; never put plaintext BO accounts into ordinary responses, audit/version/workflow
   metadata, or hashes.
5. Project only CDSL metadata/milestones into the existing package and checklist reads. Preserve
   PoA/SH-4/checklist completion and signatures, package status, share balances, file access,
   loan-account state, and disbursement readiness; ensure projection conflicts roll back the full
   pledge write and ledger.
6. Update the durable API contract and assumption ledger, generate one migration, run scoped tests
   after every tracer bullet, then run Django check, migration sync, the impacted suite, the full
   coverage suite, and all frontend build/typecheck/lint/test gates. Run the declared PostgreSQL
   races twice when the configured test database is available.
7. Save reviewable API examples and terminal evidence; complete changed-files, risk assessment,
   review packet, final summary, state/progress/handoff, selected-slice status, and sharpen the next
   one or two Not Started slices using only source material already opened.
