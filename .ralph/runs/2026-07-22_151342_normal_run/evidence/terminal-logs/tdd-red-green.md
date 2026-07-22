# TDD Red/Green Evidence

## Recovery decision tracer

RED command:

`/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_recovery_decision_api.RecoveryDecisionApiTests.test_matching_terminal_approval_creates_one_frozen_decision --verbosity 1`

RED result: exit 1. One test failed because the endpoint returned HTTP 404 instead of 200; the
public recovery-decision route did not exist.

GREEN command: the exact command above.

GREEN result: exit 0. One test passed in 0.775s; Django system check reported no issues.

## Existing approval-owner composition

RED command:

`/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_recovery_decision_api.RecoveryDecisionApiTests.test_existing_approval_owner_requires_every_distinct_recovery_authority --verbosity 1`

RED result: exit 1. One test failed with HTTP 409 `TRANSITION_CONFLICT`; the approval owner still
reported that recovery decisions were unavailable at the Non-Payment Note stage.

GREEN command: the exact command above.

GREEN result: exit 0. One test passed in 0.744s; three distinct configured authorities produced
pending, pending, then approved states.
