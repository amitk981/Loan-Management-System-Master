# Review Packet: 2026-07-19_041708_architecture_review

## Result

Complete with significant Epic 009 closure findings; corrective 009L added.

## Slice

`architecture-review`

## Review Boundary

- Fixed point: `c90cb3263e3f5f34609baba3ba57ed67016b4768`.
- Reviewed product commits: `bc476293` (009H9D), `7e88fe42` (009J), and `eeb0ba7d` (009K).
- Diff command: `git diff c90cb326...HEAD`.

## Standards

- **Hard / High — authority bypass:** the disbursement workspace accepts raw
  `approval_authority_type` as CFC authority after the governed effective-role check can fail. This
  violates API §3/current-effective-authority and codebase-design §42. Tests omit the revoked or
  inactive governed-authority case.
- **Hard / High — false server-owned SAP action:** the workspace emits enabled completion with
  nonexistent `finance.sap_customer_code.complete` rather than `finance.sap_request.complete`, and
  turns optional completion fields into required fields. This violates the working SAP/action
  contract and codebase-design §42.
- **Hard / Medium — SAP owner seam bypass:** Loan Account 360 and the workspace import SAP models
  and reconstruct current-code/request truth rather than consuming the public SAP owner, contrary
  to codebase-design §16.1/§42 and 009B3C.
- **Hard / Medium — mixed real/fake account:** later Loan Account 360 tabs can combine the selected
  real account with `loanAccounts[0]` mock financial history and client calculations, contrary to
  the frontend mock ratchet.
- **Judgment / Medium — shallow reads:** both new coordinators project the complete portfolio before
  pagination and repeat per-row fetch/evaluation, contrary to bounded-selector guidance; one-row
  tests hide the cost.

## Spec

- **High — 009K is incomplete but Complete:** S36 requires Credit Manager create/send, while the
  workspace admits only Senior Finance/CFC and exposes completion only. The committed 009K packet
  itself records S36 open.
- **High — visual acceptance absent:** 009J and 009K each require four real-Django screenshots; both
  evidence packets retain none, so prototype fidelity and a real-backend walkable path are unproved.
- **Medium — Senior Finance can hit 500:** workspace admission requires initiate authority, then an
  uncaught internal loan-read exception can escape. No Senior Finance backend workspace test exists.
- **Medium — 009J rejects named source filters:** API §30.2 names search/status/member/DPD filters,
  while the implementation accepts only page/page-size without an explicit owner deferral.
- **Medium — 009J negative tests are partial:** most required creation/terms/SAP/transfer/activation/
  cross-object/balance drift cases are absent.
- **Medium — MP14 opposite-order regression remains open:** the required two finance-relevant rows
  in opposite orders are still not exercised.

## Local Architecture and Test Audit

- Direct contract inspection adds one executable-path fact to the independent reports: both
  disbursement pages forward `datetime-local` values unchanged, while SAP completion and transfer
  success reject naive timestamps. Mocked frontend tests therefore pass a wire shape the real
  backend rejects.
- Two review-only probes fail on their intended assertions: an admitted Senior Finance request
  returns 500, and an approved disbursement with incoherent immutable initiation evidence remains in
  the workspace. The real mutation owners still fail closed; no unauthorized transfer was proved.
- Epic traceability covers M07-FR-001-008/010 and M08-FR-001-011 in retained owners, but source
  M07-FR-009 (initial-loan-payment SAP entry) has no model/API/slice or explicit assumption.
- 009H9D closes all four findings assigned to it. Three current copied contract tests pass, along
  with 10 retained 009J/009K backend and 14 focused frontend tests.

## Corrective Work

- Added `009L-epic-009-staff-workflow-and-sap-posting-closure` as High risk, `Not Started`, with a
  valid dependency on 009K and a `localhost-e2e-server` browser contract.
- 009L groups S36-S41 reachability, exact action/authority/evidence parity, aware timestamp
  transport, M07-FR-009, SAP owner/query boundaries, 009J/MP14 negative coverage, and all missing
  visual evidence. This is one root-owner correction rather than multiple leaf patches.
- Added 009L to 010A's dependencies so Epic 010 servicing cannot build on an unclosed disbursement
  boundary. Existing 010M remains final owner for real servicing tabs.

## Convergence Metrics

- Findings closed: 4
- New Critical: 0
- New High: 3
- New Medium: 4
- New Low: 0
- Corrective slices added: 1

## Repository Health

- `docs/working/CONTEXT.md` remains truthful; no run-history append was needed.
- No slice is marked `Blocked`, so no prerequisite became stale.
- No ADR was added because the correction restores already-binding public-owner, source, and
  browser-evidence contracts rather than selecting a durable new architecture.
- Candidate changes are confined to review documentation, one corrective slice/dependency, and
  this run's evidence. Product code remains unchanged.

## Recommended Next Action

Run 009L before 010A and before any `staging` to `main` promotion. It must preserve the passing
009H9D/009J/009K behavior while closing the recorded source, authority, evidence, SAP-posting, and
trusted-browser contracts.

Standards: 5 findings, worst High false authority/action; Spec: 6 findings, worst High incomplete
S36-S41 and absent binding visual acceptance.
