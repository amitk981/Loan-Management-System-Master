# Slice 008K3: Final Checklist Evidence Closure

## Status
Complete

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008K2

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Make every final-checklist completion and approval depend on current source-owned evidence with a
durable public action identity, then prove the full terminal matrix and winner/loser attribution.

## Source / Review References

- `docs/source/functional-spec.md` M06-FR-007 through M06-FR-019
- `docs/source/api-contracts.md` §§6-8 and 27.3-27.7
- `docs/source/data-model.md` §§16-17, 28-30, and 34
- `docs/source/auth-permissions.md` §§15.4-15.11, 16.4, 18-19, and 26.4
- `docs/source/codebase-design.md` §§9.1-9.4, 15.1-15.4, and 39.1-39.2
- `docs/slices/008K-final-documentation-approval-sequence.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-15_034859_architecture_review`

## Concrete Requirements

1. Company Secretary approval must lock the current checklist and require exactly one retained
   `item_completion` action for every current required/applicable complete item. Each action must
   match that item, its linked current-renderer document, verifier, completion time/remarks, current
   applicability cycle, and terminal-evidence digest. A status-only/bulk/stale row, extra action,
   missing action, changed link, or mismatched verifier is `EVIDENCE_BLOCKED` with zero writes.
2. Bind blank/cancelled-cheque completion to the current source-owned cheque and verified bank
   decision, not an arbitrary latest `VersionHistory` JSON row. Require exact application, package,
   member, bank-account, blank-cheque, cancelled-cheque, scan/document, custody workflow, preparer,
   custodian, and verification ids/statuses issued through the immutable cross-owner evidence
   interface. Reject synthetic, stale, superseded, cross-object, and partial ledgers.
3. Revalidate all other terminal item evidence at completion: exact ₹500 active PoA with current
   stamp/notary/execution facts; conditional verified tri-party; physical SH-4 custody or demat CDSL
   created/accepted; current borrower/nominee/witness/signatory identities; resolved mismatch; and
   current-renderer document checksum. For Term Sheet amounts above ₹5,00,000 require the frozen CFO
   plus two eligible frozen directors; at or below require the frozen CFO route. Preserve A-101's
   real-path configuration blocker rather than fabricating governed sanction terms.
4. Freeze the canonical role that actually authorised each item/approval action. Multi-role users
   must record the required stage role, not whichever effective role sorts first; later role/name
   changes cannot rewrite retained identity. Continue to require active, permission-bearing,
   distinct stage actors and the explicit one-eligible-director checklist signature rule.
5. Expand tests so every current applicable item completes through the public §27.3 API. Fixtures
   may create source-owned prerequisite aggregates, but must not bulk-update completion status,
   fabricate terminal version JSON, or bypass public completion in an ordered-approval success.
   Add adverse matrices for every terminal blocker and assert zero success evidence.
6. Strengthen exact replay and PostgreSQL races: bind the retained item/stage payload, request id,
   actor, workflow, audit, version, and action to the sole material winner; prove each changed loser
   has no success action/audit/version/workflow identity. Run item and all approval-stage races twice.

## Test Cases

- Public completion of every physical/demat, subsidiary, mismatch, cheque, stamp/notary/signature,
  Term Sheet threshold, Loan Agreement, and final-checklist item, followed by ordered approvals.
- Missing/extra/stale completion action, bulk status mutation, changed document/verifier/remarks,
  old applicability cycle, synthetic cheque ledger, wrong exact id, and cross-application evidence.
- Single- and multi-role CS/Credit/frozen-director authority, inactive/permission-only/wrong-role/
  unrelated cases, immutable canonical role/name, exact replay, and changed replay.
- Five changed concurrent completions and every approval stage twice on PostgreSQL with exact winner
  and per-loser zero-success evidence identities.
- No checklist path receives ciphertext/hash/reveal authority or changes package, bank, security,
  loan-account, disbursement, download, invocation, return, or readiness truth.

## Evidence Required

Failing-first regressions for status-only approval and synthetic cheque completion; public terminal
matrix responses; exact evidence reconciliation; focused/full gates; and PostgreSQL races twice.

## Risk Level
High

## Acceptance Criteria

- No checklist item or approval can be completed from forged, stale, or status-only truth.
- Every success has one current public action identity and exact source-owned terminal evidence.
- Role attribution and race winner/loser evidence are complete and immutable.
- All configured gates pass.

## 008K2 Completion Sharpening (2026-07-15)

- Consume only the coordinated K2 security evidence contract. Checklist completion must not receive
  encrypted BO/cheque fields, lookup hashes, display suffix storage, reveal callbacks, or caller-
  constructed evidence adapters; ordinary cheque evidence remains the fixed `******` mask.
- Reconcile a blank-cheque terminal item against the current locked cheque/package/member/bank/
  cancelled-cheque/scan/custody identities. K2 partial PATCH and its zero-write replay history are
  mutation history, not substitutes for the exact current terminal custody action.
- Preserve K2 finance object scope: Senior Manager Finance sees post-sanction checklist/security
  metadata only at `sanction_approved`; CFC remains denied until an Epic 009 disbursement-ready
  owner exists. No approval action may manufacture either read state.

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
