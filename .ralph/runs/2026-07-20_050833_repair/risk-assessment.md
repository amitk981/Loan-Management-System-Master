# Risk Assessment

Risk level: High, inherited from slice 010E2.

- Selected slice: 010E2-effective-rate-versioning-and-borrower-notices
- Mode: repair
- Manual review required: yes; independent Ralph validation remains mandatory.

## Repair scope risk

The repair changes only two legacy migration-test projection filters. It does not alter production
models, migrations, APIs, financial rate behavior, borrower-notice behavior, or the preserved 010E2
implementation. The primary risk is masking a real cross-app migration defect. That risk is bounded
because the dependency probe showed `configurations.0006` legitimately pulls current application
and credit ancestors, while the migration operations do not touch the witness or credit tables.

## Regression risk

Excluding `configurations` is consistent with each test's existing exclusion of downstream owners
whose current leaves outrun the intentionally historical application schema. The exact five failing
tests now pass, and the selected slice's focused tests, Django check, and migration-sync check remain
green. Ralph's complete independent coverage run will verify that no other migration-test ordering or
parallel-worker interaction remains.

## Product risk unchanged

The original High financial, communication, concurrency, migration, and open-policy risks remain as
documented in the normal run's risk assessment. This repair neither broadens nor weakens their
controls.
