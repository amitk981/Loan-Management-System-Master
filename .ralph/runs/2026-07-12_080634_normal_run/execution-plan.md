# Execution Plan

Selected slice: 006Y-member-create-update-and-identity-governance

1. Confirm the existing member, KYC, permission, audit, envelope, and object-action seams against
   the slice and its cited source sections. Record any source-silent governance choice in
   `docs/working/ASSUMPTIONS.md`.
2. Add one migration for member change history, optimistic versioning, and any missing protected
   institutional-signatory identity storage required by the create contract.
3. Drive implementation through vertical red/green API tests: governed individual create, FPC
   create, ordinary PATCH, identity-lock rejection, explicit reverification, permissions,
   maker-checker/action parity, stale writes, masking, atomic no-write denials, and audits.
4. Implement POST/PATCH and reverification behind a transactional member application-service seam;
   retain the existing GET envelopes and expose the six-field authoritative action projection on
   member detail.
5. Update the durable API contract and Epic 004 digest, then run focused tests followed by backend
   check, migration sync, full coverage, and unchanged frontend quality gates.
6. Save red/green and request/response evidence, changed-files, risk assessment, review packet, and
   final summary; update slice status, Ralph state/progress/handoff, and sharpen the next two
   Not Started slices using only requirements opened during this run.
