# Dependency and Public-Tracer Proof

- `legal_documents/views.py` is the only production caller importing
  `legal_documents.serializers`; `legal_documents/modules/**` has no transport-serializer import.
- The HTTP serializer adapter re-exports strict value contracts from
  `legal_documents/request_contracts.py`. Views authorize before parsing and pass typed contracts
  into the same domain interfaces used by direct callers.
- `public-generation-tracer.txt` proves a genuine DOCX template crossed
  `document_generation.generate`, produced renderer-validated PDF metadata, captured canonical
  borrower/nominee signatures, and completed §26.6 verification.
- `postgresql-stage4-full.txt` proves all 45 Stage-4 cases on PostgreSQL. The tri-party class contains
  two exact and two different-remarks five-worker executions; `postgresql-tri-party-races.txt`
  records all four passing.

Verification command:

```text
rg -n 'legal_documents\.serializers' sfpcl_credit/legal_documents/modules
```

Result: no matches.
