# Execution Plan

Selected slice: 006Z4-active-member-rule-and-snapshot-closure

## Public interface and invariants

- Deepen `members.modules.active_member_status.ActiveMemberStatusModule` as the single member-owned
  calculate/verify seam. Calculation returns a dated, immutable, complete row/result projection;
  verification owns authority, object scope, maker-checker, optimistic locking, reason, audit, and
  history behavior.
- Keep supply capture/verification HTTP adapters thin and preserve the standard error envelope and
  six-field action projections.
- Make `as_of_date` authoritative against the last completed financial year. Every persisted row
  remains visible, with a stable `qualifying` flag and `non_qualifying_reason`; only qualifying rows
  contribute to continuity and totals.
- Persist the complete active-member result used by credit so eligibility readback is unchanged if
  member facts later change. Portal output consumes the same row projection and remains scoped only
  through the authenticated `PortalAccount`.

## TDD tracer bullets

1. RED/GREEN: add a public-module regression for six qualifying years split across three clusters;
   retain all six rows and report longest uninterrupted continuity of three.
2. RED/GREEN: add the dated/rule matrix for exact four-year individual and institution paths,
   future/incomplete/malformed/pending/evidence-free/wrong-route rows, service false/missing,
   individual three-year service alternative, inactive member, Producer Institution routing, and
   recorded one-year relaxation.
3. RED/GREEN: add public verification/API authority tests for permission, member/object mismatch,
   maker-checker, required reason, stale version/result, repeated decision, and zero loser evidence;
   retain a PostgreSQL transaction race acceptance that is authoritative only on PostgreSQL.
4. RED/GREEN: add portal contract tests proving every row carries its canonical classification,
   totals use qualifying rows only, and protected/member IDs plus staff actions/cross-member facts
   stay absent.
5. RED/GREEN: add credit integration/readback proof that the exact dated active-member result and row
   evidence snapshot survives later member supply changes.

## Implementation and documentation

- Make the smallest model/migration changes needed for dated verified results and credit-owned JSON
  snapshot persistence, respecting the one-migration limit and transactional integrity.
- Move/replace scattered supply verification logic behind the public module rather than layering a
  second implementation; callers may retain compatibility wrappers only when needed by established
  imports.
- Update `docs/working/API_CONTRACTS.md` and the Epic 006 digest with dated, classification, and
  snapshot fields. Record only source-silent technical defaults in `ASSUMPTIONS.md`.

## Verification and evidence

- Save failing-first and green focused logs under `evidence/terminal-logs/`, using only
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for backend commands.
- Run focused module/API/credit tests, dependency scans, the declared PostgreSQL five-race suite
  twice where the configured database is available, then all configured frontend/backend gates.
- Save API examples, changed-files, risk assessment, review packet, final summary, and update Ralph
  progress/state/handoff/slice status only after green gates.
- Before completion, sharpen the next one or two Not Started slices using already-open Epic 006
  sources/digests without changing any other slice status.
