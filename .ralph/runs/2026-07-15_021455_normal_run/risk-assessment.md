# Risk Assessment

Risk level: High

## Why high

- The slice adds a sensitive negotiable-instrument record, reversible field encryption, equality
  hash, explicit plaintext reveal, physical custody maker-checker, and one schema migration.
- It changes cross-owner application/bank/document/checklist coordination and adds public mutation
  routes whose misuse could expose cheque data or falsely imply recovery/disbursement readiness.
- Correctness depends on PostgreSQL row locks under five concurrent changed creates/custody writes.

## Controls verified

- Only an exact terminal-sanction package and application-owned active verified bank plus its exact
  single verified cancelled cheque can establish capture authority. Caller account text and stale,
  cross-member, pending, conflicting, or mismatched rows fail before success writes.
- New values use independently keyed `FieldEncryption`; ordinary responses and every ordinary
  audit/version/workflow snapshot use fixed `******`. The central reveal owner requires dedicated
  permission, Company Secretary role, canonical object scope, reason, expiry/rate decision, audited
  outcome, and no-store/no-cache response. Missing keys fail closed as audited 409.
- Compliance prepares; a distinct Company Secretary records exact retained held custody. Model
  constraints retain one package row and keep invocation approval, presentation date/amount, and
  return date null for later owners.
- Checklist/package projection preserves completion, verifier, remarks, signatures, status,
  readiness, file access, bank/cancelled-cheque truth, and null loan account. No frontend, custody
  event stream, invocation, presentment, return, payment, or download action was added.
- Two five-worker PostgreSQL races passed twice, proving one changed-create winner, one terminal
  custody winner, exact winning actor/request/workflow evidence, and zero loser success evidence.

## Residual risk

- Production key provisioning/whole-repository rotation remains owned by 012E3; this slice relies on
  the delivered central encryption contract.
- 008K must decide checklist completion only from the masked terminal ledger and canonical bank
  decision; it must not decrypt or treat masked existence as completion.
- Cheque invocation/presentation and return remain intentionally unavailable until 011I/013 and
  closure/NOC owners implement their separately approved workflows.

Manual review remains appropriate because this is High risk. Standing approval is active and no
owner veto exists.
