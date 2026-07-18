# Test Evidence Summary

- SMS channel RED: `01-sms-channel-red.log` — SMS crossed `send_email`.
- SMS channel GREEN: `02-sms-channel-green.log`.
- Validation RED/GREEN: `03-channel-validation-red.log`, `04-channel-validation-green.log`.
- Provider evidence RED: `05-provider-evidence-red.log` — model absent.
- Provider/replay GREEN: `08-provider-replay-green.log`.
- Final focused regression: `28-final-review-resolved-regression.log` — 113 passed, 20 skipped.
- Final PostgreSQL generic Email/SMS response/claim races twice:
  `26-postgresql-replay-races-run1.log`, `26-postgresql-replay-races-run2.log` — 8 passed each.
- PostgreSQL advice replay/claim races: `27-postgresql-advice-replay-races.log` — 4 passed.
- Final Django/migration gates: `29-final-django-check.log`, `30-final-migration-sync.log`.

All backend commands used `/Users/amitkallapa/LMS/.ralph/venv/bin/python`. The authoritative full
suite and coverage floor are intentionally delegated to the orchestrator.
