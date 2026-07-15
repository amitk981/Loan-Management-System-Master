# Slice 007O: Frozen Terminal Decision and Register Source Closure

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007N

## Runtime Capabilities

none

## Goal

Make the final sanction decision and Credit Sanction Register consume only the approval case's
validated frozen review/provenance package, even when mutable application or appraisal rows change
after routing but before the terminal action.

## Source / Review References

- `docs/source/codebase-design.md` §§13.1, 26.1-26.3, 27.1, and 36.1
- `docs/source/api-contracts.md` §§25.4-25.10 and §44
- `docs/source/data-model.md` §§15.3-15.6 and §34
- `docs/source/functional-spec.md` M05-FR-007 and M05-FR-009
- `docs/slices/007K-frozen-review-snapshot-and-selector-boundary-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_034706_architecture_review`

## Concrete Requirements

1. The final approval transaction must derive sanctioned amount and every available sanction-
   decision copy field from the exact validated frozen case package. It must not read mutable
   `LoanAppraisalNote` or `LoanApplication` values to create the decision. Where no frozen source
   fact exists, retain the honest nullable/empty A-079 contract rather than copying live truth.
2. Credit Sanction Register generation must freeze application reference, borrower/name/type,
   requested/eligible/recommended amounts, purpose/risk facts, and decision data from the same
   case/cycle package and terminal ledger. A mutable owner-row edit before the last action must not
   alter the decision or register.
3. Re-run canonical frozen validity while holding the terminal action locks immediately before any
   decision/register write. Missing, malformed, or inconsistent frozen truth fails closed with no
   action, decision, register, notification, audit, or workflow write.
4. Route General Meeting availability and mutation through `approval_case_is_readable` so detail,
   approval actions, evidence actions, decisions, and registers consume one public readability
   decision rather than recomposing routability plus scope in individual modules.
5. Preserve historical cycle immutability, optimistic version handling, communication adapter
   atomicity, and the existing PostgreSQL final-action race semantics.

## Test Cases

- Route a valid case, record a partial approval, then directly change live appraisal amount,
  tenure/security, loan-limit JSON, application amount/purpose/borrower display, and risk before the
  last approver acts. The terminal decision/register equal the pre-mutation frozen package exactly.
- Repeat with a rejected case and prove register reasons/borrower/application facts remain frozen.
- Corrupt only the frozen package before the final action while leaving live rows valid and stored
  projection flags true; all terminal ledgers remain zero-write and counts disclose nothing.
- Static and behavioral matrices prove General Meeting and ordinary action paths call the single
  readable-case boundary and retain exact denial parity.

## Evidence Required

Backend RED/GREEN output for the between-routing-and-terminal mutation, zero-write malformed rows,
focused final-action regressions, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Mutable owner rows cannot change a routed case's terminal financial decision or formal register.
- Every action/decision/register path shares one frozen-readable approval boundary.
- Backend TDD evidence and all configured gates pass.
