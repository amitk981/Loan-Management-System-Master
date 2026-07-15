# Risk Assessment

Risk level: High — covered by the owner's standing approval; no revocation applies.

- The migration transfers Django state ownership for two retained legal/security tables and adds
  activation evidence columns plus a strengthened active-state constraint. It does not rename or
  recreate the live tables. Migration tests preserve a package and fully linked active PoA; SQLite
  and PostgreSQL paths are independently exercised.
- Package access now fails closed unless canonical latest-cycle terminal sanction facts match the
  checklist's immutable creation-cycle ids. This intentionally removes status-only access.
- PoA activation changes legal authority: Compliance is the mutable draft maker, a distinct active
  Company Secretary is checker/attorney, and active is terminal. The frozen evidence and generic
  document-consumption audit prevent later signature/stamp/notary rewrite.
- Legacy active PoAs cannot truthfully supply the newly required workflow identity. A-112 preserves
  them as readable terminal history with an explicit legacy marker and rejects PATCH replay.
- No external calls, frontend behavior, package readiness, invocation/release, share custody,
  repayment, disbursement, or loan-account behavior was added.

Mitigations: authority-first tests, exact-cycle tests, transaction locks, database constraints,
state/table preservation tests, full regression coverage, and twice-run PostgreSQL five-worker
activation/downgrade races.
