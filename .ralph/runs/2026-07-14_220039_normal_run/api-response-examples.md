# SH-4 API Response Examples

## Compliance creates a pending form

`POST /api/v1/security-packages/{security_package_id}/sh4-share-transfer-form/`

```json
{
  "member_id": "uuid",
  "witness_id": "uuid",
  "shareholding_id": "uuid",
  "share_count": 75,
  "loan_document_id": "uuid",
  "form_status": "pending",
  "custody_location": null,
  "signed_at": null
}
```

Success data is metadata-only:

```json
{
  "sh4_share_transfer_form_id": "uuid",
  "security_package_id": "uuid",
  "member_id": "uuid",
  "witness_id": "uuid",
  "shareholding_id": "uuid",
  "share_count": 75,
  "loan_document_id": "uuid",
  "form_status": "pending",
  "custody_location": null,
  "signed_at": null,
  "prepared_by_user_id": "uuid",
  "custodian_user_id": null,
  "custody_evidence": null
}
```

## Company Secretary records terminal custody

The PATCH request uses the same exact eight fields with `form_status: "held_in_custody"`, the
retained signed date, and a bounded custody location. Success and exact replay return:

```json
{
  "entity_type": "sh4_share_transfer_form",
  "entity_id": "uuid",
  "previous_status": "signed",
  "new_status": "held_in_custody",
  "workflow_event_id": "uuid",
  "available_actions": []
}
```

`invoked`, `returned`, unknown fields, cross-scope facts, legacy/null-maker evidence, and missing
authority return standard errors with no SH-4 success ledger. Responses never contain a download
URL, storage key, document bytes, or invocation/return authority.
