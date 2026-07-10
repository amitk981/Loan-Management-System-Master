# Witness API Response Examples

## Successful create

```json
{
  "success": true,
  "data": {
    "witness_id": "2abce893-3ac7-4a24-a4f6-0df5c067ce7c",
    "loan_application_id": "f075eec1-87be-4908-b0fe-cab69f565318",
    "member_id": "393b70d1-4fd0-41a5-b73e-dc493d654776",
    "folio_number": "FOL-004E",
    "witness_name": "Sita Patil",
    "pan": {"masked": "******234F", "can_view_full": false},
    "aadhaar": {"masked": "********1234", "can_view_full": false},
    "shareholder_verified_flag": true,
    "verification_status": "verified",
    "verified_by_user_id": "14242607-965f-489a-818d-73858d9ed67e",
    "verified_at": "2026-07-10T18:29:19.110008Z",
    "created_at": "2026-07-10T18:29:19.110084Z"
  },
  "meta": {"request_id": null, "timestamp": "2026-07-10T18:29:19.129540Z", "api_version": "v1"}
}
```

## Non-shareholder rejection

```json
{
  "success": false,
  "error": {
    "code": "WITNESS_NOT_SHAREHOLDER",
    "message": "Witness is not an existing shareholder.",
    "field_errors": {"member_id": "Member has no active positive shareholding."}
  }
}
```

Examples use synthetic UUIDs and test-only identity values. Full PAN/Aadhaar, protected tokens, and
keyed hashes are intentionally absent.
