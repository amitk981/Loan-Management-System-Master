# API Response Examples

## Eligible Assessment

```json
{
  "success": true,
  "data": {
    "eligibility_assessment_id": "uuid",
    "loan_application_id": "uuid",
    "member_active_check": "pass",
    "default_check": "no_default",
    "document_check": "complete",
    "terms_acceptance_check": "accepted",
    "purpose_check": "agriculture_aligned",
    "nominee_check": "valid",
    "overall_result": "eligible",
    "assessment_notes": "All mandatory eligibility criteria passed.",
    "assessed_by_user_id": "uuid",
    "assessed_at": "2026-07-10T00:00:00Z"
  }
}
```

## Blocked Assessment

```json
{
  "success": true,
  "data": {
    "eligibility_assessment_id": "uuid",
    "loan_application_id": "uuid",
    "member_active_check": "pass",
    "default_check": "default_found",
    "document_check": "incomplete",
    "terms_acceptance_check": "accepted",
    "purpose_check": "non_agriculture",
    "nominee_check": "minor",
    "overall_result": "ineligible",
    "assessment_notes": "BR-008 default history blocks normal eligibility; BR-013/BR-014 required checklist evidence is incomplete; BR-018 purpose is not agriculture-aligned; BR-009 nominee is a minor.",
    "assessed_by_user_id": "uuid",
    "assessed_at": "2026-07-10T00:00:00Z"
  }
}
```

## Pending Manual Evidence

```json
{
  "success": true,
  "data": {
    "eligibility_assessment_id": "uuid",
    "loan_application_id": "uuid",
    "member_active_check": "pass",
    "default_check": "no_default",
    "document_check": "complete",
    "terms_acceptance_check": "accepted",
    "purpose_check": "agriculture_aligned",
    "nominee_check": "pending",
    "overall_result": "pending_manual_evidence",
    "assessment_notes": "Source-backed default, document, terms, and purpose checks passed. Application-specific nominee evidence is pending because the current application schema has no submitted nominee selection.",
    "assessed_by_user_id": "uuid",
    "assessed_at": "2026-07-10T00:00:00Z"
  }
}
```
