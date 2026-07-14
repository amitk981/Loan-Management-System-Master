# Standards Review

Fixed point: `85f142c2`

Reviewed commits: `555c148b`, `11cc0e75`, `df0af073`, `a3e8c348`, `447e965b`.

## Findings

1. **Critical — recoverable plaintext is embedded in encrypted columns.**
   `shared/encryption.py:24-43` writes `value[-4:]` outside AES-GCM ciphertext. A six-digit blank
   cheque exposes four digits without a key, and CDSL BO suffixes are similarly recoverable. The
   existing test checks only absence of the complete value and uses the suffix for masking.
2. **High — finance reader object scope is broader than source.**
   `security_package.py:166-172` and `document_checklist_access.py:88-101` admit Senior Manager
   Finance/CFC for every sanctioned Stage-4 row rather than documentation-approved/pending-
   disbursement and disbursement-ready rows respectively.
3. **Medium — PATCH is replacement.**
   `BlankDatedChequeRequest` requires every request field on PATCH, contrary to API §5.1 partial
   update semantics.
4. **Medium — promised architectural proof is incomplete.**
   Dependency scanning covers one direction, forged callback tests cover one package-read path,
   the I4 duplicate-hash case is absent, and redaction policy remains divergent across evidence
   owners.

## Judgement exclusions

- No §45 `Idempotency-Key` finding: the specific source list contains financial actions and omits
  the reviewed §27/§28 routes; A-118 records the interpretation.
- No CFO checklist-signature finding: the specific 008K/SOP documentation rule requires one
  eligible director even though CFO belongs to the broader Sanction Committee.

Corrective owner: `008K2-sensitive-security-contract-closure`.
