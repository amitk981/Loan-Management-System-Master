# CDSL API evidence examples

These are representative response shapes verified by
`sfpcl_credit.tests.test_cdsl_share_pledge_api`; identifiers are synthetic.

## Ordinary masked GET

`GET /api/v1/security-packages/10000000-0000-0000-0000-000000000001/cdsl-share-pledge/`

```json
{
  "success": true,
  "data": {
    "cdsl_share_pledge_id": "20000000-0000-0000-0000-000000000002",
    "security_package_id": "10000000-0000-0000-0000-000000000001",
    "pledgor_member_id": "30000000-0000-0000-0000-000000000003",
    "pledgee_entity_name": "Sahyadri Farmers Producer Company Limited",
    "pledgor_bo_account": "************3456",
    "pledgee_bo_account": "************7654",
    "pledgor_dp_name": "Pledgor DP",
    "pledgee_dp_name": "Pledgee DP",
    "prf_status": "submitted",
    "pledge_sequence_number": "PSN-CDSL-0001",
    "pledge_acceptance_status": "accepted",
    "pledged_share_count": 100,
    "agreement_number": "LA-CDSL-0001",
    "pledge_status": "created",
    "future_shares_pledged_flag": true,
    "evidence_document_id": "40000000-0000-0000-0000-000000000004",
    "created_at_cdsl": "2026-07-14T17:30:00Z",
    "prepared_by_user_id": "50000000-0000-0000-0000-000000000005",
    "verified_by_user_id": "60000000-0000-0000-0000-000000000006",
    "acceptance_evidence": {
      "pledge_sequence_number": "PSN-CDSL-0001",
      "agreement_number": "LA-CDSL-0001",
      "pledged_share_count": 100,
      "future_shares_pledged_flag": true,
      "pledgor_bo_account": "************3456",
      "pledgee_bo_account": "************7654"
    }
  }
}
```

## Terminal acceptance action

```json
{
  "success": true,
  "data": {
    "entity_type": "cdsl_share_pledge",
    "entity_id": "20000000-0000-0000-0000-000000000002",
    "previous_status": "pending",
    "new_status": "created",
    "workflow_event_id": "70000000-0000-0000-0000-000000000007",
    "available_actions": []
  }
}
```

## Explicit audited reveal

Request:

```json
{ "reason": "Verify retained DP instructions." }
```

Response (returned only to an authorised Company Secretary and never copied into evidence logs):

```json
{
  "success": true,
  "data": {
    "cdsl_share_pledge_id": "20000000-0000-0000-0000-000000000002",
    "pledgor_bo_account": "<full value returned once>",
    "pledgee_bo_account": "<full value returned once>",
    "expires_at": "2026-07-14T17:35:00Z"
  }
}
```
