# 010F Repair Evidence

## Exact symptom

The focused command containing the three independently failing migration-test classes ran six tests
and produced six errors before repair. The retained raw output is
`terminal-logs/migration-worker-order-red.log`.

## Root-cause probes

Migration graph inspection showed `interest.0001_initial` in both legacy projection target lists.
In the credit projection, `EligibilityAssessment` resolved under `credit` rather than the intended
historical `applications` owner. In the witness projection, the supposedly pre-0012 `Witness` model
already contained the three verification fields. These results directly falsified a production table
or invoice-calculation defect and identified projection contamination.

## Closure

- `terminal-logs/migration-worker-order-green.log`: 6 tests, OK, exit 0.
- `terminal-logs/migration-worker-order-green-repeat.log`: 6 tests, OK, exit 0.
- `terminal-logs/interest-invoice-focused-green.log`: 6 tests, OK, exit 0.
- `terminal-logs/backend-check.log`: no system-check issues, exit 0.
- `terminal-logs/migrations-sync.log`: no model/migration drift, exit 0.

Full-suite and PostgreSQL closure remain independently owned by the Ralph orchestrator.
