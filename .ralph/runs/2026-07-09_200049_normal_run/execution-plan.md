# Execution Plan: 005D Application Document Checklist

## Scope
- Backend-only implementation for application document metadata, verification, and checklist read/refresh endpoints.
- Reuse existing standard API envelopes, audit log model, and applications.services.evaluate_application_object_access(...) for object scope.
- Add one non-destructive applications migration for application_documents metadata.
- No frontend screen changes; no storage/file-byte behavior changes.

## Permission Check Before Editing
- Allowed by .ralph/permissions.json: sfpcl_credit/**, docs/working/**, docs/slices/**, docs/epics/**, .ralph/runs/**, .ralph/state.json, .ralph/progress.md.
- Protected/read-only paths will not be edited: scripts/**, .ralph/config.yaml, .ralph/permissions.json, AGENTS.md, CLAUDE.md, .gitignore, docs/source/**, HIGH_RISK_APPROVALS.md, DECISION_POLICY.md, FRONTEND_DESIGN_RULES.md.

## TDD Plan
1. Add API regression tests to sfpcl_credit/tests/test_loan_applications_api.py for source document checklist, upload metadata audit, verify audit, 404/403/object-scope denials, and duplicate version preservation.
2. Run the targeted test with /Users/amitkallapa/LMS/.ralph/venv/bin/python and save RED output.
3. Implement ApplicationDocument model/migration, services, URLs, and views.
4. Run targeted tests and save GREEN output.
5. Run full backend and frontend gates; save logs.

## Documentation and Evidence
- Update docs/working/API_CONTRACTS.md and epic digest with the new contract.
- Save changed-files.txt, risk-assessment.md, review-packet.md, final-summary.md.
- Update handoff, progress, state, and slice status after gates.
