# DPD API Examples

## Single-loan calculation

Request:

```json
POST /api/v1/loan-accounts/11111111-1111-1111-1111-111111111111/dpd-status/calculate/
{"as_of_date":"2026-07-01"}
```

Representative success data (the standard scheme is optional and was absent):

```json
{
  "loan_account_id": "11111111-1111-1111-1111-111111111111",
  "as_of_date": "2026-07-01",
  "days_past_due": 1,
  "sop_bucket": "current",
  "standard_bucket": null,
  "principal_overdue_amount": "1000.00",
  "interest_overdue_amount": "100.00",
  "total_overdue_amount": "1100.00",
  "calculation_version": "DPD-CALC-1",
  "operational_scheme_version": null
}
```

The complete response uses the standard `success/data/meta` envelope and also includes the immutable
snapshot id and creation time. Exact replay returns those same retained values.

## Configured operational boundary

The public boundary matrix proves the effective `DPD-STD-1` scheme independently from SOP ageing:

```json
{
  "as_of_date": "2024-03-31",
  "days_past_due": 31,
  "sop_bucket": "current",
  "standard_bucket": "31_60",
  "operational_scheme_version": "DPD-STD-1"
}
```

## Portfolio result

```json
{
  "run_id": "22222222-2222-2222-2222-222222222222",
  "as_of_date": "2026-07-01",
  "calculated_count": 1,
  "skipped_count": 0,
  "failed_count": 0,
  "results": [
    {
      "loan_account_id": "11111111-1111-1111-1111-111111111111",
      "outcome": "calculated",
      "dpd_status": {"days_past_due": 1, "sop_bucket": "current"}
    }
  ]
}
```

The permanent test also proves a mixed selected batch reports one inactive loan as `skipped` and one
inaccessible id as `failed`, without hiding either outcome.
