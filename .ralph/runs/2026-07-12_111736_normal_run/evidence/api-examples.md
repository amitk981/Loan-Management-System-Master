# Produce Supply API Examples

## Staff capture

`POST /api/v1/members/{member_id}/produce-supply-records/` with
`financial_year=2025-26`, `supplied_to_entity_type=sfpcl`, `supply_route=direct`, synthetic crop,
quantity, value, and ERP reference returns a pending record at `version=1`. Its verification action
is disabled for the maker.

## Independent verification

`POST /api/v1/produce-supply-records/{record_id}/verify/` with `version=1` returns the verified
record at `version=2`, with immutable verifier/time evidence. Reusing version 1 returns
`409 STALE_WRITE`; a maker attempt returns `403 FORBIDDEN` and creates no verification evidence.

## Portal own-scope read

`GET /api/v1/portal/produce-supply/?member_id={another_member}` ignores the query parameter as an
authority source. The response contains only the active PortalAccount member's rows, omits
`member_id` and staff actions, and returns persisted totals and continuous verified years.

Executable examples: `sfpcl_credit/tests/test_produce_supply_api.py`.
