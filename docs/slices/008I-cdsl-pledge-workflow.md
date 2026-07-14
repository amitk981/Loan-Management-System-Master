# Slice 008I: CDSL Pledge Workflow

## Status
Complete

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Goal
Create and maintain the source-defined dematerialised-share CDSL pledge milestones for the one
sanctioned security package, with protected BO-account data, PRF/PSN/acceptance evidence, and an
explicit future-shares pledge obligation, without invoking or unpledging securities.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 008H

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Source References
- docs/source/implementation-roadmap.md section 13
- docs/source/api-contracts.md sections 26-28
- docs/source/data-model.md document/checklist/security tables
- docs/source/Final SOP - Loan Disbursement V10 (1).pdf
- docs/source/SFPCL_Loan Sanction- Doc & Disbursement-SOP_WhatsLoan-25052026.pdf

## Prototype Reference
- sfpcl-lms/src/pages/documentation/DocumentationHub.tsx
- sfpcl-lms/src/components/loan/DocumentChecklist.tsx
- sfpcl-lms/src/pages/borrower/portal/documents/*

## Screens Involved
None directly.

## Frontend Scope
None. DocumentationHub/security-package wiring remains owned by 008M; do not add mock or hidden UI
actions.

## Backend/API Scope
1. Add §28.5 `POST/GET /api/v1/security-packages/{security_package_id}/cdsl-share-pledge/` and
   `PATCH /api/v1/cdsl-share-pledges/{cdsl_share_pledge_id}/`, accepting exactly pledgor member,
   pledgee entity, pledgor/pledgee BO accounts, both DP names, PRF status, PSN, acceptance status,
   pledged share count, agreement number, pledge status, and evidence document id.
2. Refresh only the existing 008F package's demat requirement from 008C2 frozen share mode. `demat`
   requires CDSL; `physical` does not; missing/`mixed` remains a blocker and creates no pledge.
3. Keep one current pledge per package under the locked package row. POST/PATCH exact replay is
   zero-write; real changes retain old/new evidence. Do not implement invocation or unpledge.
4. Project pledge existence/milestones into existing checklist/security reads without completing
   the checklist or changing package/disbursement readiness.

## Database/Model Impact
Add §17.4 `cdsl_share_pledges` with one protected package and borrower, encrypted+hashed pledgor BO
account, nullable protected pledgee BO account, bounded/indexed PRF/acceptance/pledge states, unique
nullable PSN, positive nullable pledged count, agreement reference, protected evidence file, and
nullable CDSL/invocation/unpledge times. Constrain invocation/unpledge facts null until 011I. Retain
008F package/loan-account integrity and never add a local depository/subsidiary aggregate.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Require `security.package.read` for GET and `security.cdsl_pledge.manage` for mutation plus canonical
sanctioned package scope. Compliance Team prepares/submits PRF facts; Company Secretary verifies
pledgee/acceptance evidence. BO-account reveal requires an explicit sensitive-data reveal decision
and audit; ordinary reads return only masked values. Other document/security permissions imply no
pledge mutation or file access, and unrelated scope remains nondisclosing.

## Audit Requirements
Every real create/change writes attributable audit, version, and workflow evidence with application,
package, pledgor, PSN, agreement, evidence, maker/checker, request/network/role/team facts. Exact
replay/denial writes no success evidence. Every permitted BO-account reveal is separately audited.

## Validation Rules
- Applicable only to frozen `demat`; pledgor must be the sanctioned borrower with active demat
  shareholding. Do not guess `mixed` or use caller names as identity.
- Protect BO accounts using the repository encryption/hash conventions; never return plaintext in
  ordinary responses or evidence. Pledgee must be SFPCL, and both BO/DP facts required by the
  selected manual CDSL path must be retained before acceptance.
- PRF progresses through prepared/submitted; accepted/rejected requires retained PSN and a distinct
  Company Secretary checker after Compliance preparation. Accepted/created requires positive share
  count not exceeding the retained demat holding, the source-required future-shares obligation, a
  non-empty loan-agreement reference, and same-application evidence provenance.
- Preserve CDSL's manual/API-ready milestone model: PSN identifies the pledge request, acceptance is
  distinct from creation, and direct depository integration is outside this slice.
- Reject `invoked`/`unpledged` and non-null invocation/unpledge times with zero writes; 011I owns
  approval-backed invocation and closure-backed unpledge.
- Pledge creation never completes the checklist, invokes securities, changes share balances,
  creates a loan account, or makes the package ready for disbursement.

## Test Cases
- Demat create/read/change/replay, strict fields/state transitions, masked account responses, one
  pledge/unique PSN, and full attributable history.
- Physical/missing/mixed modes; wrong member/shareholding; malformed/duplicate BO hashes; missing
  PSN/agreement/evidence; over-pledged count; cross-application evidence; maker-checker violations.
- Compliance/Company Secretary/read-only/unrelated matrices plus audited explicit reveal and denial.
- Checklist/security projections preserve PoA/SH-4, completion/verifier/remarks/signatures, package
  status, file access, share balances, and readiness; projection conflict rolls back every write.
- Five concurrent create/change attempts retain one current pledge and complete history on PostgreSQL.

## Run-Ahead Sharpening (008G completion, 2026-07-14)

- Reuse the 008F package lock/serializer and 008C2 frozen share-mode owner; do not create another
  package refresh path or infer demat applicability from mutable shareholding alone.
- Treat §28.5 plaintext BO fields as write-only inputs. Reuse the existing masking/reveal/audit
  module rather than placing reversible secrets in serializers, logs, workflow metadata, or hashes.
- Keep the future-shares pledge obligation explicit in retained/audit truth even though §28.5 omits
  it from the request and §17.4 omits a column; record the exact governance mechanism in ASSUMPTIONS
  before implementation rather than silently hard-coding or dropping the SOP obligation.
- Preserve 008G tri-party verification and every earlier checklist/package projection. CDSL evidence
  is not subsidiary deduction authority and must not start repayment or claim documentation ready.

## Architecture-Review Sharpening (2026-07-14 19:20)

- Implement the pledge only in 008F2's `security_instruments` owner and preserve its canonical
  sanction/package lock. `legal_documents` may supply exact evidence provenance but must not own
  BO-account, depository, pledge, invocation, or custody decisions.
- A real PRF/BO/evidence change transfers current maker attribution before Company Secretary
  acceptance. Exact replay never transfers maker identity; a multi-role editor cannot approve the
  facts they changed.
- The declared PostgreSQL gate must exercise different PSN/acceptance payloads twice and prove one
  current pledge, unique PSN integrity, masked evidence, and a complete attributable loser ledger.

## 008F2 Completion Sharpening (2026-07-14)

- Add CDSL state beneath the retained `security_instruments` package and canonical sanction/checklist
  scope without recreating tables or changing active PoA/SH-4 facts. Keep request parsing in the
  security contract and authority-first HTTP adapter.
- Company Secretary acceptance returns one durable §6.3 action; replay is zero-write and downgrade,
  rejection, unpledged, or invoked changes conflict. Freeze consumed legal evidence through the
  shared terminal guard while preserving every existing package projection.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
High

## Acceptance Criteria
- The named capability works through the intended backend/API/frontend path, where applicable.
- Source-doc business rules are enforced or documented as assumptions.
- Permissions and audit expectations are tested when applicable.
- The implementation stays within one small Ralph slice.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Database rules followed, if needed
- [x] Permissions tested, if needed
- [x] Audit events tested, if needed
- [x] Visual evidence saved, if frontend (not applicable; backend-only slice)
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [x] Commit created only after passing gates (delegated to the Ralph orchestrator)
