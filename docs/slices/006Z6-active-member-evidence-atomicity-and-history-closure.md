# Slice 006Z6: Active-Member Evidence Atomicity and History Closure

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Make 006Z5's effective status source-complete and concurrency-safe: one shared member authority,
immutable service/relaxation evidence in the result, and chronologically valid effective history.

## Depends On
- 006Z5

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Source / Review References
- `docs/source/functional-spec.md` BR-003 through BR-007 and M02-FR-004 through M02-FR-006
- `docs/source/data-model.md` §10.2-§10.3, §11.5-§11.6, and §34
- `docs/source/codebase-design.md` §10.2, §22.1, §26.1-§26.3, §27.1, and §42.2
- `docs/source/auth-permissions.md` §12.2, §25.1, and §34.2
- `docs/slices/006Z5-active-member-evidence-and-verification-governance-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_234227_architecture_review`

## Scope

- Extract/expose one member-owned object-authority evaluator used by `MemberRegistry` and active-
  status projection/write. Remove active-status role hard-coding and prove identical results for
  owners, globally authorised staff, permission denials, and object denials.
- Include every qualifying `MemberServiceEvidence` fact in the deterministic result and persisted
  evidence snapshot: row ID, type, service dates, recipient type/ID, evidence reference, verifier,
  and verification time. These facts must participate in `result_id`; changing any review-relevant
  fact makes a prior result stale.
- Require source-backed relaxation evidence distinct from a free-text decision reason. Persist and
  snapshot the qualifying one-year supply plus the relaxation evidence summary/reference; reject a
  relaxation decision that has only reason text.
- Lock or version the exact supply/service evidence set used during verification. A concurrent
  evidence create/update/verify and active-status verification must produce one coherent winner;
  stale evidence cannot become the current status and loser transactions write no record/history/
  audit evidence.
- Enforce chronological effective ranges. A new record must start after the current record's
  `effective_from`, or follow an explicit non-destructive same-date replacement rule; never write
  `effective_to < effective_from`. Preserve all closed records byte-for-byte.
- Complete separate module/API rows for missing/future date, malformed/unknown fields, permission,
  object scope, maker-checker, stale member version, stale result/evidence, repeat, unsupported
  decision, missing reason/evidence, active/inactive/relaxation success, and zero failure evidence.

## Test Cases

- BR-006 result and stored record contain the complete dated service-evidence row; changing any
  evidence fact changes the result and invalidates the old verification request.
- One-year relaxation fails with reason-only input and succeeds only with persisted, snapshotted
  relaxation evidence plus one complete qualifying supply year.
- Backdated/same-date/later decisions preserve valid non-overlapping ranges and immutable prior rows.
- PostgreSQL verifier-vs-supply/service mutation races yield one coherent current record/pointer and
  zero loser evidence; retain and run the existing verifier race plus five credit races twice.
- Member Registry and active-status checks consume the same public member-authority result for the
  full permission/object-role matrix and equivalent missing/existing out-of-scope IDs.

## Evidence Required

Failing service-snapshot, backdated-history, shared-authority, and evidence-race logs; green full
module/API matrices; effective-history example; portal-redaction table; two PostgreSQL race runs;
dependency scan; and all configured gates.

## Risk Level
High

## Acceptance Criteria

- M02-FR-004..006 and BR-003..007 resolve from one immutable, reviewable, dated evidence snapshot;
  reason text alone cannot create relaxation evidence.
- Verification is object-consistent, evidence-atomic, chronologically valid, and concurrency-safe,
  while portal/borrower projections remain deliberately redacted.
