# Risk Assessment

Risk level: High

- Selected slice: 009E4-source-bank-rationale-and-approval-evidence-closure
- Mode: normal_run
- Standing approval: active; no owner veto is recorded.

## Risk Surface

- Critical configuration governance controls the bank account from which disbursements originate.
- The slice changes retained audit/version attribution and adds one schema migration with a bounded
  protected rationale/context manifest.
- A false current decision could affect financial initiation; a plaintext rationale could leak bank
  or capability material; an invented approver would overstate governance.

## Mitigations Verified

- No role receives `config.source_bank_account.activate`; the catalogue test proves the Critical
  permission remains unassigned by default.
- Blank, over-500-character, control-character, long numeric bank-number, encrypted-token, and
  bank hash/ciphertext content are rejected before governance/version/audit writes.
- Canonical row, version, audit, request/network, author/role/team, effective-range, and predecessor/
  successor facts are digest-bound and reconciled before current resolution.
- Version rows retain the provisioner only as author. Reviewer/approver/reference/timestamp fields
  are empty, and migration 0005 clears the known legacy false claims without fabricating reasons.
- Six focused contract tests, a one-field tamper matrix, 42 downstream/catalogue tests, and both
  PostgreSQL five-caller race methods pass.
- Account ciphertext, hash, digits, capability material, and unrelated identity facts are excluded
  from the retained review manifest and test evidence.

## Residual Risk

- A-126 remains open because source governance has not named the business role allowed to provision
  the source bank. Production remains fail-closed until an explicit Critical grant is made.
- Legacy rows cannot recover a rationale that was never retained. They remain non-current rather
  than receiving fabricated history.
- The orchestrator still owns full backend-suite coverage, protected-path, queue, and migration
  validation before commit/merge.
