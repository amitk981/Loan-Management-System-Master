# Risk Assessment

Risk level: Medium (slice-declared), with schema/routing changes requiring Ralph's fail-closed
independent backend lane.

- Selected slice: `011J-archive-record-and-retention`
- Mode: `normal_run`
- Data integrity: one migration adds the one-per-loan/closure archive manifest, immutable manager,
  database location/date/destruction constraints, protected foreign keys, and unique replay key.
- Concurrency: creation locks the retained closure before checking/creating the manifest and advances
  the archive requirement in the same transaction. The exact declared PostgreSQL class contains one
  five-racer test; local SQLite confirmed discovery and skip, while trusted PostgreSQL validation
  must execute it.
- Permission/privacy: create is limited to Compliance/CS with Compliance object scope; reads add only
  those roles and governed Internal Auditor scope. Borrowers are explicitly denied. Creation,
  detail/search access, and denials are audited without physical/digital paths or search text.
- Retention: start is always the retained closure date. The server supplies the eight-calendar-year
  minimum and rejects a shorter caller date. A later supplied obligation may lengthen, never shorten,
  retention.
- Immutability/destruction: location correction, deletion, certificate capture, and destruction are
  unavailable. Database constraints keep the persisted destruction fields false/null; the response
  exposes date eligibility only as information with no available action.
- Reverse consumers: financial close, NOC, security return, document download, and audit tests ran in
  a 62-test focused pack. Closure/NOC/security records and loan status history are not rewritten by
  archive creation.
- Dependencies: none added. Frontend: untouched; slice 011P owns archive UI.
- Residual validation risk: PostgreSQL scheduling/locking semantics and the authoritative impacted or
  complete suite remain Ralph-owned and must pass before commit.
