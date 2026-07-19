# Risk Assessment

Risk level: High

- Selected slice: 010D2-statement-evidence-owner-and-scope-closure
- Mode: normal_run
- Standing approval: applicable; no matching `[revoked]` entry was present.
- Financial/data-integrity risk: a relationship-owner and migration change can affect receipt
  admission, manual-allocation evidence, and reconciliation visibility.
- Privacy risk: bank-statement and collection-account facts are restricted financial data.
- Concurrency risk: automatic, manual, exception, and direct-claim decisions can race.

## Controls

- One database one-to-one owner replaces two independently writable truths.
- Legacy orphan/incomplete/contradictory UUIDs become immutable exception evidence; no line or actor
  is invented, and the reverse migration restores only exact retained identities.
- Central source-bank governance replaces raw collection-account label input/storage/output for new
  imports; unmapped legacy labels are encrypted.
- Effective permission and loan-object scope are applied before match decisions, counts, pages, or
  receipt identities.
- Six public owner/scope/source/privacy tests, a forward/backward migration test, 010B–010D reverse
  consumers, backend static checks, and all frontend gates passed locally.
- Four PostgreSQL race tests collect under the exact declared class. Local SQLite skipped them as
  designed; the orchestrator must execute that class twice on PostgreSQL before acceptance.

Residual risk is High until independent PostgreSQL races and the orchestrator's full backend
coverage suite pass. No deployment, communication, external service, or real financial data was used.
