# Slice 008K5: Final Evidence Authority and Migration Closure

## Status
Complete

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008L3

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Close the independently reproduced Stage-4 bank-authority and borrower-safe reconciliation gaps,
restore legal-document migration ownership, and replace existence-only evidence claims with exact
public-path ledgers before the staff documentation hub consumes them.

## Source / Review References

- `docs/source/auth-permissions.md` §§19.2, 19.4, 20.1, and 26.4
- `docs/source/api-contracts.md` §§3, 6-8, 27, and 44
- `docs/source/data-model.md` §§16-17, 29-30, and 34
- `docs/source/codebase-design.md` §§6.2, 7.1-7.3, 9.2, 21, 26.3, and 36.2
- `docs/source/functional-spec.md` M06-FR-005, M06-FR-006, and M06-FR-018
- `docs/slices/008K4-current-evidence-and-security-read-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-15_181520_architecture_review`

## Concrete Requirements

1. Put immutable bank-verification decision creation behind canonical application object access and
   Stage-4 workflow scope inside the application-owned module. Compliance/Company Secretary role
   plus permission is necessary but never sufficient: missing, unrelated, pre-sanction, returned,
   closed, or otherwise non-documentation applications must be nondisclosing/zero-write and cannot
   leave a decision, audit, workflow, or version row that later becomes checklist truth.
2. Return the standard §6.3 workflow-action body from the bank-decision endpoint, including entity,
   previous/new state, workflow event, and `available_actions`, while retaining the decision id and
   source identities needed by the documented resource projection. Exact replay must not duplicate
   immutable evidence; changed requests cannot reuse retained evidence silently.
3. Repair `borrower_safe_completed_item_ids` so every audit, workflow, version, action, current
   renderer, terminal evidence body, and digest predicate is unconditionally evaluated. Parenthesise
   conditional expressions explicitly. Missing, extra, changed, deleted, cross-object, newer valid
   bank decisions, and tampered retained JSON must project the item non-complete without raising an
   internal error or exposing evidence.
4. Re-establish legal-document schema ownership after the cross-app 0016 operation. Add a
   non-destructive legal-documents migration/graph anchor that depends on the applied application
   migration and makes future legal migrations own `ChecklistAction.audit_log` and
   `version_history` state deterministically. Do not rewrite applied history or add duplicate
   columns; prove fresh install, forward plan, reverse plan to the supported boundary, and
   `makemigrations --check`.
5. Replace the 404-only finance-reader proof with real current PoA, SH-4, CDSL, blank-cheque,
   package, and checklist rows before and after documentation approval for every source reader role.
   Assert ordinary DTO allowlists and recursively scan for evidence blobs, request/network context,
   signer snapshots, internal action ids, hashes, ciphertext, storage keys, and plaintext.
6. Strengthen both generation-versus-completion/CS races to bind the sole winner's exact current
   document, request, checklist action, audit, workflow, version, and terminal digest and prove zero
   loser success artifacts. Run each five-worker changed race twice on PostgreSQL.

## Test Cases

- A Compliance/CS user cannot record a bank decision for draft, returned, unrelated, missing, or
  non-documentation applications; a canonically scoped Stage-4 case succeeds through the HTTP API.
- Changing only the completion VersionHistory request id/body, action-linked audit, workflow,
  terminal body/digest, or creating a newer current verified bank decision removes borrower-safe
  completion and blocks Company Secretary approval with zero new success evidence.
- Migration tests start from the pre-0016 graph and from current leaves without duplicate-column or
  missing-state failures; future legal state depends deterministically on the anchor.
- Every ordinary reader/state/instrument matrix uses real rows and returns only its allowlisted DTO.
- Both PostgreSQL race families retain exact winner identities and no loser ledger twice.

## Evidence Required

The two architecture-review probes GREEN unchanged; failing-first scope/envelope/migration/reader/
race probes; focused and full gates; migration plans; sanitized API examples; DTO scans; and both
declared PostgreSQL races twice.

## Risk Level
High

## Acceptance Criteria

- Immutable bank evidence cannot be created outside canonical Stage-4 object scope.
- Borrower/staff checklist truth rejects every changed durable or current-evidence fact.
- Legal schema ownership and future migration ordering are deterministic.
- Public reader and concurrency evidence proves exact production behavior, not existence alone.
- All configured gates pass.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Database rules followed, if needed
- [x] Permissions tested
- [x] Audit events tested
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
