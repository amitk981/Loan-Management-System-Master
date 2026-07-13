# Risk Assessment

Risk level: High (standing approval; no veto)

- Financial/decision risk: appraisal decisions now use copied canonical public projections rather
  than mutable current assessments. Same-UUID rerun and amount-boundary regressions prove the
  frozen behavior.
- Database risk: one additive migration adds two JSON projections, provenance, repayment notes,
  and submission remarks. Safe legacy copy requires both source timestamps and audit chronology;
  uncertain rows remain blocked rather than being silently relabelled.
- Permission risk: revalidation requires `credit.appraisal.update`,
  `credit.risk_assessment.manage`, existing application object scope, draft state, and
  `legacy_unverified` provenance. It is one-way and cannot repin verified appraisals.
- Privacy/audit risk: projections use existing redacted public contracts. Free-text summaries,
  repayment notes, risk mitigation, and submit remarks are excluded from audit JSON.
- Transaction risk: create, PATCH, revalidation, and submit are atomic with audit/workflow evidence;
  forced audit/workflow failures roll back domain and evidence writes.
- Concurrency risk: loan-limit locking/calculation code is unchanged. Existing PostgreSQL tests are
  still mandatory for changes to the calculator/import seam; the exact command is in the review
  packet. SQLite's two skips are explicitly not concurrency proof.
- Rollback: reverse the additive migration only before later review data depends on the new fields;
  otherwise retain columns and disable the new action through a corrective slice. No destructive
  data rewrite is present.
- Protected/source files: untouched. No dependency or frontend change.
- Manual review: orchestrator validation and commit only; focus on migration chronology and
  metadata redaction.
