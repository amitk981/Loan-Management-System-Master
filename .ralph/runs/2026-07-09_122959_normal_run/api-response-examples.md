# API Response Examples — 004F Shareholding

## Create Shareholding

`POST /api/v1/members/{member_id}/shareholdings/`

```json
{
  "success": true,
  "data": {
    "shareholding_id": "uuid",
    "folio_number": "FOL-004F",
    "number_of_shares": 100,
    "holding_mode": "physical",
    "valuation_per_share": "2000.00",
    "valuation_effective_date": "2026-04-01",
    "pledged_share_count": 15,
    "available_share_count": 85,
    "future_shares_pledge_flag": true,
    "status": "active"
  },
  "meta": {
    "request_id": "req-create-shareholding",
    "timestamp": "2026-07-09T00:00:00Z",
    "api_version": "v1"
  }
}
```

## List Shareholdings

`GET /api/v1/members/{member_id}/shareholdings/`

```json
{
  "success": true,
  "data": [
    {
      "shareholding_id": "uuid",
      "folio_number": "FOL-004F",
      "number_of_shares": 100,
      "holding_mode": "physical",
      "valuation_per_share": "2000.00",
      "valuation_effective_date": "2026-04-01",
      "pledged_share_count": 15,
      "available_share_count": 85,
      "future_shares_pledge_flag": true,
      "status": "active"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-09T00:00:00Z",
    "api_version": "v1"
  }
}
```

## Validation Error

`POST /api/v1/members/{member_id}/shareholdings/`

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Shareholding payload failed validation.",
    "details": {},
    "field_errors": {
      "pledged_share_count": "Pledged shares cannot exceed total shares."
    }
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-09T00:00:00Z",
    "api_version": "v1"
  }
}
```
