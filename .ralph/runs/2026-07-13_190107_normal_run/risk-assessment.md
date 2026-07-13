# Risk Assessment

Risk level: Medium

- Selected slice: 007H-credit-sanction-register
- Mode: normal_run
- Standing approval: applies; no owner veto is present.
- Money/compliance impact: the slice freezes requested, eligible, recommended, and sanctioned
  amounts plus statutory-style register references. It does not calculate new money or approval
  authority.
- Permission impact: two existing source permissions gate the read endpoints; the canonical seed
  grants register read only to CFO, Director, Company Secretary, and Internal Auditor.
- Data impact: one migration adds the generated register with one-to-one case/workflow identity,
  nullable sanction linkage for rejected outcomes (A-088), decision/link constraints, indexes, and
  application-level instance/queryset immutability guards.
- Privacy impact: borrower identity and approval names are internal register fields. General
  Meeting document ids are metadata only and do not grant download access.
- Residual risks: direct SQL and privileged database operators remain outside application-level
  immutability; production database privileges/auditing must retain that control. Annexure K is
  blocked under OC-002/A-087. The independent architecture review cadence is now due.
- Mitigations verified: atomic transaction rollback, exact case-frozen sources, permission
  negatives, no mutation route, audit/workflow linkage, database consistency constraints,
  RED/GREEN tests, full backend/frontend gates, and independent standards/spec review.
