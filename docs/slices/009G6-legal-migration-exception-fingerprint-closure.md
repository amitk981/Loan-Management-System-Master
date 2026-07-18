# Slice 009G6: Legal Migration Exception Fingerprint Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Make the two retained disbursements-0005 legal-checklist exceptions exact over the complete before/
after `DocumentChecklist` model state, not only the changed constraint name.

## Depends On
- 009G5

## Source / Review References
- `docs/source/codebase-design.md` §§35-36 and 42
- `docs/source/data-model.md` §34
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-18_152831_architecture_review`
- Review probe `evidence/review-probes/review_contract_probes.py`

## Concrete Requirements
1. Retain the exact path/module/class/operation-index identity checks from 009G5 and additionally
   compare a canonical complete `DocumentChecklist` `ModelState` fingerprint before and after each
   historical exception. The only permitted difference is the one named constraint add/remove.
2. Reject an operation that also changes any checklist field, option, index, constraint definition,
   base, manager, table identity, or another model, even when the expected constraint-name delta is
   present. Do not trust operation-supplied descriptions or metadata as the fingerprint.
3. Keep legal 0015, disbursements 0005, physical schema, rows, ids, APIs, and checklist behavior
   unchanged; this slice changes only the executable ownership guard and its tests.

## Test Cases
- Copy the failing same-model review probe first: the exact retained class/path/index adds the
  expected constraint and one extra checklist option/field mutation, and the guard must reject it.
- One-field matrices cover fields, complete constraint definitions, indexes, options, bases, and
  managers; exact historical 0005 and a future legal-owned operation still pass.
- Re-run the 009G4 forward/reverse/reapply manifest, guard suite, migration sync, and zero-SQL legal
  anchor proof.

## Runtime Capabilities

none

## Database / Migration Impact
None.

## Risk Level
High

## Acceptance Criteria
- No changed `DocumentChecklist` footprint can hide behind either retained exception identity.
- Only the exact historical constraint transitions pass, with no schema or business-behavior change.

## Done Checklist
- [ ] Execution plan written
- [ ] Review probe written failing first
- [ ] Complete state fingerprint guard implemented
- [ ] Migration owner/manifest tests green
- [ ] Risk, evidence, handoff, state, and digest updated
- [ ] Commit delegated to the orchestrator after gates

