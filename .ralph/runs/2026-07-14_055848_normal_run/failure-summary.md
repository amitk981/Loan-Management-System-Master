# Failure Summary

- Run: 2026-07-14_055848_normal_run
- Mode: normal_run
- Slice: 008A-document-template-model-and-versioning
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
postgresql-acceptance-results.md:- FAIL: first independent run did not satisfy all acceptance predicates.
postgresql-acceptance-results.md:- FAIL: second independent run did not satisfy all acceptance predicates.
postgresql-acceptance-results.md:- FAIL: PostgreSQL environment evidence is missing.
```

## Last 50 lines: postgresql-acceptance-results.md

```
# PostgreSQL Acceptance Results

- FAIL: first independent run did not satisfy all acceptance predicates.
- FAIL: second independent run did not satisfy all acceptance predicates.
- FAIL: PostgreSQL environment evidence is missing.
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/008A-document-template-model-and-versioning.md
docs/slices/008C-documentation-checklist-applicability.md
docs/slices/008D-stamp-duty-and-notarisation-tracking.md
docs/working/API_CONTRACTS.md
docs/working/HANDOFF.md
docs/working/digests/epic-008-documentation-security-package.md
sfpcl_credit/config/urls.py
sfpcl_credit/documents/models.py
sfpcl_credit/documents/views.py
.ralph/runs/2026-07-14_055848_normal_run/
sfpcl_credit/documents/migrations/0002_documenttemplate.py
sfpcl_credit/documents/modules/
sfpcl_credit/tests/test_document_templates_api.py
```
