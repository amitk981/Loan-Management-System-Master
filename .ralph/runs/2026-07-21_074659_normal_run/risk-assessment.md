# Risk Assessment

Risk level: High (financial export and sensitive download)

- Financial integrity: exporter calls the canonical ledger projection and copies running balances; it owns no financial model or calculation table.
- Data leakage: default masking, requester-private jobs, own-member portal scope, short signed capabilities, checksum verification, and metadata-only audit reduce exposure.
- Persistence: existing `ScheduledJob`, `DocumentFile`, and `AuditLog` truth is reused; no migration or duplicate export-job table was introduced.
- Residual risk: generation is synchronous behind a scheduler row; operational worker offloading can be added later without changing the public contract.
- Validation: focused statement and reverse-consumer ledger tests, Django check, migration-sync, compile, and diff checks are green; the orchestrator owns full coverage and complete-suite validation.
