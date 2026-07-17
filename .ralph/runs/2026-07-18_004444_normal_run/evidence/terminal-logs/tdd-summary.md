# TDD Evidence Summary

## Pending-age behavior

- RED: `pending-age-red.log` forced detail/queue reads from 10 to 11 seconds and detail reads from
  2 to 3 seconds. Both prior complete-payload assertions failed on that live value.
- GREEN: `pending-age-green.log` passed after isolating only pending age, preserving exact stable
  payload comparisons, and asserting valid non-decreasing live age separately.

## Parallel traceback behavior

- RED: `parallel-traceback-red.log` failed because the clean development requirements did not pin
  Django's traceback-pickling support.
- GREEN: `parallel-traceback-green.log` passed after pinning `tblib==3.1.0`; the test proves an
  assertion exception and non-null traceback survive a `RemoteTestResult` event pickle round trip.

## Focused gates

- `approval-routing-class.log`: 127/127 pass serially.
- `backend-infrastructure-class.log`: 7/7 pass serially.
- `django-check.log`: no issues.
- `migration-sync.log`: no changes detected.
- `dependency-check.log`: no broken requirements.
