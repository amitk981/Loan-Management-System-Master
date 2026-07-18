# Review Packet: 2026-07-18_232234_normal_run

## Result
Ready for independent Ralph validation

## Slice
009H9C-communication-channel-interface-and-provider-evidence-closure

## Outcome

- Email and SMS now use distinct configured/manual/fake/future adapter contracts; provider SMS
  payloads include the frozen template code.
- Unsupported phone/courier and unsafe SMS requests fail before every persistent/audit side effect.
- Generic accepted delivery has one immutable provider-evidence row and exact crash/replay recovery.
- Generic and advice exact-key HTTP replays use `{idempotency_replayed, original_response}` from
  lock-protected retained truth.
- The source-shaped public facade signatures are frozen for create/send; batching, claims,
  provider calls, advice finalization, and safe evidence shaping remain behind the deep module.

## Traceability

- The source says Email and SMS require distinct `EmailAdapter.send_email` and
  `SmsAdapter.send_sms` seams (`codebase-design.md` §20.6; `integrations.md` §§10-11); the code routes
  by frozen Communication channel and includes SMS template identity, verified by
  `CommunicationChannelContractTests.test_sms_job_uses_only_sms_adapter` and the adapter-mode test.
- The source says SMS must exclude PAN, Aadhaar, full bank/cheque/IFSC/ciphertext values
  (`codebase-design.md` §40.2; INT-COMM-005); the dispatcher validates names and rendered values
  before writes, verified by the ten-plus-case zero-write SMS safety matrix.
- The source says duplicate keys return the original response (`api-contracts.md` §45.2); generic
  and advice replay classification is made under the dispatcher lock, verified by exact replay
  tests and the final PostgreSQL five-caller matrices (one original, four replays).
- The source says provider status is retained as integration evidence (`codebase-design.md` §42.4);
  the communications integration owner stores a singular immutable evidence record bound to job,
  Communication, channel, payload, key, actor, adapter, result, and acceptance time, verified by
  immutable/tamper/crash-replay and migration-backfill tests.
- The source says Celery tasks are thin wrappers (`codebase-design.md` §34); due iteration and safe
  evidence shaping live in the dispatcher, with static boundary and worker-runtime regressions.

## Two-Axis Review

### Standards

The independent standards review identified unlocked replay classification, missing SMS template
identity, an over-constrained provider ID, and placeholder run artifacts. All were resolved: replay
truth moved under the dispatcher lock, SMS payload gained `template_code`, provider IDs are scoped
by their one-to-one job evidence rather than globally unique, and this packet/risk/final evidence is
substantive. The communications-owned evidence row is the §42.4 integration evidence owner and is
documented in `API_CONTRACTS.md` and the epic digest.

### Spec

The independent spec review repeated the replay race and found missing rendered cheque detection,
an overbroad ciphertext heuristic, and partial dependency/leakage proof. All were resolved: the
PostgreSQL response-shape races pass, a standalone six-digit cheque case is blocked, the arbitrary
long-token heuristic was removed in favor of ciphertext markers/variable semantics, and static
caller-boundary plus SMS job-evidence leakage assertions were added. No scope creep was found.

## Verification

- RED/green logs: `01`-`08` in `evidence/terminal-logs/`.
- Final focused backend: `28-final-review-resolved-regression.log` — 113 tests, all green; 20
  PostgreSQL-only cases skipped under SQLite as declared.
- Final PostgreSQL Email/SMS caller/worker matrix: `26-postgresql-replay-races-run1.log` and
  `run2.log` — 8/8 green each. Advice replay/worker matrix:
  `27-postgresql-advice-replay-races.log` — 4/4 green.
- Django check: `29-final-django-check.log`; migration sync: `30-final-migration-sync.log`.
- The complete backend suite/coverage was deliberately not run locally per the run prompt; the
  orchestrator owns that authoritative gate.

## Recommended Next Action
Run the independent Ralph gates, then let the orchestrator commit and merge only if all pass.
