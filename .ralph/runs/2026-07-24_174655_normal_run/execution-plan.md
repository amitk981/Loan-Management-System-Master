# Execution Plan

Selected slice: 012F-security-privacy-regression-checks

## Boundary

Build one deterministic backend release-hardening command over existing public tests and
production configuration. Do not add a second authentication, authorisation, encryption, audit,
or storage subsystem, and do not repair unrelated product defects.

## Public interface

- `manage.py security_regression --output <path>` runs the fixed control matrix, production
  configuration probes, a tracked-file secret scan, and pinned Python/npm dependency audits.
- The command writes a secret-free JSON summary and exits non-zero for any mandatory failure,
  missing scanner, unexpected skip, malformed scanner output, or incomplete control mapping.
- A checked-in control matrix documents the exact existing Django test labels that provide
  evidence for `SEC-AUTH-001..010`, `SEC-AUTHZ-001..007`, `SEC-PII-001..012`,
  `SEC-WEB-001..010`, and `AUD-001..016`.

## TDD sequence

1. RED: command-level behavior test proves a controlled failed control returns non-zero and names
   the exact control without leaking scanner output. GREEN: add the minimal runner and command.
2. RED: summary contract test requires deterministic counts, approved skips, scanner versions, and
   a canonical SHA-256 hash. GREEN: implement canonical summary generation.
3. RED: matrix validation requires every source control exactly once and rejects unknown,
   duplicate, or missing mappings. GREEN: add the fixed control matrix and validator.
4. RED: production-settings probes reject missing/malformed secrets and insecure
   debug/host/origin/cookie/HTTPS/HSTS/tracer configuration. GREEN: harden the production settings
   module and add isolated probes.
5. RED: scanner orchestration fails visibly when a required scanner is unavailable or reports a
   finding, while summaries contain only counts/IDs/hashes. GREEN: add pinned scanner dependencies,
   deterministic arguments, and redacted result parsing.
6. RED: no-secret output scan rejects JWT/secret/PII-shaped values in command output and reports.
   GREEN: centralise redaction and safe result serialization.

## Files expected

- Backend regression runner/control matrix under `sfpcl_credit/security_regression/`.
- Django management command under `sfpcl_credit/shared/management/commands/`.
- Focused tests in `sfpcl_credit/tests/test_security_regression.py`.
- Production-only secure settings in `sfpcl_credit/config/production_settings.py`.
- Exact required scanner versions in the lane policy; unavailable or mismatched external scanner
  executables fail rather than entering the application dependency set.
- Slice evidence only under `.ralph/runs/2026-07-24_174655_normal_run/`.

No migrations, business APIs, frontend code, protected files, or source documents are in scope.

## Focused validation

- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.
- Save each focused RED and GREEN run under `evidence/terminal-logs/`.
- Run the new focused test module, existing production isolation/field-key tests, mapped security
  test labels as practical without launching the complete backend suite, `manage.py check`, and
  `makemigrations --check --dry-run`.
- Run the command failure demo and a real scanner-backed green lane once dependencies are available.
- Save the control matrix, production-setting negatives, scanner reports and hashes, no-secret
  scan, risk assessment, review packet, and final summary. Leave the full authoritative backend
  coverage lane to the orchestrator.
