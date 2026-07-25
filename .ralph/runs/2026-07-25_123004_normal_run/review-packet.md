# Review Packet: 2026-07-25_123004_normal_run

## Result
Ready for independent validation

## Slice
012F3-soak-and-stress-release-evidence-admission

## Delivered Behaviour

- Added the non-mutating `admit_release_evidence` management command and a deep validation owner
  under `performance_readiness`.
- Reconciles every 012F2 target/PERF row and all seven section-24.3 rows exactly once.
- Requires fresh post-012H staging identity, trusted interval proof, at least four sustained hours,
  passing thresholds, complete measurements, safe worker/Redis/database recovery, and 30 retained
  hash-valid raw JSON results.
- Separates agreed threshold authority from collector results: the command hash-checks an external,
  commit/environment-bound threshold manifest before exact matching and numeric comparison.
- Keeps complete synthetic parser fixtures visibly non-admissible and scans summaries/raw results
  for credential, URL, and live-PII shapes.
- Documents the stable command and evidence contract without altering the 012F2 command or schema.

## Current Admission Outcome

No real staging environment bundle or agreed-threshold release record was supplied. The command
returned exit 1 and wrote no admitted summary. `evidence/release-admission-status.md` records the
exact release blocker; `terminal-logs/environment-admission-fail-closed.log` records the bounded
command and explicit non-zero result. Existing bounded-local 012F2 and local 012H evidence was not
relabelled as environment evidence.

## Traceability

| Source requirement | Implementation | Verification |
|---|---|---|
| `test-plan.md` §24.3 requires seven soak/stress outcomes | Exact `PROBE_IDS` reconciliation plus existing probe outcome owner | missing/duplicate/outcome tests in `test_release_evidence_admission` |
| Sustained workflow runs four real hours | timezone-aware, non-overlapping interval calculation; caller duration must equal computed duration; minimum 14,400 seconds | `test_sustained_workflow_requires_four_nonoverlapping_real_hours` |
| Exact candidate/environment after smoke; every result fresh | commit/environment equality, staging/pass smoke, max-age and post-smoke checks for smoke and every result | identity, authority, candidate-smoke, per-result freshness, and timestamp tests |
| Reconcile §24.1 and PERF-001–010 thresholds/results | preserves 012F2 source loads/measures/source thresholds; independently hash-binds agreed thresholds and evaluates observations | reconciliation, agreed-threshold, threshold-breach, and reverse 012F2 tests |
| Worker/Redis/database failures block | existing typed probe outcomes are mandatory | `test_admission_rejects_skip_failure_or_recovery_loss` |
| Raw evidence is tamper-evident and safe | exact external manifest, bounded paths, byte/SHA checks, raw-to-summary reconciliation, recursive redaction | raw hash/path/content and sensitive-evidence tests |
| Synthetic fixtures are parser-only | separate synthetic seam always returns `release_ready: false`; production command rejects it | `test_complete_synthetic_fixture_is_validated_but_not_admitted`; command non-zero test |

## Focused Validation

- Final focused/reverse pack: 51 tests passed
  (`evidence/terminal-logs/backend-focused-final-green.log`).
- Slice admission suite: 19 tests passed
  (`evidence/terminal-logs/admission-tests-final.log`).
- 012F2 reverse consumer included and passed without command/schema changes.
- 012H health plus non-socket smoke command reverse consumers passed.
- Django system check passed; migration check reports no changes.
- Expected TDD red/green logs are retained under `evidence/terminal-logs/`.
- No frontend scope, browser acceptance, migration, dependency, or database write.

## Two-Axis Review

### Standards

The initial review found only run-artifact issues: disposable-worktree paths in red logs, incomplete
placeholders, and a fail-closed log without its command/exit. Paths are sanitized, this packet/risk/
summary are complete, and the admission log now records the bounded command, exit 1, and no output.
No implementation-file standards violations were found.

### Spec

The first review found four admission gaps: per-result freshness, collector-controlled environment
thresholds, unenforced measurements, and raw-to-summary mismatch. The follow-up also required fresh
candidate smoke and visibly non-admissible synthetic fixtures. All were repaired with retained
RED/GREEN tests. Final targeted spec re-review reported no remaining or new findings.

## Residual Release Blocker

Independent validation can validate and commit the admission mechanism. It cannot mark the release
ready without the owner-selected staging environment's complete four-hour/source-load bundle,
exact deployed identity, agreed-threshold manifest/hash, and retained raw files. 012I must remain
blocked until the production command emits `result=admitted`.

## Recommended Next Action

Run the orchestrator-owned High-risk backend lane. If the mechanism is green, retain the fail-closed
release status and obtain the real staging soak/stress bundle before selecting 012I.

