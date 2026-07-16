# Executable Review Probes

Backend interpreter: `/Users/amitkallapa/LMS/.ralph/venv/bin/python`

## Canonical terminal-sanction probe

Command:

`PYTHONPATH=/tmp .../python manage.py test review_probes.BankDecisionTerminalScopeProbe.test_status_label_cannot_replace_canonical_terminal_sanction --verbosity 2`

Result: expected review failure. The fixture retained
`application_status=approved_by_sanction_committee`, changed the latest `ApprovalCase` to rejected,
and verified `document_checklist_facts.resolve_approved_facts(...) is None`. The public bank-decision
POST nevertheless returned HTTP 200 (expected 403) and serialized a new version-2 rejected decision
with a new workflow, audit, and VersionHistory identity.

Failing assertion:

`AssertionError: 200 != 403`

The test database was created/destroyed normally and Django system check reported no issues.

## Deficiency workflow-evidence probe

Command:

`PYTHONPATH=/tmp .../python manage.py test review_probes.DeficiencyWorkflowEvidenceProbe.test_missing_response_workflow_cannot_project_responded_truth --verbosity 1`

Result: expected review failure. The fixture uploaded one response through the public portal API,
deleted its `application_deficiency_response` WorkflowEvent, and fetched the public projection. The
response still returned `response_status=responded`.

Failing assertion:

`AssertionError: 'responded' == 'responded'`

The test database was created/destroyed normally and Django system check reported no issues.

These probes are diagnostic evidence only. They were kept outside production/test source and are
owned by corrective slice 008L5.
