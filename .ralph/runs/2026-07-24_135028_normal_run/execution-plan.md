# Execution Plan

Selected slice: 012E3-field-encryption-key-separation

## Boundaries

- Extend `sfpcl_credit.shared.encryption`; do not introduce another encryption owner.
- Change backend/security behavior and operational working notes only. No frontend work, package
  installation, source-document edits, protected-path edits, or orchestrator-owned state/status
  bookkeeping.
- Preserve the existing masking/reveal audit contract and the CDSL/blank-cheque consumers.
- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.

## Behaviors and TDD Order

1. Inventory the real encrypted columns and current shared-encryption consumers, then add one public
   behavior test proving configured key validation and old-version reads without `SECRET_KEY`.
   Save failing and passing output.
2. Add one rotation-command behavior at a time: fixture re-encryption to the current version,
   reconciliation counts, then resumable/idempotent reruns. Cover every repository column that uses
   the shared reversible field format and preserve unknown/irreversible legacy identity tokens.
3. Add production-startup behavior proving missing/malformed dedicated field and lookup keys fail
   closed while explicit valid keys boot.
4. Add reverse-consumer regression tests for CDSL/blank-cheque reveal and member reveal audit
   behavior if existing focused coverage does not already exercise the versioned interface.
5. Document environment-variable custody, rotation order, rollback, and the requirement to retain
   every key version needed by database backups.

## Verification

- Run focused RED/GREEN Django labels after each behavior and retain terminal logs under
  `evidence/terminal-logs/`.
- Run focused encryption, rotation, settings-startup, CDSL/blank-cheque, and member-reveal
  regressions; run `manage.py check` and `makemigrations --check`.
- Do not run the complete backend suite or full coverage; independent validation owns the High-risk
  complete-suite lane.
- Inspect targeted diff hunks and protected-path status, then complete `risk-assessment.md`,
  `review-packet.md`, and `final-summary.md`. Set the review result exactly to
  `Ready for independent validation`.
