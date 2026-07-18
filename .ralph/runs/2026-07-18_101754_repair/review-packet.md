# Review Packet: 2026-07-18_101754_repair

## Result
Ready for independent revalidation

## Slice
009G4-legal-checklist-migration-ownership-anchor

## Demonstrated Failure and Cause

Independent coverage failed both cases in `CreditAssessmentModelOwnershipMigrationTests` because
the test's pre-move projected registry no longer contained `applications.EligibilityAssessment`.
The 009G4 legal leaf is now a descendant of current disbursement and communications migrations;
including that leaf made the historical projection inherit `credit.0001`, where the two assessment
models have already moved from applications to credit.

## Repair

The retained migration test now excludes `legal_documents` from its pre-move leaf projection,
alongside its existing downstream exclusions. This is test isolation only. The legal 0015 anchor,
migration ownership guard, schema, production rows, checklist behavior, API, and 009G3 aggregate
are byte-for-byte unchanged by the repair.

## Evidence

- `evidence/terminal-logs/tdd-red.txt`: exact `EligibilityAssessment` lookup failure.
- `evidence/terminal-logs/migration-projection-diagnosis.txt`: legal leaf included means zero
  application assessments; excluding it restores both expected historical models.
- `evidence/terminal-logs/tdd-green.txt`: both forward/reverse credit ownership cases pass.
- `evidence/terminal-logs/impacted-migration-tests.txt`: all 15 selected/adjacent migration tests
  pass in one database run.
- Django check, migration sync, and compilation logs are green. Complete coverage is delegated to
  Ralph's independent validator as required.

## Recommended Next Action
Run full independent revalidation and commit only if every configured gate passes.
