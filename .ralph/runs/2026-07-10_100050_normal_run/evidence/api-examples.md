# Nominee Contract API Examples

## Staff draft create

Request adds the existing member nominee UUID:

```json
{"member_id":"member-uuid","nominee_id":"nominee-uuid","required_loan_amount":"400000.00","declared_purpose":"Crop production","purpose_category":"crop_production"}
```

Staff and own-member portal detail return the same safe summary:

```json
{"nominee":{"nominee_id":"nominee-uuid","nominee_name":"Selected Nominee","age_at_application":42,"minor_flag":false,"kyc_status":"verified","relationship_to_borrower":"Spouse","signature_required_flag":true}}
```

PAN, Aadhaar, encrypted tokens, and hashes are absent.

## Invalid selection

Cross-member, unknown, minor, and missing-age selections return:

```json
{"success":false,"error":{"code":"VALIDATION_ERROR","field_errors":{"nominee_id":"Selected nominee validation failed."}}}
```

No application, success audit, or workflow event is created.

## Legacy completeness and eligibility

A legacy null selection returns `nominee_selection_status: "pending"` and
`can_generate_reference: false` from completeness. Reference generation returns a nominee field
validation error. Eligibility persists `nominee_check: "pending"` and
`overall_result: "pending_manual_evidence"`.
