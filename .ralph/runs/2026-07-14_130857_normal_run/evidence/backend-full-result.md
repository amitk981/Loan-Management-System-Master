# Backend full-gate result

Command used:

`/Users/amitkallapa/LMS/.ralph/venv/bin/python -m coverage run --source=sfpcl_credit sfpcl_credit/manage.py test sfpcl_credit.tests`

Observed result on 2026-07-14:

- 752 tests run in 195.889 seconds after the independent-review corrections.
- Result: `OK (skipped=23)`; skips are the expected PostgreSQL-only acceptance classes.
- Coverage report: 27,995 statements, 2,016 missed, 93% total. The test-file line map changed while
  the runner was already collecting, so the final DOCX/PDF replay-selector test was rerun separately
  and passed in `terminal-logs/24-docx-pdf-current-replay-selector.txt`.
- Required floor: 85%.

The complete per-file coverage table is retained in
`terminal-logs/23-final-backend-full-coverage.txt`.
