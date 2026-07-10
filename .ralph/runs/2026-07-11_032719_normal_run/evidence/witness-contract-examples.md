# Witness Contract Evidence

## Malformed request

Request body: `[]`

Verified response shape:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Witness payload failed validation.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": null,
    "timestamp": "<server timestamp>",
    "api_version": "v1"
  }
}
```

The public endpoint test verifies HTTP 400 and unchanged witness, audit, and workflow counts for
malformed JSON, an array, and a scalar string.

## Stable verification evidence

At creation, the qualifying holding has UUID `<original-shareholding-id>`, folio `FOL-004E`, 25
shares, and active status. Both POST and subsequent GET expose:

```json
{
  "verification_shareholding_id": "<original-shareholding-id>",
  "folio_number": "FOL-004E",
  "shareholder_verified_flag": true,
  "verification_status": "verified"
}
```

The regression then changes that holding to folio `FOL-CHANGED`, zero shares, and inactive status,
and creates a new active 50-share holding with folio `FOL-NEW`. GET still returns the original UUID
and `FOL-004E` snapshot.

## Legacy and index inspection

Migration tests verify:

- one audited folio + one member-owned match is linked;
- two matching holdings, no matching holding, or no audit leave both provenance fields null;
- running the backfill function twice is stable and reverse migration preserves all legacy rows;
- `idx_witnesses_application` covers only `loan_application_id`, `idx_witnesses_pan_hash` covers
  only `pan_hash`, and `idx_witnesses_aadhaar_hash` covers only `aadhaar_hash`;
- no second physical index exists for any of those three column sets.

See `terminal-logs/01-malformed-json-red.log`, `02-malformed-json-green.log`,
`03-stable-evidence-red.log`, `04-stable-evidence-green.log`, `05-migration-regressions.log`, and
`06-migration-green.log` for executable evidence.
