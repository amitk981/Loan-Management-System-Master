# Sanitised Auditor Observation API Examples

## Create request

```json
{
  "audit_scope": "audit_readonly",
  "observation": "Sampled evidence is complete and traceable.",
  "source_references": [
    {
      "source_type": "audit_log",
      "source_id": "11111111-1111-4111-8111-111111111111"
    }
  ]
}
```

## Create/detail data

```json
{
  "audit_observation_id": "22222222-2222-4222-8222-222222222222",
  "creator": {
    "user_id": "33333333-3333-4333-8333-333333333333",
    "full_name": "Internal Auditor",
    "role_code": "internal_auditor",
    "team_codes": []
  },
  "audit_scope": "audit_readonly",
  "observation": "Sampled evidence is complete and traceable.",
  "source_references": [
    {
      "source_type": "audit_log",
      "source_id": "11111111-1111-4111-8111-111111111111",
      "entity_type": "compliance_evidence",
      "entity_id": "44444444-4444-4444-8444-444444444444"
    }
  ],
  "created_at": "2026-07-24T03:00:00Z"
}
```

## Restricted evidence projection

```json
{
  "source_type": "compliance_evidence",
  "source_id": "55555555-5555-4555-8555-555555555555",
  "entity_type": "document_file",
  "entity_id": "66666666-6666-4666-8666-666666666666",
  "evidence_type": "annual_audit_report",
  "evidence": {
    "document_id": "66666666-6666-4666-8666-666666666666",
    "file_name": "annual-audit-evidence.pdf",
    "sensitivity_level": "restricted",
    "download_url": "/api/v1/audit-observations/22222222-2222-4222-8222-222222222222/evidence/55555555-5555-4555-8555-555555555555/download/?token=<short-lived-signed-capability>",
    "expires_at": "2026-07-24T03:15:00Z"
  }
}
```

Without current document-download authority, `download_url` and `expires_at` are `null`. Responses
never contain evidence summaries, review comments, raw source payloads, checksums, storage providers,
storage keys, or permanent object URLs.

## Validation/nondisclosure response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Audit observation request failed validation.",
    "details": {},
    "field_errors": {
      "status": "Unknown field."
    }
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-24T03:00:00Z",
    "api_version": "v1"
  }
}
```

Unsafe text is never echoed. Missing, guessed, wrong-family, revoked, or cross-observation evidence
uses the same `404 NOT_FOUND` shape.
