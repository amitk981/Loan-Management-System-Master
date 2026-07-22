# Security Return API Examples

## Physical/PoA release request

```http
POST /api/v1/loan-closures/{loan_closure_id}/security-return/
Idempotency-Key: security-return-example-001
Content-Type: application/json
```

```json
{
  "security_package_id": "00000000-0000-0000-0000-000000000101",
  "expected_version": 0,
  "acknowledgement_document_id": "00000000-0000-0000-0000-000000000102",
  "items": [
    {
      "item_type": "poa",
      "source_item_id": "00000000-0000-0000-0000-000000000103",
      "outcome": "released",
      "returned_released_to": "Authorised recipient",
      "returned_released_at": "2026-07-22T10:30:00Z"
    }
  ]
}
```

## CDSL item result

```json
{
  "item_type": "cdsl",
  "source_item_id": "00000000-0000-0000-0000-000000000201",
  "outcome": "completed",
  "psn": "PSN-EXAMPLE-001",
  "urf_document_id": "00000000-0000-0000-0000-000000000202",
  "urf_date": "2026-07-21",
  "unpledge_type": "full",
  "pledgor_dp_submitted_at": "2026-07-21T09:00:00Z",
  "pledgee_dp_acted_at": "2026-07-22T09:30:00Z",
  "pledgee_dp_outcome": "accepted",
  "auto_unpledge_flag": false,
  "completed_at": "2026-07-22T09:30:00Z",
  "completion_evidence_document_id": "00000000-0000-0000-0000-000000000203"
}
```

The response returns aggregate status/version and all four derived items. CDSL BO accounts are represented only as masked last-four values; encrypted or full account values are never returned.
