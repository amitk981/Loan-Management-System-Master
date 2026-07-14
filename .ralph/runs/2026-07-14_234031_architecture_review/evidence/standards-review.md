# Standards Review

Fixed point: `e046a9d3`  
Reviewed head: `bacc285d`  
Range: `git diff e046a9d3...bacc285d`

## Findings

1. **High — reversed dependency and forwarding shell.**
   `security_instruments.modules.power_of_attorney` delegates all implementation to
   `legal_documents`, mutates the imported module with `bind_security_owner`, and forwards unknown
   attributes through `__getattr__`. Security package, SH-4, and CDSL modules also import legal or
   approvals owners. This contradicts codebase-design §§28.1/36.2. Corrective: 008I2 and 008I3.
2. **High — reversible data bypasses central owners.**
   `members.protected_identity` implements local XOR/HMAC counter mode derived from Django
   `SECRET_KEY`; CDSL locally decrypts, authorizes reveal, and writes reveal audit. This contradicts
   the `shared.encryption` and `documents.modules.sensitive_data_access` seams in codebase-design
   §§9.4/39. Corrective: 008I4 and sharpened 012E3.
3. **High — package read roles are too narrow.**
   The common actor guard limits reads to Compliance/Company Secretary despite auth §§12.8/14.1/
   19.2-19.4 granting scoped masked security reads to Credit, finance approvers, directors, and
   auditors. Corrective: 008I2.
4. **Medium — ledger duplication and incomplete race evidence.**
   Security/legal modules repeat audit/version/workflow writers, and some changed-payload races do
   not assert exactly one material winner with zero success identity for every loser. Corrective:
   008I3.

## Substantive strengths

008G2 has real latest-maker transfer, strict request/action contracts, consumed-signature guards,
and a public renderer tracer. SH-4 and CDSL use terminal row locking, masked ordinary projections,
and explicit no-invocation/no-readiness side-effect contracts. No additional indexing,
idempotency, or action-envelope defect was found.

Totals: 3 High, 1 Medium. Worst issues: reversed ownership and local reversible cryptography.
