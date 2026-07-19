# Risk Assessment

## Classification

Risk: Medium repair to a High-risk slice.

The repair changes only historical migration-test setup. It does not alter production models,
migrations, transfer behavior, SAP posting behavior, permissions, frontend behavior, or external
integration semantics.

## Demonstrated failure and cause

`CommunicationReceiptOwnerMigrationTests` intentionally migrated the communications owner boundary
while pinning `disbursements` to migration `0007`. Its fixture invokes the current transfer-success
endpoint, which slice 009L correctly changed to use the SAP posting table created by disbursements
migration `0008`. The resulting historical schema/current-code mismatch raised
`OperationalError: no such table: initial_loan_payment_sap_postings`.

## Repair and residual risk

- The test now pins disbursements to `0008` on both sides of the communications migration under test.
  Only communications moves from `0003` to `0004` and back, preserving the test's owner-transfer scope.
- Exact RED and GREEN runs prove the failure and repair at the same test seam.
- All 10 tests in the migration-owner module pass, covering forward, reverse, and reapply behavior.
- Django check and migration-sync pass.
- Residual risk is low and limited to interactions visible only in the complete parallel suite. The
  orchestrator will rerun that authoritative suite under coverage before any commit.

## Safety controls

- No protected paths or `docs/source/` files were modified.
- No migration or production code was changed in repair mode.
- No network, external provider, deployment, git staging, commit, or push action was performed.
