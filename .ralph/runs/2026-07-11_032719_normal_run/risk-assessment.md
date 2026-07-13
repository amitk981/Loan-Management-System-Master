# Risk Assessment

Risk level: Medium (standing autonomous approval; no veto applies).

- Data risk: one additive nullable protected FK and folio snapshot, plus a conservative data
  migration. Existing rows are changed only when one creation-audit folio resolves to exactly one
  shareholding for the witness member; uncertain rows remain nullable.
- Referential risk: protected verification shareholdings cannot be deleted while referenced. New
  witnesses always store the exact qualifying row selected by the existing active-positive rule.
- Index risk: automatic indexes were disabled only where the existing named application/PAN/Aadhaar
  indexes already cover the same columns. Physical schema inspection asserts exactly one index per
  required column set.
- Contract risk: adds `verification_shareholding_id` and makes `folio_number` explicitly snapshot
  based. Existing fields, permissions, object scope, masking, qualification, audit action, and
  workflow behavior are preserved.
- Input risk: malformed/non-object JSON is now caught at this nested adapter and standardized as
  400; unknown/missing-field behavior remains service-owned.
- Frontend risk: none; no frontend code changed. All frontend regression gates passed.
- Controls: API red/green, migration backfill/reverse/idempotency/index tests, 11 focused witness
  tests, 394 backend tests at 94% coverage, and all configured frontend/backend gates.
- Residual risk: legacy audit metadata may be incomplete; nullable provenance deliberately exposes
  that uncertainty rather than guessing. A-063 owns any future authoritative remediation.
