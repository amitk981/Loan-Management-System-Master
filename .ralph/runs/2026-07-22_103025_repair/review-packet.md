# Review Packet: 2026-07-22_103025_repair

## Result
Ready for independent validation

## Slice
011A-default-case-opening

## Failed Gate and Repair

The complete backend coverage lane exposed one error in the existing witness evidence migration
test. The new `defaults.0001_initial` migration is a leaf that depends on current loan state, which
transitively depends on `applications.0017`. Because the legacy test projected every non-excluded
leaf, its historical Witness model included `verification_folio_number` and later fields while the
physical table had been reversed to `applications.0011_witness`.

The repair adds `defaults` to the test's existing downstream-owner exclusion set. A focused graph
probe proved `defaults` was the sole included leaf pulling `applications.0012` through `0017` into
the pre-0012 projection; excluding it restored the exact `0011` Witness field set. No product
behavior or schema changed.

## Evidence

- RED: `evidence/terminal-logs/red-witness-evidence-migration.log` — the exact failed test reproduced
  the validator's missing-column error (1 test, 1 error).
- GREEN: `evidence/terminal-logs/green-witness-evidence-migration.log` — the exact focused behavior
  passed (1 test).
- Regression: `evidence/terminal-logs/migration-domain-regression.log` — the witness and credit
  ownership migration modules, 011A default-opening API module (11 tests total), Django check, and
  migration sync all passed.

## Traceability

The source contract says a missed principal repayment opens at most one default case and 011A owns
the new `defaults` model/migration (`docs/source/product-requirements.md` §11.26;
`docs/source/data-model.md` §21.1). The candidate implements that downstream owner. The repair keeps
the older witness migration test historically isolated so it continues to verify the original
pre-0012 backfill and reverse-preservation behavior as later owners are added. This is verified by
`WitnessEvidenceMigrationTests`, `CreditAssessmentModelOwnershipMigrationTests`, and
`test_default_case_opening_api`.

## Residual Risk

The authoritative complete-suite coverage lane was not rerun by the repair agent, per the Ralph
workflow. Independent validation must execute it and enforce the configured 85% floor. No other
known repair risk remains.

## Recommended Next Action
Run Ralph's independent validation against the preserved candidate; commit only if the complete
backend coverage lane and all other selected gates pass.
