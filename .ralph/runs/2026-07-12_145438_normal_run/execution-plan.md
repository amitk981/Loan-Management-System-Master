# Execution Plan

Selected slice: 006Y7-member-registry-race-and-action-scope-closure

1. Add a public Registry authority matrix test that exercises create, update, get, identity-change
   request, projection, and approval directly, including an object-denied checker whose projected
   reason exactly matches the rejected write and leaves evidence cardinalities unchanged.
2. Run that focused test first and save the failing output under `evidence/terminal-logs/`.
3. Move the complete identity-approval predicate and six-field action projection into
   `MemberRegistry`; make both detail serialization and approval writes consume it, including exact
   permission, object scope, requester/checker, pending status, versions, and KYC state.
4. Add transaction-level duplicate-create and duplicate-approval race tests for PostgreSQL. Ensure
   uniqueness conflicts become field-level `ValidationError`s inside atomic Registry operations and
   assert exact member/request/history/audit cardinality.
5. Run focused SQLite tests and the PostgreSQL five-race acceptance suite twice, preserving red and
   green logs plus HTTP/masking/dependency evidence.
6. Run every configured backend and frontend gate, then complete Ralph evidence, changed-file,
   risk, review, summary, state/progress/handoff, slice status, epic digest, and next-slice
   sharpening artifacts.
