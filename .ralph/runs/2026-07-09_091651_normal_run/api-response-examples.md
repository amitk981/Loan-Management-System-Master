# API Response Examples

## Individual farmer

`GET /api/v1/members/{member_id}/` returns:

```json
{
  "success": true,
  "data": {
    "member_type": "individual_farmer",
    "pan": {"masked": "******234F", "can_view_full": false},
    "aadhaar": {"masked": "********9012", "can_view_full": false},
    "individual_profile": {
      "first_name": "Ramesh",
      "middle_name": null,
      "last_name": "Patil",
      "gender": "male",
      "date_of_birth": "1980-01-15",
      "occupation": "Farmer",
      "land_area_under_cultivation_acres": "5.00",
      "primary_crop": "grapes",
      "services_availed_flag": true,
      "employment_or_service_years": "12.50"
    },
    "producer_institution_profile": null
  }
}
```

## FPC / producer institution

```json
{
  "success": true,
  "data": {
    "member_type": "fpc",
    "individual_profile": null,
    "producer_institution_profile": {
      "institution_type": "farmer_producer_company",
      "registration_number": "U00000MH2021PTC000000",
      "authorised_signatory_name": "Authorised Person",
      "board_resolution_required_flag": true,
      "services_availed_flag": true,
      "produce_supply_years": "2.00"
    }
  }
}
```

When the member has no matching profile row, both type-specific profile properties are `null`.
Producer authorised-signatory PAN and Aadhaar keys are deliberately absent.
