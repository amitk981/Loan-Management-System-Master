# Risk Assessment

Risk level: High

- Selected slice: `008D2-stamp-notary-verification-authority-closure`
- Mode: `normal_run`
- Manual review required: No; the owner's standing Ralph approval applies and no veto exists.
- Data/schema: One additive migration adds nullable protected preparer identities and non-conflicting
  reverse names for verifier identities. It performs no destructive rewrite. A-108 deliberately
  leaves pre-attribution rows nullable instead of inventing a maker.
- Legal/compliance: Stamp/notary outcomes affect later legal readiness. All positive/adverse outcomes
  now require active Company Secretary authority and a distinct retained Compliance preparer;
  preparers cannot downgrade or replace checker evidence. Corrections retain old/new attribution.
- Concurrency: Five changed checker submissions serialize under the owning loan-document lock.
  Two final PostgreSQL runs prove one current row and all six attributable ledger entries.
- Access/disclosure: The documents module exposes generic immutable upload facts only. Legal role,
  category, purpose, and same-application policy is enforced in `legal_documents`; responses remain
  metadata-only and no download audit or descriptor is produced.
- Compatibility: New HTTP parsing remains exact and direct callers use the same parser. Legacy rows
  may replay exactly but cannot be changed without real maker evidence. This fail-closed behavior is
  recorded in A-108 and sharpened into 008F.
- Money/business rule: Supplied stamp amounts are persisted; no ₹500/ad-valorem calculation or
  override path was invented.
- External effects: None. No deployment, communication, payment, download, or external service call.
