# Slice 006Z5: Active-Member Evidence and Verification Governance Closure

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Make 006Z4's active-member result and verification source-faithful: object-scoped, fully evidenced,
effective-dated, and unable to grant BR-006 from an unsupported scalar alone.

## Depends On
- 006Z4

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Source / Review References
- `docs/source/functional-spec.md` BR-003 through BR-007 and M02-FR-004 through M02-FR-006
- `docs/source/data-model.md` §10.2-§10.3, §11.5-§11.6, and §34
- `docs/source/codebase-design.md` §10.2, §22.1, §26.1-§26.3, and §42.2
- `docs/source/auth-permissions.md` §12.2, §25.1, and §34.2
- `docs/slices/006Z4-active-member-rule-and-snapshot-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_220748_architecture_review`

## Scope

- Persist an effective-dated active-member verification record matching data-model §11.5: member,
  status (`active`, `inactive`, or `relaxation`), member type, service/supply route facts, continuous
  years, relaxation reason/evidence summary, verifier/time, and effective range. The Member's current
  pointer/projection may remain for compatibility but must reference the persisted record; do not use
  a result hash as a substitute for a verification record primary key.
- Expand each immutable supply-row snapshot with every classification input needed to review the
  result: entity type/id, route, producer-institution member reference, evidence reference,
  verification facts, financial year, and stable qualifying reason. Credit stores the exact complete
  internal snapshot. Portal/borrower projections continue stripping member IDs, evidence references,
  row IDs, verifier facts, and staff actions.
- Reuse the existing public member/Registry object-access evaluation for active-status verification.
  Permission alone is insufficient: out-of-scope existing and missing member IDs return the standard
  non-disclosing category before result verification.
- Require an explicit ISO `as_of_date`; reject missing/future dates and unknown fields with standard
  validation envelopes. Execute separate stale-member-version, stale-result, repeated-decision,
  unsupported-decision, missing-reason, permission, object, maker-checker, and success rows.
- BR-006 may pass only from persisted evidence of three continuous service/employment years to SFPCL,
  a subsidiary, or a step-down subsidiary. If current persistence cannot prove dates, continuity,
  recipient, and evidence, return `manual_evidence_required` and record the open governance gap;
  never treat `employment_or_service_years >= 3` alone—especially with service usage false—as proof.
- One-year relaxation requires a persisted relaxation reason/evidence record plus one completed
  qualifying supply year. Cover individual, FPC, and Producer Institution four-year/relaxation paths,
  inactive/manual/evidence-free results, and the exact M02-FR-004..006 stored facts.
- Keep verification plus current Member projection, history, audit, and effective-record writes in one
  transaction. PostgreSQL races assert one complete winner, one current effective record, immutable
  prior records on later decisions, and zero loser evidence. Re-run the existing five credit races.

## Test Cases

- Calculation matrix covers complete row fields, all member types/routes, gap/as-of boundaries,
  missing service evidence, BR-006 evidence/no-evidence, and persisted one-year relaxation.
- Verify projection/write matrix covers permission, object scope/non-disclosure, maker-checker,
  reason/date/payload validation, stale version/result, repeat, inactive/relaxation decisions, and
  exact zero-evidence failures.
- Existing and random out-of-scope member IDs must assert equivalent `403` error facts before
  verification-record lookup, matching the application-subresource non-disclosure pattern.
- Credit snapshot remains byte-for-byte stable after member/supply/status changes; portal responses
  expose classification summaries without internal IDs/evidence/verifier fields.
- PostgreSQL competing verifiers produce exactly one effective record/current pointer/history/audit
  winner and no loser evidence in two independent runs.

## Evidence Required

Failing-first object-scope/incomplete-snapshot/BR-006 logs, green module and API matrices, migration
and effective-history examples, portal redaction table, two PostgreSQL verification races, existing
five-race logs, dependency scan, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- M02-FR-004..006 and BR-003..007 are backed by persisted, dated, reviewable evidence rather than
  summary scalars or generic history JSON.
- Verification is permission- and object-scoped, non-disclosing, atomic, and concurrency-safe; credit
  and portal consume one complete internal result with deliberate external redaction.

## Run-Ahead Sharpening Review (006Y13, 2026-07-12)

- Mounted verification success must seed conflicting write-result/current-record projections and
  assert the effective record is rendered/consumed only after one canonical member/result read; no
  caller may merge the verification mutation response or infer current authority locally.
- The PostgreSQL request ledger must show one verification write followed by one canonical effective
  record read for the winner, with no duplicate write/read or loser evidence; retain exact object-scope
  non-disclosure before verification-record lookup.
