# Performance Readiness Lane

Slice 012F2 provides a deterministic, fail-closed evaluator for the source performance inventory.
It does not claim production capacity from a local run and cannot mark R8-AC-004 release-ready.

## Stable command

Run from the repository root with the Ralph backend interpreter:

```bash
/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py performance_readiness \
  --run-local \
  --results-output <raw-results.json> \
  --environment-output <environment-manifest.json> \
  --expected-commit <40-character-candidate-commit> \
  --matrix-output <scenario-matrix.json> \
  --output <performance-summary.json> \
  --max-age-seconds 86400
```

The command exits non-zero for a missing/duplicate/unknown scenario, malformed threshold or sample,
unsupported skip, failed measurement, unsafe environment field, stale evidence, or commit mismatch.
The matrix and output are canonical JSON; the summary includes a SHA-256 over its unhashed body.
`--run-local` executes the mapped Django public-boundary behavior tests in one isolated test
process, repeating each behavior four times (one cold warm-up plus three measured repetitions) and
timing each test independently through the dedicated timing runner. For admission of separately collected environment measurements, omit
`--run-local` and supply `--results` plus `--environment`.

## Measurement contract

`sfpcl_credit.performance_readiness.matrix.PERFORMANCE_SCENARIOS` is the executable matrix. It
contains exactly:

- `PERF-001..010`, with the source load and a bounded-local load;
- all twelve independent test-plan §24.1 targets, including Application Detail, Loan Account 360,
  Disbursement Readiness, and Capitalisation Dry Run; and
- all seven test-plan §24.3 probes.

Every row declares the public API/service seam, least-privilege role, synthetic dataset, warm-up,
repetitions, measure, threshold and source, and evidence authority. API rows use canonical
role/object scope. Async document, export, DPD, accrual, and capitalisation rows name their public
API or service entrypoints; no private task invocation or admin shortcut is admitted.

Fixed source thresholds are evaluated from the three warm samples by the lane (nearest-rank p95,
strict less-than); the retained first sample reports cold setup behavior separately. A
caller-supplied `pass` never overrides a computed breach. Where the source says
“agreed file-size target”, “agreed batch window”, or another environment-specific outcome, the
threshold remains `environment_bound` and the only valid bounded-local status is
`release-evidence-required`. Skips are not approved in this lane.

## Input and output schema

The results file is a JSON array with exactly one row per matrix scenario:

```json
{
  "scenario_id": "TARGET-DASHBOARD",
  "status": "pass",
  "samples": [0.41, 0.38, 0.43],
  "raw_result_sha256": "<sha256 of the retained raw result>"
}
```

Environment-bound rows use status `release-evidence-required`; an observed failure uses `fail`.
Samples must be finite non-negative numbers. The environment manifest contains only safe facts:
environment ID/class, exact commit, UTC generation time, deterministic seed, dataset counts, tool
versions, and optional operating-system/CPU/database/Redis/worker/frontend versions. Credentials,
tokens, live PII, connection URLs, and arbitrary fields are rejected.

The summary records versions, commit/environment, dataset counts, counts, computed observations,
failures, approved skips (always empty here), per-result hashes, and its own hash. Its best local
outcome is `bounded-local-pass` with:

```json
{
  "release_ready": false,
  "release_readiness_reason": "012F3_RELEASE_EVIDENCE_REQUIRED"
}
```

## Trusted browser smoke

The exact spec is `sfpcl-lms/e2e/performance-readiness.e2e.spec.ts`. It uses the real seeded staff
login and application shell, the existing populated Credit Manager dashboard pattern, and two
repetitions with equivalent dashboard request/card counts. It retains
`performance-readiness-dashboard.png` and `performance-readiness-dashboard-run-2.png`. It adds no
production UI, styling, performance-only state, test endpoint, or authority shortcut.

The seven §24.3 matrix rows additionally map to bounded public-behavior probes. Their result
validators fail closed on unstable memory/latency, storage instability, unacceptable audit queries,
an unresponsive API under export queue, duplicate worker output, unequal Redis-restart
system-of-record hashes or nonzero loss, and uncontrolled/unrecovered database pressure. These
local definitions and negatives do not replace the real environment operations required by 012F3.

## Mandatory 012F3 handoff

012F3 must run after deployment smoke and admit fresh evidence for the exact release candidate. It
must replace every `release-evidence-required` result with environment-bound, hash-valid evidence
and prove all seven §24.3 outcomes: four real hours of stable sustained usage, stable large-document
storage, acceptable large-audit queries, responsive API under heavy export queue, idempotent worker
restart, Redis restart with unchanged system-of-record hashes, and controlled database-pressure
degradation. It must reconcile all §24.1 and `PERF-001..010` results, elapsed times, loads, thresholds,
tool/dataset manifests, environment identity, and raw hashes. A local smoke, copied/stale bundle,
shortened duration, skip, synthetic clock, failed threshold, data loss, or wrong commit is not
admissible.

Sources: `docs/source/test-plan.md` §24.1–24.3; `docs/source/implementation-roadmap.md` R8-E5 and
R8-AC-004; `docs/source/screen-spec.md` §12.2; `docs/source/deployment-ops.md` §§7.3–7.6, 17, 24,
29, and 32–33.
