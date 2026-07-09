This file intentionally records representative 006A API response shapes from the green API tests.

POST /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/run/

```json
{
  "success": true,
  "data": {
    "eligibility_assessment_id": "uuid",
    "loan_application_id": "uuid",
    "member_active_check": "manual_evidence_required",
    "default_check": "pending",
    "document_check": "pending",
    "terms_acceptance_check": "pending",
    "purpose_check": "pending",
    "nominee_check": "pending",
    "overall_result": "pending_manual_evidence",
    "assessment_notes": "BR-004 through BR-007 require continuous produce/service history or relaxation evidence. Current persistence has no source history rows for this application, so manual evidence is required.",
    "assessed_by_user_id": "uuid",
    "assessed_at": "2026-07-10T00:00:00Z"
  },
  "meta": {
    "request_id": "req-run-eligibility",
    "timestamp": "2026-07-10T00:00:00Z",
    "api_version": "v1"
  }
}
```

GET /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/

```json
{
  "success": true,
  "data": {
    "eligibility_assessment_id": "uuid",
    "loan_application_id": "uuid",
    "member_active_check": "manual_evidence_required",
    "default_check": "pending",
    "document_check": "pending",
    "terms_acceptance_check": "pending",
    "purpose_check": "pending",
    "nominee_check": "pending",
    "overall_result": "pending_manual_evidence",
    "assessment_notes": "BR-004 through BR-007 require continuous produce/service history or relaxation evidence. Current persistence has no source history rows for this application, so manual evidence is required.",
    "assessed_by_user_id": "uuid",
    "assessed_at": "2026-07-10T00:00:00Z"
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-10T00:00:00Z",
    "api_version": "v1"
  }
}
```
