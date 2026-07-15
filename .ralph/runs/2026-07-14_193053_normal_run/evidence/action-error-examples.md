# Action and Error Contract Evidence

## Tri-party verification success (§6.3)

```json
{
  "success": true,
  "data": {
    "entity_type": "loan_document",
    "entity_id": "<loan-document-uuid>",
    "previous_status": "pending",
    "new_status": "verified",
    "workflow_event_id": "<workflow-event-uuid>",
    "available_actions": []
  },
  "meta": {
    "request_id": "req-tri-party-verify",
    "timestamp": "<UTC timestamp>",
    "api_version": "v1"
  }
}
```

Verified by
`TriPartyAgreementApiTests.test_company_secretary_verifies_applicable_current_signed_agreement`.
The test also proves `workflow_event_id` identifies the retained workflow row. Exact replay returns
the same data and creates no audit/version/workflow row.

## Unresolved mismatch overwrite (§7.2)

```json
{
  "success": false,
  "error": {
    "code": "SIGNATURE_MISMATCH_UNRESOLVED",
    "message": "An unresolved signature mismatch can only be cleared through mismatch resolution.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": null,
    "timestamp": "<UTC timestamp>",
    "api_version": "v1"
  }
}
```

Verified by
`SignatureMismatchApiTests.test_unresolved_mismatch_cannot_be_cleared_by_same_signer_capture`;
HTTP status is 400 and every Stage-4 success ledger remains unchanged.
