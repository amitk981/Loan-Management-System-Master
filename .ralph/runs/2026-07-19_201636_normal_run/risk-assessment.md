# Risk Assessment

Risk level: High

- Selected slice: CR-013-epic-009-terminal-owner-boundary-correction
- Mode: normal_run
- Manual review required: yes; independent validation must confirm public nondisclosure and mutation
  parity because the corrected selectors protect member and financial records.

## Material risks and controls

- **Disclosure or count oracle:** stale transfer/initiation identities could appear in totals,
  pagination, lists, or detail even when projection rejects them. Control: apply owner-backed SQL
  filters before count and pagination, with public 0/empty/404 regressions and PostgreSQL coverage.
- **Stale financial mutation:** broad read eligibility could accidentally widen action authority.
  Control: action/mutation owners remain unchanged, terminal evidence is matched by exact immutable
  identities, and paired regressions retain denial behavior.
- **Historical data integrity:** blindly populating a new SAP checksum could legitimize incoherent
  legacy delivery evidence. Control: migration backfill is limited to sent/completed rows whose file
  snapshot still equals the retained file and whose checksum is a 64-character SHA-256 value;
  unmatched data remains blank/fail-closed.
- **Fixture/data collision:** independently seeded E2E families shared governed template identities.
  Control: template reuse is keyed by the existing domain uniqueness identity, with reverse-order
  and idempotency regressions. The Epic 009 runtime asset is synthetic and contains no production
  data.
- **Performance:** the new account selector uses correlated `Exists` predicates. Control: it runs
  within the existing database-pageable candidate query and the bounded PostgreSQL acceptance label
  remains green. Independent validation should retain the configured query ceiling.

## Scope and reversibility

No external services were called, no production data was changed, no dependency was added, and no
frontend presentation contract changed. Product changes are limited to owner selectors, a bounded
historical migration, seed composition, and regressions. Reversion is source-level; migration
reverse intentionally leaves backfilled evidence intact because erasing coherent evidence would be
more destructive than preserving it.
