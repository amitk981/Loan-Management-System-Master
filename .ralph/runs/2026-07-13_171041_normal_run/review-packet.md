# Review Packet: 2026-07-13_171041_normal_run

## Result

Success — ready for independent Ralph validation.

## Slice

`007E2-conflict-authority-projection-and-scope-closure`

## Standards review

- Deep module: one explicit approval-owned projection interface replaces hidden model-save
  cross-table mutation; views and callers retain their existing public interfaces.
- Transactionality: creation, linkage, enrichment, actions/abstention, and appraisal refresh call
  the updater inside their existing transactions. Migration-local backfill is deterministic.
- Data/API: immutable route and action ledgers remain unchanged; one migration tightens the reason
  constraint and rebuilds only derived reader rows. API additions are documented.
- Test quality: public HTTP/enrichment tests assert status, counts, authority identity, replacement
  attribution, action facts, no-sanction outcomes, and zero-write denials. Migration tests start
  from 0012 historical state.

## Spec review and traceability

- Auth §§16.2/27.1 and M05-FR-004..006 say exact CFO + Director counts; code fills distinct frozen
  user slots and blocks missing authority; verified by both public two-Director exclusion tests.
- Auth §§17.1-17.3 and security §§12.2-12.3 say conflicted actors are excluded, denied exactly, and
  audited; code evaluates real declarations/frozen maker facts and writes sole COI-006 denials;
  verified by the five-class public conflict matrix.
- API §25.4 and data-model §§15.3-15.4 say route and immutable decisions remain attributable; code
  exposes raw route, executable replacements, and every action; verified by collection/detail/
  action parity and route immutability tests.
- Auth §§32.1/37.3 say unassigned Directors disclose no object; code indexes only original,
  effective, or acted users before SQL counts; verified by unused-alternate declaration/count and
  migration tests.
- API §25.11/data-model §15.8 say Director/relative/committee borrowing triggers meeting evidence;
  code detects active borrower/relative declarations independently of assignment; verified by the
  noncommittee-related and public declaration matrices.

## Validation

- Backend: Django check and migration sync GREEN.
- Backend tests: 651 GREEN, 19 expected PostgreSQL-only SQLite skips; coverage 93% (floor 85%).
- Focused: 86 conflict/projection/migration tests GREEN; 112 broader approvals tests GREEN.
- Frontend: build, typecheck, lint GREEN; 208 Vitest tests GREEN.
- Diff: within 30-file/2,000-line/one-migration limits; no protected/source file changed.

## Recommended next action

Independently validate and let the Ralph orchestrator commit/merge. Then execute 007F.
