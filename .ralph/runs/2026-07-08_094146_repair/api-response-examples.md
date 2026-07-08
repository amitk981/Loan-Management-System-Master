# API Response Examples: 004B Member Profile

## `GET /api/v1/members/{member_id}/` success

```json
{
  "success": true,
  "data": {
    "member_id": "00000000-0000-0000-0000-000000000125",
    "member_number": "MEM-00125",
    "member_type": "individual_farmer",
    "legal_name": "Ramesh Patil",
    "display_name": "Ramesh Patil",
    "folio_number": "FOL-456",
    "membership_start_date": "2021-04-01",
    "membership_status": "active",
    "kyc_status": "verified",
    "rekyc_due_date": "2027-06-22",
    "default_status": "no_default",
    "mobile_number": "******7890",
    "email": "ramesh@example.com",
    "pan": { "masked": "******234F", "can_view_full": false },
    "aadhaar": { "masked": "********9012", "can_view_full": false },
    "registered_address": {
      "line1": "Village Road",
      "line2": "Near Market",
      "village_city": "Nashik",
      "district": "Nashik",
      "state": "Maharashtra",
      "pincode": "422001"
    },
    "individual_profile": {
      "land_area_under_cultivation_acres": "5.00",
      "primary_crop": "grapes",
      "services_availed_flag": true
    },
    "producer_institution_profile": null,
    "available_actions": [
      {
        "action_code": "create_loan_application",
        "label": "Start Application",
        "enabled": true,
        "disabled_reason": null,
        "required_permission": "applications.loan_application.create"
      }
    ]
  },
  "meta": {
    "request_id": "req-member-detail",
    "api_version": "v1"
  }
}
```

## Error cases

- Missing bearer token: `401 AUTH_REQUIRED`.
- Authenticated user without `members.member.read`: `403 PERMISSION_DENIED`.
- Valid UUID for an unknown or soft-deleted member: `404 NOT_FOUND`.

Full PAN/Aadhaar reveal is not implemented in 004B. Responses expose only masked values and
`can_view_full: false`.
