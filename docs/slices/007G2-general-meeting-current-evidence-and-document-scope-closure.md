# Slice 007G2: General Meeting Current Evidence and Document Scope Closure

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007F2

## Runtime Capabilities

none

## Goal

Expose the applicable pending/rejected General Meeting outcome on the case being reviewed and
accept evidence documents only through the document owner's per-file access decision.

## Source / Review References

- `docs/source/api-contracts.md` §§25.4, 25.11, and §44
- `docs/source/data-model.md` §15.8 and §34
- `docs/source/auth-permissions.md` §§12.6, 17.2, 19.2, 19.4, 25.4, 32.1, 34.5, and 37.3
- `docs/source/functional-spec.md` M05-FR-012 and BR-032
- `docs/source/codebase-design.md` §§13.1, 26.3, 27.1, and 42.1-42.2
- `docs/slices/007G-general-meeting-evidence-for-special-cases.md` requirements 1, 3, and 4
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_200023_architecture_review`

## Concrete Requirements

1. The canonical case projection exposes the applicable unsuperseded General Meeting record while
   an evidence-required case is pending, including pending and rejected outcomes. Once a cycle is
   returned or terminal, it exposes only the record frozen on that cycle. Later application-level
   supersession must not rewrite historical case reads.
2. Collection, detail, action success, and final-gate error details use one source-shaped meeting
   projection and distinguish current-pending from cycle-frozen evidence without inventing client
   state. `POST /api/v1/loan-applications/{loan_application_id}/general-meeting-approval/` and the
   canonical case readers expose the same missing/pending/rejected/approved vocabulary, so the S24
   UI can render the gate before attempting final approval.
3. Replace the General Meeting module's direct `DocumentFile` permission/existence lookup with one
   document-owned access interface. Each notice, minutes, and resolution reference must prove the
   actor's document-read permission, access to the related loan application, allowed sensitivity/
   category/workflow scope, and same-application attribution. If current metadata cannot prove that
   relationship, fail closed; a global download permission alone is insufficient.
4. Keep all three document ids distinct and preserve exact replay/supersession. Per-file denial is
   nondisclosing and zero-write: no meeting row, audit, workflow event, case mutation, exception
   mutation, or document-download audit. Recording evidence never grants later document download.
5. Update `API_CONTRACTS.md`, A-085's resolution note, the Epic 007 digest, and 007I's run-ahead
   contract with the final current-versus-frozen field semantics and document access seam.
6. Consume 007F2's canonical coherent case projection without recomputing exception truth. Adding
   pending/rejected meeting evidence must preserve the independently authored
   `reason_for_approval` and `exception_reason`, the same-case Exception Register linkage, and
   ordinary/assigned visibility throughout the pending cycle.

## Test Cases

- Record pending, rejected, then approved evidence through the public endpoint and assert canonical
  list/detail/action/final-gate parity before and after each supersession.
- Return and final approval freeze the then-applicable row; later supersession changes only a later
  pending cycle and never historical detail or register references.
- Same-permission cross-application, disallowed-sensitivity/category, unrelated-file, missing-file,
  and unscoped-actor matrices deny each of the three document fields without disclosing which
  protected file exists and without writes.
- Public upload/reference path proves valid same-application documents can be recorded; no test
  bypasses the document access interface with direct unrestricted metadata fixtures.
- Run the current-evidence lifecycle on a real 007F2 above-limit case and prove meeting
  supersession never hides the case or rewrites either exception reason field/register identity.

## Risk Level
High

## Acceptance Criteria

- Pending and rejected General Meeting outcomes are visible on the case detail that must act on them.
- Every referenced evidence document passes the document owner's object/sensitivity decision.
- Historical cycle evidence remains immutable and all configured gates pass.
