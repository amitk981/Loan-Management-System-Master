# Execution Plan

Selected slice: 008G2-stage4-maker-and-verification-contract-closure

## Scope and constraints

- Change only Stage-4 stamp/notary/signature/tri-party contracts in `legal_documents` plus the
  migration, tests, contract notes, and Ralph bookkeeping required by this slice.
- Preserve `docs/source/`, protected workflow files, checklist/package/repayment/file/readiness
  facts, and the existing v1 routes.
- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.

## TDD behavior sequence

1. Add one public-module regression proving a material stamp/notary editor becomes the current
   maker and cannot verify their own changed facts; save the failing RED output, implement the
   smallest maker-handoff/history change, and save GREEN output.
2. Add the equivalent signature capture/mismatch regression, including secondary-role identity and
   legacy-null denial; implement current capture-maker attribution and database integrity.
3. Add a public HTTP regression proving consumed borrower/nominee signatures cannot be rewritten
   after tri-party verification; implement immutable consumed-signature evidence and mutation guard.
4. Add transport/direct-module regressions for strict fields, dependency direction, permission-first
   denial, the `SIGNATURE_MISMATCH_UNRESOLVED` error, and the §6.3 tri-party action response; move
   shape parsing to HTTP serializers while keeping domain validation behind module interfaces.
5. Add direct ORM constraint matrices for new/current stamp, notary, and resolved-signature rows;
   create one migration that preserves honest nullable legacy history while rejecting invalid new
   evidence.
6. Replace metadata-only tri-party setup with a public generation-to-signature-to-verification
   tracer and extend the PostgreSQL five-worker exact/changed race to run twice with a complete
   attributable winner/loser ledger.

## Verification and closeout

- Run focused tests after every RED/GREEN cycle, then Django check, migration sync, full backend
  coverage, and all configured frontend build/typecheck/lint/test gates.
- Retain terminal logs, action/error examples, dependency proof, public tracer evidence, and twice-run
  PostgreSQL evidence in this run folder.
- Record changed files, risk, review traceability, API contract updates, assumptions if any, final
  summary, slice completion, state/progress/handoff, and sharpen the next one or two eligible
  Not Started slices using only already-open source material.
