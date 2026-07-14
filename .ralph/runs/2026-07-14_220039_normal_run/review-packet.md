# Review Packet: 2026-07-14_220039_normal_run

## Result

Implementation complete; all local configured gates pass. Independent Ralph validation and
orchestrator commit/merge/push remain pending.

## Slice

`008H-sh-4-physical-share-security-workflow`

## Review focus

- One `SH4ShareTransferForm` is owned by `security_instruments` beneath the retained package; the
  legal module supplies only current renderer/stamp/signature facts through selectors.
- §28.4 POST/GET/PATCH uses a strict lower request contract and authority-first thin HTTP adapter.
- Frozen `physical` is required; member/witness/shareholding/document/signature/stamp matrices fail
  closed. `invoked`/`returned` and their database facts remain unavailable.
- Compliance owns pending/signed facts; a distinct Company Secretary owns terminal custody and its
  durable §6.3 action. Exact replay is zero-write and terminal evidence is immutable.
- Checklist/security reads expose metadata only and preserve every completion/approval/readiness
  owner. The generic version ledger avoids a reverse `legal_documents -> security_instruments`
  model dependency.

## Traceability for non-developers

- The SOP says physical-share borrowers require an SH-4 signed by the shareholder and a valid
  witness and held in custody (V10 §4.5; digest `008H`). The code requires frozen physical mode,
  the sanctioned borrower, verified shareholder witness, active borrower physical shareholding,
  and exact signatures; verified by `SH4ApiTests`.
- API contracts §28.4 names the exact three routes and eight request fields. The code exposes those
  routes and rejects missing/unknown/forbidden fields; verified by the public create/read/custody and
  zero-write denial tests.
- Data model §17.3 names the SH-4 security table and invocation/return facts. The migration creates
  one protected form per package, positive nullable share count, bounded indexed status, and
  database-null later-lifecycle facts; verified by migration sync and the full suite.
- Auth §§12.8/16.4/25.6 says Compliance prepares, Company Secretary manages custody, and invocation
  requires later approval. The code preserves maker-checker identity and blocks invocation/return;
  verified by custody, legacy exclusion, authority-first denial, and both PostgreSQL race tests.

## Validation evidence

- TDD: `evidence/terminal-logs/tdd-cycle-{1,2,3}-{red,green}.txt`
- Focused/impacted: `focused-sh4-poa-tests.txt`, `security-boundary-focused.txt`, and
  `impacted-backend-tests.txt` (61 tests green).
- PostgreSQL: `postgresql-sh4-races-pass1.txt` and `pass2.txt` (two tests each, zero skips).
- Migration repair: `migration-regression-repair.txt`; migration sync reports no changes.
- Full backend: 819 tests, 34 expected SQLite skips, 93% coverage.
- Frontend: build/typecheck/lint green; 293 tests green; no frontend files changed.

## Recommended next action

Run independent Ralph validation, then let the orchestrator commit/merge/push. If green, execute
008I against the same package lock and projection invariants.
