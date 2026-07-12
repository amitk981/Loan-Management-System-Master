# Risk Assessment

Risk level: High.

- Selected slice: 006Z3-active-member-supply-evidence-boundary-hardening
- Mode: normal_run
- Manual review required: yes; independent Ralph validation must confirm the strict contract and
  full-suite behavior before commit/merge.
- Primary risks: eligibility false positives/negatives, stale-write evidence duplication, portal
  totals diverging from staff eligibility, and legacy fixtures silently relying on active flags.
- Mitigations: one immutable public member projection; atomic member-version lock on capture;
  maker-checker supply-record lock on verification; explicit non-qualifying row reasons; shared
  portal/credit consumption; focused and full-suite gates.
- Data/security: metadata-only audit/history projections remain unchanged; portal scope remains
  derived from PortalAccount and exposes neither member IDs nor staff actions.
- Schema/dependency/deployment impact: none.
