# Diagnosis and Red Evidence

Original independent browser command:

```text
RALPH_EVIDENCE_DIR=<run>/evidence/screenshots \
E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python \
npm run e2e -- e2e/staff-documentation-workspace.e2e.spec.ts
```

Original result: real Django returned the workspace, then Playwright timed out locating
`Term Sheet` → `Record borrower signature`.

Minimal fresh-seed probe returned:

```text
{'status': 'complete', 'labels': []}
AssertionError: browser symptom reproduced: borrower-signature action absent
```

Retained facts proved the cause:

```text
{'item_status': 'complete',
 'signature_facts': [('borrower', 'signed'), ('nominee', 'signed'), ('user', 'signed')],
 'permissions': ['documents.checklist.update', 'documents.file.upload',
                 'documents.notary.record', 'documents.signature.record',
                 'documents.stamp.record']}
```

Failing-first regression:

```text
/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py test \
  sfpcl_credit.tests.test_seed_portal_e2e_fixture.SeedPortalE2eFixtureTests.test_seed_is_idempotent_and_exposes_real_portal_contracts

FAIL: all six pending PoA action labels were absent before the fixture created a PoA document.
```
