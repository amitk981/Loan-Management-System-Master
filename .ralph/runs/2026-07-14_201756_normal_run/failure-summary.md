# Failure Summary

- Run: 2026-07-14_201756_normal_run
- Mode: normal_run
- Slice: 008F2-security-instrument-boundary-and-poa-lifecycle-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
diff-limits-results.md:- FAIL: changed-line count exceeds limits.max_lines_changed.
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/008F2-security-instrument-boundary-and-poa-lifecycle-closure.md
docs/slices/008H-sh-4-physical-share-security-workflow.md
docs/slices/008I-cdsl-pledge-workflow.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
docs/working/HANDOFF.md
docs/working/digests/epic-008-documentation-security-package.md
sfpcl_credit/config/settings.py
sfpcl_credit/config/urls.py
sfpcl_credit/identity/modules/auth_service.py
sfpcl_credit/legal_documents/models.py
sfpcl_credit/legal_documents/modules/document_authority.py
sfpcl_credit/legal_documents/modules/power_of_attorney.py
sfpcl_credit/legal_documents/modules/signatures.py
sfpcl_credit/legal_documents/modules/stamp_notary.py
sfpcl_credit/legal_documents/request_contracts.py
sfpcl_credit/legal_documents/serializers.py
sfpcl_credit/legal_documents/views.py
sfpcl_credit/tests/test_power_of_attorney_api.py
sfpcl_credit/tests/test_tri_party_agreement_api.py
.ralph/runs/2026-07-14_201756_normal_run/
sfpcl_credit/security_instruments/
sfpcl_credit/tests/test_security_instrument_boundary.py
```
