# Risk Assessment

Risk level: Low for this review's mutations; High product findings.

- Selected slice: architecture-review
- Mode: architecture_review
- Reviewed product boundary: `e3d965ad` through commits `35dd95ce`, `4bdff96c`, `9b1113af`, and
  `4bebe1af`
- Production code changed: no
- Database/schema changed: no
- Protected files or `docs/source/` changed: no

## Material Findings

- High: communications migration 0008 promotes an internally checksummed queued outbox with a
  blank required template fact to verified provenance, violating the binding H9A contract.
- High: advice-only authority can read and resolve a generic assigned exception (and vice versa by
  the same union policy), violating backend permission and working API contracts.
- Medium: provider vocabulary/pagination, the communications adapter/task boundary, required
  cross-channel replay coverage, and the MP14 opposite-order selection regression remain partial.

## Controls and Disposition

- The three failing probes are retained verbatim as independent evidence; they were not converted
  into product fixes in architecture-review mode.
- One High-risk root-owner corrective (`009H9D`) covers both High defects and related communications
  Medium symptoms, and 009J now depends on it.
- Focused retained tests remain green (74 backend and 10 frontend); PostgreSQL-only race evidence
  remains in the accepted H9B/H9C run folders.
- No new business rule or architecture decision was invented, so no ADR or assumption was added.

Manual review is recommended before promoting `staging` to `main`, with 009H9D treated as the
immediate release-blocking correction.
