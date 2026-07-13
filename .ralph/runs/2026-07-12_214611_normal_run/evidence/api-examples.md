# Active-member API examples

The focused API tests exercised the standard success envelope. Representative response fields are:

```json
{
  "data": {
    "decision": "active",
    "reason": "Dated source evidence reviewed.",
    "version": 2,
    "result": {
      "result_id": "<deterministic UUID>",
      "calculated_as_of_date": "2026-07-12",
      "member_type": "individual_farmer",
      "member_active_check": "pass",
      "continuous_supply_years": 4,
      "qualification_route": "four_year_supply",
      "supply_rows": [
        {"financial_year": "2025-26", "verified": true, "qualifying": true, "non_qualifying_reason": null}
      ]
    }
  }
}
```

Portal `GET /api/v1/portal/produce-supply/` returns every own-member row with `qualifying` and
`non_qualifying_reason`, plus summary `result_id` and `calculated_as_of_date`. It returns no top-level
member ID and no row `available_actions`; cross-member query parameters are ignored in favor of the
authenticated active `PortalAccount`.

Eligibility run/read responses now include `active_member_snapshot`. The immutable-readback test
deletes all current supply rows after calculation and proves the returned snapshot remains byte-for-
byte equal to the stored response.
