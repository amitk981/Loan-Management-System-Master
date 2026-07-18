# Slice 009G5: Legal Migration State Guard Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Make 009G4's legal checklist migration-ownership guard genuinely fail closed and keep business-
specific ownership policy out of the shared package.

## Depends On
- 009G4

## Source / Review References
- `docs/source/codebase-design.md` §§6-8, 35, 36.1-36.2, and 42
- `docs/source/data-model.md` §34
- `docs/working/REVIEW_FINDINGS.md` entry for
  `2026-07-18_104345_architecture_review`
- Review probe `red-migration-owner-guard-bypass.txt` in that run's evidence

## Concrete Requirements
1. Replace the literal-string AST heuristic in `shared` with a legal-owned or test-infrastructure
   guard that evaluates actual Django migration state transitions. Shared code must contain no
   legal/disbursement filenames, model names, or allowlist policy.
2. For every non-legal migration, compare the projected legal model state immediately before and
   after each state-bearing operation. Reject any new mutation of `DocumentChecklist` regardless of
   module constants, helper functions, imported custom operations, subclassing, or operation-name
   spelling. Ordinary database-only `RunPython` work must not be misreported as a state mutation.
3. Allow only the two exact retained operation identities in disbursements 0005. The allowlist must
   be immutable, path/class exact, and incapable of blessing another file, renamed class, sibling
   operation, or changed target model.
4. Keep legal migration 0015 zero-operation and preserve its current graph, live checklist
   constraints, physical schema, rows, ids, and forward/reverse/reapply behavior. Do not change
   checklist APIs, statuses, aggregate truth, or production business behavior.

## Test Cases
- Copy the architecture-review module-constant probe failing first; add imported-operation,
  inherited-operation, helper-indirection, renamed-path/class, and changed-target variants. Every
  real cross-app legal checklist state mutation is reported with its exact migration/operation.
- Prove the two historical disbursements 0005 operations alone pass and that a legal-owned future
  operation is accepted.
- Re-run the complete 009G4 anchor manifest plus adjacent migration-isolation tests and migration
  sync; assert the replacement guard introduces no model/schema/data SQL.

## Runtime Capabilities

none

## Database / Migration Impact
None. This is an executable test/ownership-boundary correction; legal 0015 and applied migration
history remain unchanged.

## Risk Level
High

## Acceptance Criteria
- The review probe and indirection matrix pass against the real migration graph, while only the
  exact historical exception remains allowed.
- No business-specific dependency points from `shared` into legal/disbursement concepts.
- Current legal checklist state/schema/rows remain byte-for-byte equivalent through the retained
  forward/reverse/reapply proof.

## Done Checklist
- [ ] Execution plan written
- [ ] Failing guard-bypass tests written first
- [ ] State-transition guard implemented at the correct owner/test seam
- [ ] 009G4 migration manifest and adjacent isolation tests green
- [ ] Django check and migration sync green
- [ ] Risk assessment, handoff, state, digest, and evidence updated
- [ ] Commit delegated to the orchestrator after gates
