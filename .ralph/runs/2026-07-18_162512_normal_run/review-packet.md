# Review Packet: 2026-07-18_162512_normal_run

## Result

Implementation complete; independent Ralph validation and commit remain pending.

## Slice

`009H6-legacy-advice-template-provenance-closure`

## Traceability for a non-developer

- The source says disbursement advice must be sent after transfer, through template-backed,
  idempotent, safely retained communication evidence (functional BR-054/M08-FR-010; integrations
  §§10, 19.3, 21, 33.3). The code preserves every historical delivery fact but stops a later
  mutable template from being presented as the historical source. Verified by
  `LegacyAdviceTemplateProvenanceMigrationTests` and the coherent pre-outbox migration fixture.
- The slice says copied legacy template facts must be `legacy_partial`, never guessed. Migration
  0008 clears the mutable template FK, name/type/language/audience/version/approval/effective range/
  variables/source templates/checksum and records exact-legacy or honest-ambiguous origin. Verified
  by the template-drift, retained-outbox, pending, malformed, ambiguous, and post-0005 cases.
- The slice says legacy history cannot become replay, portal, or download truth and must not resend.
  The dispatcher requires frozen verified origin plus coherent checksum/attempt evidence; the
  portal artifact selector consumes that same interface. Verified by
  `test_legacy_partial_attempt_cannot_be_upgraded_or_redispatched` and
  `test_legacy_partial_advice_is_not_current_or_downloadable`.
- Data-model §34 requires atomic coherent evidence. The database constraints bind provenance
  origin, status, and complete/null snapshot shape; reverse refuses when losing that marker would
  make history unsafe. Verified by the status-flip IntegrityError and forward/reverse/reapply tests.

## Standards review

No production/test standard violation was found. Review identified in-progress Ralph bookkeeping
and a final evidence-format issue. Bookkeeping is complete, and the evidence issue was resolved by
adding terminal-generated raw RED/GREEN transcripts and replacing the duplicated GREEN prose with
an evidence index.

## Spec review

The first pass found four gaps: copied template facts remained, timestamp heuristics erased
ambiguity, coordinated provenance was under-constrained, and reverse coverage was partial. The
implementation was revised to clear guessed facts, classify attempt-less rows ambiguous, add
origin/status/snapshot-shape constraints plus runtime legacy-attempt rejection, and exercise genuine
legacy fail-closed reverse plus clean verified reverse/reapply. Re-review reported no remaining
spec-fidelity finding and no scope creep.

## Verification

- Four contemporaneous RED records plus a terminal-generated raw RED/GREEN reproduction are saved
  under `evidence/terminal-logs/`.
- Final provenance/migration/terminal group: 5 tests, OK.
- Impacted advice/portal/persistence group: 39 tests, OK.
- Retained migration cases: 2 tests, OK.
- Django check, migration sync, and compilation: OK.
- PostgreSQL acceptance: both two-method five-caller classes passed in two independent final runs.

## Recommended next action

Run independent Ralph validation and commit this slice; then execute 009H7.
