# API Response Examples

## GET /api/v1/portal/dashboard/

```json
{
  "success": true,
  "data": {
    "member": {
      "member_id": "uuid",
      "display_name": "Ganesh Thorat",
      "member_number": "M-005FB",
      "folio_number": "FOL-005FB",
      "member_type": "individual_farmer",
      "membership_status": "active",
      "kyc_status": "verified",
      "default_status": "no_default"
    },
    "application_counts": {
      "total": 1,
      "draft": 0,
      "submitted": 0,
      "incomplete_returned": 1,
      "reference_generated": 0
    },
    "loan_counts": { "active": 0, "closed": 0, "overdue": 0 },
    "pending_actions": {
      "open_deficiencies": 1,
      "signature_pending": 0,
      "repayment_due": 0,
      "kyc_update_due": 0,
      "closure_actions": 0
    },
    "notices": []
  },
  "meta": { "api_version": "v1" }
}
```

## GET /api/v1/portal/profile/

```json
{
  "success": true,
  "data": {
    "member": {
      "member_id": "uuid",
      "display_name": "Ganesh Thorat",
      "pan": { "masked": "******234F", "can_view_full": false },
      "aadhaar": { "masked": "********9012", "can_view_full": false }
    },
    "nominees": [{ "nominee_name": "Suman Thorat", "pan": { "masked": "******678K" } }],
    "shareholdings": [{ "folio_number": "FOL-005FB", "number_of_shares": 5 }],
    "land_holdings": [{ "survey_number": "123/4", "area_acres": "4.50" }],
    "crop_plans": [{ "season": "Kharif 2026", "crop_type": "grapes" }],
    "kyc_profile": { "kyc_status": "verified", "rekyc_due_date": "2027-06-22" },
    "bank_accounts": [{ "account_number": { "masked": "********9012" } }],
    "cancelled_cheques": []
  },
  "meta": { "api_version": "v1" }
}
```

## GET /api/v1/portal/produce-supply/

```json
{
  "success": true,
  "data": {
    "member_id": "uuid",
    "records": [],
    "summary": {
      "continuous_supply_years": null,
      "total_quantity": null,
      "total_value": null
    },
    "source_status": "model_not_implemented"
  },
  "meta": { "api_version": "v1" }
}
```
