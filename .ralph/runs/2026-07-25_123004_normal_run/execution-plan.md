# Execution Plan

Selected slice: 012F3-soak-and-stress-release-evidence-admission

## Boundary

Implement only the non-mutating 012F3 release-evidence admission command and its
public validation seam. Preserve the 012F2 performance command/schema and the
012H candidate identity contract. Do not run load tests, deploy, change source
requirements, or manufacture environment evidence.

## Permission Check

- Allowed: `sfpcl_credit/**`, `docs/working/**`, and this run's
  `.ralph/runs/2026-07-25_123004_normal_run/**` evidence.
- Forbidden/protected and untouched: `docs/source/**`, `scripts/**`,
  `.ralph/config.yaml`, `.ralph/permissions.json`, `.codex/config.toml`,
  `.github/**`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, and the protected
  decision/approval/design documents.
- No frontend work, dependency installation, migration, external call, deploy,
  or Git mutation is required.

## Behavior-First TDD Plan

1. Inspect the existing 012F2 public schema/command and 012H smoke identity
   output, plus current test conventions and any environment bundle already
   present in committed run evidence.
2. RED→GREEN: require an exact, hash-valid, commit/environment-bound bundle
   containing all seven section-24.3 scenarios exactly once.
3. RED→GREEN one behavior at a time for four-hour trusted timestamp proof,
   freshness and identity, result/recovery/degradation failures, 012F2
   target/PERF reconciliation, duplicate/unknown/skip/partial rejection, and
   sensitive-evidence redaction.
4. Add the management command as a thin public adapter over the validator;
   prove non-zero failure and zero success using synthetic parser fixtures,
   while labelling synthetic fixtures non-admissible for release.
5. Locate and validate the real environment bundle if supplied. If none exists,
   retain an honest fail-closed admission result rather than fabricating a pass,
   and record that release blocker in the review evidence.
6. Run focused tests with the mandated Ralph Python interpreter, followed by
   Django check and migration consistency. Save red/green and negative-test
   transcripts under `evidence/terminal-logs/`.
7. Inspect targeted diff/stat, run a credential/PII redaction scan over the
   evidence, and complete `risk-assessment.md`, `review-packet.md`, and
   `final-summary.md`. Set the review result exactly to
   `Ready for independent validation` only when the implementation and focused
   gates are green.
