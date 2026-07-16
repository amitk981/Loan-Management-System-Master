# Risk Assessment

Risk level: High (owner standing approval applies; no veto is recorded).

- The slice changes immutable compliance evidence and the authority boundary between applications
  and approvals. A stale or malformed sanction cycle now denies bank writes and downstream
  checklist truth, which is intentionally fail-closed.
- Migration `applications.0017` adds two nullable indexed UUID snapshots. Nullable state preserves
  historical rows honestly; rows without exact terminal ids cannot become current checklist truth.
  No applied migration is rewritten and migration drift is clean.
- MP11 now treats incomplete or contradictory workflow evidence as `evidence_invalid`. This can
  block a borrower resubmission that previously succeeded from row existence alone, which is the
  source-required integrity correction; staff deficiency rows are never auto-resolved.
- The application row is the shared lock for bank decisions and approval-cycle invalidation. The
  PostgreSQL race ran twice and proved either one current-cycle writer with one exact evidence
  ledger or an invalidated-cycle denial with zero writer artifacts.
- Privacy impact is reduced: denials remain 403/404-style nondisclosing and neither API exposes
  internal response workflow ids. No sensitive bank value, storage fact, or plaintext identity was
  added to audit/version evidence.
- Rollback requires reversing only migration 0017 plus these code changes before new snapshot-bound
  decisions are relied upon. No destructive data migration or external side effect exists.
