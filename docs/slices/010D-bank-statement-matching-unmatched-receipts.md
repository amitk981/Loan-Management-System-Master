# Slice 010D: Bank Statement Matching and Unmatched Receipts

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Import manual bank-statement evidence into traceable lines, match only unambiguous receipt facts, and
route missing or conflicting evidence to an auditable reconciliation queue.

## User Value
Treasury and Accounts can reconcile receipts without double-consuming a bank line or guessing which
borrower should receive credit.

## Depends On
- 010C

## Source References
- `docs/source/user-flows.md` §§27.4, 28.4
- `docs/source/functional-spec.md` M09-FR-007–009
- `docs/source/data-model.md` §19.5 (`bank_statement_line_id` owner link)
- `docs/source/implementation-roadmap.md` §§15.2–15.4
- `docs/source/screen-spec.md` S44–S45
- `docs/source/test-plan.md` MOD-REP-010, API-REP-006/007, INT-SUB-004/005/007
- `docs/source/security-privacy.md` §22.2
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010D

## Concrete Requirements
1. Add bounded manual statement-upload and statement-line persistence sufficient to retain source
   file/evidence identity, SFPCL bank account, transaction/value date, amount, narration, reference,
   parse status, match status, and audit timestamps. Do not store more raw bank data than required.
2. Define permission-scoped upload/list/match/unmatch-or-exception APIs in the repository API contract;
   use existing document/storage and idempotency seams instead of a new file store.
3. Candidate matching may use exact UTR/reference, amount/date, borrower name, and loan
   application/account reference. Auto-match only a singular high-confidence candidate; ambiguous,
   missing, parse-failed, or conflicting lines remain `unmatched`/`exception` with safe reason codes.
4. An authorised manual match requires a chosen receipt/account, reason, actor, and audit evidence.
   A line and receipt cannot each be matched to more than one counterpart unless an explicitly
   approved split policy exists; no such split policy is introduced here.
5. Matching links evidence only. It must not create a repayment, allocate money, alter balances, or
   mark SAP posted.
6. Enforce finance read/create scope and restrict statement contents from ordinary logs/responses.

## Scope Boundaries / Non-Goals
- No bank API/feed, OCR, fuzzy/ML matcher, automatic receipt creation, split transaction policy,
  repayment allocation, subsidiary-specific capture, SAP integration, or frontend wiring.
- Do not fabricate a match when borrower/application narration is absent.

## Acceptance and Reverse-Consumer Tests
- A valid fixture uploads into deterministic lines; an exact singular candidate matches; repeated
  import/request does not duplicate the statement or consume a line twice.
- Duplicate/ambiguous references, amount/date mismatch, missing borrower/application reference,
  malformed input, forbidden file, wrong permission, and cross-scope access stay unmatched or fail
  without financial mutation.
- Manual match captures mandatory reason/audit and concurrent attempts retain one counterpart.
- 010B receipts and 010C allocations/balances are byte-for-byte unchanged by match-only operations;
  the linked line remains visible from the receipt projection.

## Evidence Required
- RED/GREEN parser/service/API/permission tests using synthetic nonsensitive files, database uniqueness
  evidence, match/reconciliation response examples, PostgreSQL double-match race, audit evidence, and
  010A–010C reverse-consumer results.

## Risk Level
High

## Acceptance Criteria
- Statement lines have bounded provenance, singular safe matches, explicit unmatched exceptions, and
  no authority to move money.
- Statement data and manual decisions are permission-scoped and audit-visible.
- Required focused, contention, reverse-consumer, and full gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Substantive risks/decisions recorded in `review-packet.md` (and HANDOFF only when needed)
- [ ] Commit created only after passing gates
