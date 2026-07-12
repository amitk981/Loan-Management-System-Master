# Trusted Browser Failure Diagnosis

The independent validator ran this command twice from `sfpcl-lms/`:

```text
RALPH_EVIDENCE_DIR=<run-evidence>/screenshots \
E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python \
npm run e2e -- e2e/member-governance-variants.e2e.spec.ts
```

Both runs reached the same deterministic assertion after the real manager login and canonical member
detail GET:

```text
Expected required_permission: members.member.update
Received required_permission: members.member.identity_change.approve
```

The received action was enabled and otherwise matched all six fields. Backend confirmation used:

```text
/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test \
sfpcl_credit.tests.test_member_governance_api.MemberGovernanceApiTests.test_every_public_registry_operation_enforces_its_own_exact_authority \
--verbosity 2
```

Result: pass. `MemberRegistry.APPROVE_PERMISSION`, the permission catalogue, seed grant, and API
projection all use `members.member.identity_change.approve`. The repair therefore updates only the
stale E2E expected value. Local post-repair browser launch is sandbox-denied before the test body;
`browser-collection.log` confirms the corrected spec still discovers exactly one scenario, and the
orchestrator owns the post-repair trusted executions.
