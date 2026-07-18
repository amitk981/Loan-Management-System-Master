# Slice 009G4: Legal Checklist Migration Ownership Anchor

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Restore legal-document schema-state ownership after 009G2 changed `DocumentChecklist` constraints
from a downstream disbursements migration, without replaying or weakening those live constraints.

## Depends On
- 009G3
- 009H3BB

## Source / Review References
- `docs/source/codebase-design.md` §§6-8, 21, 36.1-36.2, and 42
- `docs/source/data-model.md` §34
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_210855_architecture_review`

## Concrete Requirements
1. Add one legal-documents-owned state anchor whose dependencies include the current legal leaf and
   the disbursements migration that introduced the checklist constraints plus the current G3/H3B
   migration leaves. It emits no destructive table/data SQL and preserves exact live names.
2. Prove forward/reverse migration state retains `checklist_finance_requires_sanction` and
   `checklist_ready_evidence_complete` once, with no resurrection of either Epic-009 placeholder
   constraint and no change to existing checklist/action ids or rows.
3. Add an executable dependency guard preventing future migrations outside an app from mutating
   another app's model state through custom schema operations. Allowlist only the reviewed historical
   009G2 migration; future legal checklist changes live in `legal_documents/migrations`.
4. Do not change checklist behavior, statuses, APIs, production rows, or the 009G3 aggregate contract.

## Test Cases
- Migration graph/state tests start immediately before 009G2, migrate through the anchor, reverse,
  and reapply; compare constraint names, retained checklist/action facts, and physical schema.
- Static guard fails on a synthetic cross-app state mutation and passes the one named historical
  exception. `makemigrations --check` and impacted migration-isolation tests remain green.

## Runtime Capabilities

none

## Database / Migration Impact
Exactly one legal-documents migration. It is a state/dependency repair and must be zero-data-loss;
retain a SQL/state manifest in evidence.

## Risk Level
High

## Acceptance Criteria
- Future legal migrations inherit complete checklist state from the legal owner, and executable
  guardrails prevent recurrence without rewriting applied migration history.

## Done Checklist
- [ ] Execution plan written
- [ ] Failing migration/guard tests written first
- [ ] Legal state anchor added without destructive SQL
- [ ] Forward/reverse/state and migration-sync evidence saved
- [ ] Risk assessment, handoff, state, and evidence updated
- [ ] Commit delegated to the orchestrator after gates
