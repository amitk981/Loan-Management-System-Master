# Execution Plan

Selected slice: 008D2-stamp-notary-verification-authority-closure

1. Preserve the public §26.9/§26.10 routes while introducing a legal HTTP serializer seam for
   exact request shape/type/date/decimal/enum parsing. Keep the `stamp_notary` module interface
   authoritative for direct callers and centralise action/role decisions in
   `legal_documents.modules.document_authority`.
2. Use vertical TDD cycles through the HTTP and direct module interfaces: first reproduce adverse
   outcome and downgrade authority failures; then require a distinct retained preparer before any
   Company Secretary verification and prove maker/checker replay and attribution; then relocate
   notary upload policy behind a generic immutable documents provenance fact and prove malformed,
   duplicate, changed, wrong-category, and cross-application evidence fails closed.
3. Add the smallest migration needed to retain preparer identity and to constrain every checker-
   owned positive/adverse state to a verifier. Preserve one current row, all audit/version/workflow
   history, renderer targeting, projection atomicity, and exact replay zero-write.
4. Extend the authoritative PostgreSQL five-worker race to changed Company Secretary decisions
   after a separate Compliance preparation, with attributable winner/loser ledger evidence.
5. Run scoped red/green tests with the mandated backend interpreter, then Django check, migration
   sync, full backend coverage, and all configured frontend build/typecheck/lint/test gates. Save
   terminal evidence and API/dependency proofs in the run folder.
6. Update API working contracts if the additive response attribution is documented, sharpen the
   next one or two Not Started slices using already-open Epic 008 material, and finish Ralph state,
   progress, handoff, changed-files, risk, review packet, and final summary artifacts.
