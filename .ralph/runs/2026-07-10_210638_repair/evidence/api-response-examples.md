# Epic 006 Frontend API Examples

Eligibility read/run and loan-limit read/calculate preserve backend fields and decimal strings:

```json
{"success":true,"data":{"overall_result":"eligible","assessment_notes":"Stored assessment explanation."}}
{"success":true,"data":{"final_eligible_loan_amount":"250000.00","requested_amount":"250000.00","amount_within_limit_flag":true,"calculation_rule_version":"board-policy-2026"}}
```

Sanction submission sends exactly `{"remarks":"Submit."}` and retains the response:

```json
{"success":true,"data":{"approval_case_id":"case-1","submission_status":"pending","exception_required_flag":false}}
```

Stale actions are surfaced and not retried:

```json
{"success":false,"error":{"code":"INVALID_STATE_TRANSITION","message":"State changed.","field_errors":{"remarks":"Refresh."}}}
```
